#!/usr/bin/env python3
"""
Example: Analyze a Fortran module without translation.

This example shows how to use the Static Analysis agent independently
to understand Fortran code structure.
"""

from pathlib import Path
from jax_agents import StaticAnalysisAgent
from rich.console import Console
from rich.json import JSON

console = Console()


def main():
    """Analyze CNPhenologyMod.F90 to understand its structure."""
    
    # Setup
    fortran_file = Path("/burg-archive/home/mck2199/CTSM/src/biogeochem/CNPhenologyMod.F90")
    
    console.print("[bold cyan]Static Analysis Example[/bold cyan]\n")
    console.print(f"[bold]Analyzing:[/bold] {fortran_file.name}\n")
    
    # Initialize analyzer
    analyzer = StaticAnalysisAgent()
    
    # Perform analysis
    analysis = analyzer.analyze_module(fortran_file, extract_physics=True)
    
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
    
    # Save analysis
    output_file = Path("analysis_result.json")
    analysis.save(output_file)
    
    console.print(f"[dim]Full analysis saved to {output_file}[/dim]")
    
    # Display cost
    cost = analyzer.get_cost_estimate()
    console.print(f"\n[bold]Analysis Cost:[/bold] ${cost['total_cost_usd']:.4f}")


if __name__ == "__main__":
    main()

