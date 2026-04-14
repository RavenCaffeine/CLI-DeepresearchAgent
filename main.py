"""
CLI-DeepResearch — Entry Point

Delegates to the CLI module. Can also be invoked via the `deepresearch`
console script defined in pyproject.toml.
"""

from deepresearch.cli.main import main


if __name__ == "__main__":
    raise SystemExit(main())
