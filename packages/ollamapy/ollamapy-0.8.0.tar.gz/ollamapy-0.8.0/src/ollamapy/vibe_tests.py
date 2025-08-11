"""Built-in vibe tests for evaluating AI decision-making consistency with timing analysis and visual reporting."""

import re
import time
import statistics
from typing import List, Dict, Tuple, Any
from .ollama_client import OllamaClient
from .model_manager import ModelManager
from .analysis_engine import AnalysisEngine
from .actions import get_actions_with_vibe_tests, clear_action_logs
from .vibe_report import VibeTestReportGenerator


class TimingStats:
    """Container for timing statistics with helpful analysis methods."""
    
    def __init__(self, times: List[float]):
        """Initialize timing stats from a list of execution times.
        
        Args:
            times: List of execution times in seconds
        """
        self.times = times
        self.count = len(times)
        
        if times:
            self.mean = statistics.mean(times)
            self.median = statistics.median(times)
            self.min = min(times)
            self.max = max(times)
            self.std_dev = statistics.stdev(times) if len(times) > 1 else 0.0
            
            # Calculate percentiles for more insight
            sorted_times = sorted(times)
            self.p25 = self._percentile(sorted_times, 25)
            self.p75 = self._percentile(sorted_times, 75)
            self.p95 = self._percentile(sorted_times, 95)
        else:
            self.mean = self.median = self.min = self.max = self.std_dev = 0.0
            self.p25 = self.p75 = self.p95 = 0.0
    
    def _percentile(self, sorted_data: List[float], percentile: float) -> float:
        """Calculate percentile from sorted data."""
        if not sorted_data:
            return 0.0
        
        k = (len(sorted_data) - 1) * (percentile / 100.0)
        f = int(k)
        c = k - f
        
        if f + 1 < len(sorted_data):
            return sorted_data[f] + c * (sorted_data[f + 1] - sorted_data[f])
        else:
            return sorted_data[f]
    
    @property
    def consistency_score(self) -> float:
        """Calculate a consistency score (0-100) based on timing variability.
        
        Lower variance relative to mean indicates higher consistency.
        
        Returns:
            Consistency score from 0 (very inconsistent) to 100 (very consistent)
        """
        if self.mean == 0 or self.count < 2:
            return 100.0
        
        # Coefficient of variation (CV) = std_dev / mean
        cv = self.std_dev / self.mean
        
        # Convert CV to consistency score (lower CV = higher consistency)
        # CV of 0.1 (10%) = 90 consistency, CV of 0.5 (50%) = 50 consistency
        consistency = max(0, 100 - (cv * 200))
        return min(100, consistency)
    
    @property
    def performance_category(self) -> str:
        """Categorize performance based on mean response time."""
        if self.mean < 1.0:
            return "Very Fast"
        elif self.mean < 2.0:
            return "Fast"
        elif self.mean < 5.0:
            return "Moderate"
        elif self.mean < 10.0:
            return "Slow"
        else:
            return "Very Slow"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert timing stats to dictionary for serialization."""
        return {
            'count': self.count,
            'mean': self.mean,
            'median': self.median,
            'min': self.min,
            'max': self.max,
            'std_dev': self.std_dev,
            'p25': self.p25,
            'p75': self.p75,
            'p95': self.p95,
            'consistency_score': self.consistency_score,
            'performance_category': self.performance_category,
            'raw_times': self.times
        }


class VibeTestRunner:
    """Built-in vibe test runner with multi-action support, timing analysis, and visual reporting.
    
    Tests check if the target action is selected, regardless of what other
    actions might also be selected, and generates comprehensive visual reports
    including timing analysis.
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
        self.all_test_results = {}  # Store all results for report generation
    
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
    
    def time_analysis_execution(self, phrase: str) -> Tuple[List[Tuple[str, Dict[str, Any]]], float]:
        """Time the execution of analysis engine action selection.
        
        Args:
            phrase: The phrase to analyze
            
        Returns:
            Tuple of (selected_actions, execution_time_seconds)
        """
        start_time = time.perf_counter()
        
        try:
            # Clear any previous logs
            clear_action_logs()
            
            # Run the multi-action analysis
            selected_actions = self.analysis_engine.select_all_applicable_actions(phrase)
            
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            
            return selected_actions, execution_time
            
        except Exception as e:
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            print(f"❌ Error during analysis timing: {e}")
            return [], execution_time
    
    def run_action_test(self, action_name: str, action_info: Dict, phrases: List[str], 
                       iterations: int) -> Tuple[bool, Dict]:
        """Run a test on a specific action with its phrases, including timing analysis.
        
        Tests if the target action is selected (other actions may also be selected).
        
        Args:
            action_name: Name of the action being tested
            action_info: Information about the action (description, etc.)
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
            
            # Track secondary actions and timing per iteration for this phrase
            secondary_actions_per_iteration = []
            execution_times = []
            
            for i in range(iterations):
                try:
                    # Time the analysis execution
                    selected_actions, execution_time = self.time_analysis_execution(phrase)
                    execution_times.append(execution_time)
                    
                    # Check if target action was selected and track secondary actions
                    action_found = False
                    params_match = False
                    iteration_secondary_actions = []
                    
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
                        else:
                            # This is a secondary action
                            iteration_secondary_actions.append(selected_action)
                    
                    secondary_actions_per_iteration.append(iteration_secondary_actions)
                    total_tests += 1
                    
                except Exception as e:
                    print(f"❌ Error testing phrase iteration {i+1}: {e}")
                    secondary_actions_per_iteration.append([])
                    # Still record the time even if there was an error
                    if len(execution_times) <= i:
                        execution_times.append(0.0)
                    continue
            
            # Calculate secondary action frequencies
            secondary_action_counts = {}
            for iteration_actions in secondary_actions_per_iteration:
                for action in iteration_actions:
                    secondary_action_counts[action] = secondary_action_counts.get(action, 0) + 1
            
            # Calculate timing statistics
            timing_stats = TimingStats(execution_times)
            
            success_rate = (phrase_correct / iterations) * 100 if iterations > 0 else 0
            param_success_rate = (parameter_correct / iterations) * 100 if iterations > 0 and expected_params else 100
            
            results[phrase] = {
                'correct': phrase_correct,
                'total': iterations,
                'success_rate': success_rate,
                'parameter_success_rate': param_success_rate,
                'expected_params': expected_params,
                'secondary_action_counts': secondary_action_counts,
                'secondary_actions_per_iteration': secondary_actions_per_iteration,
                'timing_stats': timing_stats.to_dict()
            }
            total_correct += phrase_correct
            
            # Print individual results with timing
            phrase_display = phrase[:50] + '...' if len(phrase) > 50 else phrase
            print(f"Phrase: '{phrase_display}'")
            print(f"Target Action Selected: {phrase_correct}/{iterations} ({success_rate:.1f}%)")
            if expected_params:
                print(f"Parameter Success: {parameter_correct}/{iterations} ({param_success_rate:.1f}%)")
                print(f"Expected params: {expected_params}")
            
            # Print timing analysis
            print(f"Timing Analysis:")
            print(f"  Average: {timing_stats.mean:.2f}s | Median: {timing_stats.median:.2f}s")
            print(f"  Range: {timing_stats.min:.2f}s - {timing_stats.max:.2f}s")
            print(f"  Performance: {timing_stats.performance_category}")
            print(f"  Consistency: {timing_stats.consistency_score:.1f}/100")
            
            if secondary_action_counts:
                print(f"Secondary actions triggered:")
                for action, count in secondary_action_counts.items():
                    print(f"  - {action}: {count}/{iterations} times")
            print("-" * 40)
        
        overall_success_rate = (total_correct / total_tests) * 100 if total_tests > 0 else 0
        
        # Calculate overall timing statistics across all phrases
        all_times = []
        for phrase_results in results.values():
            all_times.extend(phrase_results['timing_stats']['raw_times'])
        overall_timing = TimingStats(all_times)
        
        print(f"Overall Success Rate: {total_correct}/{total_tests} ({overall_success_rate:.1f}%)")
        print(f"Overall Timing: {overall_timing.mean:.2f}s avg, {overall_timing.performance_category}, {overall_timing.consistency_score:.1f}/100 consistency")
        
        test_passed = overall_success_rate >= 60.0
        return test_passed, {
            'action_name': action_name,
            'action_description': action_info.get('description', 'No description'),
            'total_correct': total_correct,
            'total_tests': total_tests,
            'success_rate': overall_success_rate,
            'phrase_results': results,
            'overall_timing_stats': overall_timing.to_dict()
        }
    
    def run_all_tests(self, iterations: int = 1) -> bool:
        """Run all vibe tests for all actions that have test phrases.
        
        Args:
            iterations: Number of iterations per phrase
            
        Returns:
            True if all tests passed, False otherwise
        """
        print(f"🧪 Running vibe tests with multi-action support, timing analysis, and visual reporting")
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
        print(f"⏱️  Including timing analysis for performance insights...")
        print(f"📋 Found {len(self.actions_with_tests)} actions with vibe test phrases\n")
        
        if not self.actions_with_tests:
            print("❌ No actions with vibe test phrases found!")
            return False
        
        # Run tests for each action
        test_results = {}
        all_tests_passed = True
        overall_test_start = time.perf_counter()
        
        for action_name, action_info in self.actions_with_tests.items():
            test_phrases = action_info['vibe_test_phrases']
            
            if not test_phrases:
                print(f"⚠️  Skipping {action_name} - no test phrases defined")
                continue
            
            test_passed, results = self.run_action_test(
                action_name, action_info, test_phrases, iterations
            )
            
            test_results[action_name] = {
                'passed': test_passed,
                'results': results
            }
            
            if not test_passed:
                all_tests_passed = False
        
        overall_test_time = time.perf_counter() - overall_test_start
        
        # Store results for report generation
        self.all_test_results = test_results
        
        # Generate and save the HTML report using the report generator
        report_generator = VibeTestReportGenerator(self.model, self.analysis_model)
        filename = report_generator.save_report(test_results)
        print(f"\n📊 Report saved to: {filename}")
        print(f"   Open in your browser to view interactive charts with timing analysis")
        
        # Final results summary with timing
        print(f"\n📊 Final Test Results:")
        print("=" * 50)
        
        fastest_action = None
        slowest_action = None
        fastest_time = float('inf')
        slowest_time = 0.0
        
        for action_name, test_data in test_results.items():
            status_icon = "✅ PASSED" if test_data['passed'] else "❌ FAILED"
            success_rate = test_data['results']['success_rate']
            avg_time = test_data['results']['overall_timing_stats']['mean']
            consistency = test_data['results']['overall_timing_stats']['consistency_score']
            
            print(f"{action_name} Action Test: {status_icon} ({success_rate:.1f}%)")
            print(f"  Performance: {avg_time:.2f}s avg, {consistency:.1f}/100 consistency")
            
            if avg_time < fastest_time:
                fastest_time = avg_time
                fastest_action = action_name
            if avg_time > slowest_time:
                slowest_time = avg_time
                slowest_action = action_name
        
        status_icon = "✅" if all_tests_passed else "❌"
        status_text = "ALL TESTS PASSED" if all_tests_passed else "SOME TESTS FAILED"
        print(f"\nOverall Result: {status_icon} {status_text}")
        print(f"Total Test Duration: {overall_test_time:.2f}s")
        
        if fastest_action and slowest_action:
            print(f"Performance Range: {fastest_action} ({fastest_time:.2f}s) → {slowest_action} ({slowest_time:.2f}s)")
        
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
    """Convenience function to run vibe tests with timing analysis and visual reporting.
    
    Args:
        model: The model to use for testing
        iterations: Number of iterations per test
        analysis_model: Optional separate model for action analysis (defaults to main model)
        
    Returns:
        True if all tests passed, False otherwise
    """
    runner = VibeTestRunner(model=model, analysis_model=analysis_model)
    return runner.run_all_tests(iterations=iterations)