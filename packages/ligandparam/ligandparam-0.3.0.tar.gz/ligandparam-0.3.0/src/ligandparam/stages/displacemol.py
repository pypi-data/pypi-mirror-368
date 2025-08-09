import warnings
from typing import Optional,  Union

import numpy as np
import MDAnalysis as mda

from pathlib import Path

from ligandparam.stages.abstractstage import AbstractStage
from MDAnalysis.topology.guessers import guess_masses
from MDAnalysis.topology.guessers import guess_types

class StageDisplaceMol(AbstractStage):
    """Displaces a molecule based on a vector or centers it at the origin.

    Attributes:
        in_molecule (Path): Path to the input molecule file.
        out_molecule (Path): Path where the displaced/centered molecule will be written.
        displacement_vtor (Optional[np.ndarray]): The vector used for displacement.
                                                 Only set if 'vector' is provided in kwargs.
        center (bool): If True, the molecule will be centered at the origin.
                       If False, displacement is done using `displacement_vtor`.

    TODO
    ----
    - Generalize the part that guesses types and masses in the execute method.
    
    """

    def __init__(self, stage_name: str, main_input: Union[Path, str], cwd: Union[Path, str], *args, **kwargs) -> None:
        super().__init__(stage_name, main_input, cwd, *args, **kwargs)
        self.in_molecule = Path(main_input)
        self.out_molecule = Path(kwargs["out_mol"])

        if "vector" in kwargs:
            self.displacement_vtor = kwargs["vector"]
            if not isinstance(self.displacement_vtor, np.ndarray):
                raise TypeError("vector must be a numpy array")
            self.center = False
        else:
            self.center = True
        self.add_required(Path(self.in_molecule))

    def _append_stage(self, stage: "AbstractStage") -> "AbstractStage":
        return stage

    def execute(self, dry_run=False, nproc: Optional[int]=None, mem: Optional[int]=None) -> np.ndarray:

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            u = mda.Universe(self.in_molecule)
            if np.any(np.isclose(u.atoms.masses, 0, atol=0.1)):
                u.guess_TopologyAttrs(to_guess=['elements'], force_guess=['masses'])
            # We tried to get correct masses but may have failed in the process. Lack of masses will fail
            # MDAnalysis's center_of_mass(), so just set them to 1.0, since the exact values are not important
            u.atoms.masses[np.isclose(u.atoms.masses, 0, atol=0.1)] = 1.0
            
            if self.center:
                self.displacement_vtor = -u.atoms.center_of_mass()
            if np.isnan(self.displacement_vtor).any():
                print("Displacement vector contains NaN values.")
                print("Center of mass", u.atoms.center_of_mass())
                print("Displacement vector", self.displacement_vtor)
                print("Input molecule:", self.in_molecule)
                print("u.atoms.positions", u.atoms.positions)
                print("u.atoms.masses", u.atoms.masses)
                print()
                raise ValueError("Displacement vector contains NaN values.")
            u.atoms.translate(self.displacement_vtor)
            u.atoms.write(self.out_molecule)
            
        return self.displacement_vtor


    def _clean(self):
        raise NotImplementedError("clean method not implemented")
