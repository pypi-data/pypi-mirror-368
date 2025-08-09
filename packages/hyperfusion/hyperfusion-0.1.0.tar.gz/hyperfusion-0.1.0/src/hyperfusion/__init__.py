"""hyperfusion: High-performance SQL execution engine with UDTF support."""

# Export main UDTF decorator and utilities
from .udtf import udtf, UDTFFunction
from .udtf.registry import registry

# Export CLI for programmatic use
from .cli.main import main as cli_main

__version__ = "0.1.0"
__all__ = ["udtf", "UDTFFunction", "registry", "cli_main"]

# Example usage in docstring
"""
Usage as library:

    from hyperfusion import udtf
    
    @udtf
    async def my_function(x: int, y: str) -> list[dict]:
        return [{"result": x, "input": y}]

Usage as CLI:

    $ hyperfusion run
    $ hyperfusion run python-kernel --port 50051
    $ pip install hyperfusion && hyperfusion --help
"""