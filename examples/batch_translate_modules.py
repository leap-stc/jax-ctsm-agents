#!/usr/bin/env python3
"""
Batch translate all Fortran modules to JAX using analysis JSON files.

This script translates modules in the recommended dependency order,
skipping modules that have already been translated.
"""

from pathlib import Path
import json
import time
from typing import List, Dict
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

from jax_agents.translator import TranslatorAgent

console = Console()


def load_json(path: Path) -> Dict:
    """Load JSON file."""
    with open(path, 'r') as f:
        return json.load(f)


def get_translation_order(analysis_results: Dict) -> List[str]:
    """Get recommended translation order from analysis results."""
    return analysis_results.get("translation", {}).get("translation_order", [])


def get_module_complexity(translation_units: Dict, module_name: str) -> Dict:
    """Get complexity information for a module."""
    units = translation_units.get("translation_units", [])
    module_units = [u for u in units if u.get("module_name", "").lower() == module_name.lower()]
    
    if not module_units:
        return {"total_units": 0, "avg_complexity": 0, "estimated_effort": "unknown"}
    
    complexities = [u.get("complexity_score", 0) for u in module_units]
    efforts = [u.get("estimated_effort", "unknown") for u in module_units]
    
    # Count effort levels
    effort_counts = {
        "low": efforts.count("low"),
        "medium": efforts.count("medium"),
        "high": efforts.count("high"),
    }
    
    # Determine overall effort (use highest)
    if effort_counts["high"] > 0:
        overall_effort = "high"
    elif effort_counts["medium"] > 0:
        overall_effort = "medium"
    else:
        overall_effort = "low"
    
    return {
        "total_units": len(module_units),
        "avg_complexity": sum(complexities) / len(complexities) if complexities else 0,
        "max_complexity": max(complexities) if complexities else 0,
        "estimated_effort": overall_effort,
        "has_split_functions": any(u.get("unit_type") == "inner" for u in module_units),
    }


def is_module_translated(output_dir: Path, module_name: str) -> bool:
    """Check if module has already been translated."""
    module_dir = output_dir / module_name
    physics_file = module_dir / f"{module_name}.py"
    return physics_file.exists()


def translate_all_modules(
    translator: TranslatorAgent,
    translation_order: List[str],
    translation_units: Dict,
    output_dir: Path,
    skip_existing: bool = True,
    max_modules: int = None,
):
    """
    Translate all modules in dependency order.
    
    Args:
        translator: Initialized TranslatorAgent
        translation_order: List of module names in translation order
        translation_units: Translation units data for complexity info
        output_dir: Output directory for translated modules
        skip_existing: Skip modules that have already been translated
        max_modules: Maximum number of modules to translate (None = all)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Statistics
    stats = {
        "total": len(translation_order),
        "translated": 0,
        "skipped": 0,
        "failed": 0,
        "time_taken": {},
    }
    
    console.print(f"\n[bold green]📦 Batch Translation Plan[/bold green]")
    console.print(f"Total modules: {len(translation_order)}")
    if max_modules:
        console.print(f"Limit: Translating first {max_modules} modules")
    console.print(f"Skip existing: {skip_existing}")
    console.print(f"Output directory: {output_dir}\n")
    
    # Create summary table
    table = Table(title="Module Translation Summary")
    table.add_column("Module", style="cyan")
    table.add_column("Units", justify="right")
    table.add_column("Complexity", justify="right")
    table.add_column("Effort", justify="center")
    table.add_column("Status", justify="center")
    
    modules_to_process = translation_order[:max_modules] if max_modules else translation_order
    
    for i, module_name in enumerate(modules_to_process, 1):
        # Get complexity info
        complexity_info = get_module_complexity(translation_units, module_name)
        
        # Check if already translated
        if skip_existing and is_module_translated(output_dir, module_name):
            stats["skipped"] += 1
            table.add_row(
                module_name,
                str(complexity_info["total_units"]),
                f"{complexity_info['avg_complexity']:.1f}",
                complexity_info["estimated_effort"],
                "[yellow]⊘ Skipped (exists)[/yellow]"
            )
            continue
        
        console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
        console.print(f"[bold]Module {i}/{len(modules_to_process)}: {module_name}[/bold]")
        console.print(f"[dim]Units: {complexity_info['total_units']} | "
                     f"Complexity: {complexity_info['avg_complexity']:.1f} | "
                     f"Effort: {complexity_info['estimated_effort']}[/dim]")
        
        if complexity_info["has_split_functions"]:
            console.print("[yellow]⚠ Contains split functions[/yellow]")
        
        # Translate module
        start_time = time.time()
        try:
            result = translator.translate_module(
                module_name=module_name,
                output_dir=output_dir / module_name
            )
            
            elapsed = time.time() - start_time
            stats["time_taken"][module_name] = elapsed
            stats["translated"] += 1
            
            # Show success
            lines_generated = len(result.physics_code.split('\n'))
            console.print(f"[green]✓ Success! Generated {lines_generated} lines in {elapsed:.1f}s[/green]")
            
            table.add_row(
                module_name,
                str(complexity_info["total_units"]),
                f"{complexity_info['avg_complexity']:.1f}",
                complexity_info["estimated_effort"],
                f"[green]✓ {elapsed:.1f}s[/green]"
            )
            
        except Exception as e:
            elapsed = time.time() - start_time
            stats["failed"] += 1
            console.print(f"[red]✗ Failed: {str(e)}[/red]")
            
            table.add_row(
                module_name,
                str(complexity_info["total_units"]),
                f"{complexity_info['avg_complexity']:.1f}",
                complexity_info["estimated_effort"],
                f"[red]✗ Error[/red]"
            )
            
            # Log error details
            error_log = output_dir / f"errors_{module_name}.log"
            with open(error_log, 'w') as f:
                f.write(f"Module: {module_name}\n")
                f.write(f"Error: {str(e)}\n")
                f.write(f"Time: {elapsed:.1f}s\n")
    
    # Display final summary
    console.print("\n" + "="*60)
    console.print(table)
    
    console.print(f"\n[bold green]📊 Final Statistics[/bold green]")
    console.print(f"Total modules: {stats['total']}")
    console.print(f"[green]✓ Translated: {stats['translated']}[/green]")
    console.print(f"[yellow]⊘ Skipped: {stats['skipped']}[/yellow]")
    console.print(f"[red]✗ Failed: {stats['failed']}[/red]")
    
    if stats["time_taken"]:
        total_time = sum(stats["time_taken"].values())
        avg_time = total_time / len(stats["time_taken"])
        console.print(f"\n[cyan]⏱ Total time: {total_time:.1f}s[/cyan]")
        console.print(f"[cyan]⏱ Average time per module: {avg_time:.1f}s[/cyan]")
    
    # Show slowest modules
    if stats["time_taken"]:
        sorted_times = sorted(stats["time_taken"].items(), key=lambda x: x[1], reverse=True)
        console.print(f"\n[yellow]🐌 Slowest modules:[/yellow]")
        for module, elapsed in sorted_times[:5]:
            console.print(f"  {module}: {elapsed:.1f}s")


def main():
    """Main batch translation workflow."""
    
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
    
    # Load JSON files
    console.print("[cyan]Loading analysis results...[/cyan]")
    analysis_results = load_json(analysis_results_json)
    translation_units = load_json(translation_units_json)
    
    # Get translation order
    translation_order = get_translation_order(analysis_results)
    if not translation_order:
        console.print("[yellow]Warning: No translation order found, using all modules[/yellow]")
        translation_order = list(analysis_results.get("parsing", {}).get("modules", {}).keys())
    
    console.print(f"[green]✓ Found {len(translation_order)} modules to translate[/green]")
    
    # Initialize translator
    console.print("\n[cyan]Initializing Translator Agent...[/cyan]")
    translator = TranslatorAgent(
        analysis_results_path=analysis_results_json,
        translation_units_path=translation_units_json,
        jax_ctsm_dir=jax_ctsm_dir,
        fortran_root=fortran_root,
    )
    console.print("[green]✓ Translator initialized![/green]")
    
    # Translate all modules
    translate_all_modules(
        translator=translator,
        translation_order=translation_order,
        translation_units=translation_units,
        output_dir=output_dir,
        skip_existing=True,  # Change to False to re-translate existing modules
        max_modules=None,    # Set to a number to limit translations (e.g., 5 for testing)
    )
    
    console.print("\n[bold green]✨ Batch translation complete![/bold green]")


if __name__ == "__main__":
    main()

