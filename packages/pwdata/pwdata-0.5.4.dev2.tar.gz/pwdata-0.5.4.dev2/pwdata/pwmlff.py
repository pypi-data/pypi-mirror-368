import numpy as np
import os, glob
from tqdm import tqdm
from pwdata.image import Image
from pwdata.utils.format_change import to_numpy_array
class PWNPY(object):
    def __init__(self, files):
        self.image_list:list[Image] = []
        self.load_files(files)

        assert len(self.image_list) > 0, "No data loaded!"

    def get(self):
        return self.image_list
    
    def load_files(self, files):
        # Search for .npy files in the current directory
        npy_files = glob.glob(os.path.join(files, "*.npy"))
        if not npy_files:
            npy_files = glob.glob(os.path.join(files, "*/*.npy"))

        atom_type, atomic_energy, Ep, force, atom_types_image, lattice, coord, virial, image_nums, atom_nums = self.load_npy(npy_files)
        lattice = lattice.reshape(-1, 3, 3)
        coord = coord.reshape(-1, atom_nums, 3)
        force = force.reshape(-1, atom_nums, 3)
        for i in tqdm(range(image_nums), desc="Loading data"):
            _virail = virial[i] if virial is not None else None
            image = Image(lattice=lattice[i], position=coord[i], force=force[i], Ep=float(Ep[i]), virial=virial[i] if virial is not None else None,
                          cartesian=False, image_nums=i, atom_nums=atom_nums,
                          atomic_energy=atomic_energy[i], atom_type=atom_type, atom_types_image=atom_types_image) 
            self.image_list.append(image)

    def load_npy(self, npy_files):
        atomic_energy = None
        Ep = None
        force = None
        lattice = None
        virial = None
        coord = None
        for npy_file in npy_files:
            npy_file_name = os.path.basename(npy_file)
            if "atom_type.npy" in npy_file_name:
                atom_type = to_numpy_array(np.load(npy_file).squeeze())
            elif "ei.npy" in npy_file_name:
                atomic_energy = np.load(npy_file) if atomic_energy is None else np.concatenate((atomic_energy, np.load(npy_file)))
            elif "energies.npy" in npy_file_name:
                Ep = np.load(npy_file) if Ep is None else np.concatenate((Ep, np.load(npy_file)))
            elif "forces.npy" in npy_file_name:
                force = np.load(npy_file) if force is None else np.concatenate((force, np.load(npy_file)))
            elif "image_type.npy" in npy_file_name:
                atom_types_image = np.load(npy_file).squeeze()
            elif "lattice.npy" in npy_file_name:
                lattice = np.load(npy_file) if lattice is None else np.concatenate((lattice, np.load(npy_file)))
            elif "virials.npy" in npy_file_name:
                virial = np.load(npy_file) if virial is None else np.concatenate((virial, np.load(npy_file)))
            elif "position.npy" in npy_file_name:
                coord = np.load(npy_file) if coord is None else np.concatenate((coord, np.load(npy_file)))

        image_nums = len(Ep)
        if isinstance(atom_types_image.tolist(), int):
            atom_nums = 1
        else:
            atom_nums = len(atom_types_image)
        virial = virial.reshape(-1, 3, 3) if virial is not None else None

        return atom_type, atomic_energy, Ep, force, atom_types_image, lattice, coord, virial, image_nums, atom_nums
