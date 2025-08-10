"""
microgpt - Lightweight GPT implementation designed for resource-constrained environments
"""

__version__ = "0.0.2.dev1"
__author__ = "Wu Fuheng"
__email__ = "wufuheng@gmail.com"

# Import only when the module is actually used to avoid dependency issues during package discovery
try:
    from .model import GPT, GPTConfig
    __all__ = ["GPT", "GPTConfig"]
except ImportError:
    # If dependencies aren't available, just provide the version info
    __all__ = []
