import numpy as np
from typing import List
from pwdata.image import Image
from pwdata.config import Config

def scale_cell(
    image: Config,
    scale_factor:float):
    """
    Scale the cell of the system.

    Parameters
    ----------
    image_data : Include Image Object
        The system to be scaled.
    scale_factor : float
        The scale factor of the cell.

    Returns
    -------
    tmp_system : a new Image object
        The scaled system.
    """
    image = image.images[0]
    tmp_system = image.copy()
    if tmp_system.cartesian:
        tmp_system.position = tmp_system.get_scaled_positions(wrap=False)   # for cartesian coordinates, we need to convert it to fractional coordinates
        tmp_system.cartesian = False                                        # set cartesian to False, this is important, otherwise, the scaled cell will be scaled again while saving (also in the write_struc.py)
    tmp_system.lattice = np.dot(tmp_system.lattice, scale_factor)
    tmp_system.atom_types_image = tmp_system.arrays['atom_types_image']
    return tmp_system

class ScaleCell(object):
    def __init__(self, atoms:List[Image]):
        self.atoms = atoms

    def scale(self,
        scale_factor:float):
        """
        Scale the cell of the system.

        Parameters
        ----------
        scale_factor : float
            The scale factor of the cell.

        Returns
        -------
        tmp_system : Image
            The scaled system.
        """
        tmp_system = self.atoms.copy()
        if tmp_system.cartesian:
            tmp_system.position = tmp_system.get_scaled_positions(wrap=False)   # for cartesian coordinates, we need to convert it to fractional coordinates
            tmp_system.cartesian = False                                        # set cartesian to False, this is important, otherwise, the scaled cell will be scaled again while saving (also in the write_struc.py)
        tmp_system.lattice = np.dot(tmp_system.lattice, scale_factor)
        tmp_system.atom_types_image = tmp_system.arrays['atom_types_image']
        return tmp_system

class BatchScaleCell(object):
    @staticmethod
    def batch_scale(
            raw_obj:Image,
            scale_factor:float):
        
        tmp_structure = raw_obj
        perturbed_obj = ScaleCell(tmp_structure)
        perturbed_structs = perturbed_obj.scale(scale_factor)
        return perturbed_structs