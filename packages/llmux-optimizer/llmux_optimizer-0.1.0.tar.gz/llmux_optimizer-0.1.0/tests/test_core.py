"""Test core functionality of llmux."""

import pytest
from unittest.mock import Mock, patch
import llmux


def test_optimize_cost_basic():
    """Test basic optimize_cost functionality with examples."""
    
    # Sample classification data
    examples = [
        {"input": "This is great!", "ground_truth": "positive"},
        {"input": "This is terrible!", "ground_truth": "negative"},
        {"input": "This is okay", "ground_truth": "neutral"},
    ]
    
    # Mock the actual API calls to avoid real requests in tests
    with patch('llmux.api.fetch_openrouter_models') as mock_fetch:
        mock_fetch.return_value = {
            "openai/gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
            "meta-llama/llama-3.1-8b": {"input": 0.015, "output": 0.02},
        }
        
        with patch('llmux.selector.Selector.run_evaluation') as mock_eval:
            mock_eval.return_value = {
                "openrouter/meta-llama/llama-3.1-8b": {
                    "accuracy": 0.85,
                    "time": 10.5,
                    "config": {"provider": "openrouter", "model": "meta-llama/llama-3.1-8b"}
                }
            }
            
            # This should not raise an exception
            result = llmux.optimize_cost(
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
    
    examples = [{"input": "test", "ground_truth": "label"}]
    
    # This should handle gracefully - either return error or work with fallback
    result = llmux.optimize_cost(
        baseline="invalid-model-name",
        examples=examples
    )
    
    assert isinstance(result, dict)
    # Should either succeed with fallback or return error
    assert "model" in result or "error" in result


def test_empty_dataset():
    """Test handling of empty dataset."""
    
    with pytest.raises(ValueError):
        llmux.optimize_cost(
            baseline="gpt-4",
            examples=[],  # Empty dataset
            min_accuracy=0.8
        )


def test_version():
    """Test version is accessible."""
    assert hasattr(llmux, '__version__')
    assert isinstance(llmux.__version__, str)
    assert llmux.version() == llmux.__version__


def test_imports():
    """Test all expected functions are importable."""
    
    # Test main function
    assert hasattr(llmux, 'optimize_cost')
    assert callable(llmux.optimize_cost)
    
    # Test supporting classes
    assert hasattr(llmux, 'Provider')
    assert hasattr(llmux, 'Evaluator')
    assert hasattr(llmux, 'Selector')
    assert hasattr(llmux, 'get_provider')


if __name__ == "__main__":
    pytest.main([__file__])