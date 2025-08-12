"""Enhanced project type detection with comprehensive framework support."""

import json
from pathlib import Path
from typing import Any


class ProjectDetector:
    """Intelligent project type detection based on files, dependencies,
    and structure.
    """

    def __init__(self, project_path: str = "."):
        """Initialize the project detector with a given path."""
        self.project_path = Path(project_path)

    def detect_project_type(self) -> str:
        """Detect the primary project type."""
        detections = self.detect_all_project_types()

        # Return the most specific/confident detection
        # Priority order: specific frameworks > language > generic
        priority_order = [
            "vue",
            "react",
            "next",
            "nuxt",
            "svelte",
            "angular",
            "django",
            "fastapi",
            "flask",
            "rails",
            "typescript",
            "javascript",
            "python",
            "rust",
            "go",
            "web",
            "node",
            "generic",
        ]

        for project_type in priority_order:
            if project_type in detections:
                return project_type

        return "generic"

    def detect_all_project_types(self) -> list[str]:
        """Detect all applicable project types/frameworks."""
        types = []

        # Check for specific frameworks and languages
        if self._is_vue_project():
            types.extend(["vue", "javascript", "web", "node"])

        if self._is_react_project():
            types.extend(["react", "javascript", "web", "node"])

        if self._is_next_project():
            types.extend(["next", "react", "javascript", "web", "node"])

        if self._is_nuxt_project():
            types.extend(["nuxt", "vue", "javascript", "web", "node"])

        if self._is_svelte_project():
            types.extend(["svelte", "javascript", "web", "node"])

        if self._is_angular_project():
            types.extend(["angular", "typescript", "web", "node"])

        if self._is_typescript_project():
            types.extend(["typescript", "javascript", "node"])

        if self._is_javascript_project():
            types.extend(["javascript", "node"])

        if self._is_python_project():
            types.append("python")

            # Check for Python frameworks
            if self._is_django_project():
                types.append("django")
            elif self._is_fastapi_project():
                types.append("fastapi")
            elif self._is_flask_project():
                types.append("flask")

        if self._is_rust_project():
            types.append("rust")

        if self._is_go_project():
            types.append("go")

        if self._is_web_project():
            types.append("web")

        # Remove duplicates while preserving order
        return list(dict.fromkeys(types))

    def _is_vue_project(self) -> bool:
        """Detect Vue.js projects."""
        # Check for Vue files
        if self._has_files_with_extension(".vue"):
            return True

        # Check package.json for Vue dependencies
        if self._has_npm_dependency(["vue", "@vue/cli", "vite", "nuxt"]):
            return True

        return False

    def _is_react_project(self) -> bool:
        """Detect React projects."""
        if self._has_npm_dependency(["react", "react-dom", "create-react-app"]):
            return True

        if self._has_files_with_extension([".jsx", ".tsx"]):
            return True

        return False

    def _is_next_project(self) -> bool:
        """Detect Next.js projects."""
        return self._has_npm_dependency(["next"]) or self._file_exists("next.config.js")

    def _is_nuxt_project(self) -> bool:
        """Detect Nuxt projects."""
        return self._has_npm_dependency(["nuxt", "@nuxt/cli"]) or self._file_exists(
            "nuxt.config.js"
        )

    def _is_svelte_project(self) -> bool:
        """Detect Svelte projects."""
        return self._has_npm_dependency(
            ["svelte", "@sveltejs/kit"]
        ) or self._has_files_with_extension(".svelte")

    def _is_angular_project(self) -> bool:
        """Detect Angular projects."""
        return self._has_npm_dependency(
            ["@angular/core", "@angular/cli"]
        ) or self._file_exists("angular.json")

    def _is_typescript_project(self) -> bool:
        """Detect TypeScript projects."""
        if self._file_exists("tsconfig.json"):
            return True

        if self._has_npm_dependency(["typescript"]):
            return True

        if self._has_files_with_extension([".ts", ".tsx"]):
            return True

        return False

    def _is_javascript_project(self) -> bool:
        """Detect JavaScript/Node.js projects."""
        if self._file_exists("package.json"):
            return True

        if self._has_files_with_extension([".js", ".mjs", ".cjs"]):
            return True

        return False

    def _is_python_project(self) -> bool:
        """Detect Python projects."""
        python_files = [
            "pyproject.toml",
            "setup.py",
            "requirements.txt",
            "Pipfile",
            "poetry.lock",
            "setup.cfg",
        ]

        for file in python_files:
            if self._file_exists(file):
                return True

        if self._has_files_with_extension(".py"):
            return True

        return False

    def _is_django_project(self) -> bool:
        """Detect Django projects."""
        if self._has_python_dependency(["django", "Django"]):
            return True

        if self._file_exists("manage.py"):
            return True

        return False

    def _is_fastapi_project(self) -> bool:
        """Detect FastAPI projects."""
        return self._has_python_dependency(["fastapi", "uvicorn"])

    def _is_flask_project(self) -> bool:
        """Detect Flask projects."""
        return self._has_python_dependency(["flask", "Flask"])

    def _is_rust_project(self) -> bool:
        """Detect Rust projects."""
        return self._file_exists("Cargo.toml")

    def _is_go_project(self) -> bool:
        """Detect Go projects."""
        return self._file_exists("go.mod") or self._has_files_with_extension(".go")

    def _is_web_project(self) -> bool:
        """Detect general web projects."""
        web_files = ["index.html", "style.css", "styles.css", "main.css"]
        for file in web_files:
            if self._file_exists(file):
                return True

        if self._has_files_with_extension([".html", ".css", ".scss", ".sass"]):
            return True

        return False

    def _file_exists(self, filename: str) -> bool:
        """Check if a file exists in the project root."""
        return (self.project_path / filename).exists()

    def _has_files_with_extension(self, extensions: str | list[str]) -> bool:
        """Check if files with given extensions exist."""
        if isinstance(extensions, str):
            extensions = [extensions]

        for ext in extensions:
            if not ext.startswith("."):
                ext = "." + ext

            # Search for files with this extension
            for file_path in self.project_path.rglob(f"*{ext}"):
                # Skip node_modules, __pycache__, etc.
                if not any(
                    part.startswith(".")
                    or part in ["node_modules", "__pycache__", "venv", "env"]
                    for part in file_path.parts
                ):
                    return True

        return False

    def _has_npm_dependency(self, dependencies: list[str]) -> bool:
        """Check if any of the dependencies exist in package.json."""
        package_json_path = self.project_path / "package.json"
        if not package_json_path.exists():
            return False

        try:
            with open(package_json_path) as f:
                package_data = json.load(f)

            all_deps = {}
            all_deps.update(package_data.get("dependencies", {}))
            all_deps.update(package_data.get("devDependencies", {}))
            all_deps.update(package_data.get("peerDependencies", {}))

            for dep in dependencies:
                if dep in all_deps:
                    return True

        except (OSError, json.JSONDecodeError):
            pass

        return False

    def _has_python_dependency(self, dependencies: list[str]) -> bool:
        """Check if any of the dependencies exist in Python project files."""
        # Check pyproject.toml
        pyproject_path = self.project_path / "pyproject.toml"
        if pyproject_path.exists():
            try:
                import tomllib

                with open(pyproject_path, "rb") as f:
                    pyproject_data = tomllib.load(f)

                # Check dependencies in project section
                project_deps = pyproject_data.get("project", {}).get("dependencies", [])
                for dep_line in project_deps:
                    dep_name = (
                        dep_line.split(">=")[0].split("==")[0].split("[")[0].strip()
                    )
                    if dep_name.lower() in [d.lower() for d in dependencies]:
                        return True

            except (ImportError, Exception):
                # Fallback to text parsing if tomllib not available
                try:
                    with open(pyproject_path) as f:
                        content = f.read().lower()
                        for dep in dependencies:
                            if dep.lower() in content:
                                return True
                except OSError:
                    pass

        # Check requirements.txt
        req_path = self.project_path / "requirements.txt"
        if req_path.exists():
            try:
                with open(req_path) as f:
                    content = f.read().lower()
                    for dep in dependencies:
                        if dep.lower() in content:
                            return True
            except OSError:
                pass

        return False

    def get_project_info(self) -> dict[str, Any]:
        """Get comprehensive project information."""
        return {
            "primary_type": self.detect_project_type(),
            "all_types": self.detect_all_project_types(),
            "has_package_json": self._file_exists("package.json"),
            "has_pyproject_toml": self._file_exists("pyproject.toml"),
            "has_cargo_toml": self._file_exists("Cargo.toml"),
            "has_go_mod": self._file_exists("go.mod"),
            "has_git": self._file_exists(".git"),
            "has_docker": self._file_exists("Dockerfile")
            or self._file_exists("docker-compose.yml"),
            "has_tests": self._has_test_files(),
            "has_docs": self._has_documentation_files(),
        }

    def _has_test_files(self) -> bool:
        """Check if the project has test files."""
        test_patterns = [
            "test",
            "tests",
            "spec",
            "__tests__",
            "*.test.*",
            "*_test.*",
            "test_*",
            "*_spec.*",
        ]

        for pattern in test_patterns:
            if pattern.startswith("*"):
                # File pattern
                if self._has_files_with_extension(pattern):
                    return True
            else:
                # Directory pattern
                if (self.project_path / pattern).exists():
                    return True

        return False

    def _has_documentation_files(self) -> bool:
        """Check if the project has documentation."""
        doc_files = ["README.md", "README.rst", "README.txt", "docs", "documentation"]

        for doc_file in doc_files:
            if self._file_exists(doc_file) or (self.project_path / doc_file).is_dir():
                return True

        return False
