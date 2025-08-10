//! Graph rendering functionality for generating visual output

use anyhow::{Context, Result};
use std::fmt::Write;
use std::fs;
use std::process::Command;

use crate::config::Config;
use crate::graph::CourseGraph;

/// Render a course graph to the specified format
pub fn render_graph(
    graph: &CourseGraph,
    output_path: &str,
    format: &str,
    config: &Config,
) -> Result<()> {
    match format.to_lowercase().as_str() {
        "dot" => render_dot(graph, output_path, config),
        "svg" => render_with_graphviz(graph, output_path, "svg", config),
        "png" => render_with_graphviz(graph, output_path, "png", config),
        _ => Err(anyhow::anyhow!("Unsupported output format: {}", format)),
    }
}

/// Generate DOT format output
pub fn render_dot(graph: &CourseGraph, output_path: &str, config: &Config) -> Result<()> {
    let dot_content = generate_dot_content(graph, config)?;
    fs::write(output_path, dot_content)
        .with_context(|| format!("Failed to write DOT file: {output_path}"))?;

    Ok(())
}

/// Render graph using Graphviz to SVG or PNG
pub fn render_with_graphviz(
    graph: &CourseGraph,
    output_path: &str,
    format: &str,
    config: &Config,
) -> Result<()> {
    let dot_content = generate_dot_content(graph, config)?;

    // Check if graphviz is available
    let graphviz_cmd = if Command::new("dot").arg("-V").output().is_ok() {
        "dot"
    } else {
        return Err(anyhow::anyhow!(
            "Graphviz 'dot' command not found. Please install Graphviz to generate {} files.",
            format.to_uppercase()
        ));
    };

    // Run graphviz to generate the output
    let output = Command::new(graphviz_cmd)
        .arg(format!("-T{format}"))
        .arg("-o")
        .arg(output_path)
        .stdin(std::process::Stdio::piped())
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::piped())
        .spawn()
        .with_context(|| "Failed to spawn Graphviz process")?;

    // Write DOT content to stdin
    if let Some(mut stdin) = output.stdin.as_ref() {
        use std::io::Write;
        stdin
            .write_all(dot_content.as_bytes())
            .with_context(|| "Failed to write DOT content to Graphviz")?;
    }

    let result = output
        .wait_with_output()
        .with_context(|| "Failed to wait for Graphviz process")?;

    if !result.status.success() {
        let stderr = String::from_utf8_lossy(&result.stderr);
        return Err(anyhow::anyhow!("Graphviz failed: {}", stderr));
    }

    Ok(())
}

/// Generate DOT format content from a course graph
pub fn generate_dot_content(graph: &CourseGraph, config: &Config) -> Result<String> {
    let mut dot = String::new();

    // Start digraph
    writeln!(dot, "digraph CourseMap {{")?;
    writeln!(dot, "    rankdir=TB;")?;
    writeln!(dot, "    node [shape=box, style=filled];")?;
    writeln!(dot, "    edge [color=gray];")?;
    writeln!(dot)?;

    // Add nodes with styling based on phase
    for (_node_index, node) in graph.nodes() {
        let color = config.get_phase_color(&node.phase);
        let label = escape_dot_string(&node.display_name);

        writeln!(
            dot,
            "    \"{}\" [label=\"{}\", fillcolor=\"{}\"];",
            escape_dot_string(&node.id),
            label,
            color
        )?;
    }

    writeln!(dot)?;

    // Add edges
    for (source_idx, target_idx) in graph.edges() {
        let source_node = &graph.graph[source_idx];
        let target_node = &graph.graph[target_idx];

        writeln!(
            dot,
            "    \"{}\" -> \"{}\";",
            escape_dot_string(&source_node.id),
            escape_dot_string(&target_node.id)
        )?;
    }

    // Add phase-based subgraphs for better layout
    let mut phases: std::collections::HashMap<String, Vec<String>> =
        std::collections::HashMap::new();
    for (_, node) in graph.nodes() {
        phases
            .entry(node.phase.clone())
            .or_default()
            .push(node.id.clone());
    }

    if phases.len() > 1 {
        writeln!(dot)?;
        writeln!(dot, "    // Phase-based clustering")?;

        for (phase, node_ids) in phases {
            if node_ids.len() > 1 {
                writeln!(dot, "    subgraph cluster_{} {{", escape_dot_string(&phase))?;
                writeln!(dot, "        label=\"{phase} Phase\";")?;
                writeln!(dot, "        style=dashed;")?;
                writeln!(dot, "        color=lightgray;")?;

                for node_id in node_ids {
                    writeln!(dot, "        \"{}\";", escape_dot_string(&node_id))?;
                }

                writeln!(dot, "    }}")?;
            }
        }
    }

    writeln!(dot, "}}")?;

    Ok(dot)
}

/// Escape special characters in DOT strings
fn escape_dot_string(s: &str) -> String {
    s.replace('\\', "\\\\")
        .replace('"', "\\\"")
        .replace('\n', "\\n")
        .replace('\r', "\\r")
        .replace('\t', "\\t")
}

/// Check if Graphviz is available on the system
pub fn graphviz_available() -> bool {
    Command::new("dot")
        .arg("-V")
        .output()
        .map(|output| output.status.success())
        .unwrap_or(false)
}

/// Get information about the available Graphviz installation
pub fn graphviz_info() -> Result<String> {
    let output = Command::new("dot")
        .arg("-V")
        .output()
        .with_context(|| "Failed to run 'dot -V'")?;

    if output.status.success() {
        let version = String::from_utf8_lossy(&output.stderr);
        Ok(version.trim().to_string())
    } else {
        Err(anyhow::anyhow!("Graphviz not available"))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::Config;
    use crate::graph::{CourseGraph, CourseNode};

    fn create_test_graph() -> CourseGraph {
        let mut graph = CourseGraph::new();
        let mut petgraph = petgraph::Graph::new();

        let node1 = CourseNode {
            id: "intro".to_string(),
            title: "Introduction".to_string(),
            phase: "Pre".to_string(),
            display_name: "Introduction\n(intro)".to_string(),
        };

        let node2 = CourseNode {
            id: "advanced".to_string(),
            title: "Advanced Topics".to_string(),
            phase: "Post".to_string(),
            display_name: "Advanced Topics\n(advanced)".to_string(),
        };

        let idx1 = petgraph.add_node(node1);
        let idx2 = petgraph.add_node(node2);
        petgraph.add_edge(idx1, idx2, ());

        graph.graph = petgraph;
        graph.node_map.insert("intro".to_string(), idx1);
        graph.node_map.insert("advanced".to_string(), idx2);

        graph
    }

    #[test]
    fn test_generate_dot_content() -> Result<()> {
        let graph = create_test_graph();
        let config = Config::default();

        let dot_content = generate_dot_content(&graph, &config)?;

        assert!(dot_content.contains("digraph CourseMap"));
        assert!(dot_content.contains("\"intro\""));
        assert!(dot_content.contains("\"advanced\""));
        assert!(dot_content.contains("\"intro\" -> \"advanced\""));
        assert!(dot_content.contains("fillcolor=\"lightblue\""));
        assert!(dot_content.contains("fillcolor=\"orange\""));

        Ok(())
    }

    #[test]
    fn test_escape_dot_string() {
        assert_eq!(escape_dot_string("simple"), "simple");
        assert_eq!(escape_dot_string("with\"quotes"), "with\\\"quotes");
        assert_eq!(escape_dot_string("with\nnewline"), "with\\nnewline");
        assert_eq!(escape_dot_string("with\\backslash"), "with\\\\backslash");
    }

    #[test]
    fn test_render_dot() -> Result<()> {
        let graph = create_test_graph();
        let config = Config::default();

        let temp_file = tempfile::NamedTempFile::new()?;
        let temp_path = temp_file.path().to_str().unwrap();

        render_dot(&graph, temp_path, &config)?;

        let content = std::fs::read_to_string(temp_path)?;
        assert!(content.contains("digraph CourseMap"));

        Ok(())
    }
}
