#!/usr/bin/env python3
"""
DevOps Pipeline Failure Agent — Local Edition
===============================================
Agentic AI demo for YouTube: Cloud Advocate
Author: GK

Same agent, same tools, same agentic loop —
but running 100% locally using Qwen3:14b via Ollama.
Zero API cost. Zero data leaves your machine.

Usage:
    # Make sure Ollama is running first:
    ollama serve

    # Then run:
    python agent_local.py

Requirements:
    pip install ollama
    ollama pull qwen3:14b
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import ollama

# ─── Config ────────────────────────────────────────────────────────────────────

MODEL       = "qwen3:14b"
SAMPLES_DIR = Path(__file__).parent / "samples"
MAX_STEPS   = 8  # safety guard — 7B models can loop if not capped

# ANSI colors
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    GRAY   = "\033[90m"
    WHITE  = "\033[97m"

# ─── Tools (OpenAI format — what Ollama expects) ────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_build_log",
            "description": (
                "Read the CI/CD build log to understand what failed. "
                "Always call this first. "
                "Returns the full log including test output and error traces."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "log_path": {
                        "type": "string",
                        "description": "Path to the build log file"
                    }
                },
                "required": ["log_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_source_file",
            "description": (
                "Read a source code file from the repository. "
                "Call this after reading the log to inspect the buggy code."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the source file to read"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "post_slack_summary",
            "description": (
                "Post a diagnosis and fix recommendation to Slack. "
                "Call this as the FINAL step once you have diagnosed the root cause."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "root_cause": {
                        "type": "string",
                        "description": "One sentence root cause of the failure"
                    },
                    "affected_file": {
                        "type": "string",
                        "description": "The file that needs to be fixed"
                    },
                    "fix_summary": {
                        "type": "string",
                        "description": "Clear description of the recommended fix"
                    },
                    "code_suggestion": {
                        "type": "string",
                        "description": "Actual code change to make"
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Severity of the issue"
                    }
                },
                "required": ["root_cause", "affected_file", "fix_summary", "severity"]
            }
        }
    }
]

# ─── Tool execution ─────────────────────────────────────────────────────────────

def execute_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "read_build_log":
        path = Path(tool_input.get("log_path", ""))
        if not path.exists():
            path = SAMPLES_DIR / "failed_build.log"
        return path.read_text()

    elif tool_name == "read_source_file":
        file_path = Path(tool_input["file_path"])

        # Try exact path first
        if file_path.exists():
            return file_path.read_text()

        # Try just the filename in samples dir
        # (handles cases where Qwen3 hallucinates a deeper path)
        simple = SAMPLES_DIR / file_path.name
        if simple.exists():
            return simple.read_text()

        # Last resort — scan samples dir for any matching file
        available = list(SAMPLES_DIR.iterdir())
        for f in available:
            if f.name == file_path.name or f.stem == file_path.stem:
                return f.read_text()

        return f"Error: file not found. Available files in samples/: {[f.name for f in available]}" 

    elif tool_name == "post_slack_summary":
        severity_emoji = {
            "low": "🟡", "medium": "🟠", "high": "🔴", "critical": "🚨"
        }.get(tool_input.get("severity", "medium"), "🟠")

        print(f"\n{C.BOLD}{C.WHITE}{'─'*60}{C.RESET}")
        print(f"{C.BOLD}{C.WHITE}  📬  Slack #devops-alerts  (simulated){C.RESET}")
        print(f"{C.BOLD}{C.WHITE}{'─'*60}{C.RESET}")
        print(f"\n  {severity_emoji}  *Build Failure Diagnosed*")
        print(f"\n  *Root cause:*  {tool_input['root_cause']}")
        print(f"  *Affected file:*  `{tool_input['affected_file']}`")
        print(f"  *Severity:*  {tool_input.get('severity', 'medium').upper()}")
        print(f"\n  *Recommended fix:*")
        print(f"  {tool_input['fix_summary']}")
        if tool_input.get("code_suggestion"):
            print(f"\n  *Code change:*")
            for line in tool_input["code_suggestion"].split("\n"):
                print(f"  {line}")
        print(f"\n  _Diagnosed by Cloud Advocate Local Agent (Qwen3:14b) · {datetime.now().strftime('%H:%M:%S')}_")
        print(f"{C.BOLD}{C.WHITE}{'─'*60}{C.RESET}\n")
        return "Slack message posted successfully."

    return f"Unknown tool: {tool_name}"

# ─── Helper ─────────────────────────────────────────────────────────────────────

def print_step(icon: str, label: str, detail: str = ""):
    print(f"\n{C.CYAN}{icon}  {C.BOLD}{label}{C.RESET}", end="")
    if detail:
        print(f"  {C.GRAY}{detail}{C.RESET}", end="")
    print()

# ─── Agent loop ─────────────────────────────────────────────────────────────────

def run_agent():
    log_path = str(SAMPLES_DIR / "failed_build.log")

    print(f"\n{C.BOLD}{C.GREEN}{'═'*60}{C.RESET}")
    print(f"{C.BOLD}{C.GREEN}   🤖  DevOps Agent — Local Edition (Qwen3:14b){C.RESET}")
    print(f"{C.BOLD}{C.GREEN}{'═'*60}{C.RESET}")
    print(f"{C.GRAY}   Model:  {MODEL} via Ollama (100% local){C.RESET}")
    print(f"{C.GRAY}   Log:    {log_path}{C.RESET}")
    print(f"{C.GRAY}   Cost:   $0.00{C.RESET}")

    # Strong system prompt — critical for 7B models to follow tool order
    system_prompt = """You are a DevOps AI agent. Your job is to diagnose CI pipeline failures.

You MUST follow this exact sequence using the tools available:
STEP 1: Call read_build_log to read the failure log.
STEP 2: Call read_source_file to inspect the buggy source file. Use ONLY the filename e.g. "gateway.py" not a full path.
STEP 3: Call post_slack_summary with your diagnosis and a concrete code fix.

Rules:
- Always follow the 3 steps in order. Do not skip any step.
- In post_slack_summary, root_cause must be one clear sentence.
- code_suggestion must contain a real code fix, not a placeholder.
- severity: critical=data loss, high=feature broken, medium=degraded, low=minor."""

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                f"A CI pipeline has just failed.\n"
                f"Build log is at: {log_path}\n"
                f"Source files are in: {SAMPLES_DIR}\n\n"
                f"Please diagnose the failure and post the fix to Slack."
            )
        }
    ]

    step = 0

    # ── Agentic loop ──────────────────────────────────────────────────────────
    while step < MAX_STEPS:
        step += 1
        print_step("⟳", f"Agent thinking... (step {step}/{MAX_STEPS})")

        response = ollama.chat(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            options={
                "temperature": 0.1,   # low temp = more deterministic tool calls
            },
            think=False,              # disable Qwen3 thinking mode for faster tool calling
        )

        msg = response.message

        # Show any text the agent narrates
        if msg.content and msg.content.strip():
            print(f"\n  {C.WHITE}{msg.content.strip()}{C.RESET}")

        # Check if agent called any tools
        if not msg.tool_calls:
            # No tool calls — agent is done
            print_step("✅", "Agent complete")
            break

        # Process tool calls
        # Append assistant message first
        messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": msg.tool_calls})

        for tool_call in msg.tool_calls:
            tool_name  = tool_call.function.name
            tool_input = tool_call.function.arguments

            # Ollama sometimes returns arguments as string — parse if needed
            if isinstance(tool_input, str):
                try:
                    tool_input = json.loads(tool_input)
                except json.JSONDecodeError:
                    tool_input = {}

            print_step(
                "🔧", f"Calling tool: {C.YELLOW}{tool_name}{C.RESET}",
                f"({', '.join(f'{k}={repr(v)[:40]}' for k, v in tool_input.items())})"
            )

            result = execute_tool(tool_name, tool_input)

            # Preview result
            preview = result[:120].replace("\n", " ") + ("…" if len(result) > 120 else "")
            print(f"  {C.GRAY}→ {preview}{C.RESET}")

            # Append tool result to messages
            messages.append({
                "role": "tool",
                "content": result,
            })

    if step >= MAX_STEPS:
        print(f"\n{C.YELLOW}⚠️  Max steps reached ({MAX_STEPS}). Agent stopped.{C.RESET}")

    print(f"\n{C.GRAY}  Powered by: {MODEL} running locally via Ollama{C.RESET}")
    print(f"{C.BOLD}{C.GREEN}{'═'*60}{C.RESET}\n")

# ─── Entry point ───────────────────────────────────────────────────────────────

def main():
    # Check Ollama is running
    try:
        ollama.list()
    except Exception:
        print(f"\n{C.RED}Error: Ollama is not running.{C.RESET}")
        print(f"  Start it with:  ollama serve")
        print(f"  Then pull model: ollama pull {MODEL}\n")
        sys.exit(1)

    run_agent()

if __name__ == "__main__":
    main()
