import os
from typing import Any


# function to save as svg and pdf a fig to path for lmu
def save_fig(fig: Any, name: str | None = None, path: str | None = None) -> None:
    """Save matplotlib figure as SVG and PDF files.
    Args:
        fig: Matplotlib figure object
        name: Name of the output files (without extension)
        path: Directory path to save the files
    Raises:
        ValueError: If name or path is None
        OSError: If there is an error creating directory or saving files
    """
    if name is None:
        raise ValueError("Figure name cannot be None")
    if path is None:
        raise ValueError("Save path cannot be None")

    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except OSError as e:
        raise OSError(f"Failed to create directory {path}: {e}") from e

    try:
        path_svg = os.path.join(path, f"{name}.svg")
        fig.savefig(path_svg, format="svg")

        path_pdf = os.path.join(path, f"{name}.pdf")
        fig.savefig(path_pdf, format="pdf")
    except Exception as e:
        raise OSError(f"Failed to save figure {name}: {e}") from e
