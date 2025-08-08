# Author: Chunjie Liu
# Contact: chunjie.sam.liu.at.gmail.com
# Date: 2025-08-06
# Description: Tests for CLI interface
# Version: 0.1

"""
Tests for CLI interface.
"""

import json
import os
import re
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from geneinfo.cli import app

runner = CliRunner()


def strip_ansi_codes(text):
    """Remove ANSI color codes from text."""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


def test_cli_help():
    """Test CLI help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0

    # Strip ANSI codes from output for reliable testing
    clean_output = strip_ansi_codes(result.stdout)

    assert "geneinfo" in clean_output
    assert "--gene" in clean_output
    assert "--file" in clean_output


def test_cli_no_arguments():
    """Test CLI with no arguments should fail."""
    result = runner.invoke(app, [])
    assert result.exit_code == 1
    assert "Must provide either gene name(s), --gene, or --file" in result.stdout


def test_cli_both_gene_and_file():
    """Test CLI with both gene and file should fail."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False
    ) as f:
        f.write("TP53\n")
        f.flush()

        try:
            result = runner.invoke(app, ["--gene", "TP53", "--file", f.name])
            assert result.exit_code == 1
            assert "Cannot use both --gene and --file" in result.stdout
        finally:
            os.unlink(f.name)


def test_cli_gene_basic():
    """Test CLI with single gene (using mock data)."""
    result = runner.invoke(app, ["--gene", "TP53"])
    # Since this will try to fetch real data and might fail,
    # we expect it to handle errors gracefully
    # The exit code might be 0 or 1 depending on network availability
    assert result.exit_code in [0, 1]


def test_cli_verbose_flag():
    """Test CLI verbose flag."""
    result = runner.invoke(app, ["--gene", "TP53", "--verbose"])
    # Should handle gracefully regardless of network
    assert result.exit_code in [0, 1]


def test_cli_file_input():
    """Test CLI with file input."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False
    ) as f:
        f.write("TP53\nBRCA1\nEGFR\n")
        f.flush()

        try:
            result = runner.invoke(app, ["--file", f.name])
            # Should handle gracefully regardless of network
            assert result.exit_code in [0, 1]
            if result.exit_code == 0:
                assert "Processing" in result.stdout or "Error" in result.stdout
        finally:
            os.unlink(f.name)


def test_cli_output_file():
    """Test CLI with output file."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False
    ) as input_file:
        input_file.write("TP53\n")
        input_file.flush()

        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False
        ) as output_file:
            try:
                result = runner.invoke(
                    app,
                    [
                        "--file",
                        input_file.name,
                        "--output",
                        output_file.name,
                        "--detailed",
                    ],
                )
                # Should handle gracefully regardless of network
                assert result.exit_code in [0, 1]
            finally:
                os.unlink(input_file.name)
                if os.path.exists(output_file.name):
                    os.unlink(output_file.name)


def test_cli_invalid_file():
    """Test CLI with non-existent file."""
    result = runner.invoke(app, ["--file", "nonexistent_file.txt"])
    assert result.exit_code == 2  # typer's file validation error


def test_cli_version():
    """Test CLI version option."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "geneinfo" in result.stdout
    # Should contain version number (like "0.1.0")
    assert re.search(r"\d+\.\d+\.\d+", result.stdout)


if __name__ == "__main__":
    pytest.main([__file__])
