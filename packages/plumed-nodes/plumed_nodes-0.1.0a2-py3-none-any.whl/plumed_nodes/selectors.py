import dataclasses

import ase
import rdkit2ase

from plumed_nodes.interfaces import AtomSelector


@dataclasses.dataclass
class IndexSelector(AtomSelector):
    indices: list[int]

    def select(self, atoms: ase.Atoms) -> list[list[int]]:
        return [[x] for x in self.indices]


@dataclasses.dataclass
class SMILESSelector(AtomSelector):
    smiles: str

    def select(self, atoms: ase.Atoms) -> list[list[int]]:
        matches = rdkit2ase.match_substructure(atoms, smiles=self.smiles)
        return [list(match) for match in matches]
