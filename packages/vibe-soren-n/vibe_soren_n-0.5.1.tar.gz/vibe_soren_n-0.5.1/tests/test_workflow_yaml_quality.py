from pathlib import Path

from vibe.workflows.quality import validate_workflow_yamls


def write(base_path: Path, relative_path: str, content: str) -> Path:
    p = base_path / relative_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def test_detect_duplicate_keys(tmp_path: Path) -> None:
    yaml_content = """
name: sample
description: dup keys test
triggers: ["a"]
steps: ["x"]
conditions: ["one"]
conditions: ["two"]
"""
    write(tmp_path, "data/sample.yaml", yaml_content)

    issues = validate_workflow_yamls(root=tmp_path)
    assert any("duplicate keys detected" in m for m in issues)


def test_detect_unicode_replacement(tmp_path: Path) -> None:
    yaml_content = """
name: sample2
description: replacement char test
triggers: ["a"]
steps: ["bad � char"]
"""
    write(tmp_path, "data/sample2.yaml", yaml_content)

    issues = validate_workflow_yamls(root=tmp_path)
    assert any("Unicode replacement character" in m for m in issues)


def test_yaml_workflows_validate_clean() -> None:
    issues = validate_workflow_yamls(None)
    # Should be empty after fixing obvious issues
    assert issues == []
