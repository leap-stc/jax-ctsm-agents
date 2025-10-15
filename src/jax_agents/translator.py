"""
Translator Agent for converting Fortran to JAX.

This agent translates Fortran CTSM code to JAX following established patterns.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from jax_agents.base_agent import BaseAgent
from jax_agents.static_analysis import AnalysisResult
from jax_agents.prompts.translation_prompts import TRANSLATION_PROMPTS
from rich.console import Console

console = Console()


@dataclass
class TranslationResult:
    """Result of translating a Fortran module to JAX."""
    module_name: str
    physics_code: str
    params_code: Optional[str] = None
    test_code: Optional[str] = None
    translation_notes: str = ""
    
    def save(self, output_dir: Path) -> Dict[str, Path]:
        """
        Save translated code to files.
        
        Args:
            output_dir: Directory to save files
            
        Returns:
            Dictionary mapping file type to path
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = {}
        
        # Save main physics module
        physics_file = output_dir / f"{self.module_name}.py"
        with open(physics_file, 'w') as f:
            f.write(self.physics_code)
        saved_files["physics"] = physics_file
        console.print(f"[green]✓ Saved physics module to {physics_file}[/green]")
        
        # Save parameters if present
        if self.params_code:
            params_file = output_dir / f"{self.module_name}_params.py"
            with open(params_file, 'w') as f:
                f.write(self.params_code)
            saved_files["params"] = params_file
            console.print(f"[green]✓ Saved parameters to {params_file}[/green]")
        
        # Save tests if generated
        if self.test_code:
            test_file = output_dir / f"test_{self.module_name}.py"
            with open(test_file, 'w') as f:
                f.write(self.test_code)
            saved_files["test"] = test_file
            console.print(f"[green]✓ Saved tests to {test_file}[/green]")
        
        # Save translation notes
        if self.translation_notes:
            notes_file = output_dir / f"{self.module_name}_translation_notes.md"
            with open(notes_file, 'w') as f:
                f.write(self.translation_notes)
            saved_files["notes"] = notes_file
            console.print(f"[green]✓ Saved translation notes to {notes_file}[/green]")
        
        return saved_files


class TranslatorAgent(BaseAgent):
    """
    Agent for translating Fortran code to JAX.
    
    Responsibilities:
    - Convert Fortran syntax to JAX/Python
    - Apply JAX best practices (pure functions, immutable state)
    - Follow established jax-ctsm patterns
    - Generate type hints and documentation
    - Create parameter classes
    - Convert loops to vectorized operations
    """
    
    def __init__(
        self,
        jax_ctsm_dir: Optional[Path] = None,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.0,
        max_tokens: int = 4000,
    ):
        """
        Initialize Translator Agent.
        
        Args:
            jax_ctsm_dir: Path to jax-ctsm directory (for reference patterns)
            model: Claude model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        """
        super().__init__(
            name="Translator",
            role="Fortran to JAX code translator",
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        self.jax_ctsm_dir = jax_ctsm_dir
        self.reference_patterns = self._load_reference_patterns()
    
    def translate_module(
        self,
        fortran_file: Path,
        analysis: AnalysisResult,
        output_dir: Optional[Path] = None,
    ) -> TranslationResult:
        """
        Translate a complete Fortran module to JAX.
        
        Args:
            fortran_file: Path to Fortran source file
            analysis: Static analysis result
            output_dir: Optional directory to save output
            
        Returns:
            TranslationResult with generated code
        """
        console.print(f"\n[bold cyan]🔄 Translating {fortran_file.name} to JAX[/bold cyan]")
        
        # Read Fortran source
        with open(fortran_file, 'r') as f:
            fortran_code = f.read()
        
        # Get reference pattern
        reference_pattern = self._get_reference_pattern()
        
        # Build translation prompt
        prompt = TRANSLATION_PROMPTS["translate_module"].format(
            fortran_code=fortran_code,
            analysis=analysis.to_json(),
            reference_pattern=reference_pattern,
        )
        
        console.print("[cyan]Generating JAX translation...[/cyan]")
        
        # Query Claude for translation
        response = self.query_claude(
            prompt=prompt,
            system_prompt=TRANSLATION_PROMPTS["system"],
            max_tokens=4000,
        )
        
        # Parse response into code files
        result = self._parse_translation_response(response, analysis.module_name)
        
        console.print(f"[green]✓ Translation complete![/green]")
        
        # Save if output directory specified
        if output_dir:
            result.save(output_dir)
        
        return result
    
    def translate_function(
        self,
        fortran_code: str,
        context: Dict[str, Any],
    ) -> str:
        """
        Translate a single Fortran subroutine to JAX function.
        
        Args:
            fortran_code: Fortran subroutine code
            context: Context from static analysis
            
        Returns:
            Translated JAX function code
        """
        prompt = TRANSLATION_PROMPTS["translate_function"].format(
            fortran_code=fortran_code,
            context=context,
        )
        
        response = self.query_claude(
            prompt=prompt,
            system_prompt=TRANSLATION_PROMPTS["system"],
        )
        
        return self._extract_code(response)
    
    def convert_data_structure(
        self,
        fortran_type: str,
    ) -> str:
        """
        Convert Fortran derived type to JAX NamedTuple.
        
        Args:
            fortran_type: Fortran type definition
            
        Returns:
            Python NamedTuple code
        """
        prompt = TRANSLATION_PROMPTS["convert_data_structure"].format(
            fortran_type=fortran_type,
        )
        
        response = self.query_claude(
            prompt=prompt,
            system_prompt=TRANSLATION_PROMPTS["system"],
        )
        
        return self._extract_code(response)
    
    def vectorize_loop(
        self,
        loop_code: str,
        loop_analysis: Dict[str, Any],
    ) -> str:
        """
        Convert Fortran loop to vectorized JAX operations.
        
        Args:
            loop_code: Fortran loop code
            loop_analysis: Analysis of loop structure
            
        Returns:
            Vectorized JAX code
        """
        prompt = TRANSLATION_PROMPTS["vectorize_loop"].format(
            loop_code=loop_code,
            loop_analysis=loop_analysis,
        )
        
        response = self.query_claude(
            prompt=prompt,
            system_prompt=TRANSLATION_PROMPTS["system"],
        )
        
        return self._extract_code(response)
    
    def handle_conditional(
        self,
        conditional_code: str,
    ) -> str:
        """
        Convert Fortran conditional to JIT-compatible JAX.
        
        Args:
            conditional_code: Fortran if/else code
            
        Returns:
            JAX jnp.where code
        """
        prompt = TRANSLATION_PROMPTS["handle_conditional"].format(
            conditional_code=conditional_code,
        )
        
        response = self.query_claude(
            prompt=prompt,
            system_prompt=TRANSLATION_PROMPTS["system"],
        )
        
        return self._extract_code(response)
    
    def create_parameters(
        self,
        parameters: str,
    ) -> str:
        """
        Create JAX parameter class from Fortran parameters.
        
        Args:
            parameters: Fortran parameter definitions
            
        Returns:
            Python NamedTuple parameter class
        """
        prompt = TRANSLATION_PROMPTS["create_parameters"].format(
            parameters=parameters,
        )
        
        response = self.query_claude(
            prompt=prompt,
            system_prompt=TRANSLATION_PROMPTS["system"],
        )
        
        return self._extract_code(response)
    
    def _load_reference_patterns(self) -> Dict[str, str]:
        """
        Load reference patterns from existing jax-ctsm code.
        
        Returns:
            Dictionary of reference patterns
        """
        patterns = {}
        
        if self.jax_ctsm_dir and self.jax_ctsm_dir.exists():
            # Load maintenance respiration as main reference
            mr_file = self.jax_ctsm_dir / "src/jax_ctsm/physics/maintenance_respiration.py"
            if mr_file.exists():
                with open(mr_file, 'r') as f:
                    patterns["maintenance_respiration"] = f.read()
            
            # Load parameter example
            params_file = self.jax_ctsm_dir / "src/jax_ctsm/params/respiration.py"
            if params_file.exists():
                with open(params_file, 'r') as f:
                    patterns["params_example"] = f.read()
            
            # Load hierarchy example
            hierarchy_file = self.jax_ctsm_dir / "src/jax_ctsm/core/hierarchy.py"
            if hierarchy_file.exists():
                with open(hierarchy_file, 'r') as f:
                    patterns["hierarchy_example"] = f.read()
        
        return patterns
    
    def _get_reference_pattern(self) -> str:
        """
        Get reference pattern for translation.
        
        Returns:
            Reference pattern code
        """
        if "maintenance_respiration" in self.reference_patterns:
            # Return abbreviated version (first 100 lines as example)
            full_code = self.reference_patterns["maintenance_respiration"]
            lines = full_code.split('\n')[:100]
            return '\n'.join(lines) + "\n\n# ... (abbreviated for context) ..."
        else:
            return """# Reference pattern not available
# The translator will use general JAX best practices:
# - Pure functions with type hints
# - NamedTuples for state
# - Vectorized operations
# - Google-style docstrings
"""
    
    def _parse_translation_response(
        self,
        response: str,
        module_name: str,
    ) -> TranslationResult:
        """
        Parse Claude's translation response into code files.
        
        Args:
            response: Claude's response
            module_name: Name of module being translated
            
        Returns:
            TranslationResult with parsed code
        """
        # Extract code blocks from response
        physics_code = ""
        params_code = None
        test_code = None
        notes = ""
        
        # Split response into sections
        sections = response.split("```python")
        
        if len(sections) > 1:
            # First Python block is usually the main physics module
            physics_end = sections[1].find("```")
            physics_code = sections[1][:physics_end].strip()
            
            # Check for additional code blocks
            if len(sections) > 2:
                # Second block might be parameters
                params_end = sections[2].find("```")
                params_code = sections[2][:params_end].strip()
            
            if len(sections) > 3:
                # Third block might be tests
                test_end = sections[3].find("```")
                test_code = sections[3][:test_end].strip()
        
        # Extract any markdown notes (text before first code block)
        if "```" in response:
            notes = response[:response.find("```")].strip()
        
        return TranslationResult(
            module_name=module_name,
            physics_code=physics_code if physics_code else response,
            params_code=params_code,
            test_code=test_code,
            translation_notes=notes,
        )
    
    def _extract_code(self, response: str) -> str:
        """
        Extract code from response (handles markdown code blocks).
        
        Args:
            response: Claude's response
            
        Returns:
            Extracted code
        """
        if "```python" in response:
            start = response.find("```python") + 9
            end = response.find("```", start)
            return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            return response[start:end].strip()
        else:
            return response.strip()

