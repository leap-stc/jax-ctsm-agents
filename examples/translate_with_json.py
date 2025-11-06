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
    
    # Example 1: Translate a simple module (low complexity)
    console.print("[bold cyan]Example 1: Translating 'clm_varctl' (simple module)[/bold cyan]")
    try:
        result1 = translator.translate_module(
            module_name="clm_varctl",
            output_dir=output_dir / "clm_varctl"
        )
        console.print(f"[green]✓ Translated clm_varctl successfully![/green]")
        console.print(f"[dim]Generated {len(result1.physics_code)} chars of physics code[/dim]\n")
    except Exception as e:
        console.print(f"[red]Error translating clm_varctl: {e}[/red]\n")
    
    # Example 2: Translate a medium complexity module
    console.print("[bold cyan]Example 2: Translating 'SoilStateType' (medium complexity)[/bold cyan]")
    try:
        result2 = translator.translate_module(
            module_name="SoilStateType",
            output_dir=output_dir / "SoilStateType"
        )
        console.print(f"[green]✓ Translated SoilStateType successfully![/green]")
        console.print(f"[dim]Generated {len(result2.physics_code)} chars of physics code[/dim]\n")
    except Exception as e:
        console.print(f"[red]Error translating SoilStateType: {e}[/red]\n")
    
    # Example 3: Translate a complex module with dependencies
    console.print("[bold cyan]Example 3: Translating 'SoilTemperatureMod' (high complexity)[/bold cyan]")
    try:
        result3 = translator.translate_module(
            module_name="SoilTemperatureMod",
            output_dir=output_dir / "SoilTemperatureMod"
        )
        console.print(f"[green]✓ Translated SoilTemperatureMod successfully![/green]")
        console.print(f"[dim]Generated {len(result3.physics_code)} chars of physics code[/dim]\n")
    except Exception as e:
        console.print(f"[red]Error translating SoilTemperatureMod: {e}[/red]\n")
    
    console.print("[bold green]✨ Translation examples complete![/bold green]")


if __name__ == "__main__":
    main()

