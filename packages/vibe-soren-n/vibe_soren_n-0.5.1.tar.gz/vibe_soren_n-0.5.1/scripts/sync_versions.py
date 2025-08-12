#!/usr/bin/env python3
"""Sync version across all project files."""

import json
import sys
from pathlib import Path


def update_vscode_extension_version(version: str) -> None:
    """Update VS Code extension package.json version."""
    package_json_path = Path("vscode-extension/package.json")
    if not package_json_path.exists():
        print(f"Warning: {package_json_path} not found")
        return

    with open(package_json_path, encoding="utf-8") as f:
        package_data = json.load(f)

    package_data["version"] = version

    with open(package_json_path, "w", encoding="utf-8") as f:
        json.dump(package_data, f, indent=2)
        f.write("\n")

    print(f"✅ Updated VS Code extension version to {version}")


def main() -> None:
    """Main version sync function."""
    if len(sys.argv) != 2:
        print("Usage: python sync_versions.py <version>")
        sys.exit(1)

    version = sys.argv[1]
    print(f"🔄 Syncing version to {version}")

    # Update VS Code extension
    update_vscode_extension_version(version)

    print(f"✅ Version sync complete: {version}")


if __name__ == "__main__":
    main()
