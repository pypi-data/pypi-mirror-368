"""Tests for the coursemap Python package."""

import pytest
import tempfile
import os
from pathlib import Path
import coursemap


class TestCourseMap:
    """Test the CourseMap class."""

    def test_coursemap_creation_default(self):
        """Test creating CourseMap with default config."""
        cm = coursemap.CourseMap()
        assert cm is not None

    def test_coursemap_creation_with_config(self):
        """Test creating CourseMap with custom config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("""
root-key: test-map
phase:
  TestPhase:
    face: red
ignore:
  - test.qmd
""")
            config_path = f.name

        try:
            cm = coursemap.CourseMap(config=config_path)
            config = cm.get_config()
            assert config['root_key'] == 'test-map'
            assert 'TestPhase' in config['phase']
            assert config['phase']['TestPhase']['face'] == 'red'
        finally:
            os.unlink(config_path)

    def test_generate_course_map(self):
        """Test generating course map with test documents."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test course files
            course1_path = Path(temp_dir) / "course1.qmd"
            course1_path.write_text("""---
title: "Course 1"
course-map:
  id: course1
  phase: Pre
  prerequisites: []
---
# Course 1 Content
""")

            course2_path = Path(temp_dir) / "course2.qmd"
            course2_path.write_text("""---
title: "Course 2"
course-map:
  id: course2
  phase: InClass
  prerequisites: ["course1"]
---
# Course 2 Content
""")

            cm = coursemap.CourseMap(temp_dir)
            output_path = Path(temp_dir) / "test_output.dot"
            
            # Generate DOT format (doesn't require Graphviz)
            result = cm.save(str(output_path), format="dot")
            
            assert result == str(output_path)
            assert output_path.exists()
            
            # Check that the output contains expected content
            content = output_path.read_text()
            assert "course1" in content
            assert "course2" in content

    def test_parse_documents(self):
        """Test parsing documents from directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test course files
            course_path = Path(temp_dir) / "test_course.qmd"
            course_path.write_text("""---
title: "Test Course"
course-map:
  id: test-course
  phase: Pre
  prerequisites: ["intro"]
---
# Test Course Content
""")

            cm = coursemap.CourseMap(temp_dir)
            documents = cm.parse_documents()
            
            assert len(documents) == 1
            doc = documents[0]
            assert doc['id'] == 'test-course'
            assert doc['title'] == 'Test Course'
            assert doc['phase'] == 'Pre'
            assert doc['prerequisites'] == ['intro']

    def test_show_method(self):
        """Test the show method (matplotlib-style)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a simple test course
            course_path = Path(temp_dir) / "simple.qmd"
            course_path.write_text("""---
title: "Simple Course"
course-map:
  id: simple
  phase: Pre
  prerequisites: []
---
# Simple Course
""")

            cm = coursemap.CourseMap(temp_dir)
            
            # show() should not raise an exception
            # (it will print a message in terminal mode)
            cm.show()


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_show_function(self):
        """Test the show convenience function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test course file
            course_path = Path(temp_dir) / "test.qmd"
            course_path.write_text("""---
title: "Test"
course-map:
  id: test
  phase: Pre
  prerequisites: []
---
# Test
""")

            # show() should not raise an exception
            # (it will print a message in terminal mode)
            coursemap.show(temp_dir)

    def test_graphviz_available(self):
        """Test Graphviz availability check."""
        result = coursemap.graphviz_available()
        assert isinstance(result, bool)

    def test_graphviz_info(self):
        """Test getting Graphviz info."""
        if coursemap.graphviz_available():
            info = coursemap.graphviz_info()
            assert isinstance(info, str)
            assert len(info) > 0
        else:
            with pytest.raises(Exception):
                coursemap.graphviz_info()


class TestNewAPI:
    """Test the new matplotlib-inspired API."""

    def test_save_with_auto_extension(self):
        """Test save method with automatic extension detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test course file
            course_path = Path(temp_dir) / "test.qmd"
            course_path.write_text("""---
title: "Test"
course-map:
  id: test
  phase: Pre
  prerequisites: []
---
# Test
""")

            cm = coursemap.CourseMap(temp_dir)
            
            # Test auto-extension detection
            output_path = Path(temp_dir) / "output.png"
            result = cm.save(str(output_path))  # Should auto-detect PNG format
            
            # Should return path with correct extension
            assert result.endswith('.png')
            
            # Test explicit format
            dot_path = Path(temp_dir) / "output"
            result = cm.save(str(dot_path), format="dot")
            assert result.endswith('.dot')
            assert Path(result).exists()


class TestErrorHandling:
    """Test error handling."""

    def test_nonexistent_directory(self):
        """Test handling of nonexistent directory."""
        with pytest.raises(Exception):
            cm = coursemap.CourseMap("/nonexistent/directory")
            cm.parse_documents()

    def test_invalid_config_file(self):
        """Test handling of invalid config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            config_path = f.name

        try:
            with pytest.raises(Exception):
                coursemap.CourseMap(config=config_path)
        finally:
            os.unlink(config_path)

    def test_empty_directory(self):
        """Test handling of empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cm = coursemap.CourseMap(temp_dir)
            documents = cm.parse_documents()
            assert len(documents) == 0


if __name__ == "__main__":
    pytest.main([__file__])
