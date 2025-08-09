"""
Tests for core conversion functionality.
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from docxmd_converter.core import ConversionError, DocxMdConverter


class TestDocxMdConverter:
    """Test cases for DocxMdConverter class."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create test directories
        self.src_dir = self.temp_dir / "src"
        self.dst_dir = self.temp_dir / "dst"
        self.src_dir.mkdir()
        self.dst_dir.mkdir()

    def teardown_method(self):
        """Cleanup test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @patch("docxmd_converter.core.pypandoc.get_pandoc_version")
    def test_init_success(self, mock_version):
        """Test successful initialization."""
        mock_version.return_value = "2.19"
        converter = DocxMdConverter()
        assert converter is not None

    @patch("docxmd_converter.core.pypandoc.get_pandoc_version")
    def test_init_pandoc_not_found(self, mock_version):
        """Test initialization when pandoc is not installed."""
        mock_version.side_effect = OSError("Pandoc not found")

        with pytest.raises(ConversionError, match="Pandoc is not installed"):
            DocxMdConverter()

    @patch("docxmd_converter.core.pypandoc.get_pandoc_version")
    @patch("docxmd_converter.core.pypandoc.convert_file")
    def test_convert_docx_to_md(self, mock_convert, mock_version):
        """Test .docx to .md conversion."""
        mock_version.return_value = "2.19"
        mock_convert.return_value = None

        # Create test files
        input_file = self.src_dir / "test.docx"
        output_file = self.dst_dir / "test.md"
        input_file.touch()  # Create empty file

        converter = DocxMdConverter()
        result = converter.convert_file(input_file, output_file, "docx2md")

        assert result is True
        mock_convert.assert_called_once()

    @patch("docxmd_converter.core.pypandoc.get_pandoc_version")
    def test_convert_file_not_exists(self, mock_version):
        """Test conversion with non-existent input file."""
        mock_version.return_value = "2.19"

        converter = DocxMdConverter()
        result = converter.convert_file("nonexistent.docx", "output.md", "docx2md")

        assert result is False

    @patch("docxmd_converter.core.pypandoc.get_pandoc_version")
    def test_invalid_direction(self, mock_version):
        """Test conversion with invalid direction."""
        mock_version.return_value = "2.19"

        input_file = self.src_dir / "test.docx"
        output_file = self.dst_dir / "test.md"
        input_file.touch()

        converter = DocxMdConverter()
        result = converter.convert_file(input_file, output_file, "invalid")

        assert result is False

    @patch("docxmd_converter.core.pypandoc.get_pandoc_version")
    def test_convert_directory_no_files(self, mock_version):
        """Test directory conversion with no matching files."""
        mock_version.return_value = "2.19"

        converter = DocxMdConverter()
        successful, total = converter.convert_directory(
            self.src_dir, self.dst_dir, "docx2md"
        )

        assert successful == 0
        assert total == 0

    @patch("docxmd_converter.core.pypandoc.get_pandoc_version")
    @patch("docxmd_converter.core.pypandoc.convert_file")
    def test_convert_directory_with_files(self, mock_convert, mock_version):
        """Test directory conversion with files."""
        mock_version.return_value = "2.19"
        mock_convert.return_value = None

        # Create test files in subdirectories
        (self.src_dir / "subdir").mkdir()
        (self.src_dir / "file1.docx").touch()
        (self.src_dir / "subdir" / "file2.docx").touch()

        converter = DocxMdConverter()
        successful, total = converter.convert_directory(
            self.src_dir, self.dst_dir, "docx2md"
        )

        assert successful == 2
        assert total == 2
        assert mock_convert.call_count == 2

    @patch("docxmd_converter.core.pypandoc.get_pandoc_version")
    def test_validate_template_valid(self, mock_version):
        """Test template validation with valid template."""
        mock_version.return_value = "2.19"

        template_file = self.temp_dir / "template.docx"
        template_file.touch()

        converter = DocxMdConverter()
        result = converter.validate_template(template_file)

        assert result is True

    @patch("docxmd_converter.core.pypandoc.get_pandoc_version")
    def test_validate_template_not_exists(self, mock_version):
        """Test template validation with non-existent file."""
        mock_version.return_value = "2.19"

        converter = DocxMdConverter()
        result = converter.validate_template("nonexistent.docx")

        assert result is False

    @patch("docxmd_converter.core.pypandoc.get_pandoc_version")
    def test_validate_template_wrong_extension(self, mock_version):
        """Test template validation with wrong file extension."""
        mock_version.return_value = "2.19"

        template_file = self.temp_dir / "template.txt"
        template_file.touch()

        converter = DocxMdConverter()
        result = converter.validate_template(template_file)

        assert result is False

    @patch("docxmd_converter.core.pypandoc.get_pandoc_version")
    def test_get_supported_directions(self, mock_version):
        """Test getting supported conversion directions."""
        mock_version.return_value = "2.19"

        converter = DocxMdConverter()
        directions = converter.get_supported_directions()

        assert "docx2md" in directions
        assert "md2docx" in directions
        assert len(directions) == 2
