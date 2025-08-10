# Course Map

A tool to visualize course dependencies from Quarto/Markdown documents, available in multiple programming languages.

## Overview

Course Map analyzes Quarto/Markdown documents with course metadata and generates visual dependency graphs showing the relationships between courses. It's designed to help educators and course designers understand and visualize curriculum structures.

## Multi-Language Support

This project provides the same functionality across three programming languages:

- 🦀 **Rust** (crates.io): Core library and command-line tool
- 🐍 **Python** (PyPI): Python bindings with Quarto integration
- 📊 **R** (CRAN): R package with Quarto integration

## Quick Start

### Rust
```bash
cargo install coursemap
coursemap -i ./courses -o course_map.svg
```

### Python
```bash
pip install coursemap
```
```python
import coursemap

# Quick display (like matplotlib.pyplot.show())
coursemap.show("./courses")

# Object-oriented approach (recommended)
cm = coursemap.CourseMap("./courses")
cm.show()  # Display inline in Jupyter/Quarto
cm.save("course_map.svg")  # Save to file
```

### R
```r
install.packages("coursemap")
library(coursemap)

# Object-oriented approach (recommended)
cm <- coursemap("./courses")
plot(cm)  # Display in RStudio/knitr
write_map(cm, "course_map.svg")  # Save to file
```

## Document Format

Course documents should include frontmatter with course metadata:

```yaml
---
title: "Introduction to Economics"
course-map:
  id: intro
  phase: Pre
  prerequisites: []
---

# Course Content

Your course content here...
```

### Metadata Fields

- `id`: Unique identifier for the course
- `phase`: Course phase (Pre, InClass, Post, etc.)
- `prerequisites`: List of prerequisite course IDs

## Configuration

Create a `coursemap.yml` file to customize phases and colors:

```yaml
root-key: course-map

phase:
  Pre: 
    face: lightblue
  InClass:
    face: lightgreen
  Post:
    face: orange
  Unknown:
    face: lightgray    

ignore:
  - /index.qmd
  - /README.md
```

## Quarto Integration

### Python
```python
# In a .qmd file
```{python}
#| echo: false
import coursemap

# Simple one-liner for Quarto
coursemap.show("../courses")

# Or save and display
cm = coursemap.CourseMap("../courses")
cm.show()  # Displays inline in Quarto
```

### R
```r
# In a .qmd file
```{r}
#| echo: false
library(coursemap)

# Simple display in Quarto
cm <- coursemap("../courses")
plot(cm)  # Automatically displays inline in Quarto
```

## Output Formats

- **SVG**: Vector graphics (requires Graphviz)
- **PNG**: Raster graphics (requires Graphviz)
- **DOT**: Graphviz source format (no Graphviz required)

## Project Structure

```
coursemap/
├── coursemap-rs/       # 🦀 Rust library + CLI for crates.io
├── coursemap-py/       # 🐍 Python package for PyPI
├── coursemap-r/        # 📊 R package for CRAN (RStudio project)
├── test_docs/          # 📝 Test data
├── .bumpversion.toml   # 🔄 Version management
├── CHANGELOG.md        # 📋 Change history
├── PUBLISHING.md       # 📖 Publishing guide
└── README.md           #  This file
```

## Development

Each package can be developed independently with its own versioning:

### Rust
```bash
cd coursemap-rs
cargo build
cargo test
# Version management
bump-my-version bump patch  # Independent versioning
```

### Python
```bash
cd coursemap-py
maturin develop
# Version management
bump-my-version bump minor  # Independent versioning
```

### R (RStudio Project)
```bash
cd coursemap-r
R -e "rextendr::document()"
# Version management
bump-my-version bump patch  # Independent versioning
```

## Testing

### Run All Tests
```bash
make test           # Run all tests (Rust, Python, R)
make test-rust      # Run Rust tests only
make test-python    # Run Python tests only
make test-r         # Run R tests only
```

### Individual Package Testing

#### Rust Tests
```bash
cd coursemap-rs && cargo test
```

#### Python Tests
```bash
cd coursemap-py
uv run maturin develop
uv run --with pytest pytest tests/ -v
```

#### R Tests
```bash
cd coursemap-r
Rscript --vanilla -e "testthat::test_dir('tests/testthat')"
```

### Continuous Integration
Tests run automatically on GitHub Actions for:
- ✅ Rust (stable)
- ✅ Python (3.8, 3.9, 3.10, 3.11, 3.12)
- ✅ R (latest)
- ✅ Cross-platform builds (Linux, macOS, Windows)

### Test Coverage
- **Rust**: Unit tests for config, parser, graph, renderer
- **Python**: Integration tests with PyO3 bindings
- **R**: Package functionality and Quarto integration
- **Integration**: Cross-package compatibility tests

## Version Management Strategy

This project uses **independent versioning** for each package:

- 🦀 **Rust**: `rs-v0.1.0` → `rs-v0.1.1` (patch fixes)
- 🐍 **Python**: `py-v0.1.0` → `py-v0.2.0` (new features)
- 📊 **R**: `r-v0.1.0` → `r-v0.1.1` (bug fixes)

### Benefits
- ✅ Only changed packages get version bumps
- ✅ Clear change tracking per package
- ✅ Efficient development workflow
- ✅ Language-specific conventions

## Requirements

- **Rust**: 1.70+
- **Graphviz**: Optional, for SVG/PNG output
- **Python**: 3.8+ (for Python package)
- **R**: 4.0+ (for R package)

## Examples

### Simple Course Structure
```
courses/
├── intro.qmd          # Prerequisites: none
├── microeconomics.qmd # Prerequisites: [intro]
└── advanced.qmd       # Prerequisites: [microeconomics]
```

### Complex Dependencies
```
courses/
├── intro.qmd          # Prerequisites: none
├── micro.qmd          # Prerequisites: [intro]
├── macro.qmd          # Prerequisites: [intro]
└── advanced.qmd       # Prerequisites: [micro, macro]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## AI Acknowledgement

This project utilized generative AI tools, including Claude and ChatGPT, to assist in code generation, documentation, and testing. These tools were used to enhance productivity and facilitate the development process.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- **Repository**: https://github.com/kenjisato/coursemap
- **Rust Package**: https://crates.io/crates/coursemap
- **Python Package**: https://pypi.org/project/coursemap/
- **R Package**: https://cran.r-project.org/package=coursemap
- **Documentation**: https://docs.rs/coursemap

## Support

- 📝 [Issues](https://github.com/kenjisato/coursemap/issues)
- 💬 [Discussions](https://github.com/kenjisato/coursemap/discussions)
- 📧 Email: mail@kenjisato.jp
