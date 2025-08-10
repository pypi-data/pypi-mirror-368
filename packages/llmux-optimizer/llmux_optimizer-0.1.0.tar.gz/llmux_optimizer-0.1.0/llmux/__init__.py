"""LLMux: Automatically find cheaper LLM alternatives while maintaining performance."""

from .api import optimize_cost, optimize_speed
from .provider import Provider, get_provider
from .evaluator import Evaluator
from .selector import Selector

__version__ = "0.1.0"
__author__ = "Mihir Ahuja"
__email__ = "mihirahuja09@gmail.com"

__all__ = [
    "optimize_cost",
    "optimize_speed",
    "Provider",
    "Evaluator",
    "Selector",
    "get_provider",
]


# Convenience imports for common use cases
def version():
    """Return the current version of llmux."""
    return __version__
