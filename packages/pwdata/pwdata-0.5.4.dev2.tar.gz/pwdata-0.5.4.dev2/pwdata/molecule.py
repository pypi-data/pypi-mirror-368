import numpy as np
import os 
from pwdata.utils.format_change import to_numpy_array, to_integer, to_float
from ase.db.row import AtomsRow
# 1. initial the image class
class Molecule():
    def __init__(self, atoms_row:AtomsRow = None, formula = None,
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
        # from atoms_row.data which is dict
        self.data                   = atoms_row.data
        self.source                 = atoms_row.data['source']
        self.reference_source       = atoms_row.data['reference_source']
        self.data_id                = atoms_row.data['data_id']
        self.charge                 = atoms_row.data['charge']
        self.spin                   = atoms_row.data['spin']
        self.num_atoms              = atoms_row.data['num_atoms']
        self.num_electrons          = atoms_row.data['num_electrons']
        self.num_ecp_electrons      = atoms_row.data['num_ecp_electrons']
        self.n_scf_steps            = atoms_row.data['n_scf_steps']
        self.n_basis                = atoms_row.data['n_basis']
        self.unrestricted           = atoms_row.data['unrestricted']
        self.nl_energy              = atoms_row.data['nl_energy']
        self.integrated_densities   = atoms_row.data['integrated_densities']
        self.homo_energy            = atoms_row.data['homo_energy']
        self.homo_lumo_gap          = atoms_row.data['homo_lumo_gap']
        self.s_squared              = atoms_row.data['s_squared']
        self.s_squared_dev          = atoms_row.data['s_squared_dev']
        self.warnings               = atoms_row.data['warnings']
        self.mulliken_charges       = atoms_row.data['mulliken_charges']
        self.lowdin_charges         = atoms_row.data['lowdin_charges']
        self.composition            = atoms_row.data['composition']

        # for search param from atoms_row
        self.calculator             = atoms_row.calculator
        self.calculator_parameters  = atoms_row.calculator_parameters
        self.cell                   = atoms_row.cell
        self.charge                 = atoms_row.charge
        self.constrained_forces     = atoms_row.constrained_forces
        self.constraints            = atoms_row.constraints
        self.ctime                  = atoms_row.ctime
        self.energy                 = atoms_row.energy
        self.data                   = atoms_row.data
        self.fmax                   = atoms_row.fmax
        self.forces                 = atoms_row.forces
        self.formula                = atoms_row.formula
        self.id                     = atoms_row.id
        self.key_value_pairs        = atoms_row.key_value_pairs
        self.mass                   = atoms_row.mass
        self.mtime                  = atoms_row.mtime
        self.natoms                 = atoms_row.natoms
        self.numbers                = atoms_row.numbers
        self.pbc                    = atoms_row.pbc
        self.positions              = atoms_row.positions
        self.symbols                = atoms_row.symbols
        self.unique_id              = atoms_row.unique_id
        self.user                   = atoms_row.user
        # # end for atoms_row
