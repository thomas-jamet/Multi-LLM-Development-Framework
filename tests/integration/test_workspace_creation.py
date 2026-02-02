"""
Integration tests for workspace creation using compiled bootstrap.py.

Tests the complete workspace creation flow via the compiled bootstrap script.
"""

import tempfile
import shutil
import json
import subprocess
import sys
from pathlib import Path
import pytest


class TestBootstrapWorkspaceCreation:
    """Test workspace creation using the bootstrap.py script."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        # Cleanup
        if temp_path.exists():
            shutil.rmtree(temp_path)

    @pytest.fixture
    def bootstrap_script(self):
        """Path to the compiled bootstrap script."""
        # Assuming bootstrap.py is in parent directory
        script_path = Path(__file__).parent.parent.parent / "bootstrap.py"
        if not script_path.exists():
            pytest.skip("bootstrap.py not found - run 'make build' first")
        return script_path

    def test_lite_workspace_creation(self, temp_dir, bootstrap_script):
        """Verify Lite tier workspace creation via bootstrap.py."""
        result = subprocess.run(
            [
                sys.executable,
                str(bootstrap_script),
                "-t",
                "1",
                "-n",
                "test-lite",
            ],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"Bootstrap failed: {result.stderr}"

        workspace_path = temp_dir / "test-lite"
        assert workspace_path.exists(), "Workspace directory not created"

        # Check GEMINI.md exists
        gemini_md = workspace_path / "GEMINI.md"
        assert gemini_md.exists(), "GEMINI.md not created"

        # Check scripts are in flat structure
        scripts_dir = workspace_path / "scripts"
        assert (scripts_dir / "run_audit.py").exists(), "run_audit.py not created"

        # Validate workspace.json
        workspace_json = workspace_path / ".gemini" / "workspace.json"
        assert workspace_json.exists(), "workspace.json not created"
        ws_data = json.loads(workspace_json.read_text())
        assert ws_data["tier"] == "1", "Incorrect tier in workspace.json"
        assert ws_data["name"] == "test-lite", "Incorrect name in workspace.json"

    def test_standard_workspace_creation(self, temp_dir, bootstrap_script):
        """Verify Standard tier workspace creation via bootstrap.py."""
        result = subprocess.run(
            [
                sys.executable,
                str(bootstrap_script),
                "-t",
                "2",
                "-n",
                "test-standard",
            ],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"Bootstrap failed: {result.stderr}"

        workspace_path = temp_dir / "test-standard"
        assert workspace_path.exists(), "Workspace directory not created"

        # Check scripts have categorized structure for Standard tier
        assert (workspace_path / "scripts" / "workspace" / "run_audit.py").exists(), (
            "run_audit.py not in workspace/ subdirectory"
        )

        # Verify Standard-specific dirs exist
        assert (workspace_path / "src" / "test_standard").exists(), (
            "src/test_standard not created"
        )
        assert (workspace_path / "tests" / "unit").exists(), "tests/unit not created"
        assert (workspace_path / "tests" / "integration").exists(), (
            "tests/integration not created"
        )
        assert (workspace_path / "pyproject.toml").exists(), (
            "pyproject.toml not created"
        )

        # Validate workspace.json
        workspace_json = workspace_path / ".gemini" / "workspace.json"
        ws_data = json.loads(workspace_json.read_text())
        assert ws_data["tier"] == "2", "Incorrect tier in workspace.json"

    def test_enterprise_workspace_creation(self, temp_dir, bootstrap_script):
        """Verify Enterprise tier workspace creation via bootstrap.py."""
        result = subprocess.run(
            [
                sys.executable,
                str(bootstrap_script),
                "-t",
                "3",
                "-n",
                "test-enterprise",
            ],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"Bootstrap failed: {result.stderr}"

        workspace_path = temp_dir / "test-enterprise"
        assert workspace_path.exists(), "Workspace directory not created"

        # Verify Enterprise-specific data structure
        assert (workspace_path / "data" / "core" / "inputs").exists(), (
            "data/core/inputs not created"
        )
        assert (workspace_path / "data" / "shared").exists(), "data/shared not created"

        # Verify Enterprise-specific test dirs
        assert (workspace_path / "tests" / "evals").exists(), "tests/evals not created"

        # Validate workspace.json
        workspace_json = workspace_path / ".gemini" / "workspace.json"
        ws_data = json.loads(workspace_json.read_text())
        assert ws_data["tier"] == "3", "Incorrect tier in workspace.json"

    def test_bootstrap_version_command(self, bootstrap_script):
        """Test that bootstrap --version works."""
        result = subprocess.run(
            [sys.executable, str(bootstrap_script), "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert result.returncode == 0, "Version command failed"
        # Check for version string in output (Multi-LLM Dev Framework vX.Y.Z)
        assert "v" in result.stdout or "1.0" in result.stdout, (
            f"Version output format unexpected: {result.stdout}"
        )
