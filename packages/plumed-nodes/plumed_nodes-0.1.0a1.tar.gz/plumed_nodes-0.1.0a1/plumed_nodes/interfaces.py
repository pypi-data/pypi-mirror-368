import pathlib
from typing import Protocol

import ase
from ase.calculators.calculator import Calculator


class NodeWithCalculator(Protocol):
    """Any class with a `get_calculator` method returning an ASE Calculator."""

    def get_calculator(
        self, *, directory: str | pathlib.Path | None = None, **kwargs
    ) -> Calculator: ...


class AtomSelector(Protocol):
    """Protocol for selecting atoms within a single ASE Atoms object.

    This interface defines the contract for selecting atoms based on various
    criteria within an individual frame/structure.
    """

    def select(self, atoms: ase.Atoms) -> list[list[int]]:
        """Select atoms based on the implemented criteria.

        Parameters
        ----------
        atoms : ase.Atoms
            The atomic structure to select from.

        Returns
        -------
        list[list[int]]
            Groups of indices of selected atoms. All indices in the inner lists
            are representative of the same group, e.g. one molecule.
        """
        ...


class CollectiveVariable(Protocol):
    """Protocol for collective variables (CVs) that can be used in PLUMED."""

    prefix: str

    def to_plumed(self, atoms: ase.Atoms) -> tuple[list[str], str]:
        """
        Convert the collective variable to a PLUMED string.

        Parameters
        ----------
        atoms : ase.Atoms
            The atomic structure to use for generating the PLUMED string.

        Returns
        -------
        tuple[list[str], str]
            - List of distance labels.
            - PLUMED input string.
        """
        ...


class MetadynamicsBiasCollectiveVariable(Protocol):
    """Protocol for metadata associated with a bias in PLUMED."""

    cv: CollectiveVariable
    sigma: float | None = None
    grid_min: float | None = None
    grid_max: float | None = None
    grid_bin: int | None = None
