"""Evaluator module for testing model performance."""

import json
import time
import threading
from typing import List, Dict, Any, Tuple, Optional
from difflib import get_close_matches
from .provider import Provider


class Evaluator:
    """Evaluates models against golden dataset."""
    
    def __init__(self, provider: Provider):
        self.provider = provider
        self._stop_spinner = False
        
    def load_dataset(self, path: str) -> List[Dict[str, Any]]:
        """Load JSONL dataset."""
        data = []
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    data.append(json.loads(line))
        return data
    
    def _spinner_animation(self, message: str):
        """Animated spinner with green color."""
        frames = ["✦", "✧", "★", "✱", "✴", "✱", "★", "✧", "✦"]
        GREEN = "\033[92m"
        RESET = "\033[0m"
        
        i = 0
        while not self._stop_spinner:
            frame = frames[i % len(frames)]
            print(f"\r   {GREEN}{frame}{RESET} {message}", end="", flush=True)
            time.sleep(0.1)
            i += 1
    
    def evaluate(self, dataset: List[Dict[str, Any]], system_prompt: str = "", task: Optional[str] = None, options: Optional[List] = None) -> Tuple[float, List[Dict]]:
        """Evaluate model on dataset with task-specific logic and fuzzy matching.
        
        Updates each item with LLM_Decision field.
        If Human_Input/ground_truth is provided, calculates accuracy against it.
        """
        correct = 0
        total_with_labels = 0
        results = []
        
        # Start spinner in background thread
        self._stop_spinner = False
        spinner_thread = threading.Thread(
            target=self._spinner_animation, 
            args=(f"Processing {len(dataset)} items...",)
        )
        spinner_thread.daemon = True
        spinner_thread.start()
        
        for item in dataset:            
            # Use the provided system prompt (already task-specific)
            full_prompt = f"{system_prompt}\n\n{item['input']}"
            response = self.provider.complete(full_prompt).strip()
            
            # Parse response based on task type
            prediction = self._parse_response(response, task, options)
            
            # Update the item with LLM decision
            item_result = item.copy()
            item_result['LLM_Decision'] = prediction
            
            # Check accuracy against ground truth
            ground_truth = item.get('Human_Input') or item.get('ground_truth')
            if ground_truth is not None:
                total_with_labels += 1
                if self._evaluate_with_fuzzy_matching(prediction, ground_truth, options):
                    correct += 1
            
            results.append(item_result)
        
        # Stop spinner
        self._stop_spinner = True
        if spinner_thread.is_alive():
            spinner_thread.join(timeout=0.2)
        print("\r   ", end="")  # Clear spinner line
                
        # Calculate accuracy
        accuracy = correct / total_with_labels if total_with_labels > 0 else None
        
        return accuracy, results
    
    def _parse_response(self, response: str, task: Optional[str], options: Optional[List]) -> Any:
        """Parse LLM response based on task type."""
        response_clean = response.strip()
        
        # For binary tasks, extract 0/1 or boolean
        if task == "binary":
            response_lower = response_clean.lower()
            if '1' in response_clean or 'true' in response_lower or 'yes' in response_lower:
                return 1
            elif '0' in response_clean or 'false' in response_lower or 'no' in response_lower:
                return 0
            # Try to match against provided options
            if options:
                for opt in options:
                    if str(opt).lower() in response_lower:
                        return opt
            return 0  # Default to 0 if unclear
        
        # For classification, try to match against valid options
        elif task == "classification" and options:
            response_lower = response_clean.lower()
            # First try exact matches
            for opt in options:
                if str(opt).lower() == response_lower:
                    return opt
            # Then try substring matches
            for opt in options:
                if str(opt).lower() in response_lower:
                    return opt
            # Fuzzy matching as last resort
            options_lower = [str(opt).lower() for opt in options]
            close_matches = get_close_matches(response_lower, options_lower, n=1, cutoff=0.7)
            if close_matches:
                # Return the original case option
                match_idx = options_lower.index(close_matches[0])
                return options[match_idx]
            return response_clean  # Return as-is if no match
        
        # For extraction tasks, return cleaned response
        elif task == "extraction":
            if response_clean.lower() in ['none', 'null', 'n/a', 'not found']:
                return None
            return response_clean
        
        # Default: return cleaned response
        return response_clean
    
    def _evaluate_with_fuzzy_matching(self, prediction: Any, ground_truth: Any, options: Optional[List]) -> bool:
        """Evaluate prediction against ground truth with fuzzy matching."""
        pred_str = str(prediction).strip().lower() if prediction is not None else ""
        gt_str = str(ground_truth).strip().lower() if ground_truth is not None else ""
        
        # Exact match
        if pred_str == gt_str:
            return True
        
        # If options provided, both prediction and ground truth should be in options
        if options:
            options_lower = [str(opt).lower() for opt in options]
            pred_in_options = pred_str in options_lower
            gt_in_options = gt_str in options_lower
            
            if pred_in_options and gt_in_options:
                return pred_str == gt_str
            
            # If prediction is close to an option, use that for comparison
            if not pred_in_options:
                close_matches = get_close_matches(pred_str, options_lower, n=1, cutoff=0.8)
                if close_matches:
                    return close_matches[0] == gt_str
        
        return False