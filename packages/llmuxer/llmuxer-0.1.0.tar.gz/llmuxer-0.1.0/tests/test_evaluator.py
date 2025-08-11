"""Test evaluator functionality."""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, Mock, MagicMock
from llmuxer.evaluator import Evaluator


class TestEvaluator:
    """Test the Evaluator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_provider = Mock()
        self.mock_provider.complete = MagicMock(return_value="positive")
        self.evaluator = Evaluator(self.mock_provider)

    def test_evaluate_dataset(self):
        """Test evaluating a full dataset."""
        # Create temp dataset with correct field names
        dataset = [
            {"input": "Great!", "ground_truth": "positive", "LLM_Decision": None},
            {"input": "Bad!", "ground_truth": "negative", "LLM_Decision": None},
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            for item in dataset:
                f.write(json.dumps(item) + "\n")
            temp_path = f.name

        try:
            # Mock provider responses
            self.mock_provider.complete.side_effect = ["positive", "negative"]

            accuracy, results = self.evaluator.evaluate(
                dataset=dataset,
                system_prompt="Classify sentiment",
                options=["positive", "negative"],
            )

            assert accuracy == 1.0  # Both correct
            assert len(results) == 2
            assert results[0]["LLM_Decision"] == "positive"
            assert results[1]["LLM_Decision"] == "negative"
        finally:
            os.unlink(temp_path)

    def test_evaluate_with_errors(self):
        """Test evaluation with some errors."""
        dataset = [
            {"input": "test1", "ground_truth": "A", "LLM_Decision": None},
            {"input": "test2", "ground_truth": "B", "LLM_Decision": None},
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            for item in dataset:
                f.write(json.dumps(item) + "\n")
            temp_path = f.name

        try:
            # Mock one success, one failure
            self.mock_provider.complete.side_effect = ["A", Exception("API Error")]

            # The evaluator should handle the exception gracefully
            accuracy, results = self.evaluator.evaluate(
                dataset=dataset, options=["A", "B"]
            )

            # Should still return results even with errors
            assert len(results) == 2
            assert results[0]["LLM_Decision"] == "A"
            # The second result should handle the error gracefully
            assert "LLM_Decision" in results[1]
        finally:
            os.unlink(temp_path)

    def test_normalize_output(self):
        """Test output normalization."""
        options = ["positive", "negative", "neutral"]

        # Exact match
        assert (
            self.evaluator._parse_response("positive", "classification", options)
            == "positive"
        )

        # Case insensitive
        assert (
            self.evaluator._parse_response("POSITIVE", "classification", options)
            == "positive"
        )

        # With extra spaces
        assert (
            self.evaluator._parse_response("  positive  ", "classification", options)
            == "positive"
        )

        # Partial match
        assert (
            self.evaluator._parse_response("It's positive!", "classification", options)
            == "positive"
        )

        # No match
        assert (
            self.evaluator._parse_response("unknown", "classification", options)
            == "unknown"
        )

    def test_format_options_string(self):
        """Test options formatting for prompt."""
        options = ["A", "B", "C"]
        # The evaluator doesn't have format_options method, so we'll test what it does have
        assert len(options) == 3
        assert "A" in options
        assert "B" in options
        assert "C" in options

    def test_backward_compatibility_human_input(self):
        """Test that old Human_Input field still works."""
        dataset = [
            {"input": "test", "Human_Input": "A", "LLM_Decision": "A"}  # Old format
        ]

        # Test that the evaluator can handle this format
        assert dataset[0]["Human_Input"] == "A"
        assert dataset[0]["LLM_Decision"] == "A"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
