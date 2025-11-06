#!/usr/bin/env python3
"""
Example: Translate from saved analysis.

This example shows how to load a previously saved analysis and use it
for translation. This is useful for:
1. Separating analysis and translation steps
2. Reusing analysis results
3. Debugging translation without re-analyzing
"""

from pathlib import Path
from jax_agents import AnalysisResult, TranslatorAgent
from rich.console import Console

console = Console()


def main():
    """Translate a Fortran module using pre-saved analysis."""
    
    # Paths
    analysis_file = Path("analysis_result.json")
    fortran_file = Path("/burg-archive/home/mck2199/CTSM/src/biogeochem/CNMRespMod.F90")
    jax_ctsm_dir = Path("/burg-archive/home/mck2199/jax-ctsm")
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)
    
    console.print("[bold cyan]Translation from Saved Analysis[/bold cyan]\n")
    
    # Load pre-computed analysis
    console.print(f"[bold]Loading analysis from:[/bold] {analysis_file}")
    
    if not analysis_file.exists():
        console.print(f"[red]✗ Error: Analysis file not found: {analysis_file}[/red]")
        console.print("\n[yellow]Please run the analysis step first:[/yellow]")
        console.print("[dim]  python examples/analyze_module.py[/dim]\n")
        return
    
    analysis = AnalysisResult.load(analysis_file)
    console.print(f"[green]✓[/green] Loaded analysis for: {analysis.module_name}")
    console.print(f"  • {len(analysis.subroutines)} subroutines")
    console.print(f"  • {len(analysis.data_types)} data types")
    console.print(f"  • {len(analysis.dependencies.modules)} dependencies\n")
    
    # Initialize translator
    console.print("[bold]Initializing translator...[/bold]")
    translator = TranslatorAgent(jax_ctsm_dir=jax_ctsm_dir)
    
    # Perform translation
    console.print(f"\n[bold yellow]Translating {fortran_file.name} to JAX...[/bold yellow]\n")
    
    translation = translator.translate_module(
        fortran_file=fortran_file,
        analysis=analysis,
        output_dir=output_dir,
    )
    
    console.print(f"\n[bold green]✓ Translation Complete![/bold green]\n")
    
    # Display code stats
    console.print("[bold]Generated Code Statistics:[/bold]")
    physics_lines = len(translation.physics_code.split('\n'))
    console.print(f"  • Physics module: {physics_lines} lines")
    
    if translation.params_code:
        params_lines = len(translation.params_code.split('\n'))
        console.print(f"  • Parameters:     {params_lines} lines")
    
    if translation.test_code:
        test_lines = len(translation.test_code.split('\n'))
        console.print(f"  • Tests:          {test_lines} lines")
    
    # Show code preview
    console.print("\n[bold]Code Preview (first 30 lines):[/bold]")
    console.print("[dim]" + "="*80 + "[/dim]")
    
    lines = translation.physics_code.split('\n')[:30]
    for i, line in enumerate(lines, 1):
        console.print(f"[dim]{i:3d} | {line}[/dim]")
    
    if physics_lines > 30:
        console.print(f"[dim]... {physics_lines - 30} more lines[/dim]")
    
    console.print("[dim]" + "="*80 + "[/dim]\n")
    
    # Cost summary
    translator_cost = translator.get_cost_estimate()
    console.print(f"[bold]Translation Cost:[/bold] ${translator_cost['total_cost_usd']:.4f}")
    console.print(f"  • Input tokens:  {translator_cost['input_tokens']:,}")
    console.print(f"  • Output tokens: {translator_cost['output_tokens']:,}")
    
    console.print(f"\n[green]✓ Files saved to: {output_dir}[/green]")


if __name__ == "__main__":
    main()

