"""Validate HACS integration repository structure from the checkout.

The upstream hacs/action downloads hacs.json and manifest.json from
raw.githubusercontent.com, which returns 404 for private repositories.
This script validates the same layout from the checked-out workspace instead.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CUSTOM_COMPONENTS = REPO_ROOT / "custom_components"
HACS_JSON = REPO_ROOT / "hacs.json"
REQUIRED_MANIFEST_KEYS = (
    "domain",
    "name",
    "version",
    "documentation",
    "issue_tracker",
    "codeowners",
)


def fail(message: str) -> None:
    """Print a GitHub Actions error annotation and exit."""
    print(f"::error::{message}")
    sys.exit(1)


def load_json(path: Path, label: str) -> dict:
    """Load and validate a JSON object from disk."""
    if not path.is_file():
        fail(f"Missing {label}: {path.relative_to(REPO_ROOT)}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        fail(f"Invalid {label}: {err}")

    if not isinstance(data, dict):
        fail(f"{label} must be a JSON object")

    return data


def main() -> None:
    """Run HACS structure checks against the local checkout."""
    hacs_data = load_json(HACS_JSON, "hacs.json")
    if not hacs_data.get("name"):
        fail("hacs.json must define 'name'")

    if not CUSTOM_COMPONENTS.is_dir():
        fail("Missing custom_components directory")

    integration_dirs = sorted(
        path
        for path in CUSTOM_COMPONENTS.iterdir()
        if path.is_dir() and not path.name.startswith((".", "__"))
    )
    if len(integration_dirs) != 1:
        fail(
            "custom_components must contain exactly one integration directory, "
            f"found {len(integration_dirs)}"
        )

    integration_dir = integration_dirs[0]
    manifest = load_json(integration_dir / "manifest.json", "manifest.json")

    for key in REQUIRED_MANIFEST_KEYS:
        if key not in manifest:
            fail(f"manifest.json missing required key: {key}")

    brand_icon = integration_dir / "brand" / "icon.png"
    if not brand_icon.is_file():
        fail(f"Missing brand icon: {brand_icon.relative_to(REPO_ROOT)}")

    print("HACS structure validation passed")


if __name__ == "__main__":
    main()
