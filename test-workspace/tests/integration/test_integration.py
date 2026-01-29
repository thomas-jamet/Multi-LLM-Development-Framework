"""Integration tests for test_workspace.

Tests that verify multiple components work together.
Run with: pytest tests/integration/
"""

import pytest


def test_end_to_end_flow():
    """Test complete workflow from input to output."""
    # Example: Test file processing pipeline
    # 1. Create test input
    # 2. Run processing
    # 3. Verify output
    pass  # Replace with actual integration test


@pytest.mark.slow
def test_external_api_integration():
    """Test integration with external services.

    Mark as slow to skip in fast test runs: pytest -m "not slow"
    """

    pass  # Replace with actual API integration test
