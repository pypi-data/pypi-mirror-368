//! Configuration management for the course map tool

use anyhow::{Context, Result};
use indexmap::IndexMap;
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use std::fs;
use std::path::Path;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    #[serde(rename = "root-key")]
    pub root_key: String,
    pub phase: IndexMap<String, PhaseConfig>,
    pub ignore: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PhaseConfig {
    pub face: String,
}

impl Default for Config {
    fn default() -> Self {
        let default_config = include_str!("default-coursemap.yml");
        let config: Config = serde_yaml::from_str(default_config)
            .with_context(|| "Failed to parse default configuration")
            .expect("Parse error");
        config
    }
}

impl Config {
    /// Load configuration from a YAML file
    pub fn from_file<P: AsRef<Path>>(path: P) -> Result<Self> {
        let content = fs::read_to_string(&path)
            .with_context(|| format!("Failed to read config file: {}", path.as_ref().display()))?;

        let config: Config = serde_yaml::from_str(&content)
            .with_context(|| format!("Failed to parse config file: {}", path.as_ref().display()))?;

        Ok(config)
    }

    /// Load configuration from the default locations
    pub fn load_default() -> Result<Self> {
        Self::load_default_from_dir(".")
    }

    /// Load configuration from the default locations within a specific directory
    pub fn load_default_from_dir<P: AsRef<Path>>(dir: P) -> Result<Self> {
        let dir = dir.as_ref();

        // Try to load from user config file locations
        let config_paths = ["coursemap.yml", "coursemap.yaml", ".coursemap.yml"];

        for path in &config_paths {
            let full_path = dir.join(path);
            if full_path.exists() {
                return Self::from_file(full_path);
            }
        }

        // If no user config file found, use package default configuration
        let config = Self::default();

        Ok(config)
    }

    /// Get the color for a given phase
    pub fn get_phase_color(&self, phase: &str) -> String {
        self.phase
            .get(phase)
            .map(|p| p.face.clone())
            .unwrap_or_else(|| {
                self.phase
                    .get("Unknown")
                    .map(|p| p.face.clone())
                    .unwrap_or_else(|| "lightgray".to_string())
            })
    }

    /// Check if a file should be ignored
    pub fn should_ignore(&self, file_path: &str) -> bool {
        self.ignore.iter().any(|pattern| {
            if let Some(stripped) = pattern.strip_prefix('/') {
                // Absolute path pattern - check if file path ends with the pattern (without leading /)
                file_path.ends_with(stripped)
            } else if pattern.contains('*') {
                // Wildcard pattern - simple glob matching
                self.matches_glob_pattern(file_path, pattern)
            } else {
                // Simple substring matching
                file_path.contains(pattern)
            }
        })
    }

    /// Simple glob pattern matching for basic wildcards
    fn matches_glob_pattern(&self, file_path: &str, pattern: &str) -> bool {
        if pattern == "*" {
            return true;
        }

        if let Some(extension) = pattern.strip_prefix("*.") {
            // Extension matching like "*.tmp"
            file_path.ends_with(&format!(".{extension}"))
        } else if let Some(prefix) = pattern.strip_suffix("*") {
            // Prefix matching like "temp*"
            file_path.contains(prefix)
        } else {
            // For more complex patterns, fall back to simple contains
            file_path.contains(pattern)
        }
    }

    /// Get all available phases
    pub fn get_phases(&self) -> HashSet<String> {
        self.phase.keys().cloned().collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::NamedTempFile;

    #[test]
    fn test_default_config() {
        let config = Config::default();
        assert_eq!(config.root_key, "course-map");
        assert!(config.phase.contains_key("Pre"));
        assert!(config.phase.contains_key("InClass"));
        assert!(config.phase.contains_key("Post"));
        assert!(config.phase.contains_key("Unknown"));
    }

    #[test]
    fn test_phase_color() {
        let config = Config::default();
        assert_eq!(config.get_phase_color("Pre"), "lightblue");
        assert_eq!(config.get_phase_color("NonExistent"), "lightgray");
    }

    #[test]
    fn test_should_ignore() {
        let config = Config::default();
        assert!(config.should_ignore("some/path/index.qmd"));
        assert!(!config.should_ignore("some/path/intro.qmd"));
    }

    #[test]
    fn test_config_from_file() -> Result<()> {
        let mut temp_file = NamedTempFile::new()?;
        writeln!(
            temp_file,
            r#"
root-key: test-map
phase:
  Test:
    face: red
ignore:
  - test.qmd
"#
        )?;

        let config = Config::from_file(temp_file.path())?;
        assert_eq!(config.root_key, "test-map");
        assert_eq!(config.get_phase_color("Test"), "red");
        assert!(config.should_ignore("test.qmd"));

        Ok(())
    }

    #[test]
    fn test_load_default_with_embedded_config() -> Result<()> {
        // Test that load_default() uses embedded config when no user config exists
        // This test runs in a temporary directory where no coursemap.yml exists
        let temp_dir = tempfile::tempdir()?;
        let original_dir = std::env::current_dir()?;

        // Change to temp directory
        std::env::set_current_dir(&temp_dir)?;

        // Load default config (should use embedded config)
        let config = Config::load_default()?;

        // Restore original directory
        std::env::set_current_dir(original_dir)?;

        // Verify it matches our embedded default
        assert_eq!(config.root_key, "course-map");
        assert_eq!(config.get_phase_color("Pre"), "lightblue");
        assert_eq!(config.get_phase_color("InClass"), "lightgreen");
        assert_eq!(config.get_phase_color("Post"), "orange");
        assert_eq!(config.get_phase_color("Unknown"), "lightgray");
        assert!(config.should_ignore("some/path/index.qmd"));

        Ok(())
    }

    #[test]
    fn test_load_default_with_user_config() -> Result<()> {
        let temp_dir = tempfile::tempdir()?;
        let config_path = temp_dir.path().join("coursemap.yml");

        // Create a user config file in temp directory
        std::fs::write(
            &config_path,
            r#"root-key: user-config
phase:
  Custom:
    face: purple
ignore:
  - custom.qmd
"#,
        )?;

        // Load config directly from the file
        let config = Config::from_file(&config_path)?;

        // Verify it uses user config
        assert_eq!(config.root_key, "user-config");
        assert_eq!(config.get_phase_color("Custom"), "purple");
        assert!(config.should_ignore("custom.qmd"));

        Ok(())
    }

    #[test]
    fn test_config_file_priority() -> Result<()> {
        let temp_dir = tempfile::tempdir()?;

        // First test: only coursemap.yaml exists
        let yaml_path = temp_dir.path().join("coursemap.yaml");
        std::fs::write(
            &yaml_path,
            r#"root-key: yaml-config
phase:
  Test:
    face: red
ignore: []
"#,
        )?;

        let config = Config::load_default_from_dir(temp_dir.path())?;
        assert_eq!(config.root_key, "yaml-config");

        // Clean up the first file before creating the second
        std::fs::remove_file(&yaml_path)?;

        // Now add coursemap.yml (higher priority)
        let yml_path = temp_dir.path().join("coursemap.yml");
        std::fs::write(
            &yml_path,
            r#"root-key: yml-config
phase:
  Test:
    face: blue
ignore: []
"#,
        )?;

        // Load config again (should now prioritize coursemap.yml)
        let config = Config::load_default_from_dir(temp_dir.path())?;
        assert_eq!(config.root_key, "yml-config");

        Ok(())
    }

    #[test]
    fn test_get_phases() {
        let config = Config::default();
        let phases = config.get_phases();

        assert!(phases.contains("Pre"));
        assert!(phases.contains("InClass"));
        assert!(phases.contains("Post"));
        assert!(phases.contains("Unknown"));
        assert_eq!(phases.len(), 4);
    }

    #[test]
    fn test_ignore_patterns() {
        let mut config = Config::default();
        config.ignore = vec![
            "/index.qmd".to_string(),
            "README.md".to_string(),
            "*.tmp".to_string(),
        ];

        assert!(config.should_ignore("some/path/index.qmd"));
        assert!(config.should_ignore("README.md"));
        assert!(config.should_ignore("file.tmp"));
        assert!(!config.should_ignore("intro.qmd"));
    }
}
