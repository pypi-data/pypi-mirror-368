#!/usr/bin/env python3
"""
Test script to run ReAct agents against Crafter environment using LM class with Synth backend.
This demonstrates using the LM class with Synth models through native integration.

This version properly handles the provider routing to use Synth/Modal endpoints.
"""

import asyncio
import json
import uuid
import math
import argparse
import toml
import logging
import time
import functools
from datetime import datetime
from typing import Dict, Any, Optional, List, Set, Literal
from pydantic import BaseModel, Field
from httpx import AsyncClient
import httpx
import sys
import os
from pathlib import Path
from tqdm.asyncio import tqdm_asyncio
from tqdm import tqdm
import random
import glob
from collections import defaultdict

# Configure logging to suppress noisy third-party logs when in quiet mode
def setup_logging(quiet_mode: bool = False):
    """Setup logging configuration."""
    if quiet_mode:
        # Suppress most third-party logging in quiet mode
        logging.getLogger("httpx").setLevel(logging.ERROR)
        logging.getLogger("synth_ai.tracing_v2.duckdb.manager").setLevel(logging.ERROR)
        logging.getLogger("synth_ai.tracing_v2").setLevel(logging.ERROR)
        logging.getLogger("duckdb").setLevel(logging.ERROR)
        # Also set the root logger for synth_ai tracing to be quiet
        logging.getLogger("synth_ai.tracing_v2.duckdb").setLevel(logging.ERROR)
        logging.getLogger("synth_ai.tracing_v2.session_tracer").setLevel(logging.ERROR)
        # Suppress httpcore as well (used by httpx)
        logging.getLogger("httpcore").setLevel(logging.ERROR)
    else:
        # Normal logging levels
        logging.getLogger("httpx").setLevel(logging.INFO)
        logging.getLogger("synth_ai.tracing_v2.duckdb.manager").setLevel(logging.INFO)
        logging.getLogger("synth_ai.tracing_v2").setLevel(logging.INFO)

# Set default logging to avoid noisy logs during import
setup_logging(quiet_mode=True)

# Setup environment
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent))

# Disable v1 logging to see v2 tracing clearly
os.environ["LANGFUSE_ENABLED"] = "false"
os.environ["SYNTH_LOGGING"] = "false"

import numpy as np

# Import Synth warmup utilities  
from synth_ai.lm.warmup import warmup_synth_model
from synth_ai.lm.config import SynthConfig

# Import session tracer for v2 tracing
from synth_ai.tracing_v2.session_tracer import (
    SessionTracer, SessionEventMessage, TimeRecord,
    RuntimeEvent, EnvironmentEvent, LMCAISEvent
)
from synth_ai.tracing_v2.utils import create_experiment_context
from synth_ai.tracing_v2.duckdb.manager import DuckDBTraceManager
from synth_ai.tracing_v2.decorators import (
    set_active_session_tracer, set_system_id, set_turn_number, get_config
)
from synth_ai.environments.examples.crafter_classic.trace_hooks import CRAFTER_HOOKS
from datetime import datetime

# Import LM components
from synth_ai.lm.core.main_v2 import LM

# Import Crafter hooks
try:
    from synth_ai.environments.examples.crafter_classic.trace_hooks import CRAFTER_HOOKS
    print(f"✅ Loaded {len(CRAFTER_HOOKS)} Crafter achievement hooks (Easy, Medium, Hard)")
except ImportError:
    print("Warning: Could not import CRAFTER_HOOKS")
    CRAFTER_HOOKS = []

# Configuration constants
HTTP_TIMEOUT = 30.0  # Increased from 10.0 for better handling of concurrent load and LM response times
MAX_RETRIES = 3
RETRY_DELAY = 1.0


def cleanup_old_files():
    """Clean up old trace files and result files to keep directory clean."""
    # Remove old JSON result files (keep only the latest 5)
    result_files = glob.glob("crafter_lm_synth_results_*.json")
    if len(result_files) > 5:
        # Sort by modification time and keep only the latest 5
        result_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        for old_file in result_files[5:]:
            try:
                os.remove(old_file)
                print(f"🗑️  Cleaned up old result file: {old_file}")
            except OSError:
                pass
    
    # Remove old JSON trace files (keep only DuckDB)
    trace_dirs = ["traces_v2_synth", "traces_v2_lm_synth"]
    for trace_dir in trace_dirs:
        if os.path.exists(trace_dir):
            json_files = glob.glob(f"{trace_dir}/session_*.json")
            for json_file in json_files:
                try:
                    os.remove(json_file)
                    print(f"🗑️  Cleaned up old trace file: {json_file}")
                except OSError:
                    pass


def setup_synth_environment():
    """Setup environment variables for Synth/Modal endpoints."""
    synth_base_url = os.getenv('SYNTH_BASE_URL') or os.getenv('MODAL_BASE_URL')
    synth_api_key = os.getenv('SYNTH_API_KEY') or os.getenv('MODAL_API_KEY')
    
    if not synth_base_url or not synth_api_key:
        raise ValueError("SYNTH_BASE_URL/MODAL_BASE_URL and SYNTH_API_KEY/MODAL_API_KEY must be set")
    
    # OpenAI client needs base URL WITH /v1 (it doesn't add it automatically)
    # Ensure /v1 is present
    if not synth_base_url.endswith('/v1'):
        synth_base_url = synth_base_url.rstrip('/') + '/v1'
    synth_base_url = synth_base_url.rstrip('/')
    
    # Set environment variables for OpenAI client to use Synth endpoints
    os.environ["OPENAI_API_BASE"] = synth_base_url
    os.environ["OPENAI_BASE_URL"] = synth_base_url
    os.environ["OPENAI_API_KEY"] = synth_api_key
    
    return synth_base_url, synth_api_key


async def retry_http_request(client: AsyncClient, method: str, url: str, **kwargs) -> Any:
    """Retry HTTP requests with exponential backoff and jitter."""
    last_exception = None
    
    for attempt in range(MAX_RETRIES):
        try:
            if attempt > 0:
                delay = min(RETRY_DELAY * (2 ** (attempt - 1)), RETRY_DELAY * 2) # Use RETRY_DELAY
                jitter = random.uniform(0, 0.1 * delay)
                total_delay = delay + jitter
                await asyncio.sleep(total_delay)
            
            response = await client.request(method, url, timeout=HTTP_TIMEOUT, **kwargs)
            
            if response.status_code < 500:
                return response
            
            last_exception = Exception(f"HTTP {response.status_code}: {response.text}")
            
        except httpx.ReadError as e:
            last_exception = e
            if attempt < MAX_RETRIES - 1:
                read_error_delay = min(1.0 * (2 ** attempt), 5.0)
                await asyncio.sleep(read_error_delay)
        except Exception as e:
            last_exception = e
    
    print(f"    ❌ HTTP request failed after {MAX_RETRIES} attempts: {type(last_exception).__name__}: {str(last_exception)[:200]}")
    raise last_exception


def create_message(content: Any, message_type: str, origin_system_id: Any, turn: int) -> SessionEventMessage:
    """Create a message with origin system ID embedded in content."""
    return SessionEventMessage(
        content={
            "origin_system_id": str(origin_system_id),
            "payload": content
        },
        message_type=message_type,
        time_record=TimeRecord(
            event_time=datetime.now().isoformat(),
            message_time=turn
        )
    )


def compress_observation_for_trace(obs: Dict[str, Any]) -> Dict[str, Any]:
    """Compress observation for trace storage to avoid huge trace files."""
    compressed = obs.copy()
    
    # Compress semantic map if present
    if "semantic_map" in compressed:
        del compressed["semantic_map"]
    
    # Compress other large fields
    if "rgb" in compressed:
        del compressed["rgb"]
    
    return compressed


def format_semantic_map_view_v2(obs: Dict[str, Any], view_size: int = 7) -> str:
    """Format a semantic map view around the player with normal names."""
    # Get semantic map
    semantic_map = obs.get("semantic_map")
    if semantic_map is None:
        return "No semantic map available"
    
    # Convert to numpy array if needed
    sem_arr = np.asarray(semantic_map)
    if sem_arr.ndim == 1:
        # Assuming square map, reshape
        size = int(np.sqrt(sem_arr.size))
        sem_arr = sem_arr.reshape(size, size)
    
    # Get player position
    player_pos = obs.get("player_position", [sem_arr.shape[0]//2, sem_arr.shape[1]//2])
    px, py = int(player_pos[0]), int(player_pos[1])
    
    # Create view
    half = view_size // 2
    lines = []
    visible_items = set()
    
    # Map of semantic indices to normal names (not symbols)
    name_map = {
        0: 'grass',      # Empty/grass
        1: 'tree',       # Tree  
        2: 'stone',      # Stone
        3: 'coal',       # Coal
        4: 'iron',       # Iron
        5: 'table',      # Crafting table
        6: 'furnace',    # Furnace
        7: 'diamond',    # Diamond
        8: 'water',      # Water
        9: 'lava',       # Lava
        10: 'sand',      # Sand
        11: 'zombie',    # Enemy/Zombie
        12: 'skeleton',  # Skeleton
        13: 'cow',       # Cow
        14: 'unknown',   # Unknown/Other
    }
    
    for dy in range(-half, half + 1):
        row = []
        for dx in range(-half, half + 1):
            x, y = px + dx, py + dy
            
            if dx == 0 and dy == 0:
                row.append('you')  # Player
            elif 0 <= x < sem_arr.shape[0] and 0 <= y < sem_arr.shape[1]:
                val = int(sem_arr[x, y])
                item_name = name_map.get(val, 'unknown')
                row.append(item_name)
                if item_name not in ['grass', 'you']:
                    visible_items.add(item_name)
            else:
                row.append('void')  # Out of bounds
        
        lines.append(' '.join(row))
    
    # Add legend of visible items
    legend = f"Visible items: {', '.join(sorted(visible_items))}" if visible_items else "No special items visible (mostly grass)"
    
    return "\n".join(lines) + "\n" + legend


def get_openai_tools():
    """Get OpenAI-compatible tool definitions for Synth models."""
    return [
        {
            "type": "function",
            "function": {
                "name": "interact",
                "description": "Perform actions in the Crafter environment.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "actions": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "List of actions to perform in sequence (e.g., ['move_right', 'move_right', 'do']). Available actions: move_left, move_right, move_up, move_down, do, sleep, place_stone, place_table, place_furnace, place_plant, make_wood_pickaxe, make_stone_pickaxe, make_iron_pickaxe, make_wood_sword, make_stone_sword, make_iron_sword, noop"
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Reasoning for these actions"
                        }
                    },
                    "required": ["actions", "reasoning"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "terminate",
                "description": "End the episode when finished or no progress can be made.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "reason": {
                            "type": "string",
                            "description": "Reason for termination"
                        }
                    },
                    "required": ["reason"]
                }
            }
        }
    ]


# --- Configuration Class ---
class CrafterConfig:
    """Configuration for Crafter evaluation with Synth backend."""

    def __init__(self, config_path: Optional[str] = None):
        # Default values
        self.model_name: Optional[str] = None
        self.num_instances = 1
        self.max_turns = 2
        self.difficulty = "easy"
        self.service_base_url = "http://localhost:8901"
        self.service_timeout = 30.0
        self.seed = 42
        self.save_traces = True
        self.save_detailed_results = True
        self.verbose = False
        self.quiet = False  # Add quiet mode support
        self.analyze_traces = False
        
        # V2 tracing settings
        self.enable_v2_tracing = True
        self.v2_trace_dir = "./traces_v2_lm_synth"
        self.duckdb_only = True  # Store in DuckDB only, no individual JSON files
        self.auto_cleanup = True  # Clean up old files automatically
        
        # Synth-specific settings
        self.warmup_model = True
        self.warmup_max_attempts = 30
        self.warmup_timeout = 60.0  # Default timeout in seconds
        self.use_synth_backend = True  # Flag to indicate Synth backend
        
        # Load from TOML if provided
        if config_path and os.path.exists(config_path):
            self.load_from_toml(config_path)

    def load_from_toml(self, config_path: str):
        """Load configuration from TOML file."""
        config = toml.load(config_path)

        eval_config = config.get("eval", {})
        self.model_name = eval_config.get("model_name", self.model_name)
        self.num_instances = eval_config.get("episodes", self.num_instances)
        self.max_turns = eval_config.get("max_steps", self.max_turns)
        self.difficulty = eval_config.get("difficulty", self.difficulty)
        self.seed = eval_config.get("seed", self.seed)

        service_config = config.get("service", {})
        self.service_base_url = service_config.get("base_url", self.service_base_url)
        self.service_timeout = service_config.get("timeout", self.service_timeout)

        output_config = config.get("output", {})
        self.save_traces = output_config.get("save_traces", self.save_traces)
        self.save_detailed_results = output_config.get(
            "save_detailed_results", self.save_detailed_results
        )
        
        # V2 tracing config
        tracing_config = config.get("tracing_v2", {})
        self.enable_v2_tracing = tracing_config.get("enabled", self.enable_v2_tracing)
        self.v2_trace_dir = tracing_config.get("trace_dir", self.v2_trace_dir)
        self.duckdb_only = tracing_config.get("duckdb_only", self.duckdb_only)
        self.auto_cleanup = tracing_config.get("auto_cleanup", self.auto_cleanup)
        
        # Synth config
        synth_config = config.get("synth", {})
        self.warmup_model = synth_config.get("warmup_model", self.warmup_model)
        self.warmup_max_attempts = synth_config.get("warmup_max_attempts", self.warmup_max_attempts)
        self.warmup_timeout = synth_config.get("warmup_timeout", self.warmup_timeout)
        self.use_synth_backend = synth_config.get("use_synth_backend", self.use_synth_backend)


# --- Base ReAct Agent using LM with Synth ---
class BaseReActAgentWithLMSynth:
    """Base ReAct agent using LM class configured for Synth backend."""

    def __init__(self, model_name: str, max_turns: int = 20, verbose: bool = False, 
                 tracer: Optional[SessionTracer] = None, episode_id: int = 0, quiet: bool = False):
        self.model_name = model_name
        self.max_turns = max_turns
        self.verbose = verbose
        self.quiet = quiet
        self.history = []
        self.system_name = "base-react-agent-lm-synth"
        self.tools = get_openai_tools()
        self.tracer = tracer
        self.system_id = f"{self.system_name}_{uuid.uuid4()}"
        self.episode_id = episode_id
        
        # Setup Synth environment variables
        setup_synth_environment()
        
        # Create LM instance with synth provider
        self.lm = LM(
            model_name=model_name,
            formatting_model_name=model_name,
            temperature=0.7,  # Add some randomness to prevent identical responses
            synth_logging=False,  # Disable v1 tracing
            provider="synth",  # Use synth provider
            session_tracer=tracer,
            system_id=self.system_id,
            enable_v2_tracing=True,
        )
        
        # Agent state tracking
        self.agent_state = {
            "message_history": [],
            "steps_taken": 0,
            "steps_remaining": max_turns,
            "total_tokens_used": 0,
            "tool_calls_made": 0,
            "current_turn": 0
        }

    async def decide(self, obs: str, system_message: str, turn: int) -> Dict[str, Any]:
        """Get agent decision based on observation using LM class with Synth backend."""
        # Update agent state
        self.agent_state["current_turn"] = turn
        self.agent_state["steps_taken"] = turn
        self.agent_state["steps_remaining"] = self.max_turns - turn
        
        # Create conversation context with unique episode ID to prevent caching
        context = f"Episode {self.episode_id} - Turn {turn + 1}/{self.max_turns}\n\n{obs}"
        
        # Build messages in OpenAI format for tools
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": context}
        ]
        
        # Add to message history
        self.agent_state["message_history"].extend(messages)
        
        # Truncate history if too long
        max_history_length = 20
        if len(self.agent_state["message_history"]) > max_history_length:
            self.agent_state["message_history"] = (
                [self.agent_state["message_history"][0]] +
                self.agent_state["message_history"][-(max_history_length-1):]
            )
        
        try:
            llm_start = time.time()
            
            # Only show LM call logs if verbose enabled
            # Note: self.verbose is not directly available but could be passed in
            
            # Print the full prompt on the final turn to debug achievements
            if turn == self.max_turns - 1:
                print("\n🔍 FINAL TURN PROMPT:")
                print("="*80)
                print(f"System: {system_message[:200]}...")
                print(f"\nUser message:\n{context}")
                print("="*80)
            
            # Call LM with turn number for v2 tracing
            # The LM class should handle Synth routing internally
            response = await self.lm.respond_async(
                messages=messages,
                turn_number=turn,
                # Pass tools in the format expected by LM class
                # This might need adjustment based on LM implementation
                tools=self.tools
            )
            
            llm_end = time.time()
            
            # Parse the response to extract tool calls
            # The LM class returns a BaseLMResponse
            raw_response = response.raw_response
            
            # Check if response has tool calls
            if hasattr(response, 'tool_calls') and response.tool_calls:
                # Parse tool calls from response
                tool_call = response.tool_calls[0]
                decision = {
                    "name": tool_call.get("name", "interact"),
                    "parameters": tool_call.get("parameters", {})
                }
            else:
                # Parse from raw response
                decision = self._parse_tool_response(raw_response)
            
            # Update agent state
            self.agent_state["tool_calls_made"] += 1
            
            # Add assistant response to history
            assistant_message = {
                "role": "assistant",
                "content": raw_response
            }
            self.agent_state["message_history"].append(assistant_message)
            
            if self.verbose:
                print(f"🤖 LM Response (turn {turn}): {json.dumps(decision, indent=2)}")
                print(f"📊 Response time: {llm_end - llm_start:.2f}s")
            
            # Suppress noisy tool call logs - only show minimal info
            if not self.quiet:
                print(f"\n🔧 Turn {turn + 1} - Tool Call: {decision['name']}")
                if decision['name'] == 'interact':
                    print(f"   Actions: {decision['parameters'].get('actions', [])}")
                    print(f"   Reasoning: {decision['parameters'].get('reasoning', 'No reasoning provided')}")
                elif decision['name'] == 'terminate':
                    print(f"   Reason: {decision['parameters'].get('reason', 'No reason provided')}")

        except Exception as e:
            print(f"❌ Error in LM decide: {e}")
            import traceback
            traceback.print_exc()
            # Fallback decision
            decision = {
                "name": "interact",
                "parameters": {
                    "actions": ["do"],
                    "reasoning": f"Error occurred: {str(e)}"
                }
            }

        return decision
    
    def _parse_tool_response(self, raw_response: str) -> Dict[str, Any]:
        """Parse raw LM response to extract tool calls."""
        # Try to parse JSON if present
        try:
            # Look for JSON in the response
            import re
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                if "name" in data:
                    return data
                elif "function" in data:
                    return {
                        "name": data["function"].get("name", "interact"),
                        "parameters": data["function"].get("arguments", {})
                    }
        except:
            pass
        
        # Fallback to text parsing
        if "terminate" in raw_response.lower():
            return {
                "name": "terminate",
                "parameters": {
                    "reason": "Agent decided to terminate"
                }
            }
        
        # Try to extract actions from the response
        actions = []
        action_keywords = [
            "move_up", "move_down", "move_left", "move_right", "do", "sleep",
            "place_stone", "place_table", "place_furnace", "place_plant",
            "make_wood_pickaxe", "make_stone_pickaxe", "make_iron_pickaxe",
            "make_wood_sword", "make_stone_sword", "make_iron_sword"
        ]
        
        for keyword in action_keywords:
            if keyword in raw_response.lower():
                actions.append(keyword)
        
        if not actions:
            actions = ["do"]  # Default action
        
        return {
            "name": "interact",
            "parameters": {
                "actions": actions,  # Return as array of actions
                "reasoning": "Parsed from response"
            }
        }

    def get_system_message(self) -> str:
        """Return system message for agent. Override in subclasses."""
        return """You are an AI agent playing Crafter. Use the available tools to interact with the environment.

CRITICAL RULE: You MUST provide MULTIPLE actions (2-5) in EVERY interact() tool call!

The 'interact' function accepts a LIST of 1-5 actions. ALWAYS provide 2-5 actions for efficiency.

GOOD Examples (what you SHOULD do):
✓ interact(actions=["move_right", "move_right", "do"], reasoning="Move to tree and collect wood")
✓ interact(actions=["move_up", "move_up", "move_right", "do"], reasoning="Navigate to stone and mine it")
✓ interact(actions=["place_table", "make_wood_pickaxe", "move_left"], reasoning="Craft and continue exploring")

BAD Examples (what you should AVOID):
✗ interact(actions=["move_right"], reasoning="Move right") - TOO FEW ACTIONS!
✗ interact(actions=["do"], reasoning="Collect") - TOO FEW ACTIONS!

REMEMBER: Single actions waste time. Always plan 2-5 actions ahead and execute them together!"""

    def format_observation(self, obs: Dict[str, Any]) -> str:
        """Format observation for agent. Override in subclasses."""
        return str(obs)


# --- Crafter-specific ReAct Agent ---
class CrafterReActAgentWithLMSynth(BaseReActAgentWithLMSynth):
    """Crafter-specific ReAct agent with enhanced prompting for Synth models."""

    def get_system_message(self) -> str:
        """Return Crafter-specific system message optimized for Synth models."""
        return """You are CrafterAgent playing Crafter survival environment. Your goal is to unlock as many achievements as possible while staying alive.

You will see a semantic map view showing your surroundings. Use this to navigate toward resources.

Key mechanics:
• 'do' action: collect wood from trees, stone from deposits, food from cows/plants
• 'do' does nothing on grass/water - move to find resources first
• Craft progression: wood → table → wood_pickaxe → stone → stone_pickaxe → iron tools
• Sleep when energy low to restore and unlock wake_up achievement
• Use semantic map view to navigate toward resources you can see

Available actions: move_left, move_right, move_up, move_down, do, sleep, place_stone, place_table, place_furnace, place_plant, make_wood_pickaxe, make_stone_pickaxe, make_iron_pickaxe, make_wood_sword, make_stone_sword, make_iron_sword, noop

KEY ACHIEVEMENTS TO UNLOCK:
Basic Resource Collection (PRIORITY #1):
- collect_wood: Move NEXT TO a tree, then use action="do" to collect wood
- collect_stone: Move NEXT TO stone, then use action="do" (requires wood_pickaxe in inventory)
- collect_coal: Move NEXT TO coal, then use action="do" (requires stone_pickaxe)
- collect_iron: Move NEXT TO iron, then use action="do" (requires stone_pickaxe)
- collect_diamond: Move NEXT TO diamond, then use action="do" (requires iron_pickaxe)

Tool Crafting (enables resource collection):
- make_wood_pickaxe: Use action="make_wood_pickaxe" when you have wood (unlocks ability to mine stone)
- make_stone_pickaxe: Use action="make_stone_pickaxe" when you have wood and stone (unlocks coal/iron mining)
- make_iron_pickaxe: Use action="make_iron_pickaxe" when you have wood, coal, and iron (unlocks diamond mining)

Weapon Crafting (for defense):
- make_wood_sword: Use action="make_wood_sword" when you have wood
- make_stone_sword: Use action="make_stone_sword" when you have wood and stone  
- make_iron_sword: Use action="make_iron_sword" when you have wood, coal, and iron

Survival Actions:
- eat_plant: Use action="eat_plant" when food < 9 and you see a plant nearby
- eat_cow: Move NEXT TO cow, use action="do" to kill it, then action="eat_cow"
- collect_drink: Move NEXT TO water, then use action="drink" when drink < 9
- sleep: Use action="sleep" when energy < 5 (restores energy to 9)

Building/Placing:
- place_table: Use action="place_table" when you have wood (enables advanced crafting)
- place_furnace: Use action="place_furnace" when you have stone (for smelting)
- place_plant: Use action="place_plant" when you have sapling (grows into tree)
- place_stone: Use action="place_stone" when you have stone (creates barrier)

Combat:
- defeat_zombie: Move NEXT TO zombie, then use action="do" repeatedly to attack
- defeat_skeleton: Move NEXT TO skeleton, then use action="do" repeatedly to attack

CRITICAL: The action="do" is your INTERACTION button! Use it when adjacent to:
- Trees → get wood
- Stone/Coal/Iron/Diamond → mine resources (need appropriate pickaxe)
- Enemies → attack them
- Cows → kill for food

Simple Strategy:
1. Look for resources (trees, stones) in the semantic map
2. Move toward the nearest resource
3. When adjacent to a resource, use action="do" to collect it
4. If you have wood, try action="make_wood_pickaxe"
5. Repeat: find resources, move to them, use "do"

Critical Gameplay Tips:
- You must be ADJACENT (one tile away) to objects to interact with them
- Use "do" when next to: trees (for wood), stone (for stone), coal, iron, diamond
- Use "do" to attack zombies/skeletons when adjacent
- First priority: Find a tree, move next to it, then use "do" to collect wood
- Wood is essential for crafting your first pickaxe
- With wood_pickaxe you can mine stone, with stone_pickaxe you can mine iron, etc.

CRITICAL INSTRUCTION: You MUST ALWAYS provide MULTIPLE actions (2-5) in EVERY interact() tool call!

The 'interact' function accepts a LIST of 1-5 actions. NEVER use single actions - always plan 2-5 actions ahead!

MANDATORY action sequences (ALWAYS use multiple):
✓ interact(actions=["move_right", "move_right", "do"], reasoning="Move to tree and collect wood") 
✓ interact(actions=["move_up", "move_up", "move_right", "do"], reasoning="Navigate and collect")
✓ interact(actions=["place_table", "make_wood_pickaxe", "move_left", "move_left"], reasoning="Craft and explore")
✓ interact(actions=["do", "move_right", "do", "move_right", "do"], reasoning="Collect multiple resources")

FORBIDDEN (NEVER do this):
✗ interact(actions=["move_right"], ...) - WRONG! Too few actions!
✗ interact(actions=["do"], ...) - WRONG! Too few actions!

RULE: If you use less than 2 actions, you are playing inefficiently. Always think 2-5 steps ahead!

Key Strategy:
1. Plan a sequence of moves to reach resources
2. Execute multiple moves in one tool call (e.g., ["move_right", "move_right", "move_up"])
3. When adjacent to a resource, use "do" to collect it
4. Chain crafting actions together (e.g., ["place_table", "make_wood_pickaxe"])

Remember:
- Use "do" when ADJACENT to trees (for wood), stones, or other resources
- Collect wood FIRST before trying to craft anything
- Be efficient - use multiple actions per tool call!
- Focus on unlocking achievements by collecting resources and crafting items."""

    def format_observation(self, obs: Dict[str, Any]) -> str:
        """Format Crafter observation with semantic map view."""
        # Get semantic map view
        semantic_view = format_semantic_map_view_v2(obs, view_size=7)
        
        # Extract key information
        inventory = obs.get('inventory', {})
        # Try both possible keys for achievements
        achievements = obs.get('achievements_status', obs.get('achievements_info', {}))
        health = obs.get('health', 10)
        food = obs.get('food', 10)
        drink = obs.get('drink', 10)
        energy = obs.get('energy', 10)
        
        # Count achievements
        achieved = sum(1 for v in achievements.values() if v)
        total_achievements = len(achievements)
        
        # Format inventory (only show non-zero items)
        inv_items = []
        for item, count in inventory.items():
            if count > 0:
                inv_items.append(f"{item}: {count}")
        inv_str = ", ".join(inv_items) if inv_items else "empty"
        
        # List unlocked achievements
        unlocked = [k for k, v in achievements.items() if v]
        unlocked_str = ", ".join(unlocked) if unlocked else "none"
        
        # Recent achievements (from info if available)
        recent_str = ""
        
        return f"""=== SEMANTIC MAP VIEW (15x15) ===
{semantic_view}

=== STATUS ===
Health: {health}/10 | Food: {food}/10 | Drink: {drink}/10 | Energy: {energy}/10
Inventory: {inv_str}
Achievements: {achieved}/{total_achievements} unlocked
Unlocked: {unlocked_str}
{recent_str}

What do you see in the map? What actions should you take? 

REMINDER: You MUST provide 2-5 actions in your interact() tool call. Plan multiple steps ahead!
Example: interact(actions=["move_right", "move_right", "do"], reasoning="Move to tree and collect wood")"""


async def run_episode(
    episode_id: int,
    config: CrafterConfig,
    session_tracer: Optional[SessionTracer] = None,
    progress_bar: Optional[tqdm] = None,
    quiet: bool = False
):
    """Run a single episode."""
    episode_start_time = time.time()
    
    # Create agent
    agent = CrafterReActAgentWithLMSynth(
        model_name=config.model_name,
        max_turns=config.max_turns,
        verbose=config.verbose,
        tracer=session_tracer,
        episode_id=episode_id,
        quiet=quiet
    )
    
    # Initialize environment
    async with AsyncClient(base_url=config.service_base_url) as client:
        try:
            # Initialize environment with unique seed for each episode
            # Use simple sequential seeds: 1, 2, 3, 4, etc.
            episode_seed = episode_id + 1  # Start from 1 instead of 0
            
            init_response = await retry_http_request(
                client, "POST", "/env/CrafterClassic/initialize",
                json={
                    "config": {
                        "difficulty": config.difficulty, 
                        "seed": episode_seed
                    }
                }
            )
            
            if config.verbose and episode_id == 0 and not quiet:
                print(f"🎲 Episode {episode_id} using seed: {episode_seed}")
            init_data = init_response.json()
            instance_id = init_data["env_id"]
            obs = init_data["observation"]
            
            # Debug: print first observation structure (only for first episode)
            if config.verbose and episode_id == 0 and not quiet:
                print(f"\n🔍 First observation keys: {list(obs.keys())}")
                if 'inventory' in obs:
                    inv = obs['inventory']
                    non_zero = {k: v for k, v in inv.items() if v > 0}
                    print(f"📦 Starting inventory: {non_zero if non_zero else 'Empty'}")
                if 'achievements_status' in obs:
                    print(f"🏆 Achievement keys: {list(obs['achievements_status'].keys())[:5]}...")
            
            # Start initial timestep and send initial observation as message
            if session_tracer and session_tracer.current_session:
                session_tracer.start_timestep(0)  # Start timestep for turn 0
                obs_msg = create_message(
                    compress_observation_for_trace(obs),
                    "observation",
                    f"crafter_env_{instance_id}",
                    0
                )
                session_tracer.record_message(obs_msg)
            
            # Run episode
            episode_reward = 0
            termination_reason = None
            step_results = []
            
            for turn in range(config.max_turns):
                if progress_bar:
                    progress_bar.set_description(f"Episode {episode_id}: Step {turn+1}/{config.max_turns}")
                elif config.verbose and turn % 5 == 0 and not quiet:  # Print progress every 5 steps when no progress bar
                    print(f"  Episode {episode_id}: Step {turn+1}/{config.max_turns}")
                
                # Start timestep for this turn if not turn 0
                if turn > 0 and session_tracer and session_tracer.current_session:
                    session_tracer.start_timestep(turn)
                
                # Get agent decision
                obs_formatted = agent.format_observation(obs)
                system_msg = agent.get_system_message()
                
                decision = await agent.decide(obs_formatted, system_msg, turn)
                
                # Handle termination
                if decision["name"] == "terminate":
                    termination_reason = decision["parameters"]["reason"]
                    break
                
                # Execute actions in sequence
                actions = decision["parameters"]["actions"]
                
                # Define action mapping
                CRAFTER_ACTION_MAP = {
                    "noop": 0,
                    "move_left": 1,
                    "move_right": 2,
                    "move_up": 3,
                    "move_down": 4,
                    "do": 5,
                    "sleep": 6,
                    "place_stone": 7,
                    "place_table": 8,
                    "place_furnace": 9,
                    "place_plant": 10,
                    "make_wood_pickaxe": 11,
                    "make_stone_pickaxe": 12,
                    "make_iron_pickaxe": 13,
                    "make_wood_sword": 14,
                    "make_stone_sword": 15,
                    "make_iron_sword": 16,
                }
                
                # Execute each action in the sequence
                for action in actions:
                    # Convert action name to integer
                    action_int = CRAFTER_ACTION_MAP.get(action, 0)  # Default to noop
                    
                    # Get state before action
                    state_before = {"observation": obs} if 'obs' in locals() else {}
                    prev_obs = obs.copy()
                    
                    # Step environment
                    step_response = await retry_http_request(
                        client, "POST", "/env/CrafterClassic/step",
                        json={
                            "env_id": instance_id,
                            "action": {"tool_calls": [{"tool": "interact", "args": {"action": action_int}}]}
                        }
                    )
                    step_data = step_response.json()
                    
                    if config.verbose and not quiet:
                        print(f"Step response keys: {list(step_data.keys())}")
                        # Create a cleaned version for logging (exclude large arrays)
                        step_data_clean = {}
                        for key, value in step_data.items():
                            if key == "observation" and isinstance(value, dict):
                                obs_clean = {}
                                for obs_key, obs_value in value.items():
                                    if obs_key == "semantic_map":
                                        obs_clean[obs_key] = f"<semantic_map: {getattr(obs_value, 'shape', 'array')}>"
                                    elif hasattr(obs_value, '__len__') and len(str(obs_value)) > 200:
                                        obs_clean[obs_key] = f"<large_array: {type(obs_value).__name__}>"
                                    else:
                                        obs_clean[obs_key] = obs_value
                                step_data_clean[key] = obs_clean
                            else:
                                step_data_clean[key] = value
                        print(f"Step response: {step_data_clean}")
                    
                    obs = step_data["observation"]
                    reward = step_data.get("reward", 0)  # Default to 0 if None
                    done = step_data["done"]
                    info = step_data.get("info", {})
                    
                    if reward is not None:
                        episode_reward += reward
                    
                    # Only log action results if not in quiet mode
                    if not quiet and reward is not None:
                        print(f"\n🏆 After action '{action}':")
                        print(f"   Reward: {reward}")
                        
                        # Print any achievements unlocked
                        achievements_unlocked = []
                        for key, value in obs.get('achievements_status', {}).items():
                            if value:
                                achievements_unlocked.append(key)
                        
                        print(f"   Achievements unlocked: {achievements_unlocked}")
                        
                        # Print inventory (only non-zero items)
                        inventory = obs.get('inventory', {})
                        non_zero_inventory = {k: v for k, v in inventory.items() if v > 0}
                        print(f"   Inventory: {non_zero_inventory}")
                    
                    # Record step result
                    step_results.append({
                        "turn": turn,
                        "action": action,
                        "reward": reward,
                        "done": done,
                        "info": info
                    })
                    
                    # Record environment event for hooks to catch
                    if session_tracer and session_tracer.current_session:
                        # Create environment event with state transition
                        env_event = EnvironmentEvent(
                            time_record=TimeRecord(
                                event_time=datetime.now().isoformat(),
                                message_time=turn
                            ),
                            system_instance_id=f"crafter_env_{instance_id}",
                            system_state_before={"public_state": prev_obs},
                            system_state_after={"public_state": obs},
                            reward=reward,
                            terminated=done,
                            metadata={
                                "action": action,
                                "action_int": action_int,
                                "info": info
                            }
                        )
                        session_tracer.record_event(env_event)
                        
                        # Also record runtime event for invalid action detection
                        runtime_event = RuntimeEvent(
                            time_record=TimeRecord(
                                event_time=datetime.now().isoformat(),
                                message_time=turn
                            ),
                            system_instance_id=f"crafter_runtime_{instance_id}",
                            actions=[action_int],
                            system_state_before=state_before,
                            system_state_after={"observation": obs},
                            metadata={
                                "action_name": action,
                                "action_int": action_int,
                                "reward": reward
                            }
                        )
                        session_tracer.record_event(runtime_event)
                    
                    if done:
                        break
                
                # After all actions in sequence, send final observation message
                if session_tracer and session_tracer.current_session:
                    obs_msg = create_message(
                        compress_observation_for_trace(obs),
                        "observation",
                        f"crafter_env_{instance_id}",
                        turn + 1
                    )
                    session_tracer.record_message(obs_msg)
                
                if done:
                    break
                
                if progress_bar:
                    progress_bar.update(1)
            
            # Terminate instance
            terminate_response = await retry_http_request(
                client, "POST", f"/env/CrafterClassic/terminate",
                json={"env_id": instance_id}
            )
            
        except Exception as e:
            print(f"❌ Episode {episode_id} failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "episode_id": episode_id,
                "error": str(e),
                "duration": time.time() - episode_start_time
            }
    
    # Extract final achievements
    final_achievements = []
    if obs and 'achievements_status' in obs:
        final_achievements = [k for k, v in obs['achievements_status'].items() if v]
    
    # Return results
    return {
        "episode_id": episode_id,
        "total_reward": episode_reward,
        "steps": len(step_results),
        "termination_reason": termination_reason,
        "duration": time.time() - episode_start_time,
        "step_results": step_results,
        "achievements_unlocked": final_achievements
    }


# --- Main ---
async def main():
    """Main entry point with v2 tracing."""
    parser = argparse.ArgumentParser(description="Run Crafter evaluation with LM Synth backend")
    parser.add_argument("--config", type=str, help="Path to TOML config file")
    parser.add_argument("--model", type=str, help="Model name (overrides config)")
    parser.add_argument("--episodes", type=int, help="Number of episodes (overrides config)")
    parser.add_argument("--max-steps", type=int, help="Max steps per episode (overrides config)")
    parser.add_argument("--difficulty", type=str, choices=["easy", "normal", "hard"], help="Difficulty override")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--quiet", action="store_true", help="Suppress most output except results")
    parser.add_argument("--no-traces", action="store_true", help="Disable trace saving")
    parser.add_argument("--analyze", action="store_true", help="Analyze traces after running")
    parser.add_argument("--skip-warmup", action="store_true", help="Skip model warmup")
    
    args = parser.parse_args()
    
    # Load configuration
    config = CrafterConfig(args.config)
    
    # Setup Synth environment variables
    setup_synth_environment()
    
    # Clean up old files to keep directory clean
    if config.auto_cleanup:
        cleanup_old_files()
    
    # Apply command-line overrides
    if args.model:
        config.model_name = args.model
    if args.episodes:
        config.num_instances = args.episodes
    if args.max_steps:
        config.max_turns = args.max_steps
    if args.difficulty:
        config.difficulty = args.difficulty
    if args.verbose:
        config.verbose = True
    if args.quiet:
        config.quiet = True
        if not args.verbose:  # Don't show this if verbose is also on
            print("🔇 Quiet mode enabled - suppressing verbose logs")
    else:
        config.quiet = False
    
    # Configure logging based on quiet mode
    setup_logging(quiet_mode=config.quiet)
    
    if args.no_traces:
        config.save_traces = False
        config.enable_v2_tracing = False
    if args.analyze:
        config.analyze_traces = True
    if args.skip_warmup:
        config.warmup_model = False
    
    # Ensure model is specified
    if not config.model_name:
        parser.error("Model name must be specified via --model or config file")
    
    print(f"🎮 Crafter ReAct Agent Evaluation (LM with Synth Backend)")
    print(f"Model: {config.model_name}")
    print(f"Service: {config.service_base_url}")
    print(f"Instances: {config.num_instances}")
    print(f"Max Turns: {config.max_turns}")
    print(f"Difficulty: {config.difficulty}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test service health
    async with AsyncClient(base_url=config.service_base_url) as client:
        try:
            health_resp = await retry_http_request(client, "GET", "/health")
            health_data = health_resp.json()
            print(f"✅ Crafter service is healthy: {health_data}")
        except Exception as e:
            print(f"❌ Failed to connect to Crafter service: {e}")
            return
    
    # Warm up the model if requested
    if config.warmup_model and not args.skip_warmup:
        print(f"\n🔥 Warming up {config.model_name} on Synth backend...")
        try:
            synth_base_url = os.getenv('SYNTH_BASE_URL') or os.getenv('MODAL_BASE_URL')
            synth_api_key = os.getenv('SYNTH_API_KEY') or os.getenv('MODAL_API_KEY')
            if synth_base_url and synth_api_key:
                synth_config = SynthConfig(
                    base_url=synth_base_url,
                    api_key=synth_api_key,
                    timeout=config.warmup_timeout  # Use configurable timeout
                )
                await warmup_synth_model(config.model_name, synth_config)
                print("✅ Model warmed up successfully!")
            else:
                print("⚠️  Missing SYNTH_BASE_URL or SYNTH_API_KEY, skipping warmup")
        except Exception as e:
            print(f"⚠️  Warmup failed: {e}")
            print("Continuing anyway...")
    
    # Set up v2 tracing if enabled
    trace_manager = None
    experiment_ctx = None
    
    if config.enable_v2_tracing:
        # Create trace directory first
        os.makedirs(config.v2_trace_dir, exist_ok=True)
        
        # Initialize trace manager
        trace_manager = DuckDBTraceManager(db_path=f"{config.v2_trace_dir}/traces.duckdb")
        
        # Create experiment context
        experiment_ctx = create_experiment_context(
            db_manager=trace_manager,
            experiment_name=f"crafter_lm_synth_{config.model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description=f"Crafter LM Synth experiment with {config.model_name} on {config.difficulty} difficulty, using LM class"
        )
        
        print(f"\n📊 V2 Tracing enabled. Traces will be saved to: {config.v2_trace_dir}")
        print(f"   Experiment: {experiment_ctx['experiment_name']}")
    
    # Run episodes in parallel using asyncio.gather for better multi-container testing
    print(f"\n🚀 Running {config.num_instances} episodes in parallel to test multi-container scaling...")
    
    total_steps = config.num_instances * config.max_turns
    episode_seeds = []  # Track seeds used for each episode
    
    # Prepare episode tasks
    episode_tasks = []
    session_tracers = []
    
    for i in range(config.num_instances):
        # Calculate episode seed for logging (simple sequential: 1, 2, 3, etc)
        episode_seed = i + 1
        episode_seeds.append(episode_seed)
        
        # Create session tracer for this episode if v2 tracing is enabled
        session_tracer = None
        if config.enable_v2_tracing and trace_manager:
            session_tracer = SessionTracer(
                traces_dir=config.v2_trace_dir,
                hooks=CRAFTER_HOOKS,
                duckdb_path=f"{config.v2_trace_dir}/traces.duckdb",
                experiment_id=experiment_ctx['experiment_id']
            )
            
            # Start session with episode metadata
            session_id = f"crafter_episode_{i}_{uuid.uuid4().hex[:8]}"
            session_tracer.start_session(session_id)
        
        session_tracers.append(session_tracer)
        
        # Create episode task (but don't await it yet)
        episode_task = run_episode(i, config, session_tracer, None, args.quiet)  # No progress bar for parallel execution
        episode_tasks.append(episode_task)
    
    print(f"📤 Starting {len(episode_tasks)} episodes concurrently...")
    start_time = time.time()
    
    # Run all episodes in parallel using asyncio.gather
    results = await asyncio.gather(*episode_tasks, return_exceptions=True)
    
    end_time = time.time()
    parallel_time = end_time - start_time
    
    print(f"✅ Completed {len(episode_tasks)} episodes in {parallel_time:.2f} seconds")
    print(f"📊 Parallel execution throughput: {len(episode_tasks)/parallel_time:.2f} episodes/second")
    
    # Process results and handle any exceptions
    successful_results = []
    failed_results = []
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"❌ Episode {i} failed: {result}")
            failed_results.append({"episode_id": i, "error": str(result)})
        else:
            successful_results.append(result)
        
        # End session and save trace
        session_tracer = session_tracers[i]
        if session_tracer:
            # Only save JSON file if not in duckdb_only mode
            save_json = not config.duckdb_only
            session_tracer.end_session(save=save_json)
            
            # Trace is automatically saved to DuckDB by end_session()
            if config.save_traces and config.verbose:
                if config.duckdb_only:
                    print(f"💾 Saved trace for episode {i} to DuckDB only")
                else:
                    print(f"💾 Saved trace for episode {i} to DuckDB and JSON")
    
    # Use successful results for analysis
    results = successful_results + failed_results
    
    # Analyze results
    print("\n" + "=" * 50)
    print("📊 EVALUATION RESULTS")
    print("=" * 50)
    
    successful_episodes = [r for r in results if 'error' not in r]
    failed_episodes = [r for r in results if 'error' in r]
    
    if successful_episodes:
        total_reward = sum(r['total_reward'] for r in successful_episodes)
        total_steps = sum(r['steps'] for r in successful_episodes)
        avg_reward = total_reward / len(successful_episodes)
        avg_steps = total_steps / len(successful_episodes)
        
        print(f"Episodes completed: {len(successful_episodes)}/{config.num_instances}")
        print(f"Failed episodes: {len(failed_episodes)}")
        print(f"Total reward: {total_reward:.2f}")
        print(f"Average reward per episode: {avg_reward:.2f}")
        print(f"Total steps: {total_steps}")
        print(f"Average steps per episode: {avg_steps:.2f}")
        
        # Show seeds used
        if episode_seeds:
            print(f"\nSeeds used:")
            for i, seed in enumerate(episode_seeds[:len(successful_episodes)]):
                print(f"  Episode {i}: seed {seed}")
        
        # Extract unique achievements
        all_achievements = set()
        achievement_counts = defaultdict(int)
        
        for result in successful_episodes:
            # Use the achievements_unlocked field we added
            if 'achievements_unlocked' in result:
                for achievement in result['achievements_unlocked']:
                    all_achievements.add(achievement)
                    achievement_counts[achievement] += 1
        
        print(f"Unique achievements unlocked: {len(all_achievements)}")
        if all_achievements:
            print("\nAchievements unlocked:")
            for achievement, count in sorted(achievement_counts.items()):
                print(f"  - {achievement}: {count} episodes ({count/len(successful_episodes)*100:.1f}%)")
    else:
        print("No successful episodes completed.")
    
    # Save detailed results to DuckDB if tracing is enabled
    if config.save_detailed_results and config.enable_v2_tracing and trace_manager:
        # For now, just print that results are available in DuckDB
        # The session traces are already saved to DuckDB via the SessionTracer
        print(f"\n💾 Results available in DuckDB: {trace_manager.db_path}")
        print(f"   Experiment ID: {experiment_ctx['experiment_id']}")
        print(f"   Use DuckDB queries to analyze results")
    elif config.save_detailed_results:
        # Fallback to JSON if no tracing
        results_file = f"crafter_lm_synth_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                'config': {
                    'model': config.model_name,
                    'episodes': config.num_instances,
                    'max_steps': config.max_turns,
                    'difficulty': config.difficulty,
                    'backend': 'synth'
                },
                'results': results,
                'summary': {
                    'successful_episodes': len(successful_episodes),
                    'failed_episodes': len(failed_episodes),
                    'total_reward': total_reward if successful_episodes else 0,
                    'avg_reward': avg_reward if successful_episodes else 0,
                    'unique_achievements': list(all_achievements) if successful_episodes else []
                }
            }, f, indent=2)
        print(f"\n💾 Detailed results saved to: {results_file}")


if __name__ == "__main__":
    asyncio.run(main())