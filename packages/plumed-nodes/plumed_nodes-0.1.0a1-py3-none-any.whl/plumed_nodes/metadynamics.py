import dataclasses
from pathlib import Path

import ase
import zntrack
from ase.calculators.calculator import Calculator

from plumed_nodes.interfaces import (
    CollectiveVariable,
    MetadynamicsBiasCollectiveVariable,
    NodeWithCalculator,
)


@dataclasses.dataclass
class MetaDBiasCV(MetadynamicsBiasCollectiveVariable):
    """
    Resources
    ---------
    - https://www.plumed.org/doc-master/user-doc/html/METAD/
    """
    cv: CollectiveVariable
    sigma: float | None = None
    grid_min: float | None = None
    grid_max: float | None = None
    grid_bin: int | None = None


@dataclasses.dataclass
class MetaDynamicsConfig:
    """
    Base configuration for metadynamics.
    This contains only the global parameters that apply to all CVs.
    """

    height: float = 1.0  # kJ/mol
    pace: int = 500
    biasfactor: float | None = None
    temp: float = 300.0
    file: str = "HILLS"
    adaptive: str = "NONE"  # NONE, DIFF, GEOM


class MetaDynamicsModel(zntrack.Node, NodeWithCalculator):
    config: MetaDynamicsConfig
    data: list[ase.Atoms]
    data_idx: int = -1
    bias_cvs: list[MetaDBiasCV] = dataclasses.field(default_factory=list)

    def run(self):
        pass # not relevant for the to_plumed and get_calculator methods

    def get_calculator(
        self, *, directory: str | Path | None = None, **kwargs
    ) -> Calculator:
        raise NotImplementedError

    def to_plumed(self, atoms: ase.Atoms) -> str:
        """Generate PLUMED input string for the metadynamics model."""
        plumed_lines = []
        all_labels = []

        sigmas, grid_mins, grid_maxs, grid_bins = [], [], [], []

        for bias_cv in self.bias_cvs:
            labels, cv_str = bias_cv.cv.to_plumed(atoms)
            plumed_lines.append(cv_str)
            all_labels.extend(labels)

            # Collect per-CV parameters for later
            sigmas.append(str(bias_cv.sigma) if bias_cv.sigma is not None else None)
            grid_mins.append(str(bias_cv.grid_min) if bias_cv.grid_min is not None else None)
            grid_maxs.append(str(bias_cv.grid_max) if bias_cv.grid_max is not None else None)
            grid_bins.append(str(bias_cv.grid_bin) if bias_cv.grid_bin is not None else None)

        metad_parts = [
            "METAD",
            f"ARG={','.join(all_labels)}",
            f"HEIGHT={self.config.height}",
            f"PACE={self.config.pace}",
            f"TEMP={self.config.temp}",
            f"FILE={self.config.file}",
            f"ADAPTIVE={self.config.adaptive}",
        ]
        if self.config.biasfactor is not None:
            metad_parts.append(f"BIASFACTOR={self.config.biasfactor}")

        # Add SIGMA, GRID_MIN, GRID_MAX, GRID_BIN only if any value is set
        if any(v is not None for v in sigmas):
            metad_parts.append(f"SIGMA={','.join(v if v is not None else '0.0' for v in sigmas)}")
        if any(v is not None for v in grid_mins):
            metad_parts.append(f"GRID_MIN={','.join(v if v is not None else '0.0' for v in grid_mins)}")
        if any(v is not None for v in grid_maxs):
            metad_parts.append(f"GRID_MAX={','.join(v if v is not None else '0.0' for v in grid_maxs)}")
        if any(v is not None for v in grid_bins):
            metad_parts.append(f"GRID_BIN={','.join(v if v is not None else '0' for v in grid_bins)}")

        plumed_lines.append(f"metad: {' '.join(metad_parts)}")
        return "\n".join(plumed_lines)