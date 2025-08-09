"""Config utilities for poetry and pyproject.toml."""

from pathlib import Path
from typing import Any

import tomlkit
from tomlkit.toml_document import TOMLDocument

from winipedia_utils.projects.poetry.poetry import logger


def laod_pyproject_toml() -> TOMLDocument:
    """Load the pyproject.toml file."""
    return tomlkit.parse(Path("pyproject.toml").read_text())


def dump_pyproject_toml(toml: TOMLDocument) -> None:
    """Dump the pyproject.toml file."""
    with Path("pyproject.toml").open("w") as f:
        tomlkit.dump(toml, f)


def get_poetry_package_name() -> str:
    """Get the name of the project from pyproject.toml."""
    toml = laod_pyproject_toml()
    project_dict = toml.get("project", {})
    project_name = str(project_dict.get("name", ""))
    return project_name.replace("-", "_")


def _get_pyproject_toml_tool_configs() -> dict[str, Any]:
    """Get the tool configurations for pyproject.toml."""
    return {
        "ruff": {
            "exclude": [".*", "**/migrations/*.py"],
            "lint": {
                "select": ["ALL"],
                "ignore": ["D203", "D213", "COM812", "ANN401"],
                "fixable": ["ALL"],
                "pydocstyle": {
                    "convention": "google",
                },
            },
        },
        "mypy": {
            "strict": True,
            "warn_unreachable": True,
            "show_error_codes": True,
            "files": ".",
        },
        "pytest": {
            "ini_options": {
                "testpaths": ["tests"],
            }
        },
        "bandit": {},
    }


def _tool_config_is_correct(tool: str, config: dict[str, Any]) -> bool:
    """Check if the tool configuration in pyproject.toml is correct."""
    toml = laod_pyproject_toml()
    actual_tools = toml.get("tool", {})

    return bool(actual_tools.get(tool) == config)


def _pyproject_tool_configs_are_correct() -> bool:
    """Check if the tool configurations in pyproject.toml are correct."""
    expected_tool_dict = _get_pyproject_toml_tool_configs()
    for tool, config in expected_tool_dict.items():
        if not _tool_config_is_correct(tool, config):
            return False

    return True


def _add_configurations_to_pyproject_toml() -> None:
    """Add tool.* configurations to pyproject.toml."""
    expected_tool_dict = _get_pyproject_toml_tool_configs()
    toml = laod_pyproject_toml()
    actual_tool_dict = toml.get("tool", {})
    # update the toml dct and dump it but only update the tools specified not all tools
    for tool, config in expected_tool_dict.items():
        # if tool section already exists skip it
        if not _tool_config_is_correct(tool, config):
            logger.info("Adding tool.%s configuration to pyproject.toml", tool)
            # updates inplace of toml_dict["tool"][tool]
            actual_tool_dict[tool] = config

    dump_pyproject_toml(toml)
