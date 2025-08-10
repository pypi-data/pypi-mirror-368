//! Python bindings for the course-map library using PyO3

#![allow(clippy::useless_conversion)]

use coursemap::{App, Config};
use pyo3::prelude::*;
use pyo3::types::PyDict;

#[pyclass]
#[derive(Clone)]
pub struct CourseMap {
    config: Config,
}

#[pymethods]
impl CourseMap {
    #[new]
    #[pyo3(signature = (config_path = None))]
    pub fn new(config_path: Option<String>) -> PyResult<Self> {
        let config = if let Some(path) = config_path {
            Config::from_file(path).map_err(|e| {
                pyo3::exceptions::PyIOError::new_err(format!("Failed to load config: {e}"))
            })?
        } else {
            Config::load_default().map_err(|e| {
                pyo3::exceptions::PyIOError::new_err(format!("Failed to load default config: {e}"))
            })?
        };

        Ok(CourseMap { config })
    }

    /// Ensure the output path has the correct extension for the given format
    fn ensure_correct_extension(&self, output_path: &str, format: &str) -> String {
        let expected_ext = format!(".{format}");

        // If the path already has the correct extension, return as-is
        if output_path.ends_with(&expected_ext) {
            return output_path.to_string();
        }

        // Remove any existing extension that doesn't match
        let mut base_path = output_path.to_string();
        for ext in &[".svg", ".png", ".dot"] {
            if base_path.ends_with(ext) {
                base_path = base_path[..base_path.len() - ext.len()].to_string();
                break;
            }
        }

        // Add the correct extension
        format!("{base_path}{expected_ext}")
    }

    /// Generate a course dependency map
    #[pyo3(signature = (input_dir = ".", output_path = "course_map.svg", format = "svg"))]
    pub fn generate(&self, input_dir: &str, output_path: &str, format: &str) -> PyResult<String> {
        // Ensure the output path has the correct extension for the format
        let actual_output_path = self.ensure_correct_extension(output_path, format);

        let app = App::new(self.config.clone());

        app.run(input_dir, &actual_output_path, format)
            .map_err(|e| {
                pyo3::exceptions::PyRuntimeError::new_err(format!(
                    "Failed to generate course map: {e}"
                ))
            })?;

        Ok(actual_output_path)
    }

    /// Generate SVG format course map
    #[pyo3(signature = (input_dir = ".", output_path = "course_map.svg"))]
    pub fn generate_svg(&self, input_dir: &str, output_path: &str) -> PyResult<String> {
        self.generate(input_dir, output_path, "svg")
    }

    /// Generate PNG format course map
    #[pyo3(signature = (input_dir = ".", output_path = "course_map.png"))]
    pub fn generate_png(&self, input_dir: &str, output_path: &str) -> PyResult<String> {
        self.generate(input_dir, output_path, "png")
    }

    /// Generate DOT format course map
    #[pyo3(signature = (input_dir = ".", output_path = "course_map.dot"))]
    pub fn generate_dot(&self, input_dir: &str, output_path: &str) -> PyResult<String> {
        self.generate(input_dir, output_path, "dot")
    }

    /// Generate SVG content as string for inline embedding
    #[pyo3(signature = (input_dir = "."))]
    pub fn generate_inline_svg(&self, input_dir: &str) -> PyResult<String> {
        use std::fs;
        use tempfile::NamedTempFile;

        // Create a temporary file that persists until we read it
        let temp_file = NamedTempFile::new().map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Failed to create temp file: {e}"))
        })?;

        let temp_path = temp_file.path().to_string_lossy().to_string();

        // Generate the SVG file
        let app = App::new(self.config.clone());
        app.run(input_dir, &temp_path, "svg").map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to generate course map: {e}"))
        })?;

        // Read the content while the temp file is still alive
        let content = fs::read_to_string(&temp_path).map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Failed to read generated SVG: {e}"))
        })?;

        // Explicitly close the temp file
        temp_file.close().map_err(|e| {
            pyo3::exceptions::PyIOError::new_err(format!("Failed to close temp file: {e}"))
        })?;

        Ok(content)
    }

    /// Get configuration as dictionary
    pub fn get_config(&self) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let dict = PyDict::new_bound(py);
            dict.set_item("root_key", &self.config.root_key)?;

            let phases = PyDict::new_bound(py);
            for (phase, config) in &self.config.phase {
                let phase_dict = PyDict::new_bound(py);
                phase_dict.set_item("face", &config.face)?;
                phases.set_item(phase, phase_dict)?;
            }
            dict.set_item("phase", phases)?;
            dict.set_item("ignore", &self.config.ignore)?;

            Ok(dict.into())
        })
    }

    /// Parse documents in a directory and return metadata
    #[pyo3(signature = (input_dir = "."))]
    pub fn parse_documents(&self, input_dir: &str) -> PyResult<Vec<PyObject>> {
        let documents =
            coursemap::parser::parse_directory(input_dir, &self.config).map_err(|e| {
                pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to parse documents: {e}"))
            })?;

        Python::with_gil(|py| {
            let mut result = Vec::new();
            for doc in documents {
                let dict = PyDict::new_bound(py);
                dict.set_item("id", &doc.id)?;
                dict.set_item("title", &doc.title)?;
                dict.set_item("phase", &doc.phase)?;
                dict.set_item("prerequisites", &doc.prerequisites)?;
                dict.set_item("file_path", doc.file_path.to_string_lossy().as_ref())?;
                result.push(dict.into());
            }
            Ok(result)
        })
    }
}

/// Convenience function to generate a course map
#[pyfunction]
#[pyo3(signature = (input_dir = ".", output_path = "course_map.svg", format = "svg", config_path = None))]
pub fn generate_course_map(
    input_dir: &str,
    output_path: &str,
    format: &str,
    config_path: Option<String>,
) -> PyResult<String> {
    let course_map = CourseMap::new(config_path)?;
    course_map.generate(input_dir, output_path, format)
}

/// Convenience function to generate inline SVG
#[pyfunction]
#[pyo3(signature = (input_dir = ".", config_path = None))]
pub fn generate_inline_svg(input_dir: &str, config_path: Option<String>) -> PyResult<String> {
    let course_map = CourseMap::new(config_path)?;
    course_map.generate_inline_svg(input_dir)
}

/// Check if Graphviz is available
#[pyfunction]
pub fn graphviz_available() -> bool {
    coursemap::renderer::graphviz_available()
}

/// Get Graphviz version information
#[pyfunction]
pub fn graphviz_info() -> PyResult<String> {
    coursemap::renderer::graphviz_info().map_err(|e| {
        pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to get Graphviz info: {e}"))
    })
}

#[pymodule]
fn coursemap_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<CourseMap>()?;
    m.add_function(wrap_pyfunction!(generate_course_map, m)?)?;
    m.add_function(wrap_pyfunction!(generate_inline_svg, m)?)?;
    m.add_function(wrap_pyfunction!(graphviz_available, m)?)?;
    m.add_function(wrap_pyfunction!(graphviz_info, m)?)?;
    Ok(())
}
