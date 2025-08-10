"""Selector module for choosing best performing model."""

import time
import threading
from typing import List, Dict, Any, Optional, Tuple
from .provider import Provider, get_provider
from .evaluator import Evaluator


class Selector:
    """Selects best model based on evaluation results."""
    
    def __init__(self, models: List[Dict[str, Any]]):
        """Initialize with list of model configs.
        
        Each config should have:
        - provider: 'openai' or 'anthropic'
        - model: model name
        - any other provider-specific kwargs
        """
        self.models = models
        self.results = {}
        
    def run_evaluation(self, dataset_path: str, system_prompt: str = "", task: Optional[str] = None, options: Optional[List] = None, model_costs: Optional[Dict] = None, min_accuracy: float = 0.0) -> Dict[str, Any]:
        """Run evaluation on all models with smart stopping for model families."""
        
        # Define model families (larger to smaller) for your universe
        model_families = {
            'openai': ['gpt-4o-mini', 'gpt-3.5-turbo'],
            'anthropic': ['claude-3-sonnet', 'claude-3-haiku'],
            'google': ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-1.5-flash-8b'],
            'qwen': ['qwen-2.5-72b', 'qwen-2.5-14b', 'qwen-2.5-7b'],
            'deepseek': ['deepseek-v2.5', 'deepseek-coder', 'deepseek-chat'],
            'mistral': ['mistral-large', 'mixtral-8x7b', 'mistral-7b'],
            'llama': ['llama-3.1-70b', 'llama-3.1-8b']
        }
        
        # Track failed families
        failed_families = set()
        
        for i, config in enumerate(self.models):
            config_copy = config.copy()
            provider_name = config_copy.pop('provider')
            model_name = config_copy.get('model', 'unknown')
            short_name = model_name.split('/')[-1] if '/' in model_name else model_name
            
            # Check if this model belongs to a failed family
            skip_model = False
            for family, models in model_families.items():
                if family in failed_families and any(m in short_name for m in models):
                    print(f"  {short_name}: Skipped - larger model in family failed threshold")
                    self.results[f"{provider_name}/{model_name}"] = {
                        'skipped': True,
                        'reason': 'larger_model_failed',
                        'config': {'provider': provider_name, **config_copy}
                    }
                    skip_model = True
                    break
            
            if skip_model:
                continue
            
            print(f"  {short_name}: Testing... - Running")
            
            try:
                provider = get_provider(provider_name, **config_copy)
                evaluator = Evaluator(provider)
                dataset = evaluator.load_dataset(dataset_path)
                
                start_time = time.time()
                accuracy, results = evaluator.evaluate(dataset, system_prompt, task, options)
                elapsed = time.time() - start_time
                
                self.results[f"{provider_name}/{model_name}"] = {
                    'accuracy': accuracy,
                    'time': elapsed,
                    'results': results,
                    'config': {'provider': provider_name, **config_copy}
                }
                
                if accuracy is not None:
                    print(f"     {short_name}: {accuracy:.1%} - Done ({elapsed:.1f}s)")
                    
                    # Check if model failed threshold
                    if accuracy < min_accuracy:
                        # Mark this model's family as failed
                        for family, models in model_families.items():
                            if any(m in short_name for m in models):
                                failed_families.add(family)
                                print(f"     Note: {family} family marked as below threshold")
                                break
                else:
                    print(f"     {short_name}: No labels - Done ({elapsed:.1f}s)")
                    
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg:
                    print(f"     {short_name}: Rate limited - Skipped")
                elif "404" in error_msg:
                    print(f"     {short_name}: Not found - Skipped")
                else:
                    print(f"     {short_name}: Error - Failed")
                
                self.results[f"{provider_name}/{model_name}"] = {
                    'error': str(e),
                    'config': {'provider': provider_name, **config_copy}
                }
        
        return self.results
    
    def _create_progress_table(self, model_costs: Optional[Dict] = None):
        """Create the initial progress table."""
        print("\n" + "+" + "-"*30 + "+" + "-"*15 + "+" + "-"*15 + "+" + "-"*16 + "+")
        print(f"| {'Model':<28} | {'Cost/M tokens':<13} | {'Accuracy':<13} | {'Status':<14} |")
        print("+" + "-"*30 + "+" + "-"*15 + "+" + "-"*15 + "+" + "-"*16 + "+")
        
        # Pre-populate rows for each model
        for config in self.models:
            model_name = config.get('model', 'unknown')
            short_name = model_name.split('/')[-1] if '/' in model_name else model_name
            
            # Get cost info if available
            cost_display = '$--.---'
            if model_costs and model_name in model_costs:
                pricing = model_costs[model_name]
                total_cost = pricing['input'] + pricing['output']
                cost_display = f'${total_cost:.3f}'
            
            print(f"| {short_name[:28]:<28} | {cost_display:<13} | {'Pending...':<13} | {'Waiting':<14} |")
        
        print("+" + "-"*30 + "+" + "-"*15 + "+" + "-"*15 + "+" + "-"*16 + "+")
    
    def _update_progress_row(self, _row_index: int, model_name: str, accuracy: str, status: str):
        """Update a specific row in the progress table."""
        # For now, just print a simple status line instead of cursor manipulation
        print(f"  {model_name}: {accuracy} - {status}")
    
    def _close_progress_table(self):
        """Add final line to close the table."""
        print()  # Ensure we're on a new line
    
    def get_best_model(self) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Get the best performing model."""
        valid_results = {
            k: v for k, v in self.results.items() 
            if 'accuracy' in v and v['accuracy'] is not None
        }
        
        if not valid_results:
            return None
            
        best_model = max(valid_results.items(), key=lambda x: x[1]['accuracy'])
        return best_model