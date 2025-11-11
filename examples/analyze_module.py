#!/usr/bin/env python3
"""
Example: Analyze a Fortran module without translation.

This example shows how to use the Static Analysis agent independently
to understand Fortran code structure.
"""

import argparse
from pathlib import Path
from jax_agents import StaticAnalysisAgent
from rich.console import Console
from rich.json import JSON

console = Console()


def analyze_module(fortran_file: Path, extract_physics: bool = False, output_file: Path = None):
    """
    Analyze a Fortran module.
    
    Args:
        fortran_file: Path to Fortran module
        extract_physics: Extract detailed physics information
        output_file: Optional output file path
    """
    if not fortran_file.exists():
        console.print(f"[red]✗ Error: File not found: {fortran_file}[/red]")
        return None
    
    console.print("[bold cyan]Static Analysis Example[/bold cyan]\n")
    console.print(f"[bold]Analyzing:[/bold] {fortran_file.name}\n")
    
    # Initialize analyzer
    analyzer = StaticAnalysisAgent()
    
    # Perform analysis
    console.print(f"[dim]Extract physics: {extract_physics}[/dim]\n")
    analysis = analyzer.analyze_module(fortran_file, extract_physics=extract_physics)
    
    # Display results
    console.print("\n[bold green]Analysis Complete![/bold green]\n")
    
    # Module info
    console.print(f"[bold]Module:[/bold] {analysis.module_name}")
    console.print(f"[bold]Description:[/bold] {analysis.description}\n")
    
    # Dependencies
    console.print("[bold]Dependencies:[/bold]")
    console.print(f"  Modules: {', '.join(analysis.dependencies.modules[:5])}")
    if len(analysis.dependencies.modules) > 5:
        console.print(f"  ... and {len(analysis.dependencies.modules) - 5} more")
    console.print()
    
    # Subroutines
    console.print(f"[bold]Subroutines:[/bold] ({len(analysis.subroutines)} found)")
    for i, sub in enumerate(analysis.subroutines[:3], 1):
        console.print(f"  {i}. {sub.name}")
        console.print(f"     Purpose: {sub.purpose}")
        console.print(f"     Inputs: {len(sub.inputs)}, Outputs: {len(sub.outputs)}")
    console.print()
    
    # Translation notes
    console.print("[bold]Translation Challenges:[/bold]")
    challenges = analysis.jax_translation_notes.get("challenges", [])
    for i, challenge in enumerate(challenges[:3], 1):
        console.print(f"  {i}. {challenge}")
    console.print()
    
    # Save analysis for later use
    if output_file is None:
        output_file = Path(f"analysis_{analysis.module_name}.json")
    
    analysis.save(output_file)
    
    console.print(f"\n[green]✓ Full analysis saved to {output_file}[/green]")
    console.print(f"[dim]  Use this file with: python examples/translate_from_analysis.py {output_file}[/dim]")
    
    # Display cost
    cost = analyzer.get_cost_estimate()
    console.print(f"\n[bold]Analysis Cost:[/bold] ${cost['total_cost_usd']:.4f}")
    
    return analysis


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Analyze a Fortran module structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a specific module
  python analyze_module.py /path/to/Module.F90
  
  # With detailed physics extraction
  python analyze_module.py /path/to/Module.F90 --extract-physics
  
  # Custom output file
  python analyze_module.py /path/to/Module.F90 -o my_analysis.json
  
  # Interactive mode
  python analyze_module.py --interactive
  
  # Use default example module
  python analyze_module.py --example
        """
    )
    
    parser.add_argument(
        "fortran_file",
        nargs="?",
        help="Path to Fortran module file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output JSON file path (default: analysis_<module>.json)"
    )
    parser.add_argument(
        "--extract-physics",
        action="store_true",
        help="Extract detailed physics information (uses more tokens)"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive mode - prompts for inputs"
    )
    parser.add_argument(
        "--example",
        action="store_true",
        help="Run with default example module (CNMRespMod.F90)"
    )
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive:
        console.print("\n[bold cyan]Interactive Module Analysis[/bold cyan]\n")
        
        console.print("[cyan]Enter path to Fortran module:[/cyan]")
        fortran_path = input("> ").strip()
        fortran_file = Path(fortran_path)
        
        console.print("\n[cyan]Extract detailed physics? (y/n, default: n):[/cyan]")
        extract_physics = input("> ").strip().lower() == 'y'
        
        console.print("\n[cyan]Output file (press Enter for default):[/cyan]")
        output_path = input("> ").strip()
        output_file = Path(output_path) if output_path else None
        
        analyze_module(fortran_file, extract_physics, output_file)
        return
    
    # Example mode
    if args.example:
        console.print("[cyan]Running with example module: CNMRespMod.F90[/cyan]\n")
        fortran_file = Path("/burg-archive/home/mck2199/CTSM/src/biogeochem/CNMRespMod.F90")
        output_file = Path(args.output) if args.output else Path("analysis_result.json")
        analyze_module(fortran_file, args.extract_physics, output_file)
        return
    
    # CLI mode
    if args.fortran_file:
        fortran_file = Path(args.fortran_file)
        output_file = Path(args.output) if args.output else None
        analyze_module(fortran_file, args.extract_physics, output_file)
    else:
        parser.print_help()
        console.print("\n[yellow]Please provide a Fortran file, use --interactive, or --example[/yellow]")


if __name__ == "__main__":
    main()

