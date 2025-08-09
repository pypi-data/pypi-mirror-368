"""utils for svgs."""

from importlib.resources import as_file, files
from pathlib import Path
from types import ModuleType

from winipedia_utils.resources import svgs


def get_svg_path(svg_name: str, package: ModuleType | None = None) -> Path:
    """Get the path to a svg."""
    package = package or svgs
    svg_path = files(package) / f"{svg_name}.svg"
    with as_file(svg_path) as path:
        return path
