"""
Bootstrap Script Test Suite

This module contains tests for the Bootstrap Script modular source.

Test Categories:
- Unit tests for individual modules (config, core, etc.)
- Integration tests for build process
- Functional tests for workspace creation

Run with: make test (once pytest is configured)
"""

import pytest
from pathlib import Path
import sys

# Get the source root directory
SOURCE_ROOT = Path(__file__).parent.parent

# Add source root to path for imports
sys.path.insert(0, str(SOURCE_ROOT))


class TestConfig:
    """Tests for config.py constants and configuration."""

    def test_version_format(self):
        """VERSION should be in YYYY.XX format."""
        from config import VERSION

        assert VERSION is not None
        parts = VERSION.split(".")
        assert len(parts) == 2, f"VERSION should be YYYY.XX format, got: {VERSION}"
        assert parts[0].isdigit() and len(parts[0]) == 4, "Year should be 4 digits"
        assert parts[1].isdigit(), "Minor version should be numeric"

    def test_tiers_defined(self):
        """TIERS dictionary should contain all 3 tiers."""
        from config import TIERS

        # TIERS uses string keys "1", "2", "3"
        assert "1" in TIERS, "Tier 1 (Lite) should be defined"
        assert "2" in TIERS, "Tier 2 (Standard) should be defined"
        assert "3" in TIERS, "Tier 3 (Enterprise) should be defined"

    def test_exit_codes_defined(self):
        """Exit codes should be defined as module constants."""
        from config import EXIT_SUCCESS, EXIT_VALIDATION_ERROR

        assert EXIT_SUCCESS == 0
        assert EXIT_VALIDATION_ERROR == 1

    def test_tier_names_defined(self):
        """TIER_NAMES should provide human-readable names."""
        from config import TIER_NAMES

        assert TIER_NAMES["1"] == "Lite"
        assert TIER_NAMES["2"] == "Standard"
        assert TIER_NAMES["3"] == "Enterprise"


class TestCore:
    """Tests for core.py utilities and validators."""

    def _import_core_module(self):
        """Import core.py avoiding the core/ directory shadow."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("core_module", SOURCE_ROOT / "core.py")
        core_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(core_module)
        return core_module

    def test_validation_error_exists(self):
        """ValidationError exception should be importable."""
        core_module = self._import_core_module()
        assert issubclass(core_module.ValidationError, Exception)

    def test_workspace_error_hierarchy(self):
        """Exception hierarchy should be properly defined."""
        core_module = self._import_core_module()

        assert issubclass(core_module.ValidationError, core_module.WorkspaceError)
        assert issubclass(core_module.CreationError, core_module.WorkspaceError)

    def test_validate_project_name_valid(self):
        """Project name validator should accept valid names."""
        core_module = self._import_core_module()

        # Valid names should not raise
        core_module.validate_project_name("my-workspace")
        core_module.validate_project_name("test_project")
        core_module.validate_project_name("MyProject123")

    def test_validate_project_name_invalid(self):
        """Project name validator should reject invalid names."""
        core_module = self._import_core_module()

        # Invalid names should raise ValidationError
        with pytest.raises(core_module.ValidationError):
            core_module.validate_project_name("")  # Empty name

        with pytest.raises(core_module.ValidationError):
            core_module.validate_project_name("a" * 100)  # Too long

    def test_color_output_functions(self):
        """Color output functions should be callable."""
        core_module = self._import_core_module()

        # These should not raise
        core_module.success("test message")
        core_module.error("test message")
        core_module.warning("test message")
        core_module.info("test message")


class TestBuildProcess:
    """Tests for the build.py compilation process."""

    def test_source_modules_exist(self):
        """All modules in build order should exist."""
        required_modules = [
            "config.py",
            "core.py",
            "providers/base.py",
            "core/makefile.py",
            "core/templates.py",
            "content_generators.py",
            "operations/create.py",
            "__main__.py",
        ]

        for module in required_modules:
            module_path = SOURCE_ROOT / module
            assert module_path.exists(), f"Module missing: {module}"

    def test_build_script_exists(self):
        """build.py should exist in source root."""
        assert (SOURCE_ROOT / "build.py").exists()

    def test_build_script_has_module_order(self):
        """build.py should define module_order list."""
        build_content = (SOURCE_ROOT / "build.py").read_text()
        assert "module_order" in build_content, "build.py should define module_order"


class TestDocumentation:
    """Tests for documentation completeness."""

    def test_readme_exists(self):
        """README.md should exist."""
        assert (SOURCE_ROOT / "README.md").exists()

    def test_contributing_exists(self):
        """CONTRIBUTING.md should exist."""
        assert (SOURCE_ROOT / "CONTRIBUTING.md").exists()

    def test_docs_directory_exists(self):
        """docs/ directory should exist with key files."""
        docs_dir = SOURCE_ROOT / "docs"
        assert docs_dir.exists()
        assert (docs_dir / "architecture.md").exists()
        assert (docs_dir / "development.md").exists()
        assert (docs_dir / "tools_reference.md").exists()


# Placeholder for future tests
class TestWorkspaceCreation:
    """Integration tests for workspace creation (requires compiled bootstrap.py)."""

    @pytest.mark.skip(reason="Requires compiled bootstrap.py and temp directory")
    def test_tier1_creation(self):
        """Tier 1 (Lite) workspace should be creatable."""
        pass

    @pytest.mark.skip(reason="Requires compiled bootstrap.py and temp directory")
    def test_tier2_creation(self):
        """Tier 2 (Standard) workspace should be creatable."""
        pass

    @pytest.mark.skip(reason="Requires compiled bootstrap.py and temp directory")
    def test_tier3_creation(self):
        """Tier 3 (Enterprise) workspace should be creatable."""
        pass
