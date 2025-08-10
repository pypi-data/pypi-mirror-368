import dataclasses

from plumed_nodes.interfaces import CollectiveVariable


@dataclasses.dataclass
class PrintActionNode:
    """Node for PRINT action."""

    cv: CollectiveVariable
    stride: int = 1
    file: str = "PRINT"
