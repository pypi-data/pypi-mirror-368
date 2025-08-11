"""Simple tests for ollamapy functionality."""

from ollamapy.main import hello, greet


def test_hello():
    """Test the hello function."""
    assert hello() == "Hello, World!"


def test_greet():
    """Test the greet function."""
    assert greet("Alice") == "Hello, Alice!"


def test_vibe_test_import():
    """Test that vibe test functionality can be imported."""
    from ollamapy.vibe_tests import VibeTestRunner, run_vibe_tests
    
    # Test that we can create a runner
    runner = VibeTestRunner()
    assert runner.model == "gemma3:4b"
    assert len(runner.yes_phrases) == 5
    assert len(runner.no_phrases) == 5
    
    # Test that function exists
    assert callable(run_vibe_tests)