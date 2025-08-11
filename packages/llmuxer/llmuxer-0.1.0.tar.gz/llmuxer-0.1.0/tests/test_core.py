"""Test core functionality of llmuxer."""

import pytest
from unittest.mock import Mock, patch
import llmuxer


def test_optimize_cost_basic():
    """Test basic optimize_cost functionality with examples."""
    
    # Sample classification data
    examples = [
        {"input": "This is great!", "label": "positive"},
        {"input": "This is terrible!", "label": "negative"},
        {"input": "This is okay", "label": "neutral"},
    ]
    
    # Mock the actual API calls to avoid real requests in tests
    with patch('llmuxer.api.fetch_openrouter_models') as mock_fetch:
        mock_fetch.return_value = {
            "openai/gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
            "meta-llama/llama-3.1-8b": {"input": 0.015, "output": 0.02},
        }
        
        with patch('llmuxer.selector.Selector.run_evaluation') as mock_eval:
            mock_eval.return_value = {
                "openrouter/meta-llama/llama-3.1-8b": {
                    "accuracy": 0.85,
                    "time": 10.5,
                    "config": {"provider": "openrouter", "model": "meta-llama/llama-3.1-8b"}
                }
            }
            
            # This should not raise an exception
            result = llmuxer.optimize_cost(
                baseline="gpt-4",
                examples=examples,
                task="classification",
                min_accuracy=0.8
            )
            
            # Basic result validation
            assert isinstance(result, dict)
            assert "model" in result or "error" in result


def test_invalid_baseline():
    """Test error handling for invalid baseline."""
    
    examples = [{"input": "test", "label": "test_label"}]
    
    # This should handle gracefully - either return error or work with fallback
    result = llmuxer.optimize_cost(
        baseline="invalid-model-name",
        examples=examples
    )
    
    assert isinstance(result, dict)
    # Should either succeed with fallback or return error
    assert "model" in result or "error" in result


def test_empty_dataset():
    """Test handling of empty dataset."""
    
    with pytest.raises(ValueError):
        llmuxer.optimize_cost(
            baseline="gpt-4",
            examples=[],  # Empty dataset
            min_accuracy=0.8
        )


def test_version():
    """Test version is accessible."""
    assert hasattr(llmuxer, '__version__')
    assert isinstance(llmuxer.__version__, str)
    assert llmuxer.version() == llmuxer.__version__


def test_imports():
    """Test all expected functions are importable."""
    
    # Test main function
    assert hasattr(llmuxer, 'optimize_cost')
    assert callable(llmuxer.optimize_cost)
    
    # Test supporting classes
    assert hasattr(llmuxer, 'Provider')
    assert hasattr(llmuxer, 'Evaluator')
    assert hasattr(llmuxer, 'Selector')
    assert hasattr(llmuxer, 'get_provider')


if __name__ == "__main__":
    pytest.main([__file__])