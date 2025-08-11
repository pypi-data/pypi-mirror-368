import numpy as np
from typing import List
from pwdata.image import Image
from pwdata.config import Config
class PerturbedStructures:
    def __init__(self):
        self.structures = []

    def append(self, structure):
        self.structures.append(structure)

    def __getitem__(self, index):
        return self.structures[index]

    def __len__(self):
        return len(self.structures)
    
    def to(self, output_path, data_name = None, save_format = None, direct = True, sort = False, wrap = False):
        for i, structure in enumerate(self.structures):
            structure.to(output_path, data_name=data_name+"_{0}".format(i), save_format=save_format, direct=direct, sort=sort, wrap=wrap)

def perturb_structure(
    image_data:Config,
    pert_num:int,
    cell_pert_fraction:float,
    atom_pert_distance:float):
    """
    Perturb each frame in the system randomly.
    The cell will be deformed randomly, and atoms will be displaced by a random distance in random direction.

    Parameters
    ----------
    image_data : Include Image object, The system to be perturbed.
    pert_num : int Each frame in the system will make `pert_num` copies,
        and all the copies will be perturbed.
        That means the system to be returned will contain `pert_num` * frame_num of the input system.
    cell_pert_fraction : float
        A fraction determines how much (relatively) will cell deform.
        The cell of each frame is deformed by a symmetric matrix perturbed from identity.
        The perturbation to the diagonal part is subject to a uniform distribution in [-cell_pert_fraction, cell_pert_fraction),
        and the perturbation to the off-diagonal part is subject to a uniform distribution in [-0.5*cell_pert_fraction, 0.5*cell_pert_fraction).
    atom_pert_distance: float
        unit: Angstrom. A distance determines how far atoms will move.
        Atoms will move about `atom_pert_distance` in random direction.
        The distribution of the distance atoms move is determined by atom_pert_style

    Returns
    -------
    perturbed_system : A list of new Image objects. Each Image object contains the information of a perturbed configuration.
        The perturbed structs. It contains `pert_num` * frame_num of the input system frames.
    """
    image = image_data.images[0]
    # perturbed_structs = []
    perturbed_structs = PerturbedStructures()
    for _ in range(pert_num):
        tmp_system = image.copy()
        cell_perturb_matrix = get_cell_perturb_matrix(cell_pert_fraction)
        tmp_system.lattice = np.matmul(tmp_system.lattice, cell_perturb_matrix)
        tmp_system.position = np.matmul(tmp_system.arrays['position'], cell_perturb_matrix)
        for kk in range(len(tmp_system.position)):
            atom_perturb_vector = get_atom_perturb_vector(atom_pert_distance)
            tmp_system.position[kk] += atom_perturb_vector
        new_system = rot_lower_triangular(tmp_system)
        perturbed_structs.append(new_system)
    return perturbed_structs

def get_cell_perturb_matrix(cell_pert_fraction):
    if cell_pert_fraction<0:
        raise RuntimeError('cell_pert_fraction can not be negative')
    e0 = np.random.rand(6)
    e = (e0 * 2 - 1)* cell_pert_fraction
    cell_pert_matrix = np.array(
        [[1+e[0], 0.5 * e[5], 0.5 * e[4]],
        [0.5 * e[5], 1+e[1], 0.5 * e[3]],
        [0.5 * e[4], 0.5 * e[3], 1+e[2]]]
    )
    return cell_pert_matrix

def get_atom_perturb_vector(atom_pert_distance):
    random_vector = None
    if atom_pert_distance < 0:
        raise RuntimeError('atom_pert_distance can not be negative')

    e = np.random.randn(3)
    random_vector = atom_pert_distance * e / np.sqrt(3)

    return random_vector

def rot_lower_triangular(image) :
    qq, rr = np.linalg.qr(image.lattice.T)
    if np.linalg.det(qq) < 0 :
        qq = -qq
        rr = -rr
    image.lattice = np.matmul(image.lattice, qq)
    image.position = np.matmul(image.position, qq)
    rot = np.eye(3)
    if image.lattice[0][0] < 0 :
        rot[0][0] = -1
    if image.lattice[1][1] < 0 :
        rot[1][1] = -1
    if image.lattice[2][2] < 0 :
        rot[2][2] = -1
    assert(np.linalg.det(rot) == 1)
    new_system = Image(
            lattice=np.matmul(image.lattice, rot),
            atom_types_image=image.arrays['atom_types_image'],
            position=np.matmul(image.position, rot),
            cartesian=image.cartesian
        )
    return new_system



class PerturbStructure(object):
    def __init__(self, atoms:List[Image]):
        self.atoms = atoms

    def perturb(self,
        pert_num:int,
        cell_pert_fraction:float,
        atom_pert_distance:float):
        """
        Perturb each frame in the system randomly.
        The cell will be deformed randomly, and atoms will be displaced by a random distance in random direction.

        Parameters
        ----------
        pert_num : int
            Each frame in the system will make `pert_num` copies,
            and all the copies will be perturbed.
            That means the system to be returned will contain `pert_num` * frame_num of the input system.
        cell_pert_fraction : float
            A fraction determines how much (relatively) will cell deform.
            The cell of each frame is deformed by a symmetric matrix perturbed from identity.
            The perturbation to the diagonal part is subject to a uniform distribution in [-cell_pert_fraction, cell_pert_fraction),
            and the perturbation to the off-diagonal part is subject to a uniform distribution in [-0.5*cell_pert_fraction, 0.5*cell_pert_fraction).
        atom_pert_distance: float
            unit: Angstrom. A distance determines how far atoms will move.
            Atoms will move about `atom_pert_distance` in random direction.
            The distribution of the distance atoms move is determined by atom_pert_style

        Returns
        -------
        perturbed_system : list of ase Atoms
            The perturbed structs. It contains `pert_num` * frame_num of the input system frames.
        """
        perturbed_structs = []
        for _ in range(pert_num):
            tmp_system = self.atoms.copy()
            cell_perturb_matrix = self.get_cell_perturb_matrix(cell_pert_fraction)
            tmp_system.lattice = np.matmul(tmp_system.lattice, cell_perturb_matrix)
            tmp_system.position = np.matmul(tmp_system.arrays['position'], cell_perturb_matrix)
            for kk in range(len(tmp_system.position)):
                atom_perturb_vector = self.get_atom_perturb_vector(atom_pert_distance)
                tmp_system.position[kk] += atom_perturb_vector
            new_system = self.rot_lower_triangular(tmp_system)
            perturbed_structs.append(new_system)
        return perturbed_structs

    def get_cell_perturb_matrix(self, cell_pert_fraction):
        if cell_pert_fraction<0:
            raise RuntimeError('cell_pert_fraction can not be negative')
        e0 = np.random.rand(6)
        e = (e0 * 2 - 1)* cell_pert_fraction
        cell_pert_matrix = np.array(
            [[1+e[0], 0.5 * e[5], 0.5 * e[4]],
            [0.5 * e[5], 1+e[1], 0.5 * e[3]],
            [0.5 * e[4], 0.5 * e[3], 1+e[2]]]
        )
        return cell_pert_matrix

    def get_atom_perturb_vector(self, atom_pert_distance):
        random_vector = None
        if atom_pert_distance < 0:
            raise RuntimeError('atom_pert_distance can not be negative')

        e = np.random.randn(3)
        random_vector = atom_pert_distance * e / np.sqrt(3)

        return random_vector

    def rot_lower_triangular(self, atoms) :
        qq, rr = np.linalg.qr(atoms.lattice.T)
        if np.linalg.det(qq) < 0 :
            qq = -qq
            rr = -rr
        atoms.lattice = np.matmul(atoms.lattice, qq)
        atoms.position = np.matmul(atoms.position, qq)
        rot = np.eye(3)
        if atoms.lattice[0][0] < 0 :
            rot[0][0] = -1
        if atoms.lattice[1][1] < 0 :
            rot[1][1] = -1
        if atoms.lattice[2][2] < 0 :
            rot[2][2] = -1
        assert(np.linalg.det(rot) == 1)
        new_system = Image(
                lattice=np.matmul(atoms.lattice, rot),
                atom_types_image=atoms.arrays['atom_types_image'],
                position=np.matmul(atoms.position, rot),
                cartesian=atoms.cartesian
            )
        # atoms.lattice.matrix = np.matmul(atoms.lattice.matrix, rot)
        # atoms.cart_coords = np.matmul(atoms.cart_coords, rot)
        return new_system

class BatchPerturbStructure(object):
    @staticmethod
    def batch_perturb(
            raw_obj:Image,
            pert_num:int,
            cell_pert_fraction:float,
            atom_pert_distance:float):
        
        tmp_structure = raw_obj
        perturbed_obj = PerturbStructure(tmp_structure)
        perturbed_structs = perturbed_obj.perturb(
                                pert_num=pert_num, 
                                cell_pert_fraction=cell_pert_fraction,
                                atom_pert_distance=atom_pert_distance)

        return perturbed_structs