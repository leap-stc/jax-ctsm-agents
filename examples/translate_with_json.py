#!/usr/bin/env python3
"""
Example: Translate Fortran modules using static analysis JSON files.

This demonstrates how to use the updated TranslatorAgent with 
analysis_results.json and translation_units.json as inputs.
"""

from pathlib import Path
from jax_agents.translator import TranslatorAgent
from rich.console import Console

console = Console()


def main():
    """Example translation workflow with JSON files."""
    
    # Setup paths
    project_root = Path("/burg-archive/home/mck2199")
    
    # JSON files are in jax-agents folder
    analysis_dir = project_root / "jax-agents/static_analysis_output"
    analysis_results_json = analysis_dir / "analysis_results.json"
    translation_units_json = analysis_dir / "translation_units.json"
    
    # Path to jax-ctsm for reference patterns
    jax_ctsm_dir = project_root / "jax-ctsm"
    
    # Path to Fortran source files
    fortran_root = project_root / "CLM-ml_v1"
    
    # Output directory for translated code
    output_dir = project_root / "jax-agents/translated_modules"
    
    # Verify JSON files exist
    if not analysis_results_json.exists():
        console.print(f"[red]Error: {analysis_results_json} not found[/red]")
        return
    
    if not translation_units_json.exists():
        console.print(f"[red]Error: {translation_units_json} not found[/red]")
        return
    
    console.print("[bold green]🚀 Initializing Translator Agent with JSON files...[/bold green]")
    
    # Initialize translator with JSON files
    translator = TranslatorAgent(
        analysis_results_path=analysis_results_json,
        translation_units_path=translation_units_json,
        jax_ctsm_dir=jax_ctsm_dir,
        fortran_root=fortran_root,
        # Optional: override LLM settings
        model="claude-sonnet-4-5",
        temperature=0.0,
        max_tokens=48000,
    )
    
    console.print("[green]✓ Translator initialized successfully![/green]\n")
    
    # Track overall costs
    total_cost = 0.0
    total_input_tokens = 0
    total_output_tokens = 0
    module_costs = []
    
    # Example 1: Translate a simple module (low complexity)
    console.print("[bold cyan]Example 1: Translating 'clm_varctl' (simple module)[/bold cyan]")
    try:
        result1 = translator.translate_module(
            module_name="clm_varctl",
            output_dir=output_dir / "clm_varctl"
        )
        
        # Get cost info
        cost_info = translator.get_cost_estimate()
        module_cost = cost_info['total_cost_usd']
        module_costs.append(("clm_varctl", cost_info))
        total_cost += module_cost
        total_input_tokens += cost_info['input_tokens']
        total_output_tokens += cost_info['output_tokens']
        
        console.print(f"[green]✓ Translated clm_varctl successfully![/green]")
        console.print(f"[dim]Generated {len(result1.physics_code)} chars of physics code[/dim]")
        console.print(f"[yellow]💰 Cost: ${module_cost:.4f} ({cost_info['input_tokens']:,} in / {cost_info['output_tokens']:,} out)[/yellow]\n")
    except Exception as e:
        console.print(f"[red]Error translating clm_varctl: {e}[/red]\n")
    
    # Example 2: Translate a medium complexity module
    console.print("[bold cyan]Example 2: Translating 'SoilStateType' (medium complexity)[/bold cyan]")
    
    # Reset translator token counts for per-module tracking
    translator.total_input_tokens = 0
    translator.total_output_tokens = 0
    
    try:
        result2 = translator.translate_module(
            module_name="SoilStateType",
            output_dir=output_dir / "SoilStateType"
        )
        
        # Get cost info
        cost_info = translator.get_cost_estimate()
        module_cost = cost_info['total_cost_usd']
        module_costs.append(("SoilStateType", cost_info))
        total_cost += module_cost
        total_input_tokens += cost_info['input_tokens']
        total_output_tokens += cost_info['output_tokens']
        
        console.print(f"[green]✓ Translated SoilStateType successfully![/green]")
        console.print(f"[dim]Generated {len(result2.physics_code)} chars of physics code[/dim]")
        console.print(f"[yellow]💰 Cost: ${module_cost:.4f} ({cost_info['input_tokens']:,} in / {cost_info['output_tokens']:,} out)[/yellow]\n")
    except Exception as e:
        console.print(f"[red]Error translating SoilStateType: {e}[/red]\n")
    
    # Example 3: Translate a complex module with dependencies
    console.print("[bold cyan]Example 3: Translating 'SoilTemperatureMod' (high complexity)[/bold cyan]")
    
    # Reset translator token counts for per-module tracking
    translator.total_input_tokens = 0
    translator.total_output_tokens = 0
    
    try:
        result3 = translator.translate_module(
            module_name="SoilTemperatureMod",
            output_dir=output_dir / "SoilTemperatureMod"
        )
        
        # Get cost info
        cost_info = translator.get_cost_estimate()
        module_cost = cost_info['total_cost_usd']
        module_costs.append(("SoilTemperatureMod", cost_info))
        total_cost += module_cost
        total_input_tokens += cost_info['input_tokens']
        total_output_tokens += cost_info['output_tokens']
        
        console.print(f"[green]✓ Translated SoilTemperatureMod successfully![/green]")
        console.print(f"[dim]Generated {len(result3.physics_code)} chars of physics code[/dim]")
        console.print(f"[yellow]💰 Cost: ${module_cost:.4f} ({cost_info['input_tokens']:,} in / {cost_info['output_tokens']:,} out)[/yellow]\n")
    except Exception as e:
        console.print(f"[red]Error translating SoilTemperatureMod: {e}[/red]\n")
    
    # Display cost summary
    console.print("\n" + "="*80)
    console.print("[bold green]✨ Translation complete![/bold green]")
    console.print("="*80 + "\n")
    
    console.print("[bold cyan]💰 Cost Summary by Module:[/bold cyan]\n")
    for module_name, cost_info in module_costs:
        console.print(f"  [cyan]{module_name:25s}[/cyan] ${cost_info['total_cost_usd']:>8.4f}  "
                     f"({cost_info['input_tokens']:>8,} in / {cost_info['output_tokens']:>8,} out)")
    
    console.print("\n" + "-"*80)
    console.print(f"[bold yellow]Total Cost:                    ${total_cost:>8.4f}[/bold yellow]")
    console.print(f"[dim]Total Input Tokens:            {total_input_tokens:>8,}[/dim]")
    console.print(f"[dim]Total Output Tokens:           {total_output_tokens:>8,}[/dim]")
    console.print(f"[dim]Total Tokens:                  {total_input_tokens + total_output_tokens:>8,}[/dim]")
    console.print("="*80)


if __name__ == "__main__":
    main()

