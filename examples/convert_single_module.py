#!/usr/bin/env python3
"""
Example: Convert a single Fortran module to JAX.

This example demonstrates the basic workflow for converting a CTSM Fortran
module to JAX using the orchestrator agent.
"""

from pathlib import Path
from jax_agents import OrchestratorAgent
from rich.console import Console

console = Console()


def main():
    """Convert CNGRespMod.F90 (Growth Respiration) to JAX."""
    
    # Setup paths
    ctsm_dir = Path("/burg-archive/home/mck2199/CTSM")
    jax_ctsm_dir = Path("/burg-archive/home/mck2199/jax-ctsm")
    
    # Initialize orchestrator
    console.print("[bold cyan]Initializing JAX-CTSM Translation Orchestrator[/bold cyan]\n")
    
    orchestrator = OrchestratorAgent(
        ctsm_dir=ctsm_dir,
        jax_ctsm_dir=jax_ctsm_dir,
    )
    
    # Convert module
    fortran_file = "src/biogeochem/CNGRespMod.F90"
    
    console.print(f"[bold]Converting:[/bold] {fortran_file}\n")
    
    result = orchestrator.convert_module(
        fortran_file=fortran_file,
        output_dir=jax_ctsm_dir / "src" / "jax_ctsm" / "physics",
        generate_report=True,
    )
    
    # Display results
    console.print("\n[bold green]Conversion Complete![/bold green]\n")
    
    console.print("[bold]Generated Files:[/bold]")
    for file_type, path in result.saved_files.items():
        console.print(f"  • {file_type}: {path}")
    
    console.print(f"\n[bold]Total Cost:[/bold] ${result.cost_summary['total_cost_usd']:.4f}")
    console.print(f"[bold]Total Tokens:[/bold] {result.cost_summary['total_tokens']:,}")
    
    console.print("\n[dim]See the conversion report for detailed analysis.[/dim]")


if __name__ == "__main__":
    main()

