"""Workflow orchestrator that plans and provides execution guidance."""

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .config import VibeConfig
from .session import SessionManager
from .workflows import get_workflow_registry


class WorkflowOrchestrator:
    """Orchestrates workflow planning and provides execution guidance for AI agents."""

    def __init__(self, config: VibeConfig):
        """Initialize the workflow orchestrator with configuration."""
        self.config = config
        self.console = Console()
        self.workflow_registry = get_workflow_registry()
        self.session_manager = SessionManager()

    def plan_workflows(
        self, workflows: list[str], prompt: str, show_display: bool = True
    ) -> dict[str, Any]:
        """Plan workflows and return execution guidance."""
        if not workflows:
            return {
                "success": True,
                "workflows": [],
                "guidance": "No workflows needed.",
            }

        # Plan execution order
        execution_order = self._plan_execution_order(workflows)

        # Generate execution plan
        execution_plan = self._generate_execution_plan(execution_order, prompt)

        # Display the plan only if requested
        if show_display:
            self._display_execution_guidance(execution_plan, prompt)

        return {
            "success": True,
            "workflows": execution_order,
            "execution_plan": execution_plan,
            "guidance": self._format_guidance_for_agent(execution_plan),
        }

    def _generate_execution_plan(
        self, workflows: list[str], prompt: str
    ) -> list[dict[str, Any]]:
        """Generate detailed execution plan for each workflow."""
        plan = []

        for workflow_name in workflows:
            workflow_step = self._plan_workflow_step(workflow_name, prompt)
            if workflow_step:
                plan.append(workflow_step)

        return plan

    def _plan_workflow_step(
        self, workflow_name: str, prompt: str
    ) -> dict[str, Any] | None:
        """Plan a single workflow step."""
        # Try to get built-in workflow first
        built_in_workflow = self.workflow_registry.get_workflow(workflow_name)

        # Get config workflow
        workflow_config = self.config.workflows.get(workflow_name)

        if not built_in_workflow and not workflow_config:
            return None

        # Determine which workflow to use and get steps
        steps = []
        description = ""
        source = ""

        if built_in_workflow:
            # Use built-in workflow
            steps = built_in_workflow.steps
            description = built_in_workflow.description
            source = "built-in"
        elif workflow_config:
            # Use config workflow
            # Get project type and project-specific steps
            project_type = self.config.detect_project_type()
            project_config = self.config.project_types.get(project_type)

            if project_config and workflow_name in project_config.workflows:
                steps = project_config.workflows[workflow_name].steps
            else:
                steps = workflow_config.steps

            description = (
                workflow_config.description or f"{workflow_name.title()} workflow"
            )
            source = "custom"

        return {
            "name": workflow_name,
            "description": description,
            "steps": steps,
            "source": source,
            "reasoning": self._get_workflow_reasoning(workflow_name, prompt),
        }

    def _get_workflow_reasoning(self, workflow_name: str, prompt: str) -> str:
        """Generate reasoning for why this workflow is needed."""
        reasoning_map = {
            "analysis": (
                f"To understand the project structure and identify what "
                f"needs to be done for: '{prompt}'"
            ),
            "Research Guidance for Agents": (
                f"No specific workflow found for '{prompt}'. "
                f"Providing research guidance for online information discovery."
            ),
            "python_quality": (
                "To ensure code quality with formatting, linting, and style checks"
            ),
            "python_test": "To validate that all tests pass and code works correctly",
            "python_build": "To create distribution packages ready for release",
            "git_status": "To check the current state of the repository",
            "git_commit": "To save the current work state",
            "documentation": "To ensure project documentation is up to date",
            "cleanup": "To remove temporary files and clean up the workspace",
            "security": "To check for security vulnerabilities and sensitive files",
            "dependencies": "To verify and update project dependencies",
        }

        return reasoning_map.get(
            workflow_name, f"To complete the {workflow_name} workflow as requested"
        )

    def _display_execution_guidance(
        self, execution_plan: list[dict[str, Any]], prompt: str
    ) -> None:
        """Display execution guidance for AI agents."""
        self.console.print()

        # Show the original prompt
        self.console.print(
            Panel(
                f"[bold blue]{prompt}[/bold blue]",
                title="🎯 User Request",
                border_style="blue",
            )
        )

        # Show the execution guidance
        self.console.print(
            Panel(
                self._format_guidance_text(execution_plan),
                title="🤖 AI Agent Execution Guidance",
                border_style="green",
            )
        )

        # Show detailed steps table
        self._display_steps_table(execution_plan)

    def _format_guidance_text(self, execution_plan: list[dict[str, Any]]) -> str:
        """Format guidance text for AI agents."""
        if not execution_plan:
            return (
                "No specific workflows needed. Proceed with general project analysis."
            )

        guidance_parts = [
            "Based on the request, I recommend the following workflow execution:",
            "",
        ]

        for i, step in enumerate(execution_plan, 1):
            guidance_parts.append(f"{i}. **{step['description']}**")
            guidance_parts.append(f"   Reasoning: {step['reasoning']}")
            guidance_parts.append("")

        guidance_parts.append("Execute these workflows in order for best results.")
        return "\n".join(guidance_parts)

    def _display_steps_table(self, execution_plan: list[dict[str, Any]]) -> None:
        """Display detailed steps in a table format."""
        if not execution_plan:
            return

        table = Table(title="📋 Detailed Execution Steps")
        table.add_column("Step", style="cyan", no_wrap=True)
        table.add_column("Workflow", style="magenta")
        table.add_column("Source", style="yellow")
        table.add_column("Steps", style="green")

        for i, step in enumerate(execution_plan, 1):
            steps_text = "\n".join(step["steps"][:3])  # Show first 3 steps
            if len(step["steps"]) > 3:
                steps_text += f"\n... and {len(step['steps']) - 3} more"

            table.add_row(str(i), step["description"], step["source"], steps_text)

        self.console.print(table)

    def _format_guidance_for_agent(self, execution_plan: list[dict[str, Any]]) -> str:
        """Format guidance as concise plain text for AI agents (TPS-aware)."""
        if not execution_plan:
            return "No specific workflows needed."

        lines: list[str] = []
        # Global TPS-aware reminder (one line)
        lines.append(
            "Token-thrifty: keep outputs short, batch commands, use quiet flags, "
            "sample large listings, summarize ≤6 bullets."
        )

        for i, step in enumerate(execution_plan, 1):
            # One-liner per workflow
            lines.append(f"{i}. {step['name']}: {step['description']}")

            # Include only the first few actionable steps to reduce tokens
            max_steps = 5
            step_items = step.get("steps", [])[:max_steps]
            for s in step_items:
                lines.append(f"   - {s}")

            remaining = len(step.get("steps", [])) - len(step_items)
            if remaining > 0:
                lines.append(f"   - (+{remaining} more)")

        return "\n".join(lines)

    def _plan_execution_order(self, workflows: list[str]) -> list[str]:
        """Plan workflow execution order based on dependencies."""
        # Define execution priorities (lower number = higher priority)
        priority_order = [
            "mcp",  # MCP setup should come first
            "analysis",  # Analysis before implementation
            "implementation",  # Implementation before testing
            "quality",  # Quality checks after implementation
            "testing",  # Testing after quality checks
            "documentation",  # Documentation after implementation
            "git",  # Git operations near the end
            "session",  # Session management last
        ]

        # Sort workflows by priority order
        ordered_workflows = []

        # Add workflows in priority order
        for priority_workflow in priority_order:
            if priority_workflow in workflows:
                ordered_workflows.append(priority_workflow)

        # Add any workflows not in priority list
        for workflow in workflows:
            if workflow not in ordered_workflows:
                ordered_workflows.append(workflow)

        return ordered_workflows

    # Session-based workflow execution methods

    def start_session(self, prompt: str) -> dict[str, Any]:
        """Start a new workflow session for step-by-step execution.

        Args:
            prompt: The original prompt that triggered workflows

        Returns:
            Dict with session info and first step

        """
        try:
            # Analyze prompt to get workflows
            from .analyzer import PromptAnalyzer

            analyzer = PromptAnalyzer(self.config)
            workflow_names = analyzer.analyze(prompt, show_analysis=False)

            if not workflow_names:
                return {
                    "success": False,
                    "error": "No workflows identified for the given prompt",
                }

            # Generate execution plan to get workflow steps
            execution_order = self._plan_execution_order(workflow_names)
            workflow_steps = []

            for workflow_name in execution_order:
                steps = self._get_workflow_steps(workflow_name)
                if steps:
                    workflow_steps.append((workflow_name, steps))

            if not workflow_steps:
                return {
                    "success": False,
                    "error": "No valid workflows found with steps",
                }

            # Create session
            session = self.session_manager.create_session(prompt, workflow_steps)

            # Get first step
            current_step = session.get_current_step()

            return {
                "success": True,
                "session_id": session.session_id,
                "prompt": prompt,
                "current_step": current_step,
                "workflow_stack": [
                    frame.workflow_name for frame in session.workflow_stack
                ],
                "total_workflows": len(session.workflow_stack),
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to start session: {str(e)}"}

    def get_session_status(self, session_id: str) -> dict[str, Any]:
        """Get the current status of a workflow session.

        Args:
            session_id: ID of the session

        Returns:
            Dict with session status and current step info

        """
        session = self.session_manager.load_session(session_id)
        if not session:
            return {"success": False, "error": f"Session {session_id} not found"}

        current_step = session.get_current_step()

        return {
            "success": True,
            "session_id": session.session_id,
            "prompt": session.prompt,
            "current_step": current_step,
            "workflow_stack": [frame.workflow_name for frame in session.workflow_stack],
            "is_complete": session.is_complete,
            "created_at": session.created_at.isoformat(),
            "last_accessed": session.last_accessed.isoformat(),
        }

    def advance_session(self, session_id: str) -> dict[str, Any]:
        """Mark current step as complete and advance to next step.

        Args:
            session_id: ID of the session

        Returns:
            Dict with next step info or completion status

        """
        session = self.session_manager.load_session(session_id)
        if not session:
            return {"success": False, "error": f"Session {session_id} not found"}

        # Advance to next step
        has_next = session.advance_step()

        # Save updated session
        if has_next:
            self.session_manager.save_session(session)
            current_step = session.get_current_step()

            return {
                "success": True,
                "session_id": session.session_id,
                "current_step": current_step,
                "workflow_stack": [
                    frame.workflow_name for frame in session.workflow_stack
                ],
                "has_next": True,
            }
        else:
            # Session is complete, archive it
            self.session_manager.archive_session(session_id)

            return {
                "success": True,
                "session_id": session.session_id,
                "current_step": None,
                "workflow_stack": [],
                "has_next": False,
                "message": "All workflows completed successfully",
            }

    def break_session(self, session_id: str) -> dict[str, Any]:
        """Break out of current workflow and return to parent workflow.

        Args:
            session_id: ID of the session

        Returns:
            Dict with parent workflow step info

        """
        session = self.session_manager.load_session(session_id)
        if not session:
            return {"success": False, "error": f"Session {session_id} not found"}

        # Break to parent workflow
        has_parent = session.break_workflow()

        if has_parent:
            # Save updated session and return parent step
            self.session_manager.save_session(session)
            current_step = session.get_current_step()

            return {
                "success": True,
                "session_id": session.session_id,
                "current_step": current_step,
                "workflow_stack": [
                    frame.workflow_name for frame in session.workflow_stack
                ],
                "message": "Returned to parent workflow",
            }
        else:
            # No parent workflow, end session
            self.session_manager.archive_session(session_id)

            return {
                "success": True,
                "session_id": session.session_id,
                "current_step": None,
                "workflow_stack": [],
                "message": "Session ended - no parent workflow",
            }

    def back_session(self, session_id: str) -> dict[str, Any]:
        """Go back to the previous step in the current workflow.

        Args:
            session_id: ID of the session

        Returns:
            Dict with previous step info or error

        """
        session = self.session_manager.load_session(session_id)
        if not session:
            return {"success": False, "error": f"Session {session_id} not found"}

        # Try to go back a step
        went_back = session.back_step()

        if went_back:
            # Save updated session and return current step
            self.session_manager.save_session(session)
            current_step = session.get_current_step()

            return {
                "success": True,
                "session_id": session.session_id,
                "current_step": current_step,
                "workflow_stack": [
                    frame.workflow_name for frame in session.workflow_stack
                ],
                "message": "Went back to previous step",
            }
        else:
            return {
                "success": False,
                "error": "Cannot go back - already at first step",
                "session_id": session.session_id,
            }

    def restart_session(self, session_id: str) -> dict[str, Any]:
        """Restart the session from the beginning.

        Args:
            session_id: ID of the session to restart

        Returns:
            Dict with first step info or error

        """
        session = self.session_manager.load_session(session_id)
        if not session:
            return {"success": False, "error": f"Session {session_id} not found"}

        # Restart the session
        session.restart_session()

        # Save updated session and return first step
        self.session_manager.save_session(session)
        current_step = session.get_current_step()

        return {
            "success": True,
            "session_id": session.session_id,
            "current_step": current_step,
            "workflow_stack": [frame.workflow_name for frame in session.workflow_stack],
            "message": "Session restarted from beginning",
        }

    def list_sessions(self) -> dict[str, Any]:
        """List all active workflow sessions.

        Returns:
            Dict with list of active sessions

        """
        try:
            session_ids = self.session_manager.list_active_sessions()
            sessions = []

            for session_id in session_ids:
                session = self.session_manager.load_session(session_id)
                if session:
                    sessions.append(
                        {
                            "session_id": session.session_id,
                            "prompt": session.prompt[:100] + "..."
                            if len(session.prompt) > 100
                            else session.prompt,
                            "workflow_stack": [
                                frame.workflow_name for frame in session.workflow_stack
                            ],
                            "is_complete": session.is_complete,
                            "created_at": session.created_at.isoformat(),
                            "last_accessed": session.last_accessed.isoformat(),
                        }
                    )

            return {"success": True, "sessions": sessions}

        except Exception as e:
            return {"success": False, "error": f"Failed to list sessions: {str(e)}"}

    def _get_workflow_steps(self, workflow_name: str) -> list[str] | None:
        """Get steps for a specific workflow.

        Args:
            workflow_name: Name of the workflow

        Returns:
            List of workflow steps or None if not found

        """
        # Try built-in workflow first
        built_in_workflow = self.workflow_registry.get_workflow(workflow_name)
        if built_in_workflow:
            return built_in_workflow.steps

        # Try config workflow
        workflow_config = self.config.workflows.get(workflow_name)
        if workflow_config:
            # Get project type and project-specific steps
            project_type = self.config.detect_project_type()
            project_config = self.config.project_types.get(project_type)

            if project_config and workflow_name in project_config.workflows:
                return project_config.workflows[workflow_name].steps
            else:
                return workflow_config.steps

        return None

    def _display_execution_plan(self, execution_order: list[str]) -> None:
        """Display the execution plan."""
        plan_items = []
        for i, workflow_name in enumerate(execution_order, 1):
            workflow_config = self.config.workflows.get(workflow_name)
            if workflow_config and workflow_config.description:
                description = workflow_config.description
            else:
                description = f"📋 {workflow_name.title()} workflow"

            plan_items.append(f"  {i}. {description}")

        self.console.print(
            Panel("\n".join(plan_items), title="📋 Execution Plan", border_style="cyan")
        )
        self.console.print()
