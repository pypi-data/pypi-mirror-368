//! Command-line interface for the course map tool

use clap::{Parser, Subcommand, ValueEnum};
use std::path::PathBuf;

#[derive(Parser)]
#[command(about = "Generate course dependency maps from Quarto/Markdown documents")]
#[command(version)]
#[command(subcommand_precedence_over_arg = true)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Option<Commands>,

    /// Input directory containing course documents (when no subcommand is used)
    pub input: Option<PathBuf>,

    /// Output file path
    #[arg(short, long, default_value = "course_map.svg")]
    pub output: PathBuf,

    /// Output format
    #[arg(short, long, default_value = "svg")]
    pub format: OutputFormat,

    /// Configuration file path
    #[arg(short, long)]
    pub config: Option<PathBuf>,

    /// Verbose output
    #[arg(short, long)]
    pub verbose: bool,
}

#[derive(Subcommand)]
pub enum Commands {
    /// Show current configuration
    #[command(name = "show-config")]
    ShowConfig {
        /// Configuration file path
        #[arg(short, long)]
        config: Option<PathBuf>,
    },
}

#[derive(Clone, ValueEnum)]
pub enum OutputFormat {
    /// SVG format
    Svg,
    /// PNG format
    Png,
    /// DOT format (Graphviz source)
    Dot,
}

impl std::fmt::Display for OutputFormat {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            OutputFormat::Svg => write!(f, "svg"),
            OutputFormat::Png => write!(f, "png"),
            OutputFormat::Dot => write!(f, "dot"),
        }
    }
}

impl Cli {
    /// Parse command line arguments
    pub fn parse_args() -> Self {
        Self::parse()
    }

    /// Get the input directory as a string
    pub fn input_dir(&self) -> Option<&str> {
        self.input.as_ref().and_then(|p| p.to_str())
    }

    /// Get the output path as a string
    pub fn output_path(&self) -> &str {
        self.output.to_str().unwrap_or("course_map.svg")
    }

    /// Get the format as a string
    pub fn format_str(&self) -> String {
        self.format.to_string()
    }
}
