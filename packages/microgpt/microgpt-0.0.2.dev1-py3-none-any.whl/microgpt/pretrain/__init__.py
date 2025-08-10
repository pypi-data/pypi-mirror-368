"""
Pretraining modules for microgpt
"""

# Import only when the module is actually used to avoid dependency issues during package discovery
try:
    from .clm_pretrain_v0 import main
    __all__ = ["main"]
except ImportError:
    # If dependencies aren't available, just provide the module info
    __all__ = []
