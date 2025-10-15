#!/usr/bin/env python3
"""
Example: Translate with custom analysis and context.

This example shows how to use the Static Analysis and Translator agents
separately, with custom configuration.
"""

from pathlib import Path
from jax_agents import StaticAnalysisAgent, TranslatorAgent
from rich.console import Console

console = Console()


def main():
    """Two-step conversion with custom analysis."""
    
    # Paths
    fortran_file = Path("/burg-archive/home/mck2199/CTSM/src/biogeochem/CNGRespMod.F90")
    jax_ctsm_dir = Path("/burg-archive/home/mck2199/jax-ctsm")
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)
    
    console.print("[bold cyan]Two-Step Translation Example[/bold cyan]\n")
    
    # Step 1: Analyze
    console.print("[bold yellow]Step 1: Static Analysis[/bold yellow]\n")
    
    analyzer = StaticAnalysisAgent()
    analysis = analyzer.analyze_module(
        fortran_file=fortran_file,
        extract_physics=True,  # Get detailed physics info
    )
    
    # Save analysis for review
    analysis.save(output_dir / "analysis.json")
    
    console.print(f"\n[green]✓[/green] Analysis complete: {len(analysis.subroutines)} subroutines found")
    
    # Step 2: Translate
    console.print("\n[bold yellow]Step 2: Translation to JAX[/bold yellow]\n")
    
    translator = TranslatorAgent(jax_ctsm_dir=jax_ctsm_dir)
    
    translation = translator.translate_module(
        fortran_file=fortran_file,
        analysis=analysis,
        output_dir=output_dir,
    )
    
    console.print(f"\n[green]✓[/green] Translation complete")
    
    # Display generated code preview
    console.print("\n[bold]Generated Code Preview:[/bold]")
    console.print("[dim]" + "="*80 + "[/dim]")
    
    # Show first 20 lines of physics code
    lines = translation.physics_code.split('\n')[:20]
    for line in lines:
        console.print(f"[dim]{line}[/dim]")
    
    console.print("[dim]" + "="*80 + "[/dim]")
    console.print(f"[dim]... {len(translation.physics_code.split(chr(10))) - 20} more lines[/dim]\n")
    
    # Cost summary
    analyzer_cost = analyzer.get_cost_estimate()
    translator_cost = translator.get_cost_estimate()
    total_cost = analyzer_cost['total_cost_usd'] + translator_cost['total_cost_usd']
    
    console.print(f"[bold]Cost Breakdown:[/bold]")
    console.print(f"  Analysis:    ${analyzer_cost['total_cost_usd']:.4f}")
    console.print(f"  Translation: ${translator_cost['total_cost_usd']:.4f}")
    console.print(f"  [bold]Total:       ${total_cost:.4f}[/bold]")


if __name__ == "__main__":
    main()

