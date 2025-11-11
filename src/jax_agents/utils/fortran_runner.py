"""
Fortran Runner for compiling and executing Fortran test harnesses.

This module handles:
- Compiling Fortran code with appropriate flags
- Writing test data to files
- Executing compiled Fortran programs
- Parsing Fortran output
"""

import json
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class FortranCompilationError(Exception):
    """Raised when Fortran compilation fails."""
    pass


class FortranExecutionError(Exception):
    """Raised when Fortran execution fails."""
    pass


class FortranRunner:
    """
    Runner for compiling and executing Fortran code.
    
    Handles the complete workflow of:
    1. Writing Fortran source to temp file
    2. Compiling with appropriate compiler flags
    3. Writing test input data
    4. Executing the compiled program
    5. Reading and parsing output data
    """
    
    def __init__(
        self,
        compiler: str = "gfortran",
        compile_flags: Optional[List[str]] = None,
        include_dirs: Optional[List[Path]] = None,
    ):
        """
        Initialize Fortran runner.
        
        Args:
            compiler: Fortran compiler command (gfortran, ifort, etc.)
            compile_flags: Additional compilation flags
            include_dirs: Include directories for dependencies
        """
        self.compiler = compiler
        self.compile_flags = compile_flags or [
            "-O2",  # Optimization level 2
            "-fdefault-real-8",  # Double precision default
            "-fdefault-double-8",
            "-ffree-line-length-none",  # No line length limit
            "-fbacktrace",  # Better error messages
        ]
        self.include_dirs = include_dirs or []
    
    def compile(
        self,
        fortran_code: str,
        output_path: Optional[Path] = None,
        dependencies: Optional[List[Path]] = None,
    ) -> Path:
        """
        Compile Fortran code.
        
        Args:
            fortran_code: Fortran source code as string
            output_path: Path for compiled executable (temp file if None)
            dependencies: Additional Fortran files to compile with
            
        Returns:
            Path to compiled executable
            
        Raises:
            FortranCompilationError: If compilation fails
        """
        # Write source to temp file
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.f90', delete=False
        ) as f:
            f.write(fortran_code)
            source_path = Path(f.name)
        
        try:
            # Create output path if not provided
            if output_path is None:
                output_fd, output_name = tempfile.mkstemp(suffix='.exe')
                output_path = Path(output_name)
                # Close the file descriptor, we just need the path
                import os
                os.close(output_fd)
            
            # Build compilation command
            cmd = [self.compiler] + self.compile_flags
            
            # Add include directories
            for inc_dir in self.include_dirs:
                cmd.extend(["-I", str(inc_dir)])
            
            # Add source file (only - ignore dependencies for standalone harness)
            cmd.append(str(source_path))
            # Note: We don't add dependencies anymore since the harness should be standalone
            # if dependencies:
            #     cmd.extend(str(dep) for dep in dependencies)
            
            # Add output specification
            cmd.extend(["-o", str(output_path)])
            
            logger.info(f"Compiling standalone harness: {' '.join(cmd)}")
            
            # Compile
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )
            
            if result.returncode != 0:
                error_msg = (
                    f"Fortran compilation failed:\n{result.stderr}\n\n"
                    f"This usually means the test harness still has external dependencies.\n"
                    f"The harness should be completely standalone with all code inline."
                )
                logger.error(error_msg)
                
                # Try to provide helpful error message
                if "Can't open module file" in result.stderr:
                    error_msg += (
                        "\n\nHINT: The generated harness is trying to 'use' external modules.\n"
                        "Ask the LLM to create a STANDALONE harness with:\n"
                        "1. No 'use' statements\n"
                        "2. Direct precision definition: integer, parameter :: r8 = selected_real_kind(15, 307)\n"
                        "3. All constants defined inline\n"
                        "4. Complete subroutine code in a 'contains' section"
                    )
                
                raise FortranCompilationError(error_msg)
            
            if result.stdout:
                logger.debug(f"Compiler output: {result.stdout}")
            
            logger.info(f"Successfully compiled to {output_path}")
            return output_path
        
        finally:
            # Clean up source file
            source_path.unlink(missing_ok=True)
    
    def run(
        self,
        executable: Path,
        input_data: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """
        Run compiled Fortran executable.
        
        Args:
            executable: Path to compiled Fortran executable
            input_data: Optional input data (written to stdin or file)
            timeout: Execution timeout in seconds
            
        Returns:
            Dictionary with stdout, stderr, return_code, execution_time
            
        Raises:
            FortranExecutionError: If execution fails
        """
        start_time = time.time()
        
        try:
            # Prepare input
            input_str = None
            if input_data:
                input_str = json.dumps(input_data)
            
            # Run executable
            result = subprocess.run(
                [str(executable)],
                input=input_str,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode != 0:
                error_msg = f"Fortran execution failed:\n{result.stderr}"
                logger.error(error_msg)
                raise FortranExecutionError(error_msg)
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "execution_time": execution_time,
            }
        
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            error_msg = f"Fortran execution timed out after {timeout}s"
            logger.error(error_msg)
            raise FortranExecutionError(error_msg)
    
    def run_harness(
        self,
        fortran_harness: str,
        test_data: Dict[str, Any],
        dependencies: Optional[Path] = None,
    ) -> List[Dict[str, Any]]:
        """
        Compile and run Fortran test harness with test data.
        
        This is the main interface for running tests. It:
        1. Compiles the test harness
        2. Runs it for each test case
        3. Parses outputs
        
        Args:
            fortran_harness: Fortran test harness code
            test_data: Test data dictionary with test_cases
            dependencies: Optional original Fortran file for includes
            
        Returns:
            List of output dictionaries, one per test case
        """
        # Compile harness
        logger.info("Compiling Fortran test harness...")
        
        deps = [dependencies] if dependencies else None
        executable = self.compile(fortran_harness, dependencies=deps)
        
        try:
            results = []
            
            # Run for each test case
            for i, test_case in enumerate(test_data["test_cases"]):
                logger.info(f"Running Fortran test case {i+1}/{len(test_data['test_cases'])}")
                
                result = self.run(executable, test_case)
                
                # Parse output
                outputs = self._parse_fortran_output(result["stdout"])
                
                results.append({
                    "outputs": outputs,
                    "execution_time": result["execution_time"],
                    "stderr": result["stderr"],
                })
            
            return results
        
        finally:
            # Clean up executable
            executable.unlink(missing_ok=True)
    
    def _parse_fortran_output(self, stdout: str) -> Dict[str, Any]:
        """
        Parse Fortran output.
        
        Expected format: JSON output written by Fortran harness
        
        Args:
            stdout: Standard output from Fortran program
            
        Returns:
            Dictionary of output variables
        """
        try:
            # Try to parse as JSON first
            return json.loads(stdout)
        except json.JSONDecodeError:
            # Fall back to parsing key=value pairs
            outputs = {}
            for line in stdout.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Try to convert to float
                    try:
                        outputs[key] = float(value)
                    except ValueError:
                        outputs[key] = value
            
            return outputs


def create_fortran_test_wrapper(
    subroutine_name: str,
    parameters: List[Dict[str, Any]],
    input_vars: List[str],
    output_vars: List[str],
) -> str:
    """
    Create a basic Fortran test wrapper.
    
    This generates a simple wrapper that:
    1. Declares variables
    2. Reads inputs from a file
    3. Calls the subroutine
    4. Writes outputs to a file
    
    Args:
        subroutine_name: Name of the subroutine to test
        parameters: List of parameter specifications
        input_vars: List of input variable names
        output_vars: List of output variable names
        
    Returns:
        Fortran wrapper code as string
    """
    # Build variable declarations
    declarations = []
    for param in parameters:
        name = param["name"]
        ftype = param["type"]
        shape = param.get("shape", "")
        intent = param.get("intent", "")
        
        if shape:
            decl = f"  {ftype}, dimension({shape}) :: {name}"
        else:
            decl = f"  {ftype} :: {name}"
        
        declarations.append(decl)
    
    # Build read statements
    reads = []
    for var in input_vars:
        reads.append(f"  read(10,*) {var}")
    
    # Build write statements
    writes = []
    for var in output_vars:
        writes.append(f"  write(20,*) '{var}=', {var}")
    
    wrapper = f"""program test_{subroutine_name}
  implicit none
  
  ! Variable declarations
{chr(10).join(declarations)}
  
  ! Open input file
  open(unit=10, file='test_input.dat', status='old', action='read')
  
  ! Read inputs
{chr(10).join(reads)}
  
  close(10)
  
  ! Call subroutine
  call {subroutine_name}({', '.join(p['name'] for p in parameters)})
  
  ! Open output file
  open(unit=20, file='test_output.dat', status='replace', action='write')
  
  ! Write outputs
{chr(10).join(writes)}
  
  close(20)
  
end program test_{subroutine_name}
"""
    
    return wrapper

