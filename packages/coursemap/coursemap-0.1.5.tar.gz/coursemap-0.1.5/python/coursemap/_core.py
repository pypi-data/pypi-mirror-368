"""
Internal core functionality - Rust bindings wrapper

This module wraps the Rust bindings and should not be imported directly.
"""

try:
    from .coursemap_rs import CourseMap as _RustCourseMap
    from .coursemap_rs import generate_course_map as _rust_generate_course_map
    from .coursemap_rs import generate_inline_svg as _rust_generate_inline_svg
    from .coursemap_rs import graphviz_available as _rust_graphviz_available
    from .coursemap_rs import graphviz_info as _rust_graphviz_info
except ImportError as e:
    raise ImportError(
        "Failed to import Rust extension. Make sure the package is properly installed with maturin."
    ) from e


class _CourseMap:
    """Internal wrapper for Rust CourseMap"""

    def __init__(self, config_path=None):
        self._rust_cm = _RustCourseMap(config_path)

    def generate(self, input_dir, output_path, format):
        """Generate course map to file"""
        return self._rust_cm.generate(input_dir, output_path, format)

    def generate_inline_svg(self, input_dir):
        """Generate SVG content as string"""
        return self._rust_cm.generate_inline_svg(input_dir)

    def get_config(self):
        """Get configuration as dictionary"""
        return self._rust_cm.get_config()

    def parse_documents(self, input_dir):
        """Parse documents and return metadata"""
        return self._rust_cm.parse_documents(input_dir)


def _generate_course_map(input_dir, output_path, format, config_path=None):
    """Internal course map generation function"""
    return _rust_generate_course_map(input_dir, output_path, format, config_path)


def _generate_inline_svg(input_dir, config_path=None):
    """Internal inline SVG generation function"""
    return _rust_generate_inline_svg(input_dir, config_path)


def _graphviz_available():
    """Check if Graphviz is available"""
    return _rust_graphviz_available()


def _graphviz_info():
    """Get Graphviz version information"""
    return _rust_graphviz_info()
