"""Simple API for LLMux - Optimize your LLM costs automatically."""

from typing import Optional, Dict, Any, List
from .selector import Selector
from .provider import get_provider
import json
import os
import requests


def fetch_openrouter_models() -> Dict[str, Dict]:
    """Fetch live model pricing from OpenRouter API."""
    try:
        response = requests.get("https://openrouter.ai/api/v1/models")
        response.raise_for_status()
        models_data = response.json()
        
        # Convert to our format
        model_costs = {}
        for model in models_data.get('data', []):
            model_id = model['id']
            # Skip special models that have negative or invalid pricing
            if model_id in ['openrouter/auto', 'openrouter/best']:
                continue
                
            # Convert price per token to price per million tokens
            pricing = model.get('pricing', {})
            if pricing and 'prompt' in pricing and 'completion' in pricing:
                prompt_cost = float(pricing.get('prompt', 0)) * 1_000_000
                completion_cost = float(pricing.get('completion', 0)) * 1_000_000
                
                # Skip if costs are negative or unrealistic
                if prompt_cost >= 0 and completion_cost >= 0:
                    model_costs[model_id] = {
                        "input": prompt_cost,
                        "output": completion_cost,
                        "context_length": model.get('context_length', 0),
                        "top_provider": model.get('top_provider', {}).get('name', 'Unknown')
                    }
        
        return model_costs
    except Exception as e:
        # Fallback pricing - silent error
        return {
            "openai/gpt-4o": {"input": 2.50, "output": 10.00},
            "openai/gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "openai/gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
            "anthropic/claude-3-haiku": {"input": 0.25, "output": 1.25},
            "google/gemini-flash-1.5": {"input": 0.075, "output": 0.30},
            "meta-llama/llama-3.1-8b-instruct": {"input": 0.06, "output": 0.06},
            "mistralai/mistral-7b-instruct": {"input": 0.06, "output": 0.06},
        }


def estimate_tokens(text: str) -> int:
    """Rough estimate of tokens (1 token ≈ 4 characters)."""
    return len(text) // 4


def calculate_experiment_cost(models: List[Dict], dataset_path: str, prompt: str, model_costs: Dict, baseline_model: str = None) -> Dict:
    """Calculate estimated cost for running the experiment."""
    # Load dataset to count items
    with open(dataset_path, 'r') as f:
        dataset = []
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                dataset.append(json.loads(line))
    
    num_items = len(dataset)
    
    # Estimate tokens per item (prompt + input + response)
    avg_input_length = sum(len(item['input']) for item in dataset[:5]) // min(5, len(dataset))
    tokens_per_input = estimate_tokens(prompt) + estimate_tokens(dataset[0]['input'] if dataset else "")
    tokens_per_output = 10  # Assuming short responses
    
    total_cost = 0
    model_costs_breakdown = []
    baseline_cost_info = None
    
    # Map common model names to their OpenRouter equivalents
    model_mapping = {
        'gpt-4': 'openai/gpt-4',
        'gpt-4o': 'openai/gpt-4o',
        'gpt-3.5-turbo': 'openai/gpt-3.5-turbo',
        'claude-3-haiku': 'anthropic/claude-3-haiku'
    }
    
    # Calculate baseline cost if provided
    if baseline_model:
        mapped_baseline = model_mapping.get(baseline_model, baseline_model)
        if mapped_baseline in model_costs:
            baseline_pricing = model_costs[mapped_baseline]
            baseline_input_cost = (tokens_per_input * num_items * baseline_pricing['input']) / 1_000_000
            baseline_output_cost = (tokens_per_output * num_items * baseline_pricing['output']) / 1_000_000
            baseline_total_cost = baseline_input_cost + baseline_output_cost
            baseline_cost_info = {
                'model': baseline_model,  # Show original user-provided name
                'mapped_model': mapped_baseline,  # Show mapped name for reference
                'input_tokens': tokens_per_input * num_items,
                'output_tokens': tokens_per_output * num_items,
                'input_cost': baseline_input_cost,
                'output_cost': baseline_output_cost,
                'total_cost': baseline_total_cost
            }
    
    for model_config in models:
        model_name = model_config['model']
        if model_name in model_costs:
            pricing = model_costs[model_name]
            input_cost = (tokens_per_input * num_items * pricing['input']) / 1_000_000
            output_cost = (tokens_per_output * num_items * pricing['output']) / 1_000_000
            model_total = input_cost + output_cost
            total_cost += model_total
            
            model_costs_breakdown.append({
                'model': model_name,
                'input_tokens': tokens_per_input * num_items,
                'output_tokens': tokens_per_output * num_items,
                'cost': model_total,
                'input_cost': input_cost,
                'output_cost': output_cost
            })
    
    return {
        'total_cost': total_cost,
        'num_models': len(models),
        'num_items': num_items,
        'breakdown': model_costs_breakdown,
        'baseline_cost': baseline_cost_info,
        'tokens_per_input': tokens_per_input,
        'tokens_per_output': tokens_per_output
    }


def optimize_cost(
    baseline: Optional[str] = None,
    dataset: Optional[str] = None,
    task: Optional[str] = None,
    options: Optional[List] = None,
    success_criteria: Optional[List] = None,
    extract: Optional[str] = None,
    examples: Optional[List[Dict]] = None,
    prompt: Optional[str] = None,
    input_column: str = "input",
    ground_truth_column: str = "ground_truth",
    min_accuracy: float = 0.9,
    sample_size: Optional[float] = None,  # Percentage of dataset to use (0.0-1.0)
    # Legacy support
    base_model: Optional[str] = None,
    golden_dataset: Optional[str] = None,
    output_format: Optional[str] = None,
    output_classes: Optional[List] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Find the most cost-effective model for your task.
    
    Args:
        baseline: Reference model to beat (e.g. "gpt-4", "claude-3")
        prompt: System prompt or task description
        dataset: Path to dataset file (.jsonl, .csv) or HuggingFace dataset name
        examples: Direct list of examples [{"input": "...", "ground_truth": "..."}]
        input_column: Column name for inputs (default: "input")
        ground_truth_column: Column name for ground truth (default: "ground_truth")
        min_accuracy: Minimum acceptable accuracy (0.9 = 90%)
        output_format: Format specification ("classification", "binary", "numeric", "text")
        output_classes: List of valid output values for classification tasks
    
    Returns:
        Dict with 'model', 'provider', 'cost_savings', 'accuracy', etc.
    
    Examples:
        # Classification with explicit classes
        result = llmux.optimize_cost(
            baseline="gpt-4",
            dataset="reviews.csv",
            output_classes=["positive", "negative", "neutral"]
        )
        
        # Binary classification  
        result = llmux.optimize_cost(
            baseline="gpt-4",
            dataset="spam.jsonl",
            output_format="binary"  # Expects 0/1 or True/False
        )
        
        # Auto-detect from dataset
        result = llmux.optimize_cost("gpt-4", dataset="test.jsonl")
    """
    
    # Handle legacy API
    if base_model and not baseline:
        baseline = base_model
    if golden_dataset and not dataset:
        dataset = golden_dataset
    if 'accuracy_threshold' in kwargs:
        min_accuracy = kwargs['accuracy_threshold']
    
    # Handle new API aliases
    if success_criteria and not options:
        options = success_criteria
    if output_classes and not options:
        options = output_classes
    if output_format and not task:
        task = output_format
    
    # Load and standardize dataset
    dataset_path, processed_examples = _prepare_dataset(dataset, examples, input_column, ground_truth_column, sample_size)
    
    # Auto-detect task type and options if not specified
    if not task and not options:
        task, detected_options = _detect_task_and_options(processed_examples)
        if not options:
            options = detected_options
    elif not options and task:
        _, options = _detect_task_and_options(processed_examples, prefer_task=task)
    
    # Build task-specific prompt
    prompt = _build_task_prompt(prompt, task, options, extract)
    
    # Fetch live pricing from OpenRouter (silent)
    model_costs = fetch_openrouter_models()
    
    # Calculate baseline accuracy from dataset
    baseline_accuracy = _calculate_baseline_accuracy_from_data(processed_examples)
    
    # Select models to test (only cheaper than baseline)
    test_models = _get_test_models(baseline, model_costs)
    
    # Calculate and display cost estimates
    experiment_cost = calculate_experiment_cost(test_models, dataset_path, prompt or "", model_costs, baseline)
    
    # Display cost estimation table with baseline accuracy
    _display_cost_tables(baseline, model_costs, experiment_cost, baseline_accuracy)
    
    # Run evaluation with smart stopping
    selector = Selector(test_models)
    results = selector.run_evaluation(dataset_path, prompt or "", task, options, model_costs, min_accuracy)
    
    # Find best cost-optimized model
    best = _select_cost_optimized(results, baseline, min_accuracy, model_costs)
    
    # Display final summary table
    _display_final_summary_table(baseline, results, experiment_cost, baseline_accuracy, model_costs)
    
    return best


def _prepare_dataset(dataset_path: Optional[str], examples: Optional[List[Dict]], 
                    input_col: str, ground_truth_col: str, sample_size: Optional[float] = None) -> tuple:
    """Prepare dataset from various input formats."""
    import tempfile
    import os
    import random
    
    if examples:
        # Direct examples provided
        # Apply sampling if specified
        if sample_size and 0 < sample_size < 1.0:
            num_samples = int(len(examples) * sample_size)
            examples = random.sample(examples, min(num_samples, len(examples)))
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)
        for example in examples:
            # Standardize format
            standardized = {
                'input': example.get(input_col, example.get('input', example.get('text', ''))),
                'label': example.get(ground_truth_col, example.get('ground_truth', example.get('label', None))),
                'LLM_Decision': None
            }
            temp_file.write(json.dumps(standardized) + '\n')
        temp_file.close()
        return temp_file.name, examples
    
    elif dataset_path:
        processed_examples = _detect_and_load_dataset(dataset_path, input_col, ground_truth_col)
        
        # Apply sampling if specified
        if sample_size and 0 < sample_size < 1.0:
            num_samples = int(len(processed_examples) * sample_size)
            processed_examples = random.sample(processed_examples, min(num_samples, len(processed_examples)))
        
        # Create a temp file with sampled data
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)
        for example in processed_examples:
            # Convert to expected format
            standardized = {
                'input': example['input'],
                'label': example.get('ground_truth') or example.get('label'),
                'LLM_Decision': None
            }
            temp_file.write(json.dumps(standardized) + '\n')
        temp_file.close()
        return temp_file.name, processed_examples
    
    else:
        raise ValueError("Must provide either 'dataset' path or 'examples' list")


def _detect_and_load_dataset(file_path: str, input_col: str, ground_truth_col: str) -> List[Dict]:
    """Auto-detect and load dataset from local files only."""
    import os
    
    # Check if file exists locally
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found: {file_path}. Please provide a valid .jsonl or .csv file path.")
    
    # Auto-detect format and load
    if file_path.endswith('.jsonl'):
        return _load_jsonl_dataset(file_path, input_col, ground_truth_col)
    elif file_path.endswith('.csv'):
        return _load_csv_dataset(file_path, input_col, ground_truth_col)
    else:
        # Try JSONL first, then CSV
        try:
            return _load_jsonl_dataset(file_path, input_col, ground_truth_col)
        except:
            return _load_csv_dataset(file_path, input_col, ground_truth_col)


def _load_jsonl_dataset(file_path: str, input_col: str, ground_truth_col: str) -> List[Dict]:
    """Load and standardize JSONL dataset."""
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                item = json.loads(line)
                # Try multiple common field names
                input_text = (item.get(input_col) or item.get('input') or 
                             item.get('text') or item.get('prompt') or '')
                ground_truth = (item.get(ground_truth_col) or item.get('ground_truth') or
                               item.get('label') or item.get('Human_Input'))  # Keep backward compatibility
                
                data.append({
                    'input': input_text,
                    'ground_truth': ground_truth,
                    'original': item
                })
    return data


def _load_csv_dataset(file_path: str, input_col: str, ground_truth_col: str) -> List[Dict]:
    """Load and standardize CSV dataset."""
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("pandas required for CSV support: pip install pandas")
    
    df = pd.read_csv(file_path)
    
    # Auto-detect column names if defaults don't exist
    if input_col not in df.columns:
        for possible in ['input', 'text', 'prompt', 'question']:
            if possible in df.columns:
                input_col = possible
                break
    
    if ground_truth_col not in df.columns:
        for possible in ['ground_truth', 'label', 'answer', 'output']:
            if possible in df.columns:
                ground_truth_col = possible
                break
    
    data = []
    for _, row in df.iterrows():
        data.append({
            'input': str(row.get(input_col, '')),
            'ground_truth': row.get(ground_truth_col),
            'original': row.to_dict()
        })
    
    return data




def _calculate_baseline_accuracy_from_data(processed_examples: List[Dict]) -> Optional[float]:
    """Calculate baseline accuracy from processed examples."""
    correct = 0
    total = 0
    
    for example in processed_examples:
        # Look for existing model decision vs ground truth
        original = example.get('original', {})
        llm_decision = original.get('LLM_Decision')
        ground_truth = example.get('ground_truth')
        
        if llm_decision is not None and ground_truth is not None:
            total += 1
            if llm_decision == ground_truth:
                correct += 1
    
    return correct / total if total > 0 else None


def _calculate_baseline_accuracy(dataset_path: str) -> Optional[float]:
    """Calculate baseline accuracy from existing LLM_Decision vs label/Human_Input in golden dataset."""
    try:
        with open(dataset_path, 'r') as f:
            dataset = []
            for line in f:
                line = line.strip()
                if line:
                    dataset.append(json.loads(line))
        
        correct = 0
        total = 0
        for item in dataset:
            ground_truth = item.get('label') or item.get('Human_Input')  # Support both formats
            if item.get('LLM_Decision') is not None and ground_truth is not None:
                total += 1
                if item['LLM_Decision'] == ground_truth:
                    correct += 1
        
        return correct / total if total > 0 else None
    except Exception:
        return None


def _display_cost_tables(base_model: Optional[str], model_costs: Dict, experiment_cost: Dict, baseline_accuracy: Optional[float]):
    """Display cost estimation info with baseline and experiment costs."""
    print("\n" + "+" + "-"*78 + "+")
    print("| " + " COST ESTIMATION".center(76) + " |")
    print("+" + "-"*78 + "+")
    
    # Baseline accuracy
    if baseline_accuracy is not None:
        accuracy_text = f"BASELINE ACCURACY: {baseline_accuracy:.1%} (from existing data)"
        print(f"| {accuracy_text:<76} |")
    
    # Baseline model cost information
    baseline_cost = experiment_cost.get('baseline_cost')
    if baseline_cost:
        print(f"| {'BASE MODEL: ' + baseline_cost['model']:<76} |")
        input_tokens = baseline_cost['input_tokens']
        output_tokens = baseline_cost['output_tokens']
        input_cost = baseline_cost['input_cost']
        output_cost = baseline_cost['output_cost']
        total_cost = baseline_cost['total_cost']
        
        print(f"| {f'Input tokens: {input_tokens:,} - ${input_cost:.4f}':<76} |")
        print(f"| {f'Output tokens: {output_tokens:,} - ${output_cost:.4f}':<76} |")
        print(f"| {f'Total baseline cost: ${total_cost:.4f}':<76} |")
        print(f"| {'':<76} |")
    
    # Models to test info
    test_info = f"Testing {len(experiment_cost['breakdown'])} models cheaper than {base_model or 'baseline'}"
    print(f"| {test_info:<76} |")
    print("+" + "-"*78 + "+")
    
    # Experiment cost breakdown
    if experiment_cost['breakdown']:
        print()
        print("EXPERIMENT COST BREAKDOWN:")
        print("-" * 90)
        for model_info in experiment_cost['breakdown']:
            model_name = model_info['model'].split('/')[-1]
            input_tokens = model_info['input_tokens']
            output_tokens = model_info['output_tokens']
            input_cost = model_info['input_cost']
            output_cost = model_info['output_cost']
            total_cost = model_info['cost']
            
            print(f"{model_name}:")
            print(f"  Input tokens: {input_tokens:,} - ${input_cost:.4f}")
            print(f"  Output tokens: {output_tokens:,} - ${output_cost:.4f}")
            print(f"  Total cost: ${total_cost:.4f}")
            print()
    
    # Table header will be shown by the selector


def _display_final_summary_table(baseline_model: str, results: Dict, experiment_cost: Dict, baseline_accuracy: Optional[float], model_costs: Dict):
    """Display final summary table comparing baseline model with all experiment results."""
    print("\n" + "+" + "-"*90 + "+")
    print("| " + " FINAL RESULTS SUMMARY".center(88) + " |")
    print("+" + "-"*90 + "+")
    
    # Table header
    print(f"| {'Model':<25} | {'Accuracy':<10} | {'Cost/M tokens':<13} | {'Input Cost':<11} | {'Output Cost':<12} |")
    print("+" + "-"*27 + "+" + "-"*12 + "+" + "-"*15 + "+" + "-"*13 + "+" + "-"*14 + "+")
    
    # Always show baseline if we have the info
    baseline_cost = experiment_cost.get('baseline_cost')
    if baseline_cost:
        model_mapping = {
            'gpt-4': 'openai/gpt-4',
            'gpt-4o': 'openai/gpt-4o',
            'gpt-3.5-turbo': 'openai/gpt-3.5-turbo',
            'claude-3-haiku': 'anthropic/claude-3-haiku'
        }
        mapped_baseline = model_mapping.get(baseline_model, baseline_model)
        
        if mapped_baseline in model_costs:
            baseline_pricing = model_costs[mapped_baseline]
            total_cost_per_m = baseline_pricing['input'] + baseline_pricing['output']
            input_cost_per_m = baseline_pricing['input']
            output_cost_per_m = baseline_pricing['output']
            
            accuracy_display = f'{baseline_accuracy:.1%}' if baseline_accuracy is not None else 'N/A'
            print(f"| {f'{baseline_model} (baseline)':<25} | {accuracy_display:<10} | ${total_cost_per_m:<12.3f} | ${input_cost_per_m:<10.3f} | ${output_cost_per_m:<11.3f} |")
    
    # Add experiment results
    experiment_rows_added = 0
    for model_name, result in results.items():
        model = result['config']['model']
        short_name = model.split('/')[-1] if '/' in model else model
        
        if 'error' not in result and result.get('accuracy') is not None:
            accuracy = result['accuracy']
            
            if model in model_costs:
                pricing = model_costs[model]
                total_cost_per_m = pricing['input'] + pricing['output']
                input_cost_per_m = pricing['input']
                output_cost_per_m = pricing['output']
                
                print(f"| {short_name:<25} | {f'{accuracy:.1%}':<10} | ${total_cost_per_m:<12.3f} | ${input_cost_per_m:<10.3f} | ${output_cost_per_m:<11.3f} |")
                experiment_rows_added += 1
        else:
            # Show models that failed
            if model in model_costs:
                pricing = model_costs[model]
                total_cost_per_m = pricing['input'] + pricing['output']
                input_cost_per_m = pricing['input']
                output_cost_per_m = pricing['output']
                
                print(f"| {short_name:<25} | {'ERROR':<10} | ${total_cost_per_m:<12.3f} | ${input_cost_per_m:<10.3f} | ${output_cost_per_m:<11.3f} |")
                experiment_rows_added += 1
    
    if experiment_rows_added == 0:
        print(f"| {'No experiment results':<25} | {'-':<10} | {'-':<13} | {'-':<11} | {'-':<12} |")
    
    print("+" + "-"*90 + "+")


def optimize_speed(
    prompt: str,
    golden_dataset: str,
    base_model: Optional[str] = None,
    accuracy_threshold: float = 0.9
) -> Dict[str, Any]:
    """
    Find the fastest model that maintains quality.
    
    Similar to optimize_cost but prioritizes latency over cost.
    """
    # Fetch live pricing from OpenRouter
    model_costs = fetch_openrouter_models()
    test_models = _get_test_models(base_model, model_costs)
    selector = Selector(test_models)
    results = selector.run_evaluation(golden_dataset, prompt)
    
    # Find fastest acceptable model
    best = _select_speed_optimized(results, base_model, accuracy_threshold, model_costs)
    return best


def _get_test_models(base_model: Optional[str], model_costs: Dict) -> List[Dict]:
    """Get list of models to test from curated universe."""
    
    # Define our curated model universe
    MODEL_UNIVERSE = {
        # OpenAI - 2 models
        "openai/gpt-4o-mini",
        "openai/gpt-3.5-turbo",
        
        # Anthropic - 2 models  
        "anthropic/claude-3-haiku",
        "anthropic/claude-3-sonnet",
        
        # Google - 3 models
        "google/gemini-1.5-flash-8b", 
        "google/gemini-1.5-flash",
        "google/gemini-1.5-pro",
        
        # Qwen - 3 models
        "alibaba/qwen-2.5-7b-instruct",
        "alibaba/qwen-2.5-14b-instruct", 
        "alibaba/qwen-2.5-72b-instruct",
        
        # DeepSeek - 3 models
        "deepseek/deepseek-chat",
        "deepseek/deepseek-coder", 
        "deepseek/deepseek-v2.5",
        
        # Mistral - 3 models
        "mistralai/mistral-7b-instruct",
        "mistralai/mixtral-8x7b-instruct",
        "mistralai/mistral-large",
        
        # Meta (bonus - too good to exclude)
        "meta-llama/llama-3.1-8b-instruct",
        "meta-llama/llama-3.1-70b-instruct"
    }
    
    # Map common model names to their OpenRouter equivalents
    model_mapping = {
        'gpt-4': 'openai/gpt-4',
        'gpt-4o': 'openai/gpt-4o',
        'gpt-3.5-turbo': 'openai/gpt-3.5-turbo',
        'claude-3-haiku': 'anthropic/claude-3-haiku'
    }
    
    # Use mapped model name if available
    mapped_base_model = model_mapping.get(base_model, base_model) if base_model else None
    
    # Filter model universe to only include models that exist in model_costs
    available_models = {}
    for model_id in MODEL_UNIVERSE:
        if model_id in model_costs:
            available_models[model_id] = model_costs[model_id]
    
    models = []
    
    if mapped_base_model and mapped_base_model in model_costs:
        base_cost = model_costs[mapped_base_model]["input"] + model_costs[mapped_base_model]["output"]
        
        # Test only models from our universe that are cheaper than base model
        for model_id, pricing in available_models.items():
            model_cost = pricing["input"] + pricing["output"]
            if model_cost < base_cost:  # Must be cheaper than base
                models.append({"provider": "openrouter", "model": model_id})
        
        # Sort by cost (most expensive first for smart stopping to work)
        models.sort(key=lambda x: available_models[x['model']]['input'] + available_models[x['model']]['output'], reverse=True)
        
        # If no cheaper models found, show message
        if not models:
            print(f"\nNo models in universe cheaper than {base_model}")
            print("Testing cheapest available models from universe...")
            # Get all models from universe sorted by cost
            all_models = [(model_id, pricing["input"] + pricing["output"]) 
                         for model_id, pricing in available_models.items()]
            all_models.sort(key=lambda x: x[1])
            models = [{"provider": "openrouter", "model": model_id} 
                     for model_id, _ in all_models[:5]]
    else:
        # No baseline or baseline not in costs - use cheapest from universe
        all_models = [(model_id, pricing["input"] + pricing["output"]) 
                     for model_id, pricing in available_models.items()]
        all_models.sort(key=lambda x: x[1])
        models = [{"provider": "openrouter", "model": model_id} 
                 for model_id, _ in all_models[:5]]
    
    return models


def _select_cost_optimized(results: Dict, base_model: Optional[str], threshold: float, model_costs: Dict) -> Dict:
    """Select best model based on cost and accuracy."""
    best_score = -1
    best_model = None
    
    for model_name, result in results.items():
        if 'error' in result or result.get('accuracy') is None:
            continue
            
        accuracy = result['accuracy']
        model = result['config']['model']
        
        # Calculate cost score (lower is better)
        if model in model_costs:
            cost = model_costs[model]["input"] + model_costs[model]["output"]
            # Score = accuracy / cost (higher accuracy, lower cost = better)
            score = accuracy / (cost + 0.01)  # Add small value to avoid division by zero
            
            if score > best_score and accuracy >= threshold:
                best_score = score
                best_model = {
                    'model': model,
                    'provider': 'openrouter',
                    'accuracy': accuracy,
                    'cost_per_million': cost,
                    'time': result['time'],
                    'cost_savings': None  # Calculate if base model provided
                }
    
    # Calculate savings vs base model
    if best_model and base_model:
        # Map common model names to their OpenRouter equivalents
        model_mapping = {
            'gpt-4': 'openai/gpt-4',
            'gpt-4o': 'openai/gpt-4o',
            'gpt-3.5-turbo': 'openai/gpt-3.5-turbo',
            'claude-3-haiku': 'anthropic/claude-3-haiku'
        }
        mapped_base_model = model_mapping.get(base_model, base_model)
        
        if mapped_base_model in model_costs:
            base_cost = model_costs[mapped_base_model]["input"] + model_costs[mapped_base_model]["output"]
            best_model['cost_savings'] = 1 - (best_model['cost_per_million'] / base_cost)
    
    if not best_model:
        # Find the best performing model even if below threshold for informational purposes
        best_performer = None
        best_accuracy = -1
        for model_name, result in results.items():
            if 'error' not in result and result.get('accuracy') is not None:
                if result['accuracy'] > best_accuracy:
                    best_accuracy = result['accuracy']
                    model = result['config']['model']
                    best_performer = {
                        'model': model,
                        'accuracy': result['accuracy'],
                        'cost_per_million': model_costs[model]["input"] + model_costs[model]["output"],
                        'below_threshold': True,
                        'threshold': threshold
                    }
        
        if best_performer:
            print(f"\n⚠️  WARNING: No models met the {threshold:.0%} accuracy threshold")
            print(f"   Best model achieved: {best_performer['accuracy']:.1%}")
            print(f"   Consider lowering min_accuracy or using a better baseline")
            return best_performer
        
        return {'error': 'No suitable model found', 'threshold': threshold}
    
    return best_model


def _detect_task_and_options(examples: List[Dict], prefer_task: Optional[str] = None) -> tuple:
    """Auto-detect task type and valid options from dataset."""
    if not examples:
        return None, None
    
    # Collect all ground truth values
    ground_truths = []
    for example in examples:
        gt = example.get('ground_truth')
        if gt is not None:
            ground_truths.append(gt)
    
    if not ground_truths:
        return None, None
    
    # Get unique values
    unique_values = set(ground_truths)
    
    # If user prefers a specific task type, validate it
    if prefer_task == "binary":
        if unique_values <= {0, 1} or unique_values <= {True, False} or unique_values <= {"0", "1"} or unique_values <= {"true", "false"}:
            return "binary", sorted(list(unique_values))
    elif prefer_task == "classification":
        if len(unique_values) <= 50:
            return "classification", sorted(list(unique_values))
    elif prefer_task == "extraction":
        return "extraction", None
    elif prefer_task == "generation":
        return "generation", None
    
    # Auto-detect task type
    # Binary detection
    if (unique_values <= {0, 1} or unique_values <= {True, False} or 
        unique_values <= {"0", "1"} or unique_values <= {"true", "false"} or
        unique_values <= {"yes", "no"}):
        return "binary", sorted(list(unique_values))
    
    # Classification detection (reasonable number of classes)
    if len(unique_values) <= 20:
        return "classification", sorted(list(unique_values))
    
    # Default to generation for diverse outputs
    return "generation", None


def _build_task_prompt(user_prompt: Optional[str], task: Optional[str], options: Optional[List], extract: Optional[str]) -> str:
    """Build task-specific prompt with clear success criteria."""
    
    # Start with user prompt or default
    base_prompt = user_prompt or "Analyze the input and provide the appropriate response."
    
    # Add task-specific instructions
    task_instructions = ""
    
    if task == "classification" and options:
        options_str = ", ".join(str(opt) for opt in options)
        task_instructions = f"\n\nRespond with exactly one of: {options_str}"
        
    elif task == "binary":
        if options:
            options_str = ", ".join(str(opt) for opt in options)
            task_instructions = f"\n\nRespond with exactly one of: {options_str}"
        else:
            task_instructions = "\n\nRespond with exactly one of: 0, 1"
            
    elif task == "extraction" and extract:
        task_instructions = f"\n\nExtract only the {extract} from the input. If none found, respond with 'None'."
        
    elif options:  # Generic case with options
        options_str = ", ".join(str(opt) for opt in options)
        task_instructions = f"\n\nRespond with exactly one of: {options_str}"
    
    return base_prompt + task_instructions


def _detect_output_format(examples: List[Dict]) -> tuple:
    """Legacy function - use _detect_task_and_options instead."""
    return _detect_task_and_options(examples)


def _build_prompt_with_format(prompt: Optional[str], output_format: Optional[str], output_classes: Optional[List]) -> str:
    """Legacy function - use _build_task_prompt instead."""
    return _build_task_prompt(prompt, output_format, output_classes, None)


def _select_speed_optimized(results: Dict, base_model: Optional[str], threshold: float, model_costs: Dict) -> Dict:
    """Select best model based on speed and accuracy."""
    best_time = float('inf')
    best_model = None
    
    for model_name, result in results.items():
        if 'error' in result or result.get('accuracy') is None:
            continue
            
        accuracy = result['accuracy']
        
        if accuracy >= threshold and result['time'] < best_time:
            best_time = result['time']
            model = result['config']['model']
            best_model = {
                'model': model,
                'provider': 'openrouter',
                'accuracy': accuracy,
                'latency': result['time'],
                'cost_per_million': model_costs.get(model, {}).get('input', 0) + 
                                   model_costs.get(model, {}).get('output', 0)
            }
    
    return best_model or {'error': 'No suitable model found'}