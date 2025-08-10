import dataclasses
from enum import Enum
from typing import Union

from ase import Atoms

from plumed_nodes.interfaces import AtomSelector, CollectiveVariable


class GroupReductionStrategy(Enum):
    """How to handle groups with multiple atoms."""

    CENTER_OF_MASS = "com"
    CENTER_OF_GEOMETRY = "cog"
    FIRST_ATOM = "first"
    ALL_ATOMS = "all"


class MultiGroupStrategy(Enum):
    """
    Enum representing strategies for handling multiple groups selected by selectors.

    Attributes
    ----------
    FIRST : str
        Use only the first group from each selector.
    ALL_PAIRS : str
        Use all possible pairs of groups between selectors.
    CORRESPONDING : str
        Use corresponding groups from each selector (i.e., group 1 with group 1, group 2 with group 2, etc.).
    FIRST_TO_ALL : str
        Use the first group from one selector with all groups from the other selector.

    """

    FIRST = "first"
    ALL_PAIRS = "all_pairs"
    CORRESPONDING = "corresponding"
    FIRST_TO_ALL = "first_to_all"


@dataclasses.dataclass
class DistanceCV(CollectiveVariable):
    """
    PLUMED DISTANCE collective variable.
    """

    x1: AtomSelector
    x2: AtomSelector
    prefix: str
    group_reduction: GroupReductionStrategy = GroupReductionStrategy.CENTER_OF_MASS
    multi_group: MultiGroupStrategy = MultiGroupStrategy.FIRST
    create_virtual_sites: bool = True

    def to_plumed(self, atoms: Atoms) -> tuple[list[str], str]:
        """Generate PLUMED input string(s) for DISTANCE.

        Returns
        -------
        - list of distance labels
        - PLUMED input string
        """
        groups1 = self.x1.select(atoms)
        groups2 = self.x2.select(atoms)

        if not groups1 or not groups2:
            raise ValueError(f"Empty selection for distance CV {self.prefix}")

        # Check for overlaps
        overlaps = self._check_overlaps(groups1, groups2)
        if overlaps and self.group_reduction not in [
            GroupReductionStrategy.CENTER_OF_MASS,
            GroupReductionStrategy.CENTER_OF_GEOMETRY,
        ]:
            raise ValueError(
                f"Overlapping atoms found: {overlaps}. "
                "This is only valid with CENTER_OF_MASS or CENTER_OF_GEOMETRY reduction."
            )

        commands = self._generate_commands(groups1, groups2, atoms)

        # Extract labels from commands
        labels = []
        for cmd in commands:
            if ":" in cmd and cmd.strip().startswith((self.prefix, f"{self.prefix}_")):
                label_part = cmd.split(":")[0].strip()
                if "DISTANCE" in cmd:
                    labels.append(label_part)

        return labels, "\n".join(commands)

    def _check_overlaps(
        self, groups1: list[list[int]], groups2: list[list[int]]
    ) -> set[int]:
        """Check for overlapping indices between groups."""
        flat1 = {idx for group in groups1 for idx in group}
        flat2 = {idx for group in groups2 for idx in group}
        return flat1.intersection(flat2)

    def _generate_commands(
        self, groups1: list[list[int]], groups2: list[list[int]], atoms: Atoms
    ) -> list[str]:
        """Generate PLUMED commands based on the strategies."""
        commands = []

        # Determine which groups to process based on multi_group strategy
        if self.multi_group == MultiGroupStrategy.FIRST:
            # Only process first groups
            process_groups1 = [groups1[0]]
            process_groups2 = [groups2[0]]
            group_pairs = [(0, 0)]
        elif self.multi_group == MultiGroupStrategy.ALL_PAIRS:
            process_groups1 = groups1
            process_groups2 = groups2
            group_pairs = [
                (i, j) for i in range(len(groups1)) for j in range(len(groups2))
            ]
        elif self.multi_group == MultiGroupStrategy.CORRESPONDING:
            n = min(len(groups1), len(groups2))
            process_groups1 = groups1[:n]
            process_groups2 = groups2[:n]
            group_pairs = [(i, i) for i in range(n)]
        elif self.multi_group == MultiGroupStrategy.FIRST_TO_ALL:
            process_groups1 = [groups1[0]]
            process_groups2 = groups2
            group_pairs = [(0, j) for j in range(len(groups2))]

        # Create virtual sites for the groups we're actually using
        sites1 = {}
        sites2 = {}

        for i, group in enumerate(process_groups1):
            site, site_commands = self._reduce_group(
                group, f"{self.prefix}_g1_{i}", atoms
            )
            sites1[i] = site
            commands.extend(site_commands)

        for j, group in enumerate(process_groups2):
            site, site_commands = self._reduce_group(
                group, f"{self.prefix}_g2_{j}", atoms
            )
            sites2[j] = site
            commands.extend(site_commands)

        # Create distance commands for the specified pairs
        for i, j in group_pairs:
            if len(group_pairs) == 1:
                dist_label = self.prefix
            else:
                dist_label = f"{self.prefix}_{i}_{j}"

            commands.append(
                self._make_distance_command(sites1[i], sites2[j], dist_label)
            )

        return commands

    def _reduce_group(
        self, group: list[int], prefix: str, atoms: Atoms
    ) -> tuple[Union[str, list[int]], list[str]]:
        """
        Reduce a group to a single point based on reduction strategy.

        Returns:
            - Site identifier (atom index, virtual site label, or group)
            - List of PLUMED commands to create virtual sites
        """
        commands = []

        if len(group) == 1:
            # Single atom - no reduction needed
            return str(group[0] + 1), commands

        if self.group_reduction == GroupReductionStrategy.FIRST_ATOM:
            return str(group[0] + 1), commands

        if self.group_reduction == GroupReductionStrategy.CENTER_OF_MASS:
            if self.create_virtual_sites:
                site_label = f"{prefix}_com"
                atom_list = ",".join(str(idx + 1) for idx in group)
                commands.append(f"{site_label}: COM ATOMS={atom_list}")
                return site_label, commands
            else:
                return group, commands

        if self.group_reduction == GroupReductionStrategy.CENTER_OF_GEOMETRY:
            site_label = f"{prefix}_cog"
            atom_list = ",".join(str(idx + 1) for idx in group)
            commands.append(f"{site_label}: CENTER ATOMS={atom_list}")
            return site_label, commands

        if self.group_reduction == GroupReductionStrategy.ALL_ATOMS:
            return group, commands

        raise ValueError(f"Unknown group reduction strategy: {self.group_reduction}")

    def _make_distance_command(
        self, site1: Union[str, list], site2: Union[str, list], label: str
    ) -> str:
        """Create a single DISTANCE command."""
        if isinstance(site1, str) and isinstance(site2, str):
            return f"{label}: DISTANCE ATOMS={site1},{site2}"
        elif isinstance(site1, list) and isinstance(site2, list):
            atoms1 = ",".join(str(idx + 1) for idx in site1)
            atoms2 = ",".join(str(idx + 1) for idx in site2)
            return f"{label}: DISTANCE ATOMS1={atoms1} ATOMS2={atoms2}"
        else:
            if isinstance(site1, list):
                atoms1 = ",".join(str(idx + 1) for idx in site1)
                return f"{label}: DISTANCE ATOMS1={atoms1} ATOMS2={site2}"
            else:
                atoms2 = ",".join(str(idx + 1) for idx in site2)
                return f"{label}: DISTANCE ATOMS1={site1} ATOMS2={atoms2}"

