#!/usr/bin/env python3
"""
Complete Translation Workflow with Cost Tracking.

This example demonstrates a full translation workflow with comprehensive
cost tracking across all agents: Translation, Test Generation, and Repair.
"""

import os
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from jax_agents import (
    TranslatorAgent,
    TestAgent,
    RepairAgent,
    CostTracker
)

console = Console()


def main():
    """Run complete workflow with cost tracking."""
    
    # Initialize cost tracker
    cost_tracker = CostTracker()
    
    console.print("[bold cyan]╔══════════════════════════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║  JAX-CTSM Complete Translation Workflow with Costs       ║[/bold cyan]")
    console.print("[bold cyan]╚══════════════════════════════════════════════════════════╝[/bold cyan]\n")
    
    # Setup paths
    project_root = Path(os.environ.get("PROJECT_ROOT", "/burg-archive/home/mck2199"))
    output_dir = Path(__file__).parent.parent / "translated_modules"
    output_dir.mkdir(exist_ok=True)
    
    # Modules to translate
    modules = ["clm_varctl", "SoilStateType", "SoilTemperatureMod"]
    
    # =========================================================================
    # PHASE 1: TRANSLATION
    # =========================================================================
    console.print("[bold green]═══ PHASE 1: Translation (Fortran → JAX Python) ═══[/bold green]\n")
    
    # Initialize translator
    translator = TranslatorAgent(
        project_root=project_root,
        analysis_results_path=project_root / "jax-agents/static_analysis_output/analysis_results.json",
        translation_units_path=project_root / "jax-agents/static_analysis_output/translation_units.json",
        model="claude-sonnet-4-5",
        temperature=0.0,
        max_tokens=48000,
    )
    
    translation_results = {}
    
    for module_name in modules:
        console.print(f"[cyan]Translating: {module_name}[/cyan]")
        
        # Reset translator token counts for per-module tracking
        translator.total_input_tokens = 0
        translator.total_output_tokens = 0
        
        try:
            result = translator.translate_module(
                module_name=module_name,
                output_dir=output_dir / module_name
            )
            
            translation_results[module_name] = result
            
            # Track costs
            entry = cost_tracker.add_from_agent(
                translator, 
                operation="translate",
                module_name=module_name
            )
            
            console.print(f"[green]✓ Translation complete[/green]")
            console.print(f"[yellow]  Cost: ${entry.total_cost_usd:.4f} "
                         f"({entry.input_tokens:,} in / {entry.output_tokens:,} out)[/yellow]\n")
            
        except Exception as e:
            console.print(f"[red]✗ Translation failed: {e}[/red]\n")
            continue
    
    # =========================================================================
    # PHASE 2: TEST GENERATION
    # =========================================================================
    console.print("\n[bold green]═══ PHASE 2: Test Generation ═══[/bold green]\n")
    
    # Initialize test agent
    test_agent = TestAgent(
        model="claude-sonnet-4-5",
        temperature=0.0,
        max_tokens=48000,
    )
    
    test_results = {}
    
    for module_name in modules:
        if module_name not in translation_results:
            continue
            
        console.print(f"[cyan]Generating tests for: {module_name}[/cyan]")
        
        # Reset test agent token counts
        test_agent.total_input_tokens = 0
        test_agent.total_output_tokens = 0
        
        try:
            result = translation_results[module_name]
            
            test_result = test_agent.generate_tests(
                module_name=module_name,
                fortran_code=result.original_fortran,
                python_code=result.physics_code,
                output_dir=output_dir / module_name / "tests"
            )
            
            test_results[module_name] = test_result
            
            # Track costs
            entry = cost_tracker.add_from_agent(
                test_agent,
                operation="test",
                module_name=module_name
            )
            
            console.print(f"[green]✓ Tests generated[/green]")
            console.print(f"[yellow]  Cost: ${entry.total_cost_usd:.4f} "
                         f"({entry.input_tokens:,} in / {entry.output_tokens:,} out)[/yellow]\n")
            
        except Exception as e:
            console.print(f"[red]✗ Test generation failed: {e}[/red]\n")
            continue
    
    # =========================================================================
    # PHASE 3: REPAIR (if needed)
    # =========================================================================
    console.print("\n[bold green]═══ PHASE 3: Repair (Simulated) ═══[/bold green]\n")
    console.print("[dim]Note: This is a demonstration. Actual repairs would run if tests fail.[/dim]\n")
    
    # Initialize repair agent (for demonstration)
    repair_agent = RepairAgent(
        model="claude-sonnet-4-5",
        temperature=0.0,
        max_tokens=48000,
    )
    
    console.print("[yellow]Repair agent initialized (costs would be tracked per repair)[/yellow]\n")
    
    # =========================================================================
    # FINAL COST SUMMARY
    # =========================================================================
    console.print("\n" + "="*80)
    console.print("[bold cyan]FINAL COST SUMMARY[/bold cyan]")
    console.print("="*80 + "\n")
    
    # Total costs
    total = cost_tracker.get_total_cost()
    
    # Create summary table
    table = Table(title="Cost Breakdown by Module", show_header=True, header_style="bold cyan")
    table.add_column("Module", style="cyan", width=25)
    table.add_column("Cost", justify="right", style="yellow")
    table.add_column("Input Tokens", justify="right")
    table.add_column("Output Tokens", justify="right")
    table.add_column("Total Tokens", justify="right")
    
    by_module = cost_tracker.get_cost_by_module()
    for module_name, costs in sorted(by_module.items()):
        table.add_row(
            module_name,
            f"${costs['total_cost_usd']:.4f}",
            f"{costs['input_tokens']:,}",
            f"{costs['output_tokens']:,}",
            f"{costs['input_tokens'] + costs['output_tokens']:,}"
        )
    
    console.print(table)
    console.print()
    
    # Operation breakdown
    table2 = Table(title="Cost Breakdown by Operation", show_header=True, header_style="bold cyan")
    table2.add_column("Operation", style="cyan", width=20)
    table2.add_column("Cost", justify="right", style="yellow")
    table2.add_column("Input Tokens", justify="right")
    table2.add_column("Output Tokens", justify="right")
    
    by_operation = cost_tracker.get_cost_by_operation()
    for operation, costs in sorted(by_operation.items()):
        table2.add_row(
            operation,
            f"${costs['total_cost_usd']:.4f}",
            f"{costs['input_tokens']:,}",
            f"{costs['output_tokens']:,}"
        )
    
    console.print(table2)
    console.print()
    
    # Grand total
    console.print(f"[bold yellow]╔═══════════════════════════════════════════════╗[/bold yellow]")
    console.print(f"[bold yellow]║           WORKFLOW TOTAL COST                 ║[/bold yellow]")
    console.print(f"[bold yellow]╠═══════════════════════════════════════════════╣[/bold yellow]")
    console.print(f"[bold green]║  Total Cost:         ${total['total_cost_usd']:>16.4f}  ║[/bold green]")
    console.print(f"[bold yellow]║  Total Input Tokens: {total['total_input_tokens']:>16,}  ║[/bold yellow]")
    console.print(f"[bold yellow]║  Total Output Tokens:{total['total_output_tokens']:>16,}  ║[/bold yellow]")
    console.print(f"[bold yellow]║  Total Tokens:       {total['total_tokens']:>16,}  ║[/bold yellow]")
    console.print(f"[bold yellow]╚═══════════════════════════════════════════════╝[/bold yellow]\n")
    
    # Save cost tracking to file
    cost_file = Path(__file__).parent.parent / "workflow_costs.json"
    cost_tracker.save_to_json(str(cost_file))
    console.print(f"[green]✓ Cost details saved to: {cost_file}[/green]\n")
    
    console.print("[bold green]✨ Workflow complete![/bold green]")


if __name__ == "__main__":
    main()

