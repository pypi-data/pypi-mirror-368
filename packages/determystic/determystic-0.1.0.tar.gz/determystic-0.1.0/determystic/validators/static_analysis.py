"""Static analysis validators using ruff and ty."""

import asyncio
import asyncio.subprocess
from pathlib import Path

from .base import BaseValidator, ValidationResult


class StaticAnalysisValidator(BaseValidator):
    """
    Composite validator that runs all static analysis tools. Since these are CLI
    driven, this static analyzer operates via CLI calls where we passthrough
    the validated output for each file.
    
    """
    
    def __init__(self, path: Path, command: list[str]) -> None:
        super().__init__(name="static_analysis", path=path)
        self.command = command
    
    @classmethod
    def create_validators(cls, path: Path) -> list[BaseValidator]:
        return [
            cls(path, ["ruff", "check", str(path), "--no-fix"]),
            cls(path, ["ty", "check", str(path)])
        ]   
    
    async def validate(self, path: Path) -> ValidationResult:
        """Run the static analysis command on the given path."""
        process = await asyncio.create_subprocess_exec(
            *self.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=path
        )
        
        stdout, stderr = await process.communicate()
        return ValidationResult(
            success=process.returncode == 0,
            output=stdout.decode() if stdout else stderr.decode()
        )
