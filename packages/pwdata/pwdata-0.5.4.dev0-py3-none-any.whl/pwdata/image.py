import numpy as np
import copy
import os 
from pwdata.build.write_struc import write_config, write_vasp, write_lammps
from pwdata.calculators.const import elements
from pwdata.build.geometry import wrap_positions
from pwdata.build.cell import scaled_positions
from pwdata.lmps import Box2l
from pwdata.utils.format_change import to_numpy_array, to_integer, to_float
# 1. initial the image class
class Image(object):
    def __init__(self, formula = None,
                 atom_type = None, atom_type_num = None, atom_nums = None, atom_types_image = None, 
                 iteration = None, Etot = None, Ep = None, Ek = None, scf = None, lattice = None, 
                 virial = None, position = None, force = None, atomic_energy = None,
                 content = None, image_nums = None, pbc = None, cartesian = None):
        """
        Represents an image in a AIMD trajectory.

        Args:
            atom_type (str): The type of atom.
            atom_type_num (int): The number of atom types.
            atom_nums (list): The number of atoms.
            atom_types_image (list): The types of atoms in the image.
            iteration (int): The iteration number.
            Etot (float): The total energy.
            Ep (float): The potential energy.
            Ek (float): The kinetic energy.
            scf (float): The index of the self-consistent field.
            lattice (list): The lattice vectors.
            virial (list): The virial tensor.
            position (list): The atomic positions.
            force (list): The atomic forces.
            atomic_energy (list): The atomic energies.
            content (str): The content of the image.
            image_nums (int): The number of images.
            pbc (list): three bool, Periodic boundary conditions flags.  Examples: [True, True, False] or [1, 1, 0]. True (1) means periodic, False (0) means non-periodic. Default: [False, False, False].
        """
        self.formula = formula
        self.atom_nums = atom_nums
        self.iteration = iteration
        self.atom_type = to_numpy_array(atom_type)
        self.atom_type_num = to_numpy_array(atom_type_num)
        self.atom_types_image = to_numpy_array(atom_types_image)
        self.Etot = to_float(Etot)
        self.Ep = to_float(Ep)
        self.Ek = to_float(Ek)
        self.scf = to_integer(scf)
        self.image_nums = to_integer(image_nums)
        self.lattice = to_numpy_array(lattice)
        self.virial = to_numpy_array(virial)
        self.position = to_numpy_array(position)    # this position can be fractional coordinates or cartesian coordinates
        self.force = to_numpy_array(force)
        self.atomic_energy = to_numpy_array(atomic_energy)
        self.content = content
        self.cartesian = cartesian if cartesian is not None else False
        self.pbc = to_numpy_array(pbc) if pbc is not None else np.zeros(3, bool)
        self.arrays = self.prim_dict() # here, position will be convert to cartesian coordinates
        self.data = {}
    
    def sort_by_atomtype(self):
        sort_indices = np.argsort(self.atom_types_image)
        self.atom_types_image = self.atom_types_image[sort_indices]
        self.position = self.position[sort_indices]
        self.force = self.force[sort_indices]
        if self.atomic_energy is not None:
            self.atomic_energy = self.atomic_energy[sort_indices]
        cout_type, indices = np.unique(self.atom_types_image, return_index=True)
        sorted_indices = np.argsort(indices)
        cout_type = cout_type[sorted_indices]
        cout_num = np.bincount(self.atom_types_image)[cout_type]
        self.atom_type = to_numpy_array(cout_type)
        self.atom_type_num=to_numpy_array(cout_num)

    def copy(self):
        """Return a copy."""
        if self.cartesian:
            pass
        else:
            self._set_cartesian()
        atoms = self.__class__(lattice=self.lattice, position=self.position, pbc=self.pbc, cartesian=self.cartesian)
        atoms.arrays = {}
        # atoms.cartesian = self.cartesian
        prim_dict = self.prim_dict()
        for name, a in prim_dict.items():
            atoms.arrays[name] = a.copy()
        return atoms

    def to(self, data_path, data_name = None, format = None, direct = True, sort = False, wrap = False):
        """
        Write atoms object to a new file.

        Note: Set sort to False for CP2K, because data from CP2K is already sorted!!!. It will result in a wrong order if sort again.

        Args:
        data_path (str): The path to save the file.
        data_name (str): Save name of the configuration file.
        format (str): The format of the file. Default is None.
        direct (bool): The coordinates of the atoms are in fractional coordinates or cartesian coordinates. (0 0 0) -> (1 1 1)
        sort (bool): Whether to sort the atoms by atomic number. Default is False.
        wrap (bool): hether to wrap the atoms into the simulation box (for pbc). Default is False.
        """
        assert format is not None, "output file format is not specified"
        if not os.path.exists(data_path):
            os.makedirs(data_path)
        if format.lower() == 'pwmat/config':
            write_config(self, data_path, data_name, sort=sort, wrap=wrap)
        elif format.lower() == 'vasp/poscar':
            write_vasp(self, data_path, data_name, direct=direct, sort=sort, wrap=wrap)
        elif format.lower() == "lammps/lmp":
            write_lammps(self, data_path, data_name, sort=sort, wrap=wrap)
        elif format.lower() == "extxyz":
            raise Exception()
        else:
            raise RuntimeError('Unknown file format')
    
    def prim_dict(self):
        """Return a dictionary of the primitive image data."""
        if self.atom_types_image is None:
            return {'atom_types_image': np.array([], dtype=np.int64), 'position': np.array([]).reshape(-1, 3)}
        else:
            return {'atom_types_image': np.array(self.atom_types_image, dtype=np.int64), 'position': np.array(self.position).reshape(-1, 3)}
    
    def extend(self, other):
        """Extend atoms object by appending atoms from *other*."""
        n1 = len(self)
        n2 = len(other)

        for name, a1 in self.arrays.items():
            a = np.zeros((n1 + n2,) + a1.shape[1:], a1.dtype)
            a[:n1] = a1
            if name == 'masses':
                pass
            else:
                a2 = other.arrays.get(name)
            if a2 is not None:
                a[n1:] = a2
            self.arrays[name] = a

        for name, a2 in other.arrays.items():
            if name in self.arrays:
                continue
            a = np.empty((n1 + n2,) + a2.shape[1:], a2.dtype)
            a[n1:] = a2
            if name == 'masses':
                pass
            else:
                a[:n1] = 0

            self.set_array(name, a)

    def wrap(self, **wrap_kw):
        """Wrap positions to unit cell.

        Parameters:

        wrap_kw: (keyword=value) pairs
            optional keywords `pbc`, `center`, `pretty_translation`, `eps`,
            see :func:`ase.geometry.wrap_positions`
        """

        if 'pbc' not in wrap_kw:
            wrap_kw['pbc'] = self.pbc

        self.position= self.get_positions(wrap=True, **wrap_kw)

    def get_positions(self, wrap=False, **wrap_kw):
        """Get array of positions.

        Parameters:

        wrap: bool
            wrap atoms back to the cell before returning positions
        wrap_kw: (keyword=value) pairs
            optional keywords `pbc`, `center`, `pretty_translation`, `eps`,
            see :func:`ase.geometry.wrap_positions`
        """
        if wrap:
            if 'pbc' not in wrap_kw:
                wrap_kw['pbc'] = self.pbc
            position = self._get_positions()
            return wrap_positions(position, self.lattice, **wrap_kw)
        else:
            return self.arrays['position'].copy()
        
    def get_scaled_positions(self, wrap=True):
        """Get positions relative to unit cell.

        If wrap is True, atoms outside the unit cell will be wrapped into
        the cell in those directions with periodic boundary conditions
        so that the scaled coordinates are between zero and one.

        If any cell vectors are zero, the corresponding coordinates
        are evaluated as if the cell were completed using
        ``cell.complete_cell()``.  This means coordinates will be Cartesian
        as long as the non-zero cell vectors span a Cartesian axis or
        plane."""

        fractional = scaled_positions(self.lattice, self.position)
        if wrap:
            for i, periodic in enumerate(self.pbc):
                if periodic:
                    # Yes, we need to do it twice.
                    # See the scaled_positions.py test.
                    fractional[:, i] %= 1.0
                    fractional[:, i] %= 1.0
        self.cartesian = False
        return fractional

    def get_atomic_numbers(self):
        """Get integer array of atomic numbers."""
        return self.arrays['atom_types_image'].copy()
    
    def get_virial(self):
        """Get virial tensor."""
        return self._get_virial()
    
    def _get_virial(self):
        virial = np.array(self.virial).reshape(3, 3)
        return virial
    
    def get_stress(self):
        """Get stress tensor."""
        stress = self.get_virial() / - self.get_volume()
        return stress

    def get_volume(self):
        """Get volume of the unit cell."""
        return np.abs(np.linalg.det(self.lattice))
    
    def _get_positions(self):
        """Return reference to positions-array for in-place manipulations."""
        return self.arrays['position']
    
    def _set_orthorhombic(self):
        """Set the cell to be orthorhombic."""
        lattice = Box2l(self.lattice)
        xx = [lattice[0], 0, 0]
        yy = [lattice[1], lattice[2], 0]
        zz = [lattice[3], lattice[4], lattice[5]]
        self.lattice = [xx, yy, zz]
    
    def _set_cartesian(self):
        """Set positions in Cartesian coordinates."""
        self.position = frac2cart(self.position, self.lattice)
        self.cartesian = True
        return self
    
    def _set_fractional(self):
        """Set positions in fractional coordinates.
            no use, see get_scaled_positions(wrap=wrap) instead"""
        self.position = cart2frac(self.position, self.lattice)
        self.cartesian = False
        return self
    
    def __len__(self):
        return len(self.arrays['position'])

'''follow functions shoule be merged into the Image class later!!!'''
def elements_to_order(atom_names, atom_types_image, atom_nums, is_atom_type_name=False):
    """
    Replaces the atom types's order (from 1) to the order of the elements in the atom_names list.
    
    Args:
        atom_names (list): List of atom names.
        atom_types_image (list): List of atom types.
        atom_nums (int): Number of atoms.

    Example:
        >>> atom_names = ['C', 'N']
        >>> atom_types_image = [1, 1, 1, 1, 1, ... , 2, 2, 2, 2, 2, ... , 2]
        >>> if is_atom_type_name is Ture, the atom_types_image = ["C", "C", "C", "C", "C", ... , "N", "N", "N", "N", "N", ... , "N"]
        >>> atom_nums = 56
        >>> elements_to_order(atom_names, atom_types_image, atom_nums)
        [6, 6, 6, 6, 6, ... , 7, 7, 7, 7, 7, ... , 7]
        
    Returns:
        list: Updated list of atom types per atom.
    """
    # for idx, name in enumerate(atom_names):
    #     for ii in range(atom_nums):
    #         if name in elements and atom_types_image[ii] == idx+1:
    #             atom_types_image[ii] = elements.index(name)
    if is_atom_type_name:
        atom_types_image = [elements.index(name) for name in atom_types_image]
        return atom_types_image
    else:
        type_mapping = {idx+1: elements.index(name) for idx, name in enumerate(atom_names)}
        atom_types_image = [type_mapping[atom_type] for atom_type in atom_types_image]
        return atom_types_image

def frac2cart(position, lattice):
    """
    Convert fractional coordinates to Cartesian coordinates.

    Args:
        position (list): List of fractional coordinates.
        lattice (list): List of lattice vectors.

    Example:
        >>> position = [[0.5, 0.5, 0.5], [0.5, 0.5, 0.5]]
        >>> lattice = [[10, 0, 0], [0, 10, 0], [0, 0, 10]]
        >>> frac2cart(position, lattice)
        [[5.0, 5.0, 5.0], [5.0, 5.0, 5.0]]

    Returns:
        list: List of Cartesian coordinates.
    """
    position = np.array(position).reshape(-1, 3)
    lattice = np.array(lattice).reshape(3, 3)
    return np.dot(position, lattice)

def cart2frac(position, lattice):
    """
    Convert Cartesian coordinates to fractional coordinates.

    Args:
        position (list): List of Cartesian coordinates.
        lattice (list): List of lattice vectors.

    Example:
        >>> position = [[5.0, 5.0, 5.0], [5.0, 5.0, 5.0]]
        >>> lattice = [[10, 0, 0], [0, 10, 0], [0, 0, 10]]
        >>> cart2frac(position, lattice)
        [[0.5, 0.5, 0.5], [0.5, 0.5, 0.5]]

    Returns:
        list: List of fractional coordinates.
    """
    position = np.array(position).reshape(-1, 3)
    lattice = np.array(lattice).reshape(3, 3)
    return np.dot(position, np.linalg.inv(lattice))
