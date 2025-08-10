//! Document parsing functionality for extracting course metadata

use anyhow::{Context, Result};
use gray_matter::{engine::YAML, Matter};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};
use walkdir::WalkDir;

use crate::config::Config;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Document {
    pub id: String,
    pub title: String,
    pub file_path: PathBuf,
    pub phase: String,
    pub prerequisites: Vec<String>,
    pub metadata: HashMap<String, serde_yaml::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct CourseMapMetadata {
    pub id: String,
    pub phase: Option<String>,
    pub prerequisites: Option<Vec<String>>,
}

impl Document {
    /// Create a new document with the given metadata
    pub fn new(
        id: String,
        title: String,
        file_path: PathBuf,
        phase: String,
        prerequisites: Vec<String>,
        metadata: HashMap<String, serde_yaml::Value>,
    ) -> Self {
        Self {
            id,
            title,
            file_path,
            phase,
            prerequisites,
            metadata,
        }
    }

    /// Get the display name for this document
    pub fn display_name(&self) -> String {
        if self.title.is_empty() {
            self.id.clone()
        } else {
            format!("{}\n({})", self.title, self.id)
        }
    }
}

/// Parse all documents in a directory
pub fn parse_directory(dir_path: &str, config: &Config) -> Result<Vec<Document>> {
    let mut documents = Vec::new();
    let dir = Path::new(dir_path);

    if !dir.exists() {
        return Err(anyhow::anyhow!("Directory does not exist: {}", dir_path));
    }

    for entry in WalkDir::new(dir)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| e.file_type().is_file())
    {
        let path = entry.path();

        // Check if file should be ignored
        if let Some(path_str) = path.to_str() {
            if config.should_ignore(path_str) {
                continue;
            }
        }

        // Check if file has a supported extension
        if let Some(extension) = path.extension() {
            let ext = extension.to_string_lossy().to_lowercase();
            if matches!(ext.as_str(), "qmd" | "md" | "rmd") {
                if let Ok(doc) = parse_document(path, config) {
                    documents.push(doc);
                }
            }
        }
    }

    Ok(documents)
}

/// Parse a single document file
pub fn parse_document(file_path: &Path, config: &Config) -> Result<Document> {
    let content = fs::read_to_string(file_path)
        .with_context(|| format!("Failed to read file: {}", file_path.display()))?;

    let matter = Matter::<YAML>::new();
    let result = matter.parse(&content);

    // Extract basic metadata
    let mut metadata: HashMap<String, serde_yaml::Value> = HashMap::new();
    let mut title = String::new();
    let mut course_map_data: Option<CourseMapMetadata> = None;

    if let Some(_front_matter) = result.data {
        // Parse the front matter as YAML directly from the original content
        // Extract the YAML front matter section manually
        let lines: Vec<&str> = content.lines().collect();
        let mut yaml_content = String::new();
        let mut in_frontmatter = false;

        for line in lines {
            if line.trim() == "---" {
                if !in_frontmatter {
                    in_frontmatter = true;
                    continue;
                } else {
                    break;
                }
            }

            if in_frontmatter {
                yaml_content.push_str(line);
                yaml_content.push('\n');
            }
        }

        if !yaml_content.is_empty() {
            if let Ok(serde_yaml::Value::Mapping(map)) =
                serde_yaml::from_str::<serde_yaml::Value>(&yaml_content)
            {
                for (key, value) in map {
                    if let serde_yaml::Value::String(key_str) = key {
                        metadata.insert(key_str.clone(), value.clone());

                        // Extract title
                        if key_str == "title" {
                            if let serde_yaml::Value::String(ref title_str) = value {
                                title = title_str.clone();
                            }
                        }

                        // Extract course-map metadata
                        if key_str == config.root_key {
                            if let Ok(cm_data) = serde_yaml::from_value::<CourseMapMetadata>(value)
                            {
                                course_map_data = Some(cm_data);
                            }
                        }
                    }
                }
            }
        }
    }

    // Extract course map information
    let (id, phase, prerequisites) = if let Some(cm_data) = course_map_data {
        let phase = cm_data.phase.unwrap_or_else(|| "Unknown".to_string());
        let prerequisites = cm_data.prerequisites.unwrap_or_default();
        (cm_data.id, phase, prerequisites)
    } else {
        // Fallback: use filename as ID
        let filename = file_path
            .file_stem()
            .and_then(|s| s.to_str())
            .unwrap_or("unknown")
            .to_string();
        (filename, "Unknown".to_string(), Vec::new())
    };

    Ok(Document::new(
        id,
        title,
        file_path.to_path_buf(),
        phase,
        prerequisites,
        metadata,
    ))
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::NamedTempFile;

    #[test]
    fn test_parse_document_with_frontmatter() -> Result<()> {
        let temp_file = NamedTempFile::with_suffix(".qmd")?;

        std::fs::write(
            temp_file.path(),
            r#"---
title: "Test Course"
course-map:
  id: test-course
  phase: Pre
  prerequisites: ["intro"]
---

# Test Course Content
"#,
        )?;

        let config = Config::default();
        let doc = parse_document(temp_file.path(), &config)?;

        assert_eq!(doc.id, "test-course");
        assert_eq!(doc.title, "Test Course");
        assert_eq!(doc.phase, "Pre");
        assert_eq!(doc.prerequisites, vec!["intro"]);

        Ok(())
    }

    #[test]
    fn test_parse_document_without_frontmatter() -> Result<()> {
        let temp_file = NamedTempFile::with_suffix(".md")?;

        std::fs::write(temp_file.path(), "# Just a regular markdown file")?;

        let config = Config::default();
        let doc = parse_document(temp_file.path(), &config)?;

        assert!(!doc.id.is_empty());
        assert_eq!(doc.phase, "Unknown");
        assert!(doc.prerequisites.is_empty());

        Ok(())
    }

    #[test]
    fn test_document_display_name() {
        let doc = Document::new(
            "test-id".to_string(),
            "Test Title".to_string(),
            PathBuf::from("test.qmd"),
            "Pre".to_string(),
            vec![],
            HashMap::new(),
        );

        assert_eq!(doc.display_name(), "Test Title\n(test-id)");

        let doc_no_title = Document::new(
            "test-id".to_string(),
            "".to_string(),
            PathBuf::from("test.qmd"),
            "Pre".to_string(),
            vec![],
            HashMap::new(),
        );

        assert_eq!(doc_no_title.display_name(), "test-id");
    }

    #[test]
    fn test_parse_directory() -> Result<()> {
        let temp_dir = tempfile::tempdir()?;
        let dir_path = temp_dir.path();

        // Create test files
        std::fs::write(
            dir_path.join("course1.qmd"),
            r#"---
title: "Course 1"
course-map:
  id: course1
  phase: Pre
  prerequisites: []
---
# Course 1 Content
"#,
        )?;

        std::fs::write(
            dir_path.join("course2.md"),
            r#"---
title: "Course 2"
course-map:
  id: course2
  phase: InClass
  prerequisites: ["course1"]
---
# Course 2 Content
"#,
        )?;

        // Create a file that should be ignored
        std::fs::write(dir_path.join("index.qmd"), "# Index file")?;

        // Create a non-course file
        std::fs::write(dir_path.join("readme.txt"), "Not a course file")?;

        let config = Config::default();
        let documents = parse_directory(dir_path.to_str().unwrap(), &config)?;

        assert_eq!(documents.len(), 2);

        let course1 = documents.iter().find(|d| d.id == "course1").unwrap();
        assert_eq!(course1.title, "Course 1");
        assert_eq!(course1.phase, "Pre");
        assert!(course1.prerequisites.is_empty());

        let course2 = documents.iter().find(|d| d.id == "course2").unwrap();
        assert_eq!(course2.title, "Course 2");
        assert_eq!(course2.phase, "InClass");
        assert_eq!(course2.prerequisites, vec!["course1"]);

        Ok(())
    }

    #[test]
    fn test_parse_directory_nonexistent() {
        let config = Config::default();
        let result = parse_directory("/nonexistent/path", &config);
        assert!(result.is_err());
        assert!(result
            .unwrap_err()
            .to_string()
            .contains("Directory does not exist"));
    }

    #[test]
    fn test_parse_document_with_custom_root_key() -> Result<()> {
        let temp_file = NamedTempFile::with_suffix(".qmd")?;

        std::fs::write(
            temp_file.path(),
            r#"---
title: "Custom Course"
my-custom-key:
  id: custom-course
  phase: Post
  prerequisites: ["req1", "req2"]
---
# Custom Course Content
"#,
        )?;

        let mut config = Config::default();
        config.root_key = "my-custom-key".to_string();

        let doc = parse_document(temp_file.path(), &config)?;

        assert_eq!(doc.id, "custom-course");
        assert_eq!(doc.title, "Custom Course");
        assert_eq!(doc.phase, "Post");
        assert_eq!(doc.prerequisites, vec!["req1", "req2"]);

        Ok(())
    }

    #[test]
    fn test_parse_document_partial_metadata() -> Result<()> {
        let temp_file = NamedTempFile::with_suffix(".qmd")?;

        std::fs::write(
            temp_file.path(),
            r#"---
title: "Partial Course"
course-map:
  id: partial-course
  # phase and prerequisites are optional
---
# Partial Course Content
"#,
        )?;

        let config = Config::default();
        let doc = parse_document(temp_file.path(), &config)?;

        assert_eq!(doc.id, "partial-course");
        assert_eq!(doc.title, "Partial Course");
        assert_eq!(doc.phase, "Unknown"); // Default when not specified
        assert!(doc.prerequisites.is_empty()); // Default when not specified

        Ok(())
    }

    #[test]
    fn test_supported_file_extensions() -> Result<()> {
        let temp_dir = tempfile::tempdir()?;
        let dir_path = temp_dir.path();

        // Create files with different extensions
        std::fs::write(
            dir_path.join("test.qmd"),
            "---\ntitle: QMD\ncourse-map:\n  id: qmd\n---\n",
        )?;
        std::fs::write(
            dir_path.join("test.md"),
            "---\ntitle: MD\ncourse-map:\n  id: md\n---\n",
        )?;
        std::fs::write(
            dir_path.join("test.rmd"),
            "---\ntitle: RMD\ncourse-map:\n  id: rmd\n---\n",
        )?;
        std::fs::write(
            dir_path.join("test.txt"),
            "---\ntitle: TXT\ncourse-map:\n  id: txt\n---\n",
        )?; // Should be ignored

        let config = Config::default();
        let documents = parse_directory(dir_path.to_str().unwrap(), &config)?;

        assert_eq!(documents.len(), 3); // Only .qmd, .md, .rmd files

        let ids: Vec<&String> = documents.iter().map(|d| &d.id).collect();
        assert!(ids.contains(&&"qmd".to_string()));
        assert!(ids.contains(&&"md".to_string()));
        assert!(ids.contains(&&"rmd".to_string()));

        Ok(())
    }
}
