#!/usr/bin/env python3
"""
DevOps Pipeline Failure Agent
==============================
Agentic AI demo for YouTube: Cloud Advocate
Author: GK

Reads a CI build failure log, inspects the relevant source file,
diagnoses the root cause, and proposes a concrete fix.
All powered by Claude via the Anthropic API.

Usage:
    python agent.py                         # uses sample log + source
    python agent.py --log path/to/build.log # use your own log
"""

import os
import sys
import json
import time
import argparse
import anthropic
from pathlib import Path
from datetime import datetime

# ─── Config ────────────────────────────────────────────────────────────────────

MODEL = "claude-sonnet-4-20250514"
SAMPLES_DIR = Path(__file__).parent / "samples"

# ANSI colors for terminal output (makes the demo look great on screen)
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    GRAY   = "\033[90m"
    WHITE  = "\033[97m"

# ─── Tools the agent can call ──────────────────────────────────────────────────

TOOLS = [
    {
        "name": "read_build_log",
        "description": (
            "Read the CI/CD build log to understand what failed. "
            "Returns the full log content including test output and error traces."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "log_path": {
                    "type": "string",
                    "description": "Path to the build log file"
                }
            },
            "required": ["log_path"]
        }
    },
    {
        "name": "read_source_file",
        "description": (
            "Read a source code file from the repository. "
            "Use this to inspect the actual code that caused the failure."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the source file to read"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "post_slack_summary",
        "description": (
            "Post a summary of the diagnosis and fix recommendation to Slack. "
            "Call this as the final step after you have a complete diagnosis."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "root_cause": {
                    "type": "string",
                    "description": "One-sentence root cause of the failure"
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
                    "description": "The actual code change to make (diff or snippet)"
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
]

# ─── Tool execution ─────────────────────────────────────────────────────────────

def execute_tool(tool_name: str, tool_input: dict, log_path: str) -> str:
    if tool_name == "read_build_log":
        path = Path(tool_input.get("log_path", log_path))
        if not path.exists():
            return f"Error: log file not found at {path}"
        return path.read_text()

    elif tool_name == "read_source_file":
        file_path = Path(tool_input["file_path"])
        # For demo: resolve relative paths against samples dir
        if not file_path.is_absolute():
            file_path = SAMPLES_DIR / file_path.name
        if not file_path.exists():
            return f"Error: source file not found at {file_path}"
        return file_path.read_text()

    elif tool_name == "post_slack_summary":
        # In a real setup this would call the Slack API.
        # For the demo we print a formatted Slack-style card to terminal.
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
        print(f"\n  _Diagnosed by Cloud Advocate DevOps Agent · {datetime.now().strftime('%H:%M:%S')}_")
        print(f"{C.BOLD}{C.WHITE}{'─'*60}{C.RESET}\n")
        return "Slack message posted successfully."

    return f"Unknown tool: {tool_name}"

# ─── Agent loop ─────────────────────────────────────────────────────────────────

def print_step(icon: str, label: str, detail: str = ""):
    print(f"\n{C.CYAN}{icon}  {C.BOLD}{label}{C.RESET}", end="")
    if detail:
        print(f"  {C.GRAY}{detail}{C.RESET}", end="")
    print()

def run_agent(log_path: str):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print(f"\n{C.BOLD}{C.GREEN}{'═'*60}{C.RESET}")
    print(f"{C.BOLD}{C.GREEN}   🤖  DevOps Pipeline Failure Agent{C.RESET}")
    print(f"{C.BOLD}{C.GREEN}{'═'*60}{C.RESET}")
    print(f"{C.GRAY}   Model: {MODEL}{C.RESET}")
    print(f"{C.GRAY}   Log:   {log_path}{C.RESET}")

    system_prompt = """You are an expert DevOps AI agent specialising in CI/CD pipeline diagnosis and remediation.

Your job:
1. Use read_build_log to read and understand what failed in the pipeline.
2. Identify the failing test and the source file responsible.
3. Use read_source_file to inspect the actual code.
4. Diagnose the root cause precisely — look for bugs, misconfigurations, race conditions, timeout issues, or logic errors.
5. Use post_slack_summary to report your findings with a concrete, actionable fix including a code snippet.

Rules:
- Always read the log first, then the source file, then post your summary.
- Be precise. Name the exact line(s) causing the problem.
- Your code suggestion must be a real fix, not a placeholder.
- Keep root_cause to one clear sentence.
- Severity: critical=data loss/security, high=prod broken, medium=feature broken, low=minor issue."""

    messages = [
        {
            "role": "user",
            "content": (
                f"A CI pipeline has just failed. "
                f"The build log is at: {log_path}\n"
                f"The source files are in: {SAMPLES_DIR}\n\n"
                "Diagnose the failure, inspect the relevant source code, "
                "and post a full fix recommendation to Slack."
            )
        }
    ]

    step = 0
    total_input_tokens = 0
    total_output_tokens = 0

    # ── Agentic loop ──────────────────────────────────────────────────────────
    while True:
        step += 1
        print_step("⟳", f"Agent thinking... (step {step})")

        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system_prompt,
            tools=TOOLS,
            messages=messages
        )

        total_input_tokens  += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

        # Show any text the agent narrates
        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"\n  {C.WHITE}{block.text.strip()}{C.RESET}")

        # Check if agent is done
        if response.stop_reason == "end_turn":
            print_step("✅", "Agent complete")
            break

        # Process tool calls
        if response.stop_reason == "tool_use":
            tool_results = []

            for block in response.content:
                if block.type != "tool_use":
                    continue

                tool_name  = block.name
                tool_input = block.input
                tool_id    = block.id

                print_step(
                    "🔧", f"Calling tool: {C.YELLOW}{tool_name}{C.RESET}",
                    f"({', '.join(f'{k}={repr(v)[:40]}' for k, v in tool_input.items())})"
                )

                result = execute_tool(tool_name, tool_input, log_path)

                # Show a preview of tool result (not the full content — too noisy)
                preview = result[:120].replace("\n", " ") + ("…" if len(result) > 120 else "")
                print(f"  {C.GRAY}→ {preview}{C.RESET}")

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": result
                })

            # Append assistant response + tool results to history
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user",      "content": tool_results})

        else:
            # Unexpected stop reason
            print(f"\n{C.RED}Unexpected stop reason: {response.stop_reason}{C.RESET}")
            break

    print(f"\n{C.GRAY}  Tokens used — input: {total_input_tokens:,}  output: {total_output_tokens:,}{C.RESET}")
    print(f"{C.BOLD}{C.GREEN}{'═'*60}{C.RESET}\n")

# ─── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="DevOps Pipeline Failure Agent")
    parser.add_argument(
        "--log",
        default=str(SAMPLES_DIR / "failed_build.log"),
        help="Path to the CI build log file (default: samples/failed_build.log)"
    )
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(f"{C.RED}Error: ANTHROPIC_API_KEY environment variable not set.{C.RESET}")
        print(f"  Run: export ANTHROPIC_API_KEY=your_key_here")
        sys.exit(1)

    run_agent(args.log)

if __name__ == "__main__":
    main()
