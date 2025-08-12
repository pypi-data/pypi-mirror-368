from .serial_graph import MDLGraphProxy

try:
    from .mdl_ds import MDLGraph
except ImportError:
    MDLGraph = None
    pass

__all__ = ["MDLGraph", "MDLGraphProxy"]