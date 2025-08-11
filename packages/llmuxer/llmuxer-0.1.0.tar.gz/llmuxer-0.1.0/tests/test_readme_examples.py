"""Test that README examples work correctly."""

import pytest
from unittest.mock import patch
import llmuxer


def test_quick_start_example():
    """Test the Quick Start example from README."""
    
    # Example from README
    examples = [
        {"input": "This product is amazing!", "label": "positive"},
        {"input": "Terrible service", "label": "negative"},
        {"input": "It's okay", "label": "neutral"}
    ]
    
    # Mock the API calls
    with patch('llmuxer.api.fetch_openrouter_models') as mock_fetch:
        mock_fetch.return_value = {
            "anthropic/claude-3-haiku": {"input": 0.125, "output": 0.125},
            "openai/gpt-4": {"input": 5.0, "output": 5.0}
        }
        
        with patch('llmuxer.selector.Selector.run_evaluation') as mock_eval:
            mock_eval.return_value = {
                "anthropic/claude-3-haiku": {
                    "accuracy": 0.92,
                    "time": 2.5,
                    "config": {"provider": "openrouter", "model": "anthropic/claude-3-haiku"}
                }
            }
            
            result = llmuxer.optimize_cost(
                baseline="gpt-4",
                examples=examples,
                task="classification",
                options=["positive", "negative", "neutral"],
                min_accuracy=0.9
            )
            
            # Check the structure matches README example
            assert "model" in result
            assert "accuracy" in result
            assert "cost_per_million" in result
            assert "cost_savings" in result
            
            # Values should be reasonable
            assert result["accuracy"] >= 0.9  # Meets min_accuracy
            assert 0 <= result["cost_savings"] <= 1  # Valid percentage


def test_error_handling_example():
    """Test error handling as shown in README."""
    
    with patch('llmuxer.api.fetch_openrouter_models') as mock_fetch:
        mock_fetch.return_value = {}
        
        result = llmuxer.optimize_cost(
            baseline="gpt-4",
            examples=[{"input": "test", "label": "test_label"}],
            min_accuracy=0.99  # Very high threshold
        )
        
        # Should return error when no model meets threshold
        assert "error" in result or "model" in result


def test_dataset_format():
    """Test that dataset format matches README specification."""
    import json
    import tempfile
    
    # Create test dataset as shown in README
    dataset = [
        {"input": "What's my account balance?", "label": "balance_inquiry"},
        {"input": "I lost my card", "label": "card_lost"}
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        for item in dataset:
            f.write(json.dumps(item) + '\n')
        temp_path = f.name
    
    # Mock the API calls
    with patch('llmuxer.api.fetch_openrouter_models') as mock_fetch:
        mock_fetch.return_value = {
            "openai/gpt-3.5-turbo": {"input": 0.25, "output": 0.25}
        }
        
        with patch('llmuxer.selector.Selector.run_evaluation') as mock_eval:
            mock_eval.return_value = {
                "openai/gpt-3.5-turbo": {
                    "accuracy": 0.85,
                    "time": 1.5,
                    "config": {"provider": "openrouter", "model": "openai/gpt-3.5-turbo"}
                }
            }
            
            # Should work with JSONL format as specified
            result = llmuxer.optimize_cost(
                baseline="gpt-4",
                dataset=temp_path,
                task="classification",
                min_accuracy=0.8
            )
            
            assert "model" in result or "error" in result
    
    # Clean up
    import os
    os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__])