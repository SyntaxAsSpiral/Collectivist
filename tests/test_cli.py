#!/usr/bin/env python3
"""
Unit tests for CLI commands
Tests command parsing, pipeline integration, and error handling
"""

import unittest
import sys
import io
import argparse
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import tempfile
import os
import subprocess

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))


class TestCLICommandParsing(unittest.TestCase):
    """Test command line argument parsing"""
    
    def test_analyze_command_parsing(self):
        """Test analyze command argument parsing"""
        # Create a parser like the one in main()
        parser = argparse.ArgumentParser()
        parser.add_argument('--verbose', '-v', action='store_true')
        subparsers = parser.add_subparsers(dest='command')
        
        analyze_parser = subparsers.add_parser('analyze')
        analyze_parser.add_argument('--force-type', type=str)
        
        # Test basic analyze
        args = parser.parse_args(['analyze'])
        self.assertEqual(args.command, 'analyze')
        self.assertIsNone(args.force_type)
        
        # Test analyze with force-type
        args = parser.parse_args(['analyze', '--force-type', 'repositories'])
        self.assertEqual(args.command, 'analyze')
        self.assertEqual(args.force_type, 'repositories')
        
    def test_scan_command_parsing(self):
        """Test scan command argument parsing"""
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest='command')
        scan_parser = subparsers.add_parser('scan')
        
        args = parser.parse_args(['scan'])
        self.assertEqual(args.command, 'scan')
        
    def test_describe_command_parsing(self):
        """Test describe command argument parsing"""
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest='command')
        describe_parser = subparsers.add_parser('describe')
        describe_parser.add_argument('--max-workers', type=int, default=5)
        
        # Test default max-workers
        args = parser.parse_args(['describe'])
        self.assertEqual(args.command, 'describe')
        self.assertEqual(args.max_workers, 5)
        
        # Test custom max-workers
        args = parser.parse_args(['describe', '--max-workers', '10'])
        self.assertEqual(args.max_workers, 10)
        
    def test_render_command_parsing(self):
        """Test render command argument parsing"""
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest='command')
        render_parser = subparsers.add_parser('render')
        
        args = parser.parse_args(['render'])
        self.assertEqual(args.command, 'render')
        
    def test_update_command_parsing(self):
        """Test update command argument parsing with all options"""
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest='command')
        update_parser = subparsers.add_parser('update')
        update_parser.add_argument('--skip-analyze', action='store_true')
        update_parser.add_argument('--skip-scan', action='store_true')
        update_parser.add_argument('--skip-describe', action='store_true')
        update_parser.add_argument('--skip-render', action='store_true')
        update_parser.add_argument('--skip-process-new', action='store_true')
        update_parser.add_argument('--force-type', type=str)
        update_parser.add_argument('--max-workers', type=int, default=5)
        
        # Test basic update
        args = parser.parse_args(['update'])
        self.assertEqual(args.command, 'update')
        self.assertFalse(args.skip_analyze)
        self.assertFalse(args.skip_scan)
        self.assertEqual(args.max_workers, 5)
        
        # Test update with skip flags
        args = parser.parse_args(['update', '--skip-analyze', '--skip-scan', '--max-workers', '10'])
        self.assertTrue(args.skip_analyze)
        self.assertTrue(args.skip_scan)
        self.assertEqual(args.max_workers, 10)


class TestCLIIntegration(unittest.TestCase):
    """Test CLI integration through subprocess calls"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.collection_path = Path(self.temp_dir)
        self.cli_path = Path(__file__).parent / "__main__.py"
        
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_help_message_displayed(self):
        """Test that help message is displayed when no command is given"""
        result = subprocess.run(
            [sys.executable, str(self.cli_path)],
            capture_output=True,
            text=True,
            cwd=self.temp_dir
        )
        
        # Should exit with non-zero code and show help
        self.assertNotEqual(result.returncode, 0)
        # Help message could be in stdout or stderr
        output = (result.stdout + result.stderr).lower()
        self.assertIn("usage:", output)
        
    def test_invalid_command_error(self):
        """Test that invalid command shows error"""
        result = subprocess.run(
            [sys.executable, str(self.cli_path), "invalid_command"],
            capture_output=True,
            text=True,
            cwd=self.temp_dir
        )
        
        # Should exit with non-zero code and show error
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid choice", result.stderr.lower())
        
    def test_analyze_command_without_llm(self):
        """Test analyze command fails gracefully without LLM configuration"""
        result = subprocess.run(
            [sys.executable, str(self.cli_path), "analyze"],
            capture_output=True,
            text=True,
            cwd=self.temp_dir
        )
        
        # Should exit with non-zero code due to missing LLM config
        self.assertNotEqual(result.returncode, 0)
        # Should show some error message about LLM or configuration
        output = (result.stdout + result.stderr).lower()
        self.assertTrue(
            any(term in output for term in ["llm", "config", "error", "fatal"]),
            f"Expected LLM/config error in output: {result.stdout + result.stderr}"
        )
        
    def test_scan_command_without_collection_yaml(self):
        """Test scan command fails gracefully without collection.yaml"""
        result = subprocess.run(
            [sys.executable, str(self.cli_path), "scan"],
            capture_output=True,
            text=True,
            cwd=self.temp_dir
        )
        
        # Should exit with non-zero code due to missing collection.yaml
        self.assertNotEqual(result.returncode, 0)
        # Should show some error message about missing collection.yaml
        output = (result.stdout + result.stderr).lower()
        self.assertTrue(
            any(term in output for term in ["collection.yaml", "not found", "error"]),
            f"Expected collection.yaml error in output: {result.stdout + result.stderr}"
        )
        
    def test_describe_command_without_collection_yaml(self):
        """Test describe command fails gracefully without collection.yaml"""
        result = subprocess.run(
            [sys.executable, str(self.cli_path), "describe"],
            capture_output=True,
            text=True,
            cwd=self.temp_dir
        )
        
        # Should exit with non-zero code due to missing collection.yaml
        self.assertNotEqual(result.returncode, 0)
        # Should show some error message about missing collection.yaml
        output = (result.stdout + result.stderr).lower()
        self.assertTrue(
            any(term in output for term in ["collection.yaml", "not found", "error"]),
            f"Expected collection.yaml error in output: {result.stdout + result.stderr}"
        )
        
    def test_render_command_without_collection_yaml(self):
        """Test render command fails gracefully without collection.yaml"""
        result = subprocess.run(
            [sys.executable, str(self.cli_path), "render"],
            capture_output=True,
            text=True,
            cwd=self.temp_dir
        )
        
        # Should exit with non-zero code due to missing collection.yaml
        self.assertNotEqual(result.returncode, 0)
        # Should show some error message about missing collection.yaml
        output = (result.stdout + result.stderr).lower()
        self.assertTrue(
            any(term in output for term in ["collection.yaml", "not found", "error"]),
            f"Expected collection.yaml error in output: {result.stdout + result.stderr}"
        )
        
    def test_update_command_without_llm(self):
        """Test update command fails gracefully without LLM configuration"""
        result = subprocess.run(
            [sys.executable, str(self.cli_path), "update"],
            capture_output=True,
            text=True,
            cwd=self.temp_dir
        )
        
        # Should exit with non-zero code due to missing LLM config
        self.assertNotEqual(result.returncode, 0)
        # Should show some error message about LLM or configuration
        output = (result.stdout + result.stderr).lower()
        self.assertTrue(
            any(term in output for term in ["llm", "config", "error", "fatal"]),
            f"Expected LLM/config error in output: {result.stdout + result.stderr}"
        )


class TestCLICommandOptions(unittest.TestCase):
    """Test CLI command options and flags"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.collection_path = Path(self.temp_dir)
        self.cli_path = Path(__file__).parent / "__main__.py"
        
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_analyze_force_type_option(self):
        """Test analyze command with --force-type option"""
        result = subprocess.run(
            [sys.executable, str(self.cli_path), "analyze", "--force-type", "repositories"],
            capture_output=True,
            text=True,
            cwd=self.temp_dir
        )
        
        # Should still fail due to missing LLM config, but should accept the option
        self.assertNotEqual(result.returncode, 0)
        # Should not show argument parsing errors
        self.assertNotIn("unrecognized arguments", result.stderr.lower())
        
    def test_describe_max_workers_option(self):
        """Test describe command with --max-workers option"""
        result = subprocess.run(
            [sys.executable, str(self.cli_path), "describe", "--max-workers", "10"],
            capture_output=True,
            text=True,
            cwd=self.temp_dir
        )
        
        # Should still fail due to missing collection.yaml, but should accept the option
        self.assertNotEqual(result.returncode, 0)
        # Should not show argument parsing errors
        self.assertNotIn("unrecognized arguments", result.stderr.lower())
        
    def test_update_skip_options(self):
        """Test update command with skip options"""
        result = subprocess.run(
            [sys.executable, str(self.cli_path), "update", "--skip-analyze", "--skip-scan"],
            capture_output=True,
            text=True,
            cwd=self.temp_dir
        )
        
        # Should still fail due to missing collection.yaml, but should accept the options
        self.assertNotEqual(result.returncode, 0)
        # Should not show argument parsing errors
        self.assertNotIn("unrecognized arguments", result.stderr.lower())
        
    def test_verbose_option(self):
        """Test verbose option is accepted"""
        result = subprocess.run(
            [sys.executable, str(self.cli_path), "--verbose", "analyze"],
            capture_output=True,
            text=True,
            cwd=self.temp_dir
        )
        
        # Should still fail due to missing LLM config, but should accept the option
        self.assertNotEqual(result.returncode, 0)
        # Should not show argument parsing errors
        self.assertNotIn("unrecognized arguments", result.stderr.lower())


if __name__ == '__main__':
    unittest.main()