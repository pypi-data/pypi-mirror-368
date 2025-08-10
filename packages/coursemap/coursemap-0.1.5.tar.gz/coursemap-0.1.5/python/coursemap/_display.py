"""
Environment detection and display logic

This module handles automatic detection of Jupyter/Quarto environments
and provides appropriate display methods for each.
"""

import os


def _detect_environment():
    """
    Detect the current execution environment

    Returns:
        str: 'jupyter', 'quarto', or 'terminal'
    """
    # Jupyter detection
    try:
        from IPython import get_ipython

        if get_ipython() is not None:
            # Check if we're in Quarto with Jupyter kernel
            if (
                os.environ.get("QUARTO_PROJECT_DIR")
                or os.environ.get("QUARTO_PROJECT_ROOT")
                or os.environ.get("QUARTO_RENDER_TOKEN")
                or os.environ.get("QUARTO_PROJECT_OUTPUT_DIR")
            ):
                return "quarto"
            return "jupyter"
    except ImportError:
        pass

    # Quarto detection - check for Quarto environment variables
    if (
        os.environ.get("QUARTO_PROJECT_DIR")
        or os.environ.get("QUARTO_PROJECT_ROOT")
        or os.environ.get("QUARTO_RENDER_TOKEN")
        or os.environ.get("QUARTO_PROJECT_OUTPUT_DIR")
        or os.environ.get("QUARTO_PROFILE")
    ):
        return "quarto"

    return "terminal"


def _show_in_environment(svg_content):
    """
    Display SVG content appropriately for the current environment

    Args:
        svg_content (str): SVG content to display
    """
    env = _detect_environment()

    if env == "jupyter":
        try:
            from IPython.display import SVG, display

            display(SVG(svg_content))
            return
        except ImportError:
            pass

    elif env == "quarto":
        try:
            # Try IPython display first (works in Quarto with Jupyter kernel)
            from IPython.display import HTML, display

            # Wrap SVG in a centered div for better presentation
            html_content = f"""
            <div style="text-align: center; margin: 20px 0;">
                {svg_content}
            </div>
            """
            display(HTML(html_content))
            return
        except ImportError:
            # Fallback: print raw SVG (Quarto will render it)
            print(svg_content)
            return

    # Terminal fallback - only show messages in terminal
    print("Course map generated.")
    print(
        "💡 Tip: Use .save('filename.svg') to save to file, or run in Jupyter/Quarto for inline display."
    )


def _format_filename_with_extension(filename, format_type):
    """
    Ensure filename has the correct extension for the given format

    Args:
        filename (str): Original filename
        format_type (str): Format type ('svg', 'png', 'dot')

    Returns:
        str: Filename with correct extension
    """
    # Remove any existing extension that doesn't match
    base_name = filename
    for ext in [".svg", ".png", ".dot"]:
        if base_name.endswith(ext):
            base_name = base_name[: -len(ext)]
            break

    # Add the correct extension
    return f"{base_name}.{format_type}"
