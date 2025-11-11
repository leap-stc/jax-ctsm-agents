#!/usr/bin/env python3
"""
Example: Convert a single Fortran module to JAX.

This example demonstrates the basic workflow for converting a CTSM Fortran
module to JAX using the orchestrator agent.
"""

import argparse
from pathlib import Path
from jax_agents import OrchestratorAgent
from rich.console import Console

console = Console()


def convert_module(
    fortran_file: str,
    ctsm_dir: Path,
    jax_ctsm_dir: Path,
    output_dir: Path = None,
    generate_report: bool = True,
):
    """
    Convert a Fortran module to JAX using the orchestrator.
    
    Args:
        fortran_file: Relative path to Fortran file (from ctsm_dir)
        ctsm_dir: Root CTSM directory
        jax_ctsm_dir: Root jax-ctsm directory
        output_dir: Optional output directory
        generate_report: Whether to generate conversion report
    """
    console.print("[bold cyan]Initializing JAX-CTSM Translation Orchestrator[/bold cyan]\n")
    
    orchestrator = OrchestratorAgent(
        ctsm_dir=ctsm_dir,
        jax_ctsm_dir=jax_ctsm_dir,
    )
    
    console.print(f"[bold]Converting:[/bold] {fortran_file}\n")
    
    result = orchestrator.convert_module(
        fortran_file=fortran_file,
        output_dir=output_dir,
        generate_report=generate_report,
    )
    
    # Display results
    console.print("\n[bold green]Conversion Complete![/bold green]\n")
    
    console.print("[bold]Generated Files:[/bold]")
    for file_type, path in result.saved_files.items():
        console.print(f"  • {file_type}: {path}")
    
    console.print(f"\n[bold]Total Cost:[/bold] ${result.cost_summary['total_cost_usd']:.4f}")
    console.print(f"[bold]Total Tokens:[/bold] {result.cost_summary['total_tokens']:,}")
    
    if generate_report:
        console.print("\n[dim]See the conversion report for detailed analysis.[/dim]")
    
    return result


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Convert a single Fortran module to JAX using the orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a biogeochem module
  python convert_single_module.py src/biogeochem/CNGRespMod.F90
  
  # Convert a biogeophys module
  python convert_single_module.py src/biogeophys/SoilTemperatureMod.F90
  
  # Specify output directory
  python convert_single_module.py src/biogeochem/CNGRespMod.F90 \\
    --output /path/to/output
  
  # Skip report generation (faster)
  python convert_single_module.py src/biogeochem/CNGRespMod.F90 --no-report
  
  # Interactive mode
  python convert_single_module.py --interactive
  
  # Use default example module
  python convert_single_module.py --example
        """
    )
    
    parser.add_argument(
        "fortran_file",
        nargs="?",
        help="Relative path to Fortran file (from CTSM directory)"
    )
    parser.add_argument(
        "--ctsm-dir",
        default="/burg-archive/home/mck2199/CTSM",
        help="Path to CTSM root directory"
    )
    parser.add_argument(
        "--jax-ctsm-dir",
        default="/burg-archive/home/mck2199/jax-ctsm",
        help="Path to jax-ctsm root directory"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output directory (default: jax-ctsm/src/jax_ctsm/physics)"
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip conversion report generation"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive mode - prompts for inputs"
    )
    parser.add_argument(
        "--example",
        action="store_true",
        help="Run with default example module (CNGRespMod.F90)"
    )
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive:
        console.print("\n[bold cyan]Interactive Module Conversion[/bold cyan]\n")
        
        console.print("[cyan]Enter Fortran file path (relative to CTSM dir):[/cyan]")
        console.print("[dim]Example: src/biogeochem/CNGRespMod.F90[/dim]")
        fortran_file = input("> ").strip()
        
        console.print("\n[cyan]CTSM directory (default: /burg-archive/home/mck2199/CTSM):[/cyan]")
        ctsm_path = input("> ").strip() or "/burg-archive/home/mck2199/CTSM"
        ctsm_dir = Path(ctsm_path)
        
        console.print("\n[cyan]jax-ctsm directory (default: /burg-archive/home/mck2199/jax-ctsm):[/cyan]")
        jax_path = input("> ").strip() or "/burg-archive/home/mck2199/jax-ctsm"
        jax_ctsm_dir = Path(jax_path)
        
        console.print("\n[cyan]Output directory (press Enter for default):[/cyan]")
        output_path = input("> ").strip()
        output_dir = Path(output_path) if output_path else None
        
        console.print("\n[cyan]Generate conversion report? (y/n, default: y):[/cyan]")
        generate_report = input("> ").strip().lower() != 'n'
        
        convert_module(
            fortran_file=fortran_file,
            ctsm_dir=ctsm_dir,
            jax_ctsm_dir=jax_ctsm_dir,
            output_dir=output_dir,
            generate_report=generate_report,
        )
        return
    
    # Example mode
    if args.example:
        console.print("[cyan]Running with example module: CNGRespMod.F90[/cyan]\n")
        fortran_file = "src/biogeochem/CNGRespMod.F90"
        output_dir = Path(args.jax_ctsm_dir) / "src" / "jax_ctsm" / "physics" if not args.output else Path(args.output)
        convert_module(
            fortran_file=fortran_file,
            ctsm_dir=Path(args.ctsm_dir),
            jax_ctsm_dir=Path(args.jax_ctsm_dir),
            output_dir=output_dir,
            generate_report=not args.no_report,
        )
        return
    
    # CLI mode
    if args.fortran_file:
        output_dir = Path(args.output) if args.output else None
        convert_module(
            fortran_file=args.fortran_file,
            ctsm_dir=Path(args.ctsm_dir),
            jax_ctsm_dir=Path(args.jax_ctsm_dir),
            output_dir=output_dir,
            generate_report=not args.no_report,
        )
    else:
        parser.print_help()
        console.print("\n[yellow]Please provide a Fortran file, use --interactive, or --example[/yellow]")


if __name__ == "__main__":
    main()
