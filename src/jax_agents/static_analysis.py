"""
Static Analysis Agent for Fortran code analysis.

This agent analyzes Fortran modules to extract structure, dependencies,
and patterns needed for JAX translation.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from jax_agents.base_agent import BaseAgent
from jax_agents.prompts.analysis_prompts import ANALYSIS_PROMPTS
from rich.console import Console

console = Console()


@dataclass
class DependencyInfo:
    """Dependency information extracted from Fortran module."""
    modules: List[str]
    includes: List[str]
    external_types: List[str]


@dataclass
class DataTypeInfo:
    """Data type information."""
    name: str
    kind: str  # derived_type, parameter_type, variable
    fields: List[Dict[str, str]]
    description: str = ""


@dataclass
class SubroutineInfo:
    """Subroutine/function information."""
    name: str
    purpose: str
    inputs: List[Dict[str, str]]
    outputs: List[str]
    key_operations: List[str]
    loops: List[Dict[str, str]]
    fortran_patterns: Dict[str, List[str]]


@dataclass
class AnalysisResult:
    """Complete analysis result for a Fortran module."""
    module_name: str
    description: str
    dependencies: DependencyInfo
    data_types: List[DataTypeInfo]
    parameters: List[Dict[str, str]]
    subroutines: List[SubroutineInfo]
    spatial_hierarchy: Dict[str, Any]
    jax_translation_notes: Dict[str, Any]
    raw_analysis: Dict[str, Any]  # Full JSON from LLM
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def save(self, output_path: Path) -> None:
        """Save analysis to file."""
        with open(output_path, 'w') as f:
            f.write(self.to_json())
        console.print(f"[green]✓ Saved analysis to {output_path}[/green]")


class StaticAnalysisAgent(BaseAgent):
    """
    Agent for analyzing Fortran code structure.
    
    Responsibilities:
    - Extract module structure and organization
    - Identify dependencies
    - Map data types and derived types
    - Analyze subroutines and functions
    - Detect spatial hierarchy patterns
    - Identify loop patterns and vectorization opportunities
    """
    
    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.0,
        max_tokens: int = 4000,
    ):
        """
        Initialize Static Analysis Agent.
        
        Args:
            model: Claude model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        """
        super().__init__(
            name="Static Analysis",
            role="Fortran code structure analyzer",
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    
    def analyze_module(
        self,
        fortran_file: Path,
        extract_physics: bool = True,
    ) -> AnalysisResult:
        """
        Perform comprehensive analysis of a Fortran module.
        
        Args:
            fortran_file: Path to Fortran source file
            extract_physics: Whether to perform detailed physics extraction
            
        Returns:
            AnalysisResult with complete analysis
        """
        console.print(f"\n[bold cyan]📊 Analyzing Fortran module: {fortran_file.name}[/bold cyan]")
        
        # Read Fortran source
        with open(fortran_file, 'r') as f:
            fortran_code = f.read()
        
        console.print(f"[dim]Read {len(fortran_code)} characters of Fortran code[/dim]")
        
        # Perform main analysis
        console.print("[cyan]Running structural analysis...[/cyan]")
        analysis_prompt = ANALYSIS_PROMPTS["analyze_module"].format(
            fortran_code=fortran_code
        )
        
        response = self.query_claude(
            prompt=analysis_prompt,
            system_prompt=ANALYSIS_PROMPTS["system"],
            max_tokens=4000,
        )
        
        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_str = self._extract_json(response)
            analysis_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            console.print(f"[red]Error parsing JSON response: {e}[/red]")
            console.print(f"[yellow]Raw response:[/yellow]\n{response}")
            raise
        
        # Optional: Extract physics details
        if extract_physics:
            console.print("[cyan]Extracting physics calculations...[/cyan]")
            physics_analysis = self._analyze_physics(fortran_code)
            analysis_data["physics_details"] = physics_analysis
        
        # Convert to structured result
        result = self._parse_analysis(analysis_data, fortran_file)
        
        console.print(f"[green]✓ Analysis complete![/green]")
        console.print(f"  - Found {len(result.subroutines)} subroutines")
        console.print(f"  - Found {len(result.data_types)} data types")
        console.print(f"  - Found {len(result.dependencies.modules)} module dependencies")
        
        return result
    
    def analyze_dependencies(self, fortran_file: Path) -> DependencyInfo:
        """
        Extract just the dependencies from a Fortran module.
        
        Args:
            fortran_file: Path to Fortran source file
            
        Returns:
            DependencyInfo with module dependencies
        """
        with open(fortran_file, 'r') as f:
            fortran_code = f.read()
        
        prompt = ANALYSIS_PROMPTS["extract_dependencies"].format(
            fortran_code=fortran_code
        )
        
        response = self.query_claude(prompt, system_prompt=ANALYSIS_PROMPTS["system"])
        
        json_str = self._extract_json(response)
        data = json.loads(json_str)
        
        return DependencyInfo(
            modules=data.get("modules", []),
            includes=data.get("includes", []),
            external_types=data.get("external_types", []),
        )
    
    def analyze_loops(self, fortran_code: str) -> List[Dict[str, Any]]:
        """
        Analyze loop structures for vectorization potential.
        
        Args:
            fortran_code: Fortran code snippet or full module
            
        Returns:
            List of loop analyses
        """
        prompt = ANALYSIS_PROMPTS["analyze_loops"].format(
            fortran_code=fortran_code
        )
        
        response = self.query_claude(prompt, system_prompt=ANALYSIS_PROMPTS["system"])
        
        json_str = self._extract_json(response)
        return json.loads(json_str)
    
    def _analyze_physics(self, fortran_code: str) -> Dict[str, Any]:
        """
        Analyze physics calculations in detail.
        
        Args:
            fortran_code: Fortran code to analyze
            
        Returns:
            Physics analysis dictionary
        """
        prompt = ANALYSIS_PROMPTS["identify_physics"].format(
            fortran_code=fortran_code
        )
        
        response = self.query_claude(prompt, system_prompt=ANALYSIS_PROMPTS["system"])
        
        json_str = self._extract_json(response)
        return json.loads(json_str)
    
    def _extract_json(self, response: str) -> str:
        """
        Extract JSON from response (handles markdown code blocks).
        
        Args:
            response: Claude's response
            
        Returns:
            Extracted JSON string
        """
        # Try to find JSON in markdown code blocks
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            return response[start:end].strip()
        else:
            # Assume entire response is JSON
            return response.strip()
    
    def _parse_analysis(
        self,
        analysis_data: Dict[str, Any],
        fortran_file: Path,
    ) -> AnalysisResult:
        """
        Parse raw analysis data into structured result.
        
        Args:
            analysis_data: Raw analysis dictionary from LLM
            fortran_file: Original Fortran file
            
        Returns:
            Structured AnalysisResult
        """
        # Extract dependencies
        deps_data = analysis_data.get("dependencies", {})
        dependencies = DependencyInfo(
            modules=deps_data.get("modules", []),
            includes=deps_data.get("includes", []),
            external_types=deps_data.get("external_types", []),
        )
        
        # Extract data types
        data_types = []
        for dt in analysis_data.get("data_types", []):
            data_types.append(DataTypeInfo(
                name=dt.get("name", ""),
                kind=dt.get("kind", ""),
                fields=dt.get("fields", []),
                description=dt.get("description", ""),
            ))
        
        # Extract subroutines
        subroutines = []
        for sub in analysis_data.get("subroutines", []):
            subroutines.append(SubroutineInfo(
                name=sub.get("name", ""),
                purpose=sub.get("purpose", ""),
                inputs=sub.get("inputs", []),
                outputs=sub.get("outputs", []),
                key_operations=sub.get("key_operations", []),
                loops=sub.get("loops", []),
                fortran_patterns=sub.get("fortran_patterns", {}),
            ))
        
        return AnalysisResult(
            module_name=analysis_data.get("module_name", fortran_file.stem),
            description=analysis_data.get("description", ""),
            dependencies=dependencies,
            data_types=data_types,
            parameters=analysis_data.get("parameters", []),
            subroutines=subroutines,
            spatial_hierarchy=analysis_data.get("spatial_hierarchy", {}),
            jax_translation_notes=analysis_data.get("jax_translation_notes", {}),
            raw_analysis=analysis_data,
        )

