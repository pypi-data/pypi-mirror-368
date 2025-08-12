"""Quality tools for YAML workflow files (validation and normalization)."""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import Any

import yaml

try:  # Runtime-safe imports; avoid type resolution issues in some analyzers
    from yaml.nodes import MappingNode as _MappingNode
    from yaml.nodes import Node as _Node
    from yaml.nodes import ScalarNode as _ScalarNode
    from yaml.nodes import SequenceNode as _SequenceNode
except Exception:  # pragma: no cover
    _MappingNode = type("MappingNode", (), {})  # type: ignore
    _ScalarNode = type("ScalarNode", (), {})  # type: ignore
    _SequenceNode = type("SequenceNode", (), {})  # type: ignore
    _Node = object  # type: ignore


DATA_DIR = Path(__file__).parent / "data"

# Allowed keys in workflow YAMLs (others are preserved but flagged unless whitelisted)
ALLOWED_KEYS = {
    "name",
    "description",
    "triggers",
    "steps",
    "dependencies",
    "project_types",
    "conditions",
    # Legacy supported during migration
    "commands",
}

# Extra keys that are allowed in specific cases (metadata used by docs/UX)
ALLOWED_EXTRA_KEYS = {"display_name", "category", "guidance"}


def _iter_yaml_files(root: Path | None) -> list[Path]:
    base = root or DATA_DIR
    return sorted(p for p in base.rglob("*.yaml") if p.is_file())


def _collect_duplicate_keys_from_text(text: str) -> list[str]:
    """Return a flat list of duplicate mapping keys found via YAML AST traversal."""
    try:
        root_node = yaml.compose(text)
    except yaml.YAMLError:
        return []

    def _walk(node: Any | None) -> list[str]:
        if node is None:
            return []
        dups: list[str] = []
        if isinstance(node, _MappingNode):
            seen: set[str] = set()
            for key_node, value_node in node.value:
                key_str = (
                    key_node.value
                    if isinstance(key_node, _ScalarNode)
                    else str(key_node)
                )
                if key_str in seen:
                    dups.append(key_str)
                else:
                    seen.add(key_str)
                dups.extend(_walk(value_node))
        elif isinstance(node, _SequenceNode):
            for item in node.value:
                dups.extend(_walk(item))
        return dups

    return _walk(root_node)


def _load_yaml(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        return None, f"{path}: not UTF-8 encoded ({e})"

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        return None, f"{path}: YAML parse error: {e}"

    if not isinstance(data, dict):
        return None, f"{path}: YAML root must be a mapping/object"

    return data, None


def validate_workflow_yamls(root: Path | None = None) -> list[str]:
    """Validate all workflow YAML files. Returns a list of issue messages."""
    issues: list[str] = []
    names: dict[str, Path] = {}

    for file in _iter_yaml_files(root):
        # Detect duplicate keys by traversing the YAML AST before/alongside loading
        try:
            text_for_dups = file.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            issues.append(f"{file}: not UTF-8 encoded ({e})")
            continue

        dup_keys = _collect_duplicate_keys_from_text(text_for_dups)
        if dup_keys:
            uniq = ", ".join(sorted(set(dup_keys)))
            issues.append(f"{file}: duplicate keys detected: {uniq}")

        data, err = _load_yaml(file)
        if err:
            issues.append(err)
            continue

        if data is None:
            issues.append(f"{file}: empty or invalid YAML content")
            continue

        # Required fields
        for key in ("name", "description", "triggers", "steps"):
            if key not in data:
                issues.append(f"{file}: missing required key '{key}'")

        name = data.get("name")
        if isinstance(name, str):
            if name in names:
                issues.append(
                    f"{file}: duplicate workflow name '{name}' also in {names[name]}"
                )
            else:
                names[name] = file
        else:
            issues.append(f"{file}: 'name' must be a string")

        # Types
        if "triggers" in data and not isinstance(data["triggers"], list):
            issues.append(f"{file}: 'triggers' must be a list of strings")
        if "steps" in data and not isinstance(data["steps"], list):
            issues.append(f"{file}: 'steps' must be a list of strings")

        # Encoding sanity (replacement character indicates prior decode issues)
        replacement = "\ufffd"

        def _contains_repl(val: Any) -> bool:
            if isinstance(val, str):
                return replacement in val
            if isinstance(val, list):
                return any(_contains_repl(v) for v in val)
            if isinstance(val, dict):
                return any(_contains_repl(v) for v in val.values())
            return False

        if _contains_repl(data):
            issues.append(
                f"{file}: contains Unicode replacement character (�); fix UTF-8 content"
            )

        # Unknown keys
        unknown = set(data.keys()) - ALLOWED_KEYS - ALLOWED_EXTRA_KEYS
        if unknown:
            pretty = ", ".join(sorted(unknown))
            issues.append(f"{file}: unknown keys: {pretty}")

    return issues


def _normalize_data(data: dict[str, Any]) -> dict[str, Any]:
    """Return a normalized mapping with preferred keys order and legacy migrations."""
    # Migrate legacy commands -> steps
    if "steps" not in data and isinstance(data.get("commands"), list):
        data["steps"] = list(data["commands"])  # copy
        del data["commands"]

    # Coerce expected list fields to lists
    for key in ("triggers", "steps", "dependencies", "project_types", "conditions"):
        if key in data and data[key] is None:
            data[key] = []

    # Build ordered output
    ordered = OrderedDict()
    for key in (
        "name",
        "description",
        "triggers",
        "steps",
        "dependencies",
        "project_types",
        "conditions",
    ):
        if key in data:
            ordered[key] = data[key]
    # Preserve known extra metadata next
    for key in sorted(ALLOWED_EXTRA_KEYS):
        if key in data:
            ordered[key] = data[key]
    # Append any remaining keys to avoid destructive changes
    for key in data:
        if key not in ordered:
            ordered[key] = data[key]
    return ordered


def format_workflow_yamls(
    root: Path | None = None, *, write: bool = False
) -> list[str]:
    """Normalize workflow YAMLs and optionally write back.

    Returns list of change summaries.
    """
    changes: list[str] = []
    for file in _iter_yaml_files(root):
        original_text = file.read_text(encoding="utf-8", errors="replace")
        try:
            data = yaml.safe_load(original_text)
        except yaml.YAMLError:
            # Skip files with syntax errors (validator will report)
            continue
        if not isinstance(data, dict):
            continue

        normalized = _normalize_data(dict(data))

        # Serialize with stable formatting (no key sorting; keep our order)
        new_text = yaml.safe_dump(
            normalized,
            sort_keys=False,
            allow_unicode=True,
            width=100,
        )

        if new_text != original_text:
            change_msg = (
                f"{file}: will reformat ({len(original_text)} -> {len(new_text)} chars)"
            )
            changes.append(change_msg)
            if write:
                file.write_text(new_text, encoding="utf-8")

    return changes
