"""Built-in vibe tests for evaluating AI decision-making consistency."""

import re
from typing import List, Dict, Tuple, Any
from .ollama_client import OllamaClient
from .model_manager import ModelManager
from .analysis_engine import AnalysisEngine
from .actions import get_actions_with_vibe_tests, clear_action_logs


class VibeTestRunner:
    """Built-in vibe test runner with multi-action support.
    
    Tests now check if the target action is selected, regardless of
    what other actions might also be selected.
    """
    
    def __init__(self, model: str = "gemma3:4b", analysis_model: str = "gemma3:4b"):
        """Initialize the vibe test runner.
        
        Args:
            model: The model to use for testing
            analysis_model: Optional separate model for action analysis (defaults to main model)
        """
        self.model = model
        self.analysis_model = analysis_model or model
        self.client = OllamaClient()
        self.model_manager = ModelManager(self.client)
        self.analysis_engine = AnalysisEngine(self.analysis_model, self.client)
        self.actions_with_tests = get_actions_with_vibe_tests()
    
    def check_prerequisites(self) -> bool:
        """Check if Ollama is available and models can be used."""
        success, main_status, analysis_status = self.model_manager.ensure_models_available(
            self.model, self.analysis_model
        )
        
        if not success:
            print("❌ Error: Ollama server is not running!")
            print("Please start Ollama with: ollama serve")
            return False
        
        return True
    
    def extract_expected_parameters(self, phrase: str, action_name: str) -> Dict[str, Any]:
        """Extract expected parameter values from test phrases.
        
        Args:
            phrase: The test phrase
            action_name: The action being tested
            
        Returns:
            Dictionary of expected parameter values
        """
        expected_params = {}
        
        # Extract numbers for square_root
        if action_name == "square_root":
            # Look for numbers in the phrase
            numbers = re.findall(r'\d+(?:\.\d+)?', phrase)
            if numbers:
                expected_params['number'] = float(numbers[0])
        
        # Extract expressions for calculate
        elif action_name == "calculate":
            # Look for mathematical expressions
            # Simple pattern for basic arithmetic
            expr_match = re.search(r'(\d+\s*[+\-*/]\s*\d+)', phrase)
            if expr_match:
                expected_params['expression'] = expr_match.group(1).replace(' ', '')
        
        # Extract location for weather (if mentioned)
        elif action_name == "getWeather":
            # Look for common city names or location indicators
            location_keywords = ['in', 'at', 'for']
            for keyword in location_keywords:
                if keyword in phrase.lower():
                    parts = phrase.lower().split(keyword)
                    if len(parts) > 1:
                        potential_location_parts = parts[1].strip().split()
                        if potential_location_parts:
                            potential_location = potential_location_parts[0]
                            if len(potential_location) > 2:
                                expected_params['location'] = potential_location
                            break
        
        return expected_params
    
    def run_action_test(self, action_name: str, phrases: List[str], 
                       iterations: int) -> Tuple[bool, Dict]:
        """Run a test on a specific action with its phrases.
        
        Tests if the target action is selected (other actions may also be selected).
        
        Args:
            action_name: Name of the action being tested
            phrases: List of test phrases for this action
            iterations: Number of times to test each phrase
            
        Returns:
            Tuple of (success: bool, results: dict)
        """
        total_correct = 0
        total_tests = 0
        results = {}
        
        print(f"\n🧪 {action_name} Action Test")
        print(f"Chat Model: {self.model}")
        if self.analysis_model != self.model:
            print(f"Analysis Model: {self.analysis_model}")
        else:
            print("Using same model for analysis and chat")
        print("Mode: Multi-action selection (target action must be selected)")
        print("=" * 80)
        
        for phrase in phrases:
            phrase_correct = 0
            parameter_correct = 0
            expected_params = self.extract_expected_parameters(phrase, action_name)
            other_actions_selected = []
            
            for i in range(iterations):
                try:
                    # Clear any previous logs
                    clear_action_logs()
                    
                    # Run the multi-action analysis
                    selected_actions = self.analysis_engine.select_all_applicable_actions(phrase)
                    
                    # Check if target action was selected
                    action_found = False
                    params_match = False
                    
                    for selected_action, parameters in selected_actions:
                        if selected_action == action_name:
                            action_found = True
                            phrase_correct += 1
                            
                            # Check parameters if expected
                            if expected_params:
                                params_match = True
                                for param_name, expected_value in expected_params.items():
                                    if param_name in parameters:
                                        actual_value = parameters[param_name]
                                        # For numbers, check if they're close enough
                                        if isinstance(expected_value, (int, float)):
                                            try:
                                                actual_float = float(actual_value)
                                                if abs(actual_float - expected_value) < 0.001:
                                                    parameter_correct += 1
                                                else:
                                                    params_match = False
                                            except:
                                                params_match = False
                                        # For strings, check exact match
                                        elif str(actual_value) == str(expected_value):
                                            parameter_correct += 1
                                        else:
                                            params_match = False
                                    else:
                                        params_match = False
                            break
                        else:
                            # Track other actions that were selected
                            if selected_action not in other_actions_selected:
                                other_actions_selected.append(selected_action)
                    
                    total_tests += 1
                except Exception as e:
                    print(f"❌ Error testing phrase iteration {i+1}: {e}")
                    continue
            
            success_rate = (phrase_correct / iterations) * 100 if iterations > 0 else 0
            param_success_rate = (parameter_correct / iterations) * 100 if iterations > 0 and expected_params else 100
            
            results[phrase] = {
                'correct': phrase_correct,
                'total': iterations,
                'success_rate': success_rate,
                'parameter_success_rate': param_success_rate,
                'expected_params': expected_params,
                'other_actions': other_actions_selected
            }
            total_correct += phrase_correct
            
            # Print individual results
            phrase_display = phrase[:50] + '...' if len(phrase) > 50 else phrase
            print(f"Phrase: '{phrase_display}'")
            print(f"Target Action Selected: {phrase_correct}/{iterations} ({success_rate:.1f}%)")
            if expected_params:
                print(f"Parameter Success: {parameter_correct}/{iterations} ({param_success_rate:.1f}%)")
                print(f"Expected params: {expected_params}")
            if other_actions_selected:
                print(f"Other actions also selected: {', '.join(other_actions_selected)}")
            print("-" * 40)
        
        overall_success_rate = (total_correct / total_tests) * 100 if total_tests > 0 else 0
        print(f"Overall Success Rate: {total_correct}/{total_tests} ({overall_success_rate:.1f}%)")
        
        test_passed = overall_success_rate >= 60.0
        return test_passed, {
            'total_correct': total_correct,
            'total_tests': total_tests,
            'success_rate': overall_success_rate,
            'phrase_results': results
        }
    
    def run_all_tests(self, iterations: int = 1) -> bool:
        """Run all vibe tests for all actions that have test phrases.
        
        Args:
            iterations: Number of iterations per phrase
            
        Returns:
            True if all tests passed, False otherwise
        """
        print(f"🧪 Running vibe tests with multi-action support")
        print(f"Chat model: {self.model}")
        if self.analysis_model != self.model:
            print(f"Analysis model: {self.analysis_model}")
        else:
            print("Using same model for analysis and chat")
        print(f"Analysis mode: Multi-action (target must be selected)")
        print(f"Iterations: {iterations}")
        print("=" * 80)
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        print(f"✅ Using chat model: {self.model}")
        if self.analysis_model != self.model:
            print(f"✅ Using analysis model: {self.analysis_model}")
        print(f"🧠 Testing AI's ability to select appropriate actions (multiple allowed)...")
        print(f"📋 Found {len(self.actions_with_tests)} actions with vibe test phrases\n")
        
        if not self.actions_with_tests:
            print("❌ No actions with vibe test phrases found!")
            return False
        
        # Run tests for each action
        test_results = {}
        all_tests_passed = True
        
        for action_name, action_info in self.actions_with_tests.items():
            test_phrases = action_info['vibe_test_phrases']
            
            if not test_phrases:
                print(f"⚠️  Skipping {action_name} - no test phrases defined")
                continue
            
            test_passed, results = self.run_action_test(
                action_name, test_phrases, iterations
            )
            
            test_results[action_name] = {
                'passed': test_passed,
                'results': results
            }
            
            if not test_passed:
                all_tests_passed = False
        
        # Final results summary
        print(f"\n📊 Final Test Results:")
        print("=" * 50)
        
        for action_name, test_data in test_results.items():
            status_icon = "✅ PASSED" if test_data['passed'] else "❌ FAILED"
            success_rate = test_data['results']['success_rate']
            print(f"{action_name} Action Test: {status_icon} ({success_rate:.1f}%)")
        
        status_icon = "✅" if all_tests_passed else "❌"
        status_text = "ALL TESTS PASSED" if all_tests_passed else "SOME TESTS FAILED"
        print(f"\nOverall Result: {status_icon} {status_text}")
        
        if not all_tests_passed:
            print("\n💡 Tips for improving results:")
            print("   • Try a different model with --model")
            print("   • Try a different analysis model with --analysis-model")
            print("   • Use a smaller, faster model for analysis (e.g., gemma2:2b)")
            print("   • Increase iterations with -n for better statistics")
            print("   • Ensure Ollama server is running optimally")
            print("   • Check action descriptions and test phrases for clarity")
        
        return all_tests_passed
    
    def run_quick_test(self) -> bool:
        """Run a quick single-iteration test for fast feedback."""
        print("🚀 Running quick vibe test (1 iteration each)...")
        return self.run_all_tests(iterations=1)
    
    def run_statistical_test(self, iterations: int = 5) -> bool:
        """Run a statistical test with multiple iterations."""
        print(f"📊 Running statistical vibe test ({iterations} iterations each)...")
        return self.run_all_tests(iterations=iterations)


def run_vibe_tests(model: str = "gemma3:4b", iterations: int = 1, analysis_model: str = None) -> bool:
    """Convenience function to run vibe tests.
    
    Args:
        model: The model to use for testing
        iterations: Number of iterations per test
        analysis_model: Optional separate model for action analysis (defaults to main model)
        
    Returns:
        True if all tests passed, False otherwise
    """
    runner = VibeTestRunner(model=model, analysis_model=analysis_model)
    return runner.run_all_tests(iterations=iterations)