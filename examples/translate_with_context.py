#!/usr/bin/env python3
"""
Example: Translate with custom analysis and context.

This example shows how to use the Static Analysis and Translator agents
separately, with custom configuration.
"""

import argparse
from pathlib import Path
from jax_agents import StaticAnalysisAgent, TranslatorAgent
from rich.console import Console

console = Console()


def translate_module(
    fortran_file: Path,
    jax_ctsm_dir: Path,
    output_dir: Path,
    extract_physics: bool = True,
    save_analysis: bool = True,
):
    """
    Two-step conversion with custom analysis.
    
    Args:
        fortran_file: Path to Fortran module
        jax_ctsm_dir: Path to jax-ctsm reference directory
        output_dir: Output directory for translated code
        extract_physics: Extract detailed physics information
        save_analysis: Save analysis JSON file
    """
    if not fortran_file.exists():
        console.print(f"[red]✗ Error: File not found: {fortran_file}[/red]")
        return None
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    console.print("[bold cyan]Two-Step Translation Example[/bold cyan]\n")
    
    # Step 1: Analyze
    console.print("[bold yellow]Step 1: Static Analysis[/bold yellow]\n")
    
    analyzer = StaticAnalysisAgent()
    analysis = analyzer.analyze_module(
        fortran_file=fortran_file,
        extract_physics=extract_physics,
    )
    
    # Save analysis for review
    if save_analysis:
        analysis_file = output_dir / "analysis.json"
        analysis.save(analysis_file)
        console.print(f"[dim]Saved analysis to: {analysis_file}[/dim]")
    
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
    
    return translation


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Translate a Fortran module to JAX with two-step process",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Translate a specific module
  python translate_with_context.py /path/to/Module.F90
  
  # Specify output directory
  python translate_with_context.py /path/to/Module.F90 -o ./my_output
  
  # Skip detailed physics extraction (faster, less context)
  python translate_with_context.py /path/to/Module.F90 --no-physics
  
  # Interactive mode
  python translate_with_context.py --interactive
  
  # Use default example module
  python translate_with_context.py --example
        """
    )
    
    parser.add_argument(
        "fortran_file",
        nargs="?",
        help="Path to Fortran module file"
    )
    parser.add_argument(
        "-o", "--output",
        default="./output",
        help="Output directory (default: ./output)"
    )
    parser.add_argument(
        "--jax-ctsm-dir",
        default="/burg-archive/home/mck2199/jax-ctsm",
        help="Path to jax-ctsm directory"
    )
    parser.add_argument(
        "--no-physics",
        action="store_true",
        help="Skip detailed physics extraction (faster)"
    )
    parser.add_argument(
        "--no-save-analysis",
        action="store_true",
        help="Don't save analysis JSON file"
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
        console.print("\n[bold cyan]Interactive Module Translation[/bold cyan]\n")
        
        console.print("[cyan]Enter path to Fortran module:[/cyan]")
        fortran_path = input("> ").strip()
        fortran_file = Path(fortran_path)
        
        console.print("\n[cyan]Output directory (default: ./output):[/cyan]")
        output_path = input("> ").strip() or "./output"
        output_dir = Path(output_path)
        
        console.print("\n[cyan]Extract detailed physics? (y/n, default: y):[/cyan]")
        extract_physics = input("> ").strip().lower() != 'n'
        
        console.print("\n[cyan]Path to jax-ctsm (default: /burg-archive/home/mck2199/jax-ctsm):[/cyan]")
        jax_path = input("> ").strip() or "/burg-archive/home/mck2199/jax-ctsm"
        jax_ctsm_dir = Path(jax_path)
        
        translate_module(
            fortran_file=fortran_file,
            jax_ctsm_dir=jax_ctsm_dir,
            output_dir=output_dir,
            extract_physics=extract_physics,
            save_analysis=True,
        )
        return
    
    # Example mode
    if args.example:
        console.print("[cyan]Running with example module: CNGRespMod.F90[/cyan]\n")
        fortran_file = Path("/burg-archive/home/mck2199/CTSM/src/biogeochem/CNGRespMod.F90")
        translate_module(
            fortran_file=fortran_file,
            jax_ctsm_dir=Path(args.jax_ctsm_dir),
            output_dir=Path(args.output),
            extract_physics=not args.no_physics,
            save_analysis=not args.no_save_analysis,
        )
        return
    
    # CLI mode
    if args.fortran_file:
        fortran_file = Path(args.fortran_file)
        translate_module(
            fortran_file=fortran_file,
            jax_ctsm_dir=Path(args.jax_ctsm_dir),
            output_dir=Path(args.output),
            extract_physics=not args.no_physics,
            save_analysis=not args.no_save_analysis,
        )
    else:
        parser.print_help()
        console.print("\n[yellow]Please provide a Fortran file, use --interactive, or --example[/yellow]")


if __name__ == "__main__":
    main()
