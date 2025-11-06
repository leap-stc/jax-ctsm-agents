#!/usr/bin/env python3
"""
Verification script to test JSON-based translation system.

This script verifies that:
1. JSON files can be loaded
2. Module information can be extracted
3. Enhanced context can be built
4. The translator initializes correctly

Run this before attempting actual translations to catch issues early.
"""

from pathlib import Path
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from jax_agents.translator import TranslatorAgent

console = Console()


def verify_json_files(analysis_path: Path, units_path: Path) -> bool:
    """Verify JSON files exist and can be loaded."""
    console.print("\n[bold cyan]Step 1: Verifying JSON Files[/bold cyan]")
    
    # Check existence
    if not analysis_path.exists():
        console.print(f"[red]✗ analysis_results.json not found at: {analysis_path}[/red]")
        return False
    console.print(f"[green]✓ Found analysis_results.json[/green]")
    
    if not units_path.exists():
        console.print(f"[red]✗ translation_units.json not found at: {units_path}[/red]")
        return False
    console.print(f"[green]✓ Found translation_units.json[/green]")
    
    # Check loading
    try:
        with open(analysis_path, 'r') as f:
            analysis = json.load(f)
        console.print(f"[green]✓ Loaded analysis_results.json ({len(str(analysis))} chars)[/green]")
    except Exception as e:
        console.print(f"[red]✗ Failed to load analysis_results.json: {e}[/red]")
        return False
    
    try:
        with open(units_path, 'r') as f:
            units = json.load(f)
        console.print(f"[green]✓ Loaded translation_units.json ({len(str(units))} chars)[/green]")
    except Exception as e:
        console.print(f"[red]✗ Failed to load translation_units.json: {e}[/red]")
        return False
    
    # Show statistics
    num_modules = len(analysis.get("parsing", {}).get("modules", {}))
    num_units = len(units.get("translation_units", []))
    
    console.print(f"\n[dim]Statistics:[/dim]")
    console.print(f"  Modules: {num_modules}")
    console.print(f"  Translation units: {num_units}")
    
    return True


def verify_module_extraction(translator: TranslatorAgent, sample_modules: list) -> bool:
    """Verify that module information can be extracted."""
    console.print("\n[bold cyan]Step 2: Verifying Module Extraction[/bold cyan]")
    
    success = True
    table = Table(title="Sample Module Extraction")
    table.add_column("Module", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("File Path", style="dim")
    
    for module_name in sample_modules:
        try:
            module_info = translator._extract_module_info(module_name)
            if module_info:
                file_path = module_info.get("file_path", "N/A")
                table.add_row(module_name, "[green]✓ Found[/green]", file_path)
            else:
                table.add_row(module_name, "[red]✗ Not Found[/red]", "N/A")
                success = False
        except Exception as e:
            table.add_row(module_name, f"[red]✗ Error[/red]", str(e))
            success = False
    
    console.print(table)
    return success


def verify_context_building(translator: TranslatorAgent, module_name: str) -> bool:
    """Verify enhanced context can be built."""
    console.print(f"\n[bold cyan]Step 3: Verifying Context Building for '{module_name}'[/bold cyan]")
    
    try:
        # Extract module info
        module_info = translator._extract_module_info(module_name)
        if not module_info:
            console.print(f"[red]✗ Module '{module_name}' not found[/red]")
            return False
        
        # Build context
        context = translator._build_enhanced_context(module_name, module_info)
        
        # Display context summary
        console.print("\n[green]✓ Successfully built enhanced context[/green]")
        console.print("\n[bold]Context Summary:[/bold]")
        
        # Dependencies
        deps_uses = context.get("dependencies", {}).get("uses", [])
        deps_used_by = context.get("dependencies", {}).get("used_by", [])
        console.print(f"  Uses {len(deps_uses)} modules: {', '.join(deps_uses[:5])}{' ...' if len(deps_uses) > 5 else ''}")
        console.print(f"  Used by {len(deps_used_by)} modules: {', '.join(deps_used_by[:5])}{' ...' if len(deps_used_by) > 5 else ''}")
        
        # Translation units
        units = context.get("translation_units", [])
        unit_types = {}
        for unit in units:
            ut = unit.get("unit_type", "unknown")
            unit_types[ut] = unit_types.get(ut, 0) + 1
        
        console.print(f"\n  Translation Units ({len(units)} total):")
        for unit_type, count in unit_types.items():
            console.print(f"    {unit_type}: {count}")
        
        # Complexity
        complexity = context.get("complexity_info", {})
        console.print(f"\n  Complexity:")
        console.print(f"    Avg: {complexity.get('avg_complexity', 0):.2f}")
        console.print(f"    Max: {complexity.get('max_complexity', 0):.2f}")
        console.print(f"    Has split functions: {complexity.get('has_split_functions', False)}")
        
        effort = complexity.get("effort_breakdown", {})
        console.print(f"\n  Effort Breakdown:")
        console.print(f"    Low: {effort.get('low', 0)}")
        console.print(f"    Medium: {effort.get('medium', 0)}")
        console.print(f"    High: {effort.get('high', 0)}")
        
        return True
        
    except Exception as e:
        console.print(f"[red]✗ Failed to build context: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return False


def verify_translator_init(analysis_path: Path, units_path: Path, jax_ctsm_dir: Path, fortran_root: Path) -> TranslatorAgent:
    """Verify translator can be initialized."""
    console.print("\n[bold cyan]Step 4: Initializing Translator[/bold cyan]")
    
    try:
        translator = TranslatorAgent(
            analysis_results_path=analysis_path,
            translation_units_path=units_path,
            jax_ctsm_dir=jax_ctsm_dir,
            fortran_root=fortran_root,
        )
        console.print("[green]✓ Translator initialized successfully[/green]")
        
        # Show loaded data
        has_analysis = translator.analysis_results is not None
        has_units = translator.translation_units is not None
        has_patterns = len(translator.reference_patterns) > 0
        
        console.print(f"  Analysis results loaded: {has_analysis}")
        console.print(f"  Translation units loaded: {has_units}")
        console.print(f"  Reference patterns loaded: {has_patterns} patterns")
        
        return translator
        
    except Exception as e:
        console.print(f"[red]✗ Failed to initialize translator: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return None


def main():
    """Run verification tests."""
    
    console.print(Panel.fit(
        "[bold cyan]JSON-Based Translation System Verification[/bold cyan]\n"
        "This script verifies that the enhanced translation system is working correctly.",
        border_style="cyan"
    ))
    
    # Setup paths
    project_root = Path("/burg-archive/home/mck2199")
    
    # JSON files are in jax-agents folder
    analysis_dir = project_root / "jax-agents/static_analysis_output"
    analysis_path = analysis_dir / "analysis_results.json"
    units_path = analysis_dir / "translation_units.json"
    jax_ctsm_dir = project_root / "jax-ctsm"
    fortran_root = project_root / "CLM-ml_v1"
    
    # Run verification steps
    all_passed = True
    
    # Step 1: Verify JSON files
    if not verify_json_files(analysis_path, units_path):
        console.print("\n[red]✗ JSON file verification failed[/red]")
        all_passed = False
        return
    
    # Step 2: Initialize translator
    translator = verify_translator_init(analysis_path, units_path, jax_ctsm_dir, fortran_root)
    if not translator:
        console.print("\n[red]✗ Translator initialization failed[/red]")
        all_passed = False
        return
    
    # Step 3: Verify module extraction
    sample_modules = ["clm_varctl", "SoilStateType", "SoilTemperatureMod"]
    if not verify_module_extraction(translator, sample_modules):
        console.print("\n[yellow]⚠ Some modules could not be extracted[/yellow]")
    
    # Step 4: Verify context building
    if not verify_context_building(translator, "SoilStateType"):
        console.print("\n[red]✗ Context building failed[/red]")
        all_passed = False
        return
    
    # Final summary
    console.print("\n" + "="*60)
    if all_passed:
        console.print(Panel.fit(
            "[bold green]✓ All Verification Tests Passed![/bold green]\n\n"
            "The JSON-based translation system is ready to use.\n"
            "You can now run:\n"
            "  python examples/translate_with_json.py\n"
            "  python examples/batch_translate_modules.py",
            border_style="green"
        ))
    else:
        console.print(Panel.fit(
            "[bold red]✗ Some Verification Tests Failed[/bold red]\n\n"
            "Please fix the issues before attempting translation.\n"
            "Check the output above for details.",
            border_style="red"
        ))


if __name__ == "__main__":
    main()

