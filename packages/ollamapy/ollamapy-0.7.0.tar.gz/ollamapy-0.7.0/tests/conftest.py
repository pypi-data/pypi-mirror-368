"""Pytest configuration and fixtures for ollamapy tests."""

import pytest


def pytest_addoption(parser):
    """Add custom command line options for vibe tests."""
    parser.addoption(
        "--model", 
        action="store", 
        default="gemma3:4b", 
        help="Model to use for vibe tests (default: gemma3:4b)"
    )
    parser.addoption(
        "-N", "--iterations", 
        action="store", 
        type=int, 
        default=1, 
        help="Number of iterations to run each vibe test (default: 1)"
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "vibetest: marks tests as vibe tests for AI decision-making evaluation"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add vibetest marker to any test with 'vibe' in the name
        if "vibe" in item.name.lower():
            item.add_marker(pytest.mark.vibetest)