#!/usr/bin/env python3
"""
Example: Batch conversion of multiple modules.

This example shows how to convert multiple Fortran modules in sequence,
managing dependencies and tracking overall progress.
"""

from pathlib import Path
from jax_agents import OrchestratorAgent
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

console = Console()


def main():
    """Convert multiple biogeochemistry modules."""
    
    # Setup
    ctsm_dir = Path("/burg-archive/home/mck2199/CTSM")
    jax_ctsm_dir = Path("/burg-archive/home/mck2199/jax-ctsm")
    
    # Modules to convert (in dependency order)
    modules_to_convert = [
        "src/biogeochem/CNGRespMod.F90",           # Growth respiration (simple)
        "src/biogeochem/CNAllocationMod.F90",       # Allocation (medium)
        # "src/biogeochem/CNPhenologyMod.F90",      # Phenology (complex) - uncomment to include
    ]
    
    console.print("[bold cyan]Batch Conversion Example[/bold cyan]\n")
    console.print(f"[bold]Modules to convert:[/bold] {len(modules_to_convert)}\n")
    
    # Initialize orchestrator
    orchestrator = OrchestratorAgent(
        ctsm_dir=ctsm_dir,
        jax_ctsm_dir=jax_ctsm_dir,
    )
    
    # Track results
    results = []
    total_cost = 0.0
    
    # Convert each module
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
    ) as progress:
        
        task = progress.add_task(
            "[cyan]Converting modules...",
            total=len(modules_to_convert)
        )
        
        for i, module_path in enumerate(modules_to_convert, 1):
            module_name = Path(module_path).stem
            
            progress.update(
                task,
                description=f"[cyan]Converting {module_name} ({i}/{len(modules_to_convert)})..."
            )
            
            try:
                result = orchestrator.convert_module(
                    fortran_file=module_path,
                    generate_report=True,
                )
                
                results.append(result)
                total_cost += result.cost_summary['total_cost_usd']
                
                console.print(f"[green]✓[/green] {module_name}: Success")
                
            except Exception as e:
                console.print(f"[red]✗[/red] {module_name}: Failed - {e}")
                continue
            
            progress.advance(task)
    
    # Summary
    console.print("\n[bold green]Batch Conversion Complete![/bold green]\n")
    
    console.print(f"[bold]Modules Converted:[/bold] {len(results)}/{len(modules_to_convert)}")
    console.print(f"[bold]Total Cost:[/bold] ${total_cost:.4f}\n")
    
    # Individual summaries
    console.print("[bold]Individual Results:[/bold]")
    for result in results:
        console.print(f"\n  [cyan]{result.module_name}[/cyan]")
        console.print(f"    Status: {result.status}")
        console.print(f"    Files: {len(result.saved_files)}")
        console.print(f"    Cost: ${result.cost_summary['total_cost_usd']:.4f}")


if __name__ == "__main__":
    main()

