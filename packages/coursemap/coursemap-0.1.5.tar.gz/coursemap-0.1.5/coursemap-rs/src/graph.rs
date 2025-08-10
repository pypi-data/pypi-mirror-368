//! Graph construction and manipulation for course dependencies

use anyhow::{Context, Result};
use petgraph::graph::{DiGraph, NodeIndex};
use std::collections::HashMap;

use crate::parser::Document;

#[derive(Debug, Clone)]
pub struct CourseGraph {
    pub graph: DiGraph<CourseNode, ()>,
    pub node_map: HashMap<String, NodeIndex>,
}

#[derive(Debug, Clone)]
pub struct CourseNode {
    pub id: String,
    pub title: String,
    pub phase: String,
    pub display_name: String,
}

impl CourseNode {
    pub fn new(doc: &Document) -> Self {
        Self {
            id: doc.id.clone(),
            title: doc.title.clone(),
            phase: doc.phase.clone(),
            display_name: doc.display_name(),
        }
    }
}

impl Default for CourseGraph {
    fn default() -> Self {
        Self::new()
    }
}

impl CourseGraph {
    pub fn new() -> Self {
        Self {
            graph: DiGraph::new(),
            node_map: HashMap::new(),
        }
    }

    /// Add a document as a node to the graph
    pub fn add_node(&mut self, doc: &Document) -> NodeIndex {
        if let Some(&existing_index) = self.node_map.get(&doc.id) {
            // Update existing node
            if let Some(node) = self.graph.node_weight_mut(existing_index) {
                *node = CourseNode::new(doc);
            }
            existing_index
        } else {
            // Add new node
            let node = CourseNode::new(doc);
            let index = self.graph.add_node(node);
            self.node_map.insert(doc.id.clone(), index);
            index
        }
    }

    /// Add an edge between two nodes (prerequisite -> course)
    pub fn add_edge(&mut self, prerequisite_id: &str, course_id: &str) -> Result<()> {
        let prerequisite_index = self
            .node_map
            .get(prerequisite_id)
            .copied()
            .with_context(|| format!("Prerequisite node not found: {prerequisite_id}"))?;

        let course_index = self
            .node_map
            .get(course_id)
            .copied()
            .with_context(|| format!("Course node not found: {course_id}"))?;

        self.graph.add_edge(prerequisite_index, course_index, ());
        Ok(())
    }

    /// Get a node by its ID
    pub fn get_node(&self, id: &str) -> Option<&CourseNode> {
        self.node_map
            .get(id)
            .and_then(|&index| self.graph.node_weight(index))
    }

    /// Get all nodes in the graph
    pub fn nodes(&self) -> impl Iterator<Item = (NodeIndex, &CourseNode)> {
        self.graph
            .node_indices()
            .map(move |idx| (idx, &self.graph[idx]))
    }

    /// Get all edges in the graph
    pub fn edges(&self) -> impl Iterator<Item = (NodeIndex, NodeIndex)> + '_ {
        self.graph.edge_indices().map(move |edge_idx| {
            let (source, target) = self.graph.edge_endpoints(edge_idx).unwrap();
            (source, target)
        })
    }

    /// Check if the graph has cycles
    pub fn has_cycles(&self) -> bool {
        petgraph::algo::is_cyclic_directed(&self.graph)
    }

    /// Get nodes in topological order (if the graph is acyclic)
    pub fn topological_sort(&self) -> Result<Vec<NodeIndex>> {
        petgraph::algo::toposort(&self.graph, None)
            .map_err(|_| anyhow::anyhow!("Graph contains cycles, cannot perform topological sort"))
    }

    /// Get the number of nodes
    pub fn node_count(&self) -> usize {
        self.graph.node_count()
    }

    /// Get the number of edges
    pub fn edge_count(&self) -> usize {
        self.graph.edge_count()
    }

    /// Find nodes with no prerequisites (root nodes)
    pub fn find_root_nodes(&self) -> Vec<NodeIndex> {
        self.graph
            .node_indices()
            .filter(|&node| {
                self.graph
                    .neighbors_directed(node, petgraph::Direction::Incoming)
                    .count()
                    == 0
            })
            .collect()
    }

    /// Find nodes with no dependents (leaf nodes)
    pub fn find_leaf_nodes(&self) -> Vec<NodeIndex> {
        self.graph
            .node_indices()
            .filter(|&node| {
                self.graph
                    .neighbors_directed(node, petgraph::Direction::Outgoing)
                    .count()
                    == 0
            })
            .collect()
    }
}

/// Build a course dependency graph from a list of documents
pub fn build_graph(documents: Vec<Document>) -> Result<CourseGraph> {
    let mut graph = CourseGraph::new();

    // First pass: add all nodes
    for doc in &documents {
        graph.add_node(doc);
    }

    // Second pass: add edges based on prerequisites
    for doc in &documents {
        for prerequisite in &doc.prerequisites {
            // Check if prerequisite exists as a node
            if graph.node_map.contains_key(prerequisite) {
                graph.add_edge(prerequisite, &doc.id).with_context(|| {
                    format!("Failed to add edge from {} to {}", prerequisite, doc.id)
                })?;
            } else {
                // Log warning about missing prerequisite
                eprintln!(
                    "Warning: Prerequisite '{}' for course '{}' not found in documents",
                    prerequisite, doc.id
                );
            }
        }
    }

    // Check for cycles
    if graph.has_cycles() {
        eprintln!("Warning: The course dependency graph contains cycles");
    }

    Ok(graph)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser::Document;
    use std::collections::HashMap;
    use std::path::PathBuf;

    fn create_test_document(
        id: &str,
        title: &str,
        phase: &str,
        prerequisites: Vec<&str>,
    ) -> Document {
        Document::new(
            id.to_string(),
            title.to_string(),
            PathBuf::from(format!("{}.qmd", id)),
            phase.to_string(),
            prerequisites.into_iter().map(|s| s.to_string()).collect(),
            HashMap::new(),
        )
    }

    #[test]
    fn test_build_simple_graph() -> Result<()> {
        let documents = vec![
            create_test_document("intro", "Introduction", "Pre", vec![]),
            create_test_document("advanced", "Advanced Topics", "Post", vec!["intro"]),
        ];

        let graph = build_graph(documents)?;

        assert_eq!(graph.node_count(), 2);
        assert_eq!(graph.edge_count(), 1);
        assert!(!graph.has_cycles());

        Ok(())
    }

    #[test]
    fn test_build_complex_graph() -> Result<()> {
        let documents = vec![
            create_test_document("intro", "Introduction", "Pre", vec![]),
            create_test_document("micro", "Microeconomics", "InClass", vec!["intro"]),
            create_test_document("macro", "Macroeconomics", "InClass", vec!["intro"]),
            create_test_document(
                "advanced",
                "Advanced Topics",
                "Post",
                vec!["micro", "macro"],
            ),
        ];

        let graph = build_graph(documents)?;

        assert_eq!(graph.node_count(), 4);
        assert_eq!(graph.edge_count(), 4);
        assert!(!graph.has_cycles());

        // Check root nodes
        let root_nodes = graph.find_root_nodes();
        assert_eq!(root_nodes.len(), 1);
        let root_node = &graph.graph[root_nodes[0]];
        assert_eq!(root_node.id, "intro");

        // Check leaf nodes
        let leaf_nodes = graph.find_leaf_nodes();
        assert_eq!(leaf_nodes.len(), 1);
        let leaf_node = &graph.graph[leaf_nodes[0]];
        assert_eq!(leaf_node.id, "advanced");

        Ok(())
    }

    #[test]
    fn test_missing_prerequisite() -> Result<()> {
        let documents = vec![create_test_document(
            "advanced",
            "Advanced Topics",
            "Post",
            vec!["missing"],
        )];

        let graph = build_graph(documents)?;

        // Should still create the graph, but with a warning
        assert_eq!(graph.node_count(), 1);
        assert_eq!(graph.edge_count(), 0);

        Ok(())
    }

    #[test]
    fn test_topological_sort() -> Result<()> {
        let documents = vec![
            create_test_document("intro", "Introduction", "Pre", vec![]),
            create_test_document("micro", "Microeconomics", "InClass", vec!["intro"]),
            create_test_document("advanced", "Advanced Topics", "Post", vec!["micro"]),
        ];

        let graph = build_graph(documents)?;
        let sorted = graph.topological_sort()?;

        assert_eq!(sorted.len(), 3);

        // The first node should be intro (no prerequisites)
        let first_node = &graph.graph[sorted[0]];
        assert_eq!(first_node.id, "intro");

        // The last node should be advanced (depends on others)
        let last_node = &graph.graph[sorted[2]];
        assert_eq!(last_node.id, "advanced");

        Ok(())
    }
}
