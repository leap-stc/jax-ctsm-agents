"""
Orchestrator Agent for coordinating Fortran to JAX conversion.

This agent manages the overall workflow, coordinating between
Static Analysis and Translator agents.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
import json

from jax_agents.base_agent import BaseAgent
from jax_agents.static_analysis import StaticAnalysisAgent, AnalysisResult
from jax_agents.translator import TranslatorAgent, TranslationResult
from jax_agents.prompts.orchestrator_prompts import ORCHESTRATOR_PROMPTS
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


@dataclass
class ConversionPlan:
    """Plan for converting a Fortran module."""
    module_name: str
    complexity: str  # simple, medium, complex
    challenges: List[str]
    approach: str
    dependencies: List[str]
    analysis_focus: List[str]
    translation_requirements: Dict[str, Any]
    integration_plan: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ConversionResult:
    """Complete result of module conversion."""
    module_name: str
    status: str  # success, partial, failed
    plan: ConversionPlan
    analysis: AnalysisResult
    translation: TranslationResult
    saved_files: Dict[str, Path]
    cost_summary: Dict[str, float]
    timestamp: str
    report: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "module_name": self.module_name,
            "status": self.status,
            "plan": self.plan.to_dict(),
            "analysis": self.analysis.to_dict(),
            "saved_files": {k: str(v) for k, v in self.saved_files.items()},
            "cost_summary": self.cost_summary,
            "timestamp": self.timestamp,
        }
    
    def save_report(self, output_path: Path) -> None:
        """Save conversion report."""
        with open(output_path, 'w') as f:
            f.write(self.report)
        console.print(f"[green]✓ Saved conversion report to {output_path}[/green]")


class OrchestratorAgent(BaseAgent):
    """
    Agent for orchestrating the Fortran to JAX conversion workflow.
    
    Responsibilities:
    - Plan conversion strategies
    - Coordinate Static Analysis and Translator agents
    - Manage dependencies between modules
    - Track conversion progress
    - Generate comprehensive reports
    - Make architectural decisions
    """
    
    def __init__(
        self,
        ctsm_dir: Path,
        jax_ctsm_dir: Path,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.0,
        max_tokens: int = 4000,
    ):
        """
        Initialize Orchestrator Agent.
        
        Args:
            ctsm_dir: Path to CTSM source directory
            jax_ctsm_dir: Path to jax-ctsm directory
            model: Claude model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        """
        super().__init__(
            name="Orchestrator",
            role="Conversion workflow coordinator",
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        self.ctsm_dir = Path(ctsm_dir)
        self.jax_ctsm_dir = Path(jax_ctsm_dir)
        
        # Initialize sub-agents
        self.analyzer = StaticAnalysisAgent(model=model, temperature=temperature)
        self.translator = TranslatorAgent(
            jax_ctsm_dir=jax_ctsm_dir,
            model=model,
            temperature=temperature,
        )
        
        # Track converted modules
        self.converted_modules: List[str] = []
        
        console.print(f"[green]✓ Orchestrator initialized[/green]")
        console.print(f"  CTSM: {self.ctsm_dir}")
        console.print(f"  JAX-CTSM: {self.jax_ctsm_dir}")
    
    def convert_module(
        self,
        fortran_file: str,
        output_dir: Optional[Path] = None,
        generate_report: bool = True,
    ) -> ConversionResult:
        """
        Convert a Fortran module to JAX with full workflow.
        
        Args:
            fortran_file: Path to Fortran file (relative to ctsm_dir or absolute)
            output_dir: Directory to save output (default: jax_ctsm_dir/src/jax_ctsm/physics)
            generate_report: Whether to generate detailed report
            
        Returns:
            ConversionResult with all outputs
        """
        console.print("\n" + "="*80)
        console.print(Panel.fit(
            "[bold cyan]🚀 JAX-CTSM Module Conversion[/bold cyan]",
            border_style="cyan"
        ))
        console.print("="*80 + "\n")
        
        # Resolve paths
        if Path(fortran_file).is_absolute():
            fortran_path = Path(fortran_file)
        else:
            fortran_path = self.ctsm_dir / fortran_file
        
        if not fortran_path.exists():
            raise FileNotFoundError(f"Fortran file not found: {fortran_path}")
        
        module_name = fortran_path.stem
        
        if output_dir is None:
            output_dir = self.jax_ctsm_dir / "src" / "jax_ctsm" / "physics"
        
        console.print(f"[bold]Module:[/bold] {module_name}")
        console.print(f"[bold]Source:[/bold] {fortran_path}")
        console.print(f"[bold]Output:[/bold] {output_dir}\n")
        
        # Step 1: Plan conversion
        console.print("[bold yellow]Step 1/4: Planning Conversion Strategy[/bold yellow]")
        plan = self._plan_conversion(fortran_path)
        self._display_plan(plan)
        
        # Step 2: Static analysis
        console.print("\n[bold yellow]Step 2/4: Static Analysis[/bold yellow]")
        analysis = self.analyzer.analyze_module(fortran_path, extract_physics=True)
        
        # Step 3: Translation
        console.print("\n[bold yellow]Step 3/4: Translation to JAX[/bold yellow]")
        translation = self.translator.translate_module(fortran_path, analysis, output_dir)
        
        # Step 4: Synthesis and reporting
        console.print("\n[bold yellow]Step 4/4: Synthesis and Reporting[/bold yellow]")
        
        # Collect cost information
        cost_summary = self._collect_costs()
        
        # Generate report if requested
        report = ""
        if generate_report:
            report = self._generate_report(
                module_name=module_name,
                plan=plan,
                analysis=analysis,
                translation=translation,
                cost_summary=cost_summary,
            )
        
        # Create result
        result = ConversionResult(
            module_name=module_name,
            status="success",
            plan=plan,
            analysis=analysis,
            translation=translation,
            saved_files=translation.save(output_dir),
            cost_summary=cost_summary,
            timestamp=datetime.now().isoformat(),
            report=report,
        )
        
        # Save report
        if report:
            report_path = output_dir / f"{module_name}_conversion_report.md"
            result.save_report(report_path)
        
        # Add to converted modules
        self.converted_modules.append(module_name)
        
        # Display summary
        self._display_summary(result)
        
        return result
    
    def plan_batch_conversion(
        self,
        fortran_files: List[str],
    ) -> List[ConversionPlan]:
        """
        Plan conversion for multiple modules.
        
        Args:
            fortran_files: List of Fortran files to convert
            
        Returns:
            List of conversion plans with dependency ordering
        """
        plans = []
        for fortran_file in fortran_files:
            fortran_path = self.ctsm_dir / fortran_file
            if fortran_path.exists():
                plan = self._plan_conversion(fortran_path)
                plans.append(plan)
        
        # TODO: Order by dependencies
        return plans
    
    def _plan_conversion(self, fortran_file: Path) -> ConversionPlan:
        """
        Create conversion plan for a module.
        
        Args:
            fortran_file: Path to Fortran file
            
        Returns:
            ConversionPlan
        """
        # Get list of existing modules
        existing_modules = self._list_existing_modules()
        
        # Create planning prompt
        prompt = ORCHESTRATOR_PROMPTS["plan_conversion"].format(
            module_name=fortran_file.stem,
            module_path=str(fortran_file),
            existing_modules=json.dumps(existing_modules, indent=2),
        )
        
        response = self.query_claude(
            prompt=prompt,
            system_prompt=ORCHESTRATOR_PROMPTS["system"],
        )
        
        # Parse response
        plan_data = self._extract_json(response)
        
        return ConversionPlan(
            module_name=fortran_file.stem,
            complexity=plan_data.get("complexity", "medium"),
            challenges=plan_data.get("challenges", []),
            approach=plan_data.get("approach", ""),
            dependencies=plan_data.get("dependencies", []),
            analysis_focus=plan_data.get("analysis_focus", []),
            translation_requirements=plan_data.get("translation_requirements", {}),
            integration_plan=plan_data.get("integration_plan", {}),
        )
    
    def _generate_report(
        self,
        module_name: str,
        plan: ConversionPlan,
        analysis: AnalysisResult,
        translation: TranslationResult,
        cost_summary: Dict[str, float],
    ) -> str:
        """
        Generate comprehensive conversion report.
        
        Args:
            module_name: Module name
            plan: Conversion plan
            analysis: Analysis result
            translation: Translation result
            cost_summary: Cost summary
            
        Returns:
            Markdown report
        """
        prompt = ORCHESTRATOR_PROMPTS["generate_report"].format(
            module_name=module_name,
            status="success",
            analysis_summary=json.dumps(analysis.to_dict(), indent=2),
            translation_summary=translation.translation_notes,
            cost_summary=json.dumps(cost_summary, indent=2),
        )
        
        response = self.query_claude(
            prompt=prompt,
            system_prompt=ORCHESTRATOR_PROMPTS["system"],
            max_tokens=4000,
        )
        
        return response
    
    def _collect_costs(self) -> Dict[str, float]:
        """Collect cost information from all agents."""
        orchestrator_cost = self.get_cost_estimate()
        analyzer_cost = self.analyzer.get_cost_estimate()
        translator_cost = self.translator.get_cost_estimate()
        
        total_cost = (
            orchestrator_cost["total_cost_usd"] +
            analyzer_cost["total_cost_usd"] +
            translator_cost["total_cost_usd"]
        )
        
        total_tokens = (
            orchestrator_cost["input_tokens"] + orchestrator_cost["output_tokens"] +
            analyzer_cost["input_tokens"] + analyzer_cost["output_tokens"] +
            translator_cost["input_tokens"] + translator_cost["output_tokens"]
        )
        
        return {
            "orchestrator_cost_usd": orchestrator_cost["total_cost_usd"],
            "analyzer_cost_usd": analyzer_cost["total_cost_usd"],
            "translator_cost_usd": translator_cost["total_cost_usd"],
            "total_cost_usd": total_cost,
            "total_tokens": total_tokens,
        }
    
    def _list_existing_modules(self) -> List[str]:
        """List existing JAX-CTSM modules."""
        modules = []
        physics_dir = self.jax_ctsm_dir / "src" / "jax_ctsm" / "physics"
        if physics_dir.exists():
            for f in physics_dir.glob("*.py"):
                if not f.name.startswith("__"):
                    modules.append(f.stem)
        return modules
    
    def _extract_json(self, response: str) -> Dict[str, Any]:
        """Extract JSON from response."""
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            json_str = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            json_str = response[start:end].strip()
        else:
            json_str = response.strip()
        
        return json.loads(json_str)
    
    def _display_plan(self, plan: ConversionPlan) -> None:
        """Display conversion plan in formatted table."""
        table = Table(title="Conversion Plan", show_header=True, header_style="bold cyan")
        table.add_column("Aspect", style="cyan")
        table.add_column("Details", style="white")
        
        table.add_row("Complexity", plan.complexity)
        table.add_row("Challenges", ", ".join(plan.challenges[:3]))
        table.add_row("Dependencies", ", ".join(plan.dependencies[:3]))
        table.add_row("Approach", plan.approach[:100] + "...")
        
        console.print(table)
    
    def _display_summary(self, result: ConversionResult) -> None:
        """Display conversion summary."""
        console.print("\n" + "="*80)
        console.print(Panel.fit(
            f"[bold green]✓ Conversion Complete: {result.module_name}[/bold green]",
            border_style="green"
        ))
        console.print("="*80 + "\n")
        
        # Files generated
        console.print("[bold]Files Generated:[/bold]")
        for file_type, path in result.saved_files.items():
            console.print(f"  ✓ {file_type}: {path}")
        
        # Cost summary
        console.print(f"\n[bold]Cost Summary:[/bold]")
        console.print(f"  Total: ${result.cost_summary['total_cost_usd']:.4f}")
        console.print(f"  Tokens: {result.cost_summary['total_tokens']:,}")
        
        console.print()

