# CourseMap Python Package

Python bindings for the CourseMap tool - a Rust-based course dependency visualization tool.

## Installation

```bash
pip install coursemap
```

## Usage

### Python API

```python
import coursemap

# Generate course map
coursemap.generate_course_map("./courses", "map.svg", "svg")

# Generate inline SVG for Quarto
svg_content = coursemap.generate_inline_svg("./courses")

# Check Graphviz availability
if coursemap.check_graphviz_available():
    print(coursemap.get_graphviz_info())
```

### Command Line

```bash
course-map -i courses -o map.svg -v
course-map --check-graphviz
course-map --inline -i courses
```

### Quarto Integration

```python
#| echo: false
import coursemap

# Generate and display course map
svg_content = coursemap.create_quarto_filter("../courses")
print(svg_content)
```

## Features

- Generate course dependency maps from Quarto/Markdown documents
- Support for SVG, PNG, and DOT output formats
- Inline SVG generation for Quarto documents
- Configurable styling and phases
- Graphviz integration

## License

MIT License
