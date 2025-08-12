import pytest
import os
import tempfile
import json
from pathlib import Path
from docx import Document
from docx_json_replacer.cli import main
import sys
from unittest.mock import patch


class TestCLI:
    def test_cli_success(self, sample_docx, test_data, tmp_path):
        """Test successful CLI execution"""
        json_file = tmp_path / "test_data.json"
        output_file = tmp_path / "output.docx"
        
        # Create JSON file
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        # Mock sys.argv
        test_args = ['cli.py', str(sample_docx), str(json_file), '-o', str(output_file)]
        with patch.object(sys, 'argv', test_args):
            main()
        
        # Verify output file was created
        assert output_file.exists()
        
        # Verify content was replaced
        doc = Document(str(output_file))
        paragraphs_text = [p.text for p in doc.paragraphs]
        assert "Hello John Doe!" in paragraphs_text

    def test_cli_missing_docx(self, test_data, tmp_path):
        """Test CLI with missing DOCX file"""
        json_file = tmp_path / "test_data.json"
        missing_docx = tmp_path / "missing.docx"
        output_file = tmp_path / "output.docx"
        
        # Create JSON file
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        # Mock sys.argv
        test_args = ['cli.py', str(missing_docx), str(json_file), '-o', str(output_file)]
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_cli_missing_json(self, sample_docx, tmp_path):
        """Test CLI with missing JSON file"""
        missing_json = tmp_path / "missing.json"
        output_file = tmp_path / "output.docx"
        
        # Mock sys.argv
        test_args = ['cli.py', str(sample_docx), str(missing_json), '-o', str(output_file)]
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_cli_default_output(self, sample_docx, test_data, tmp_path):
        """Test CLI with default output filename"""
        json_file = tmp_path / "test_data.json"
        
        # Create JSON file
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        # Change to tmp directory
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            # Create a local copy of the docx file
            local_docx = tmp_path / "template.docx"
            with open(sample_docx, 'rb') as src, open(local_docx, 'wb') as dst:
                dst.write(src.read())
            
            # Mock sys.argv without -o option
            test_args = ['cli.py', str(local_docx), str(json_file)]
            with patch.object(sys, 'argv', test_args):
                main()
            
            # Check default output file was created
            expected_output = tmp_path / "template_replaced.docx"
            assert expected_output.exists()
            
        finally:
            os.chdir(original_cwd)

    def test_cli_invalid_json(self, sample_docx, tmp_path):
        """Test CLI with invalid JSON file"""
        invalid_json = tmp_path / "invalid.json"
        output_file = tmp_path / "output.docx"
        
        # Create invalid JSON file
        with open(invalid_json, 'w') as f:
            f.write("{ invalid json")
        
        # Mock sys.argv
        test_args = ['cli.py', str(sample_docx), str(invalid_json), '-o', str(output_file)]
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1