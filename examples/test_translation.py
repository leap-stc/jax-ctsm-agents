#!/usr/bin/env python3
"""
Example script for using the Test Agent to validate translations.

This script demonstrates how to:
1. Load a translated module
2. Generate test suite
3. Run validation tests
4. Generate reports
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from jax_agents.test_agent import TestAgent
from rich.console import Console

console = Console()


def test_single_module(
    module_name: str,
    fortran_file: Path,
    python_file: Path,
    output_dir: Path,
):
    """
    Test a single translated module.
    
    Args:
        module_name: Name of the module
        fortran_file: Path to original Fortran file
        python_file: Path to translated Python file
        output_dir: Directory to save test outputs
    """
    console.print(f"\n[bold cyan]Testing {module_name}[/bold cyan]")
    
    # Read source files
    with open(fortran_file, 'r') as f:
        fortran_code = f.read()
    
    with open(python_file, 'r') as f:
        python_code = f.read()
    
    # Initialize test agent
    test_agent = TestAgent(
        fortran_compiler="gfortran",
    )
    
    # Generate and run tests
    result = test_agent.generate_tests(
        module_name=module_name,
        fortran_code=fortran_code,
        python_code=python_code,
        fortran_file=fortran_file,
        output_dir=output_dir,
        num_test_cases=5,
    )
    
    # Print summary
    console.print("\n[bold green]Test Summary:[/bold green]")
    total_tests = len(result.test_results)
    passed = sum(1 for r in result.test_results if r.passed)
    
    console.print(f"  Total tests: {total_tests}")
    console.print(f"  Passed: {passed}")
    console.print(f"  Failed: {total_tests - passed}")
    
    if passed == total_tests:
        console.print("\n[bold green]✓ All tests passed![/bold green]")
    else:
        console.print("\n[bold red]✗ Some tests failed[/bold red]")
        
        # Show failed tests
        for i, result in enumerate(result.test_results):
            if not result.passed:
                console.print(f"\n[red]Failed test {i+1}:[/red]")
                for var, metrics in result.error_metrics.items():
                    console.print(
                        f"  {var}: "
                        f"max_abs_err={metrics['max_abs_error']:.2e}, "
                        f"max_rel_err={metrics['max_rel_error']:.2e}"
                    )
    
    # Show cost estimate
    cost = test_agent.get_cost_estimate()
    console.print(f"\n[dim]Cost: ${cost['total_cost_usd']:.4f}[/dim]")


def test_soil_temperature_mod():
    """Test the SoilTemperatureMod translation."""
    project_root = Path(__file__).parent.parent
    
    # Find the Fortran file (you'll need to provide this path)
    fortran_file = Path("/path/to/CTSM/src/biogeophys/SoilTemperatureMod.F90")
    
    # Translated Python file
    python_file = project_root / "translated_modules/SoilTemperatureMod/SoilTemperatureMod.py"
    
    # Output directory
    output_dir = project_root / "translated_modules/SoilTemperatureMod/tests"
    
    if not fortran_file.exists():
        console.print(f"[red]Fortran file not found: {fortran_file}[/red]")
        console.print("[yellow]Please update the fortran_file path in the script[/yellow]")
        return
    
    if not python_file.exists():
        console.print(f"[red]Python file not found: {python_file}[/red]")
        return
    
    test_single_module(
        module_name="SoilTemperatureMod",
        fortran_file=fortran_file,
        python_file=python_file,
        output_dir=output_dir,
    )


def test_from_analysis_results():
    """
    Test modules using the static analysis results.
    
    This reads the translation units JSON and tests all translated modules.
    """
    project_root = Path(__file__).parent.parent
    
    # Load translation units
    import json
    translation_units_file = project_root / "static_analysis_output/translation_units.json"
    
    if not translation_units_file.exists():
        console.print(f"[red]Translation units file not found: {translation_units_file}[/red]")
        return
    
    with open(translation_units_file, 'r') as f:
        translation_data = json.load(f)
    
    # Get list of modules that have been translated
    translated_dir = project_root / "translated_modules"
    
    if not translated_dir.exists():
        console.print(f"[red]Translated modules directory not found: {translated_dir}[/red]")
        return
    
    # Find all translated modules
    for module_dir in translated_dir.iterdir():
        if not module_dir.is_dir():
            continue
        
        module_name = module_dir.name
        python_file = module_dir / f"{module_name}.py"
        
        if not python_file.exists():
            continue
        
        console.print(f"\n[bold cyan]Found translated module: {module_name}[/bold cyan]")
        
        # Find corresponding Fortran file in translation units
        fortran_file = None
        for unit in translation_data.get("translation_units", []):
            if unit.get("module_name", "").lower() == module_name.lower():
                fortran_file = Path(unit.get("file_path", ""))
                break
        
        if fortran_file and fortran_file.exists():
            output_dir = module_dir / "tests"
            
            try:
                test_single_module(
                    module_name=module_name,
                    fortran_file=fortran_file,
                    python_file=python_file,
                    output_dir=output_dir,
                )
            except Exception as e:
                console.print(f"[red]Error testing {module_name}: {e}[/red]")
        else:
            console.print(f"[yellow]Skipping {module_name} - Fortran file not found[/yellow]")


def interactive_mode():
    """Interactive mode for testing translations."""
    console.print("\n[bold cyan]Test Agent - Interactive Mode[/bold cyan]")
    console.print("This tool helps validate Fortran-to-JAX translations\n")
    
    # Get inputs
    console.print("[cyan]Enter module name:[/cyan]")
    module_name = input("> ").strip()
    
    console.print("\n[cyan]Enter path to Fortran file:[/cyan]")
    fortran_path = input("> ").strip()
    fortran_file = Path(fortran_path)
    
    if not fortran_file.exists():
        console.print(f"[red]Error: Fortran file not found: {fortran_file}[/red]")
        return
    
    console.print("\n[cyan]Enter path to Python file:[/cyan]")
    python_path = input("> ").strip()
    python_file = Path(python_path)
    
    if not python_file.exists():
        console.print(f"[red]Error: Python file not found: {python_file}[/red]")
        return
    
    console.print("\n[cyan]Enter output directory:[/cyan]")
    output_path = input("> ").strip()
    output_dir = Path(output_path)
    
    console.print("\n[cyan]Number of test cases (default: 5):[/cyan]")
    num_cases_str = input("> ").strip()
    num_cases = int(num_cases_str) if num_cases_str else 5
    
    # Run test
    try:
        test_single_module(
            module_name=module_name,
            fortran_file=fortran_file,
            python_file=python_file,
            output_dir=output_dir,
        )
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test Agent for validating Fortran-to-JAX translations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test a specific module
  python test_translation.py --module SoilTemperatureMod \\
    --fortran /path/to/SoilTemperatureMod.F90 \\
    --python ./translated_modules/SoilTemperatureMod/SoilTemperatureMod.py \\
    --output ./translated_modules/SoilTemperatureMod/tests
  
  # Test all translated modules using analysis results
  python test_translation.py --all
  
  # Interactive mode
  python test_translation.py --interactive
        """
    )
    
    parser.add_argument(
        "--module",
        help="Module name to test"
    )
    parser.add_argument(
        "--fortran",
        help="Path to Fortran source file"
    )
    parser.add_argument(
        "--python",
        help="Path to translated Python file"
    )
    parser.add_argument(
        "--output",
        help="Output directory for test results"
    )
    parser.add_argument(
        "--num-cases",
        type=int,
        default=5,
        help="Number of test cases to generate (default: 5)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Test all translated modules"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--compiler",
        default="gfortran",
        help="Fortran compiler to use (default: gfortran)"
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    elif args.all:
        test_from_analysis_results()
    elif args.module and args.fortran and args.python and args.output:
        test_single_module(
            module_name=args.module,
            fortran_file=Path(args.fortran),
            python_file=Path(args.python),
            output_dir=Path(args.output),
        )
    else:
        parser.print_help()
        console.print("\n[yellow]Please specify either --interactive, --all, or provide all required arguments[/yellow]")


if __name__ == "__main__":
    main()

