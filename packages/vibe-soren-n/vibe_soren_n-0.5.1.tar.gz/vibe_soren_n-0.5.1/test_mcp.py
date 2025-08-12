#!/usr/bin/env python3
"""Test script for MCP workflow functionality.

This script tests the basic MCP commands to ensure they work correctly.
"""

import json
import subprocess
from pathlib import Path
from typing import Any, cast


def run_vibe_mcp_command(cmd: list[str]) -> dict[str, Any]:
    """Run a vibe mcp command and return parsed JSON result."""
    try:
        result = subprocess.run(
            ["python", "-m", "vibe.cli"] + cmd,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )

        if result.returncode != 0:
            print(f"Command failed: {' '.join(cmd)}")
            print(f"stderr: {result.stderr}")
            return {"success": False, "error": result.stderr}

        return cast(dict[str, Any], json.loads(result.stdout))
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        print(f"stdout: {result.stdout}")
        return {"success": False, "error": f"JSON parse error: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def test_mcp_workflow() -> None:
    """Test the complete MCP workflow."""
    print("🧪 Testing MCP Workflow Functionality")
    print("=" * 40)

    # Test 1: Start a session
    print("\n1. Starting workflow session...")
    result = run_vibe_mcp_command(["mcp", "start", "analyze the project structure"])

    if not result.get("success"):
        print(f"❌ Failed to start session: {result.get('error')}")
        assert False, f"Failed to start session: {result.get('error')}"

    session_id = result.get("session_id")
    if not session_id:
        print("❌ No session ID returned")
        assert False, "No session ID returned"

    current_step = result.get("current_step")

    print(f"✅ Session started: {session_id}")
    if current_step:
        print(f"   Current step: {current_step.get('step_text', 'N/A')}")
        print(f"   Workflow: {current_step.get('workflow', 'N/A')}")

    # Test 2: Get session status
    print("\n2. Getting session status...")
    result = run_vibe_mcp_command(["mcp", "status", session_id])

    if not result.get("success"):
        print(f"❌ Failed to get status: {result.get('error')}")
        assert False, f"Failed to get status: {result.get('error')}"

    print("✅ Session status retrieved")
    print(f"   Prompt: {result.get('prompt', 'N/A')}")
    print(f"   Complete: {result.get('is_complete', False)}")

    # Test 3: Advance to next step
    print("\n3. Advancing to next step...")
    result = run_vibe_mcp_command(["mcp", "next", session_id])

    if not result.get("success"):
        print(f"❌ Failed to advance: {result.get('error')}")
        assert False, f"Failed to advance: {result.get('error')}"

    has_next = result.get("has_next", False)
    current_step = result.get("current_step")

    print("✅ Advanced to next step")
    print(f"   Has next: {has_next}")
    if current_step:
        print(f"   New step: {current_step.get('step_text', 'N/A')}")

    # Test 4: List sessions
    print("\n4. Listing active sessions...")
    result = run_vibe_mcp_command(["mcp", "list"])

    if not result.get("success"):
        print(f"❌ Failed to list sessions: {result.get('error')}")
        assert False, f"Failed to list sessions: {result.get('error')}"

    sessions = result.get("sessions", [])
    print(f"✅ Found {len(sessions)} active sessions")

    for session in sessions:
        print(
            f"   - {session.get('session_id')}: {session.get('prompt', 'N/A')[:50]}..."
        )

    # Test 5: Break out of workflow (if still active)
    if has_next:
        print("\n5. Breaking out of workflow...")
        result = run_vibe_mcp_command(["mcp", "break", session_id])

        if result.get("success"):
            print("✅ Successfully broke out of workflow")
            print(f"   Message: {result.get('message', 'N/A')}")
        else:
            print(f"⚠️  Break command result: {result.get('error', 'Unknown')}")

    print("\n🎉 MCP workflow test completed successfully!")


if __name__ == "__main__":
    try:
        test_mcp_workflow()
        print("✅ All tests passed!")
        exit(0)
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        exit(1)
