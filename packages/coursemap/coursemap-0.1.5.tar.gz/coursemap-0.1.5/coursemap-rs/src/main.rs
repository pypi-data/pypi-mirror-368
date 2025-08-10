//! Course Map - A tool to visualize course dependencies from Quarto/Markdown documents

use anyhow::Result;
use coursemap::{
    cli::{Cli, Commands},
    renderer, App, Config,
};

fn main() -> Result<()> {
    let args = Cli::parse_args();

    match &args.command {
        Some(Commands::ShowConfig { config }) => {
            show_config(config.as_ref())?;
        }
        None => {
            // Default behavior: generate course map
            if let Some(input_dir) = args.input_dir() {
                generate_course_map(&args, input_dir)?;
            } else {
                eprintln!("Error: Input directory is required");
                eprintln!("Usage: coursemap <INPUT> [OPTIONS]");
                eprintln!("       coursemap show-config [OPTIONS]");
                eprintln!();
                eprintln!("For more information, try '--help'.");
                std::process::exit(1);
            }
        }
    }

    Ok(())
}

fn show_config(config_path: Option<&std::path::PathBuf>) -> Result<()> {
    let config = if let Some(config_path) = config_path {
        Config::from_file(config_path)?
    } else {
        Config::load_default()?
    };

    println!("Current Configuration:");
    println!("  Root key: {}", config.root_key);
    println!("  Phases:");
    for (phase, phase_config) in &config.phase {
        println!("    {}: {}", phase, phase_config.face);
    }
    println!("  Ignore patterns:");
    for pattern in &config.ignore {
        println!("    {pattern}");
    }

    if let Some(config_path) = config_path {
        println!("  Configuration file: {}", config_path.display());
    } else {
        println!("  Configuration: Default (built-in)");
    }

    Ok(())
}

fn generate_course_map(args: &Cli, input_dir: &str) -> Result<()> {
    // Set up logging based on verbosity
    if args.verbose {
        env_logger::Builder::from_default_env()
            .filter_level(log::LevelFilter::Debug)
            .init();
    }

    // Load configuration
    let config = if let Some(config_path) = &args.config {
        Config::from_file(config_path)?
    } else {
        Config::load_default()?
    };

    if args.verbose {
        println!("Loaded configuration:");
        println!("  Root key: {}", config.root_key);
        println!("  Phases: {:?}", config.phase.keys().collect::<Vec<_>>());
        println!("  Ignore patterns: {:?}", config.ignore);
        println!();
    }

    // Create and run the application
    let app = App::new(config);

    println!("Scanning directory: {input_dir}");
    println!("Output file: {}", args.output_path());
    println!("Format: {}", args.format_str());
    println!();

    // Check if Graphviz is available for non-DOT formats
    if args.format_str() != "dot" {
        if !renderer::graphviz_available() {
            eprintln!("Warning: Graphviz not found. Only DOT format will be available.");
            eprintln!("To generate SVG/PNG files, please install Graphviz:");
            eprintln!("  macOS: brew install graphviz");
            eprintln!("  Ubuntu/Debian: sudo apt-get install graphviz");
            eprintln!("  Windows: Download from https://graphviz.org/download/");
            eprintln!();

            if args.format_str() != "dot" {
                return Err(anyhow::anyhow!(
                    "Cannot generate {} format without Graphviz",
                    args.format_str()
                ));
            }
        } else if args.verbose {
            if let Ok(info) = renderer::graphviz_info() {
                println!("Graphviz found: {info}");
                println!();
            }
        }
    }

    // Run the application
    match app.run(input_dir, args.output_path(), &args.format_str()) {
        Ok(()) => {
            println!("Course map generated successfully!");
            Ok(())
        }
        Err(e) => {
            eprintln!("Error: {e}");

            // Print additional context for common errors
            if e.to_string().contains("Directory does not exist") {
                eprintln!("Make sure the input directory exists and contains course documents.");
            } else if e.to_string().contains("Graphviz") {
                eprintln!("Try using --format dot to generate DOT format without Graphviz.");
            }

            std::process::exit(1);
        }
    }
}
