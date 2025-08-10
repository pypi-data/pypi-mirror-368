"""
Course Map - Visualize course dependencies from Quarto/Markdown documents

A simple, intuitive API for course dependency visualization from Quarto/Markdown documents.

Example usage:
    import coursemap

    # Quick display
    coursemap.show("./courses")

    # Object-oriented approach
    cm = coursemap.CourseMap("./courses")
    cm.show()  # Display inline
    cm.save("map.png")  # Save to file
"""

from ._core import _CourseMap, _graphviz_available, _graphviz_info
from ._display import _format_filename_with_extension, _show_in_environment

__version__ = "0.1.5"


class CourseMap:
    """
    Course dependency map visualization

    A simple interface for creating and displaying course dependency maps.
    """

    def __init__(self, input_dir=".", config=None):
        """
        Create a course map from documents in a directory

        Args:
            input_dir (str): Directory containing course documents (default: current directory)
            config (str, optional): Path to configuration file (default: auto-detect coursemap.yml)

        Example:
            >>> cm = coursemap.CourseMap("./courses")
            >>> cm.show()
        """
        self._cm = _CourseMap(config)
        self._input_dir = input_dir

    def show(self):
        """
        Display the course map inline (like matplotlib.pyplot.show())

        Automatically detects the environment:
        - Jupyter: Shows as interactive SVG
        - Quarto: Embeds as HTML/SVG
        - Terminal: Shows helpful message

        Example:
            >>> cm = coursemap.CourseMap("./courses")
            >>> cm.show()  # Displays inline in Jupyter/Quarto
        """
        svg_content = self._cm.generate_inline_svg(self._input_dir)
        _show_in_environment(svg_content)

    def save(self, filename, format=None):
        """
        Save course map to file

        Args:
            filename (str): Output filename
            format (str, optional): Output format ('svg', 'png', 'dot').
                                   Auto-detected from filename extension if not specified.

        Returns:
            str: Path to the saved file

        Example:
            >>> cm = coursemap.CourseMap("./courses")
            >>> cm.save("map.png")  # Saves as PNG
            >>> cm.save("graph.dot", format="dot")  # Saves as DOT format
        """
        if format is None:
            # Auto-detect format from extension
            if filename.endswith(".png"):
                format = "png"
            elif filename.endswith(".svg"):
                format = "svg"
            elif filename.endswith(".dot"):
                format = "dot"
            else:
                format = "svg"  # default

        # Ensure filename has correct extension
        actual_filename = _format_filename_with_extension(filename, format)

        return self._cm.generate(self._input_dir, actual_filename, format)

    def get_config(self):
        """
        Get the current configuration as a dictionary

        Returns:
            dict: Configuration dictionary with 'root_key', 'phase', and 'ignore' keys
        """
        return self._cm.get_config()

    def parse_documents(self):
        """
        Parse documents and return metadata

        Returns:
            list: List of document metadata dictionaries
        """
        return self._cm.parse_documents(self._input_dir)


def show(input_dir=".", config=None):
    """
    Quick display of course map (like matplotlib.pyplot.show())

    Args:
        input_dir (str): Directory containing course documents (default: current directory)
        config (str, optional): Path to configuration file (default: auto-detect coursemap.yml)

    Example:
        >>> import coursemap
        >>> coursemap.show("./courses")  # One-liner to display course map
    """
    cm = CourseMap(input_dir, config)
    cm.show()


def graphviz_available():
    """
    Check if Graphviz is available for PNG/SVG generation

    Returns:
        bool: True if Graphviz is available, False otherwise

    Example:
        >>> import coursemap
        >>> if coursemap.graphviz_available():
        ...     print("Can generate PNG/SVG files")
        ... else:
        ...     print("Only DOT format available")
    """
    return _graphviz_available()


def graphviz_info():
    """
    Get Graphviz version and installation information

    Returns:
        str: Graphviz version information

    Raises:
        RuntimeError: If Graphviz is not available

    Example:
        >>> import coursemap
        >>> if coursemap.graphviz_available():
        ...     print(coursemap.graphviz_info())
    """
    return _graphviz_info()


# Clean public API - only expose what users should use
__all__ = [
    "CourseMap",
    "show",
    "graphviz_available",
    "graphviz_info",
]
