//! Course Map - A tool to visualize course dependencies from Quarto/Markdown documents
//!
//! This library provides functionality to parse Quarto/Markdown documents and generate
//! visual dependency graphs showing the relationships between courses. It's designed to
//! help educators and course designers understand and visualize curriculum structures.
//!
//! ## Multi-Language Support
//!
//! This Rust library serves as the core for bindings in multiple languages:
//! - 🦀 **Rust**: Core library and command-line tool
//! - 🐍 **Python**: `pip install coursemap` - Object-oriented API with `CourseMap.show()` and `CourseMap.save()`
//! - 📊 **R**: `install.packages("coursemap")` - R package with Quarto integration
//!
//! ## Rust API Example
//!
//! ```rust,no_run
//! use coursemap::{Config, App};
//!
//! // Load configuration
//! let config = Config::load_default().unwrap();
//!
//! // Create app instance
//! let app = App::new(config);
//!
//! // Generate course map
//! app.run("./courses", "course_map.svg", "svg").unwrap();
//! ```
//!
//! ## Python API (Recommended)
//!
//! ```python
//! import coursemap
//!
//! # Quick display (like matplotlib.pyplot.show())
//! coursemap.show("./courses")
//!
//! # Object-oriented approach (recommended)
//! cm = coursemap.CourseMap("./courses")
//! cm.show()  # Display inline in Jupyter/Quarto
//! cm.save("course_map.svg")  # Save to file
//! ```
//!
//! ## R API
//!
//! ```r
//! library(coursemap)
//!
//! # Object-oriented approach (recommended)
//! cm <- coursemap("./courses")
//! plot(cm)  # Display in RStudio/knitr
//! write_map(cm, "course_map.svg")  # Save to file
//! ```
//!
//! ## Document Format
//!
//! Course documents should include frontmatter with course metadata:
//!
//! ```yaml
//! ---
//! title: "Introduction to Economics"
//! course-map:
//!   id: intro
//!   phase: Pre
//!   prerequisites: []
//! ---
//! ```

pub mod cli;
pub mod config;
pub mod graph;
pub mod parser;
pub mod renderer;

pub use anyhow::{Error, Result};
pub use config::Config;

/// The main application structure
pub struct App {
    pub config: config::Config,
}

impl App {
    /// Create a new App instance with the given configuration
    pub fn new(config: config::Config) -> Self {
        Self { config }
    }

    /// Run the course map generation process
    pub fn run(&self, input_dir: &str, output_path: &str, format: &str) -> Result<()> {
        // Parse all documents in the input directory
        let documents = parser::parse_directory(input_dir, &self.config)?;

        // Build the dependency graph
        let graph = graph::build_graph(documents)?;

        // Render the graph to the specified format
        renderer::render_graph(&graph, output_path, format, &self.config)?;

        Ok(())
    }

    /// Generate DOT content as a string (for R/Python bindings)
    pub fn generate_dot_string(&self, input_dir: &str) -> Result<String> {
        // Parse all documents in the input directory
        let documents = parser::parse_directory(input_dir, &self.config)?;

        // Build the dependency graph
        let graph = graph::build_graph(documents)?;

        // Generate DOT content
        renderer::generate_dot_content(&graph, &self.config)
    }
}
