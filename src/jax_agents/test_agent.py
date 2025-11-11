"""
Test Agent for validating Fortran-to-JAX translations.

This agent orchestrates the complete testing workflow:
1. Analyzes Fortran and Python function signatures
2. Generates synthetic test data
3. Creates Fortran test harness and compiles it
4. Runs both Fortran and Python implementations
5. Compares outputs and generates test reports
6. Creates pytest files for continuous validation
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

from jax_agents.base_agent import BaseAgent
from jax_agents.utils.config_loader import get_llm_config
from jax_agents.utils.fortran_parser import FortranParser
from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Result of running a test comparison."""
    passed: bool
    fortran_outputs: Dict[str, Any]
    python_outputs: Dict[str, Any]
    differences: Dict[str, Any]
    error_metrics: Dict[str, float]
    test_data: Dict[str, Any]
    execution_time_fortran: float
    execution_time_python: float


@dataclass
class TestGenerationResult:
    """Complete result of test generation."""
    module_name: str
    pytest_file: str
    test_data_file: str
    fortran_harness: str
    test_report: str
    test_results: List[TestResult]
    
    def save(self, output_dir: Path) -> Dict[str, Path]:
        """Save all test artifacts to directory."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = {}
        
        # Save pytest file
        pytest_path = output_dir / f"test_{self.module_name}.py"
        with open(pytest_path, 'w') as f:
            f.write(self.pytest_file)
        saved_files["pytest"] = pytest_path
        console.print(f"[green]✓ Saved pytest file to {pytest_path}[/green]")
        
        # Save test data
        test_data_path = output_dir / f"test_data_{self.module_name}.json"
        with open(test_data_path, 'w') as f:
            f.write(self.test_data_file)
        saved_files["test_data"] = test_data_path
        console.print(f"[green]✓ Saved test data to {test_data_path}[/green]")
        
        # Save Fortran harness
        harness_path = output_dir / f"test_harness_{self.module_name}.f90"
        with open(harness_path, 'w') as f:
            f.write(self.fortran_harness)
        saved_files["fortran_harness"] = harness_path
        console.print(f"[green]✓ Saved Fortran harness to {harness_path}[/green]")
        
        # Save test report
        report_path = output_dir / f"test_report_{self.module_name}.md"
        with open(report_path, 'w') as f:
            f.write(self.test_report)
        saved_files["report"] = report_path
        console.print(f"[green]✓ Saved test report to {report_path}[/green]")
        
        return saved_files


class TestAgent(BaseAgent):
    """
    Agent for generating and running validation tests.
    
    Responsibilities:
    - Parse Fortran and Python function signatures
    - Generate synthetic test data
    - Create Fortran test harness
    - Compile and run both implementations
    - Compare outputs with tolerance
    - Generate pytest files and reports
    """
    
    def __init__(
        self,
        fortran_compiler: str = "gfortran",
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """
        Initialize Test Agent.
        
        Args:
            fortran_compiler: Fortran compiler command (default: gfortran)
            model: Claude model to use (defaults to config.yaml)
            temperature: Sampling temperature (defaults to config.yaml)
            max_tokens: Maximum tokens in response (defaults to config.yaml)
        """
        llm_config = get_llm_config()
        
        super().__init__(
            name="TestAgent",
            role="Fortran-to-JAX translation validator",
            model=model or llm_config.get("model", "claude-sonnet-4-5"),
            temperature=temperature if temperature is not None else llm_config.get("temperature", 0.0),
            max_tokens=max_tokens or llm_config.get("max_tokens", 48000),
        )
        
        self.fortran_compiler = fortran_compiler
        self.fortran_parser = FortranParser()
    
    def generate_tests(
        self,
        module_name: str,
        fortran_code: str,
        python_code: str,
        fortran_file: Optional[Path] = None,
        clm_tests: Optional[List[str]] = None,
        output_dir: Optional[Path] = None,
        num_test_cases: int = 5,
    ) -> TestGenerationResult:
        """
        Generate complete test suite for a translated module.
        
        Args:
            module_name: Name of the module being tested
            fortran_code: Original Fortran subroutine code
            python_code: Translated Python function code
            fortran_file: Path to original Fortran file (for includes/context)
            clm_tests: Optional existing CLM tests to incorporate
            output_dir: Optional directory to save outputs
            num_test_cases: Number of synthetic test cases to generate
            
        Returns:
            TestGenerationResult with all test artifacts
        """
        console.print(f"\n[bold cyan]🧪 Generating test suite for {module_name}[/bold cyan]")
        
        # Step 1: Analyze function signatures
        console.print("[cyan]Step 1/6: Analyzing function signatures...[/cyan]")
        fortran_sig = self._analyze_fortran_signature(fortran_code, module_name)
        python_sig = self._analyze_python_signature(python_code, module_name)
        
        # Step 2: Generate synthetic test data
        console.print("[cyan]Step 2/6: Generating synthetic test data...[/cyan]")
        test_data = self._generate_test_data(
            fortran_sig, python_sig, num_test_cases, clm_tests
        )
        
        # Step 3: Create Fortran test harness
        console.print("[cyan]Step 3/6: Creating Fortran test harness...[/cyan]")
        fortran_harness = self._create_fortran_harness(
            fortran_code, fortran_sig, test_data, module_name
        )
        
        # Step 4: Run both implementations
        console.print("[cyan]Step 4/6: Running Fortran and Python implementations...[/cyan]")
        test_results = self._run_tests(
            fortran_harness, python_code, test_data, fortran_file
        )
        
        # Step 5: Generate pytest file
        console.print("[cyan]Step 5/6: Generating pytest file...[/cyan]")
        pytest_file = self._generate_pytest(
            module_name, python_sig, test_data, test_results
        )
        
        # Step 6: Generate test report
        console.print("[cyan]Step 6/6: Generating test report...[/cyan]")
        test_report = self._generate_report(
            module_name, test_results, fortran_sig, python_sig
        )
        
        result = TestGenerationResult(
            module_name=module_name,
            pytest_file=pytest_file,
            test_data_file=json.dumps(test_data, indent=2),
            fortran_harness=fortran_harness,
            test_report=test_report,
            test_results=test_results,
        )
        
        console.print(f"[green]✓ Test suite generation complete![/green]")
        
        if output_dir:
            result.save(output_dir)
        
        return result
    
    def _analyze_fortran_signature(
        self, fortran_code: str, module_name: str
    ) -> Dict[str, Any]:
        """Analyze Fortran subroutine signature and parameters."""
        from jax_agents.prompts.test_prompts import TEST_PROMPTS
        
        prompt = TEST_PROMPTS["analyze_fortran_signature"].format(
            fortran_code=fortran_code,
            module_name=module_name,
        )
        
        response = self.query_claude(
            prompt=prompt,
            system_prompt=TEST_PROMPTS["system"],
        )
        
        # Parse JSON response
        try:
            # Extract JSON from code block if present
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                json_str = response
            
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Fortran signature: {e}")
            logger.error(f"Response: {response}")
            raise
    
    def _analyze_python_signature(
        self, python_code: str, module_name: str
    ) -> Dict[str, Any]:
        """Analyze Python function signature and parameters."""
        from jax_agents.prompts.test_prompts import TEST_PROMPTS
        
        prompt = TEST_PROMPTS["analyze_python_signature"].format(
            python_code=python_code,
            module_name=module_name,
        )
        
        response = self.query_claude(
            prompt=prompt,
            system_prompt=TEST_PROMPTS["system"],
        )
        
        # Parse JSON response
        try:
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                json_str = response
            
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Python signature: {e}")
            logger.error(f"Response: {response}")
            raise
    
    def _generate_test_data(
        self,
        fortran_sig: Dict[str, Any],
        python_sig: Dict[str, Any],
        num_cases: int,
        clm_tests: Optional[List[str]],
    ) -> Dict[str, Any]:
        """Generate synthetic test data."""
        from jax_agents.prompts.test_prompts import TEST_PROMPTS
        
        prompt = TEST_PROMPTS["generate_test_data"].format(
            fortran_signature=json.dumps(fortran_sig, indent=2),
            python_signature=json.dumps(python_sig, indent=2),
            num_cases=num_cases,
            clm_tests=json.dumps(clm_tests) if clm_tests else "None",
        )
        
        response = self.query_claude(
            prompt=prompt,
            system_prompt=TEST_PROMPTS["system"],
        )
        
        # Parse JSON response
        try:
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                json_str = response
            
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse test data: {e}")
            logger.error(f"Response: {response}")
            raise
    
    def _create_fortran_harness(
        self,
        fortran_code: str,
        fortran_sig: Dict[str, Any],
        test_data: Dict[str, Any],
        module_name: str,
    ) -> str:
        """Create Fortran test harness that reads JSON and calls subroutine."""
        from jax_agents.prompts.test_prompts import TEST_PROMPTS
        
        prompt = TEST_PROMPTS["create_fortran_harness"].format(
            fortran_code=fortran_code,
            fortran_signature=json.dumps(fortran_sig, indent=2),
            test_data_structure=json.dumps(test_data, indent=2),
            module_name=module_name,
        )
        
        response = self.query_claude(
            prompt=prompt,
            system_prompt=TEST_PROMPTS["system"],
        )
        
        # Extract Fortran code
        if "```fortran" in response:
            start = response.find("```fortran") + 10
            end = response.find("```", start)
            return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            return response[start:end].strip()
        else:
            return response
    
    def _run_tests(
        self,
        fortran_harness: str,
        python_code: str,
        test_data: Dict[str, Any],
        fortran_file: Optional[Path],
    ) -> List[TestResult]:
        """Run both Fortran and Python implementations and compare."""
        from jax_agents.utils.fortran_runner import FortranRunner
        from jax_agents.utils.comparison import compare_outputs
        
        console.print("[dim]Compiling and running Fortran...[/dim]")
        fortran_runner = FortranRunner(self.fortran_compiler)
        fortran_outputs = fortran_runner.run_harness(
            fortran_harness, test_data, fortran_file
        )
        
        console.print("[dim]Running Python...[/dim]")
        python_outputs = self._run_python(python_code, test_data)
        
        console.print("[dim]Comparing outputs...[/dim]")
        test_results = []
        for i, (f_out, p_out) in enumerate(zip(fortran_outputs, python_outputs)):
            comparison = compare_outputs(
                f_out["outputs"], p_out["outputs"], tolerance=1e-6
            )
            
            test_results.append(TestResult(
                passed=comparison["all_close"],
                fortran_outputs=f_out["outputs"],
                python_outputs=p_out["outputs"],
                differences=comparison["differences"],
                error_metrics=comparison["error_metrics"],
                test_data=test_data["test_cases"][i],
                execution_time_fortran=f_out["execution_time"],
                execution_time_python=p_out["execution_time"],
            ))
        
        return test_results
    
    def _run_python(
        self, python_code: str, test_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Run Python implementation with test data."""
        import time
        import importlib.util
        import tempfile
        
        results = []
        
        # Write Python code to temp file and import it
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            temp_path = f.name
        
        try:
            spec = importlib.util.spec_from_file_location("test_module", temp_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find the main function
            # Assume it's the first function defined or specified in signature
            function_name = test_data.get("function_name")
            if hasattr(module, function_name):
                test_func = getattr(module, function_name)
            else:
                # Try to find any function
                for name in dir(module):
                    obj = getattr(module, name)
                    if callable(obj) and not name.startswith('_'):
                        test_func = obj
                        break
            
            # Run each test case
            for test_case in test_data["test_cases"]:
                start_time = time.time()
                
                # Call function with test inputs
                outputs = test_func(**test_case["inputs"])
                
                execution_time = time.time() - start_time
                
                results.append({
                    "outputs": outputs,
                    "execution_time": execution_time,
                })
        
        finally:
            # Clean up temp file
            Path(temp_path).unlink()
        
        return results
    
    def _generate_pytest(
        self,
        module_name: str,
        python_sig: Dict[str, Any],
        test_data: Dict[str, Any],
        test_results: List[TestResult],
    ) -> str:
        """Generate pytest file."""
        from jax_agents.prompts.test_prompts import TEST_PROMPTS
        
        prompt = TEST_PROMPTS["generate_pytest"].format(
            module_name=module_name,
            python_signature=json.dumps(python_sig, indent=2),
            test_data=json.dumps(test_data, indent=2),
            test_results_summary=self._summarize_test_results(test_results),
        )
        
        response = self.query_claude(
            prompt=prompt,
            system_prompt=TEST_PROMPTS["system"],
        )
        
        # Extract Python code
        if "```python" in response:
            start = response.find("```python") + 9
            end = response.find("```", start)
            return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            return response[start:end].strip()
        else:
            return response
    
    def _generate_report(
        self,
        module_name: str,
        test_results: List[TestResult],
        fortran_sig: Dict[str, Any],
        python_sig: Dict[str, Any],
    ) -> str:
        """Generate test report in markdown."""
        from jax_agents.prompts.test_prompts import TEST_PROMPTS
        
        prompt = TEST_PROMPTS["generate_report"].format(
            module_name=module_name,
            fortran_signature=json.dumps(fortran_sig, indent=2),
            python_signature=json.dumps(python_sig, indent=2),
            test_results=json.dumps([
                {
                    "passed": r.passed,
                    "error_metrics": r.error_metrics,
                    "execution_time_fortran": r.execution_time_fortran,
                    "execution_time_python": r.execution_time_python,
                }
                for r in test_results
            ], indent=2),
        )
        
        response = self.query_claude(
            prompt=prompt,
            system_prompt=TEST_PROMPTS["system"],
        )
        
        return response
    
    def _summarize_test_results(self, test_results: List[TestResult]) -> str:
        """Create summary of test results for prompt."""
        summary = {
            "total_tests": len(test_results),
            "passed": sum(1 for r in test_results if r.passed),
            "failed": sum(1 for r in test_results if not r.passed),
            "max_error": max(
                max(r.error_metrics.values()) 
                for r in test_results 
                if r.error_metrics
            ) if test_results else 0,
        }
        return json.dumps(summary, indent=2)

