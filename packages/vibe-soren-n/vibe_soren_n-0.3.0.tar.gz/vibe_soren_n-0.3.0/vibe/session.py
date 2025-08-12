"""Session management for step-by-step workflow execution.

This module provides session-based workflow orchestration that allows
AI agents to execute workflows step-by-step without token overflow.
"""

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class WorkflowFrame:
    """Represents a single workflow in the execution stack.

    A workflow frame contains:
    - workflow_name: The name of the workflow being executed
    - steps: List of all steps in this workflow
    - current_step: Index of the current step (0-based)
    - context: Additional context data for this workflow
    """

    workflow_name: str
    steps: list[str]
    current_step: int
    context: dict[str, Any]

    @property
    def is_complete(self) -> bool:
        """Check if all steps in this workflow are complete."""
        return self.current_step >= len(self.steps)

    @property
    def current_step_text(self) -> str | None:
        """Get the text of the current step, or None if complete."""
        if self.is_complete:
            return None
        return self.steps[self.current_step]

    def advance(self) -> bool:
        """Advance to the next step.

        Returns:
            True if advanced to next step, False if workflow is complete

        """
        if not self.is_complete:
            self.current_step += 1
            return True
        return False


@dataclass
class WorkflowSession:
    """Represents a complete workflow execution session.

    A session maintains:
    - session_id: Unique identifier for this session
    - prompt: Original prompt that started this session
    - workflow_stack: Stack of workflow frames (nested workflows)
    - created_at: When this session was created
    - last_accessed: When this session was last accessed
    """

    session_id: str
    prompt: str
    workflow_stack: list[WorkflowFrame]
    created_at: datetime
    last_accessed: datetime

    @classmethod
    def create(
        cls, prompt: str, initial_workflows: list[tuple[str, list[str]]]
    ) -> "WorkflowSession":
        """Create a new workflow session.

        Args:
            prompt: The original prompt that triggered the workflows
            initial_workflows: List of (workflow_name, steps) tuples

        Returns:
            New WorkflowSession instance

        """
        session_id = str(uuid.uuid4())[:8]  # Short UUID for readability
        now = datetime.now()

        workflow_stack = []
        for workflow_name, steps in initial_workflows:
            frame = WorkflowFrame(
                workflow_name=workflow_name, steps=steps, current_step=0, context={}
            )
            workflow_stack.append(frame)

        return cls(
            session_id=session_id,
            prompt=prompt,
            workflow_stack=workflow_stack,
            created_at=now,
            last_accessed=now,
        )

    @property
    def current_frame(self) -> WorkflowFrame | None:
        """Get the current workflow frame (top of stack)."""
        if not self.workflow_stack:
            return None
        return self.workflow_stack[-1]

    @property
    def is_complete(self) -> bool:
        """Check if all workflows in the session are complete."""
        return not self.workflow_stack or all(
            frame.is_complete for frame in self.workflow_stack
        )

    def get_current_step(self) -> dict[str, Any] | None:
        """Get information about the current step.

        Returns:
            Dict with step information, or None if session is complete

        """
        current_frame = self.current_frame
        if not current_frame or current_frame.is_complete:
            return None

        return {
            "workflow": current_frame.workflow_name,
            "step_number": current_frame.current_step + 1,  # 1-based for display
            "total_steps": len(current_frame.steps),
            "step_text": current_frame.current_step_text,
            "is_command": self._is_command_step(current_frame.current_step_text or ""),
            "workflow_depth": len(self.workflow_stack),
        }

    def advance_step(self) -> bool:
        """Advance to the next step in the current workflow.

        Returns:
            True if advanced, False if no more steps

        """
        current_frame = self.current_frame
        if not current_frame:
            return False

        self.last_accessed = datetime.now()

        # Try to advance current workflow
        if current_frame.advance():
            return True

        # Current workflow is complete, pop it from stack
        self.workflow_stack.pop()

        # If there are more workflows in the stack, we've returned to parent
        return len(self.workflow_stack) > 0

    def back_step(self) -> bool:
        """Go back to the previous step in the current workflow.

        Returns:
            True if went back a step, False if already at first step

        """
        current_frame = self.current_frame
        if not current_frame or current_frame.current_step <= 0:
            return False

        current_frame.current_step -= 1
        self.last_accessed = datetime.now()
        return True

    def restart_session(self) -> None:
        """Restart the entire session from the beginning.

        Resets all workflows in the stack back to step 0.
        """
        for frame in self.workflow_stack:
            frame.current_step = 0
        self.last_accessed = datetime.now()

    def break_workflow(self) -> bool:
        """Break out of the current workflow and return to parent.

        Returns:
            True if broke to parent workflow, False if no parent

        """
        if len(self.workflow_stack) <= 1:
            return False

        self.last_accessed = datetime.now()
        self.workflow_stack.pop()
        return True

    def push_workflow(
        self,
        workflow_name: str,
        steps: list[str],
        context: dict[str, Any] | None = None,
    ) -> None:
        """Push a new workflow onto the stack (nested workflow).

        Args:
            workflow_name: Name of the new workflow
            steps: Steps for the new workflow
            context: Optional context for the new workflow

        """
        frame = WorkflowFrame(
            workflow_name=workflow_name,
            steps=steps,
            current_step=0,
            context=context or {},
        )
        self.workflow_stack.append(frame)
        self.last_accessed = datetime.now()

    def _is_command_step(self, step_text: str) -> bool:
        """Determine if a step contains executable commands.

        This is a heuristic based on common command patterns.
        """
        step_lower = step_text.lower().strip()

        # Common command indicators
        command_indicators = [
            "run ",
            "execute ",
            "install ",
            "npm ",
            "pip ",
            "git ",
            "cd ",
            "mkdir ",
            "touch ",
            "curl ",
            "wget ",
            "docker ",
            "python ",
            "node ",
            "bun ",
            "yarn ",
            "pnpm ",
            "cargo ",
            "go ",
            "rustc ",
        ]

        return any(step_lower.startswith(cmd) for cmd in command_indicators)

    def to_dict(self) -> dict[str, Any]:
        """Convert session to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "prompt": self.prompt,
            "workflow_stack": [asdict(frame) for frame in self.workflow_stack],
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkflowSession":
        """Create session from dictionary (JSON deserialization)."""
        workflow_stack = []
        for frame_data in data["workflow_stack"]:
            frame = WorkflowFrame(**frame_data)
            workflow_stack.append(frame)

        return cls(
            session_id=data["session_id"],
            prompt=data["prompt"],
            workflow_stack=workflow_stack,
            created_at=datetime.fromisoformat(data["created_at"]),
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
        )


class SessionManager:
    """Manages workflow sessions with persistence to disk.

    Sessions are stored in ~/.vibe/sessions/ as JSON files.
    """

    def __init__(self, session_dir: Path | None = None):
        """Initialize session manager.

        Args:
            session_dir: Directory to store sessions (defaults to ~/.vibe/sessions/)

        """
        if session_dir is None:
            session_dir = Path.home() / ".vibe" / "sessions"

        self.session_dir = session_dir
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Create archive directory for completed sessions
        self.archive_dir = self.session_dir / "archive"
        self.archive_dir.mkdir(exist_ok=True)

    def create_session(
        self, prompt: str, workflows: list[tuple[str, list[str]]]
    ) -> WorkflowSession:
        """Create and persist a new workflow session.

        Args:
            prompt: Original prompt that triggered workflows
            workflows: List of (workflow_name, steps) tuples

        Returns:
            New WorkflowSession instance

        """
        session = WorkflowSession.create(prompt, workflows)
        self._save_session(session)
        return session

    def load_session(self, session_id: str) -> WorkflowSession | None:
        """Load a session from disk.

        Args:
            session_id: ID of session to load

        Returns:
            WorkflowSession instance or None if not found

        """
        session_file = self.session_dir / f"{session_id}.json"
        if not session_file.exists():
            return None

        try:
            with open(session_file) as f:
                data = json.load(f)
            return WorkflowSession.from_dict(data)
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def save_session(self, session: WorkflowSession) -> None:
        """Save a session to disk.

        Args:
            session: Session to save

        """
        self._save_session(session)

    def archive_session(self, session_id: str) -> bool:
        """Archive a completed session.

        Args:
            session_id: ID of session to archive

        Returns:
            True if archived successfully, False if session not found

        """
        session_file = self.session_dir / f"{session_id}.json"
        if not session_file.exists():
            return False

        archive_file = self.archive_dir / f"{session_id}.json"
        session_file.rename(archive_file)
        return True

    def list_active_sessions(self) -> list[str]:
        """List all active session IDs.

        Returns:
            List of session IDs

        """
        session_files = self.session_dir.glob("*.json")
        return [f.stem for f in session_files]

    def cleanup_old_sessions(self, max_age_days: int = 7) -> int:
        """Clean up old sessions.

        Args:
            max_age_days: Maximum age in days before archiving

        Returns:
            Number of sessions archived

        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        archived_count = 0

        for session_file in self.session_dir.glob("*.json"):
            try:
                with open(session_file) as f:
                    data = json.load(f)

                last_accessed = datetime.fromisoformat(data["last_accessed"])
                if last_accessed < cutoff_date:
                    archive_file = self.archive_dir / session_file.name
                    session_file.rename(archive_file)
                    archived_count += 1

            except (json.JSONDecodeError, KeyError, ValueError):
                # Invalid session file, remove it
                session_file.unlink()
                archived_count += 1

        return archived_count

    def _save_session(self, session: WorkflowSession) -> None:
        """Internal method to save session to disk."""
        session_file = self.session_dir / f"{session.session_id}.json"
        with open(session_file, "w") as f:
            json.dump(session.to_dict(), f, indent=2)
