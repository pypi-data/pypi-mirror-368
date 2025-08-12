"""Configuration management for vibe."""

from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from .project_types import ProjectDetector


class WorkflowConfig(BaseModel):
    """Configuration for a specific workflow."""

    triggers: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)  # Guidance steps (preferred)
    commands: list[str] = Field(default_factory=list)  # Legacy format, maps to steps
    description: str = ""
    dependencies: list[str] = Field(default_factory=list)

    def __post_init__(self) -> None:
        """Convert legacy commands to steps if needed."""
        # If commands are provided but steps are empty, use commands as steps
        if self.commands and not self.steps:
            self.steps = self.commands


class ProjectTypeConfig(BaseModel):
    """Configuration for a project type."""

    name: str
    detection_files: list[str] = Field(default_factory=list)
    workflows: dict[str, WorkflowConfig] = Field(default_factory=dict)


class VibeConfig(BaseModel):
    """Main vibe configuration."""

    project_type: str = "auto"
    workflows: dict[str, WorkflowConfig] = Field(default_factory=dict)
    project_types: dict[str, ProjectTypeConfig] = Field(default_factory=dict)

    @classmethod
    def load_from_file(cls, config_path: Path | None = None) -> "VibeConfig":
        """Load configuration from file."""
        if config_path is None:
            config_path = cls._find_config_file()

        if config_path and config_path.exists():
            with open(config_path) as f:
                data = yaml.safe_load(f) or {}

            # Merge with defaults
            config = cls(**data)
            config._load_defaults()
            return config

        # Return default config
        config = cls()
        config._load_defaults()
        return config

    @classmethod
    def _find_config_file(cls) -> Path | None:
        """Find vibe configuration file."""
        current_dir = Path.cwd()

        # Look for config files in current directory and parents
        for path in [current_dir] + list(current_dir.parents):
            for config_name in [".vibe.yaml", "vibe.yaml", ".vibe.yml", "vibe.yml"]:
                config_path = path / config_name
                if config_path.exists():
                    return config_path

        return None

    def _load_defaults(self) -> None:
        """Load default workflow and project type configurations."""
        # Merge default workflows (do not overwrite user-defined)
        default_workflows = self._get_default_workflows()
        if not self.workflows:
            self.workflows = default_workflows
        else:
            for key, wf in default_workflows.items():
                if key not in self.workflows:
                    self.workflows[key] = wf

        # Merge default project types and their workflows
        default_pt = self._get_default_project_types()
        if not self.project_types:
            self.project_types = default_pt
        else:
            for pt_name, pt_cfg in default_pt.items():
                if pt_name not in self.project_types:
                    self.project_types[pt_name] = pt_cfg
                else:
                    # Ensure default workflows exist for the project type
                    # without overriding
                    existing = self.project_types[pt_name]
                    for wf_name, wf_cfg in pt_cfg.workflows.items():
                        if wf_name not in existing.workflows:
                            existing.workflows[wf_name] = wf_cfg

    def _get_default_workflows(self) -> dict[str, WorkflowConfig]:
        """Get default workflow configurations."""
        return {
            "analysis": WorkflowConfig(
                triggers=[
                    "analyze",
                    "explore",
                    "understand",
                    "investigate",
                    "research",
                    "review",
                    "examine",
                    "study",
                ],
                description=(
                    "🔍 Codebase exploration, pattern identification, and research"
                ),
                commands=["echo 'Analyzing project structure...'"],
            ),
            "implementation": WorkflowConfig(
                triggers=[
                    "implement",
                    "add",
                    "create",
                    "build",
                    "develop",
                    "code",
                    "make",
                    "generate",
                    "fix",
                    "refactor",
                ],
                description="🛠️ Feature development, bug fixes, and code changes",
                dependencies=["analysis"],
            ),
            "testing": WorkflowConfig(
                triggers=[
                    "test",
                    "validate",
                    "check",
                    "verify",
                    "ensure",
                    "coverage",
                    "spec",
                    "unit",
                    "integration",
                    "e2e",
                ],
                description="🧪 Test execution, validation, and quality verification",
                dependencies=["implementation"],
            ),
            "documentation": WorkflowConfig(
                triggers=[
                    "document",
                    "explain",
                    "guide",
                    "readme",
                    "docs",
                    "adr",
                    "comment",
                    "describe",
                ],
                description="📚 Documentation updates, guides, and explanations",
            ),
            "quality": WorkflowConfig(
                triggers=[
                    "lint",
                    "format",
                    "type",
                    "audit",
                    "security",
                    "compliance",
                    "standards",
                    "quality",
                ],
                description="✨ Code quality, linting, formatting, and compliance",
                dependencies=["implementation"],
            ),
            "git": WorkflowConfig(
                triggers=[
                    "commit",
                    "push",
                    "pull",
                    "merge",
                    "branch",
                    "pr",
                    "git",
                    "repository",
                    "version",
                ],
                description=(
                    "🔄 Git operations, commits, PRs, and repository management"
                ),
            ),
            "mcp": WorkflowConfig(
                triggers=[
                    "context7",
                    "github.*mcp",
                    "playwright",
                    "sequential.*thinking",
                    "mcp.*tools",
                ],
                description="🤖 MCP tools integration and AI-enhanced workflows",
            ),
            "session": WorkflowConfig(
                triggers=[
                    "complete",
                    "finish",
                    "cleanup",
                    "session",
                    "workflow",
                    "orchestrat",
                ],
                description="🎯 Session management, completion, and cleanup",
            ),
        }

    def _get_default_project_types(self) -> dict[str, ProjectTypeConfig]:
        """Get default project type configurations."""
        return {
            "python": ProjectTypeConfig(
                name="python",
                detection_files=[
                    "pyproject.toml",
                    "setup.py",
                    "requirements.txt",
                    "Pipfile",
                ],
                workflows={
                    "testing": WorkflowConfig(
                        commands=["python -m pytest", "ruff check"]
                    ),
                    "quality": WorkflowConfig(commands=["ruff format", "mypy ."]),
                    "analysis": WorkflowConfig(
                        commands=["find . -name '*.py' -type f | head -20"]
                    ),
                },
            ),
            "vue_typescript": ProjectTypeConfig(
                name="vue_typescript",
                detection_files=["package.json", "vite.config.ts", "vue.config.js"],
                workflows={
                    "testing": WorkflowConfig(
                        commands=["bun run test", "bun run type-check"]
                    ),
                    "quality": WorkflowConfig(
                        commands=["bun run lint", "bun run format"]
                    ),
                    "analysis": WorkflowConfig(
                        commands=["find src/ -name '*.vue' -o -name '*.ts' | head -20"]
                    ),
                },
            ),
            "generic": ProjectTypeConfig(
                name="generic",
                detection_files=[],
                workflows={
                    "analysis": WorkflowConfig(
                        commands=["ls -la", "find . -type f -name '*.md' | head -10"]
                    ),
                    "git": WorkflowConfig(
                        commands=["git status", "git log --oneline -10"]
                    ),
                },
            ),
        }

    def detect_project_type(self, project_path: Path | None = None) -> str:
        """Detect project type based on intelligent analysis."""
        if self.project_type != "auto":
            return self.project_type

        if project_path is None:
            project_path = Path.cwd()

        # Use the intelligent project detector
        detector = ProjectDetector(str(project_path))
        return detector.detect_project_type()
