import numpy as np
import os, glob
from tqdm import tqdm
from collections import Counter
from pwdata.image import Image
from pwdata.calculators.const import ELEMENTTABLE
from pwdata.utils.format_change import to_numpy_array, to_integer, to_float
class DPNPY(object):
    def __init__(self, dp_file):
        self.image_list:list[Image] = []
        self.load_dp_file(dp_file)

        assert len(self.image_list) > 0, "No data loaded!"

    def get(self):
        return self.image_list
    
    def load_dp_file(self, dp_file):
        type_map_raw = os.path.join(dp_file, "type_map.raw")
        type_raw = os.path.join(dp_file, "type.raw")

        # Search for .npy files in the current directory
        npy_files = glob.glob(os.path.join(dp_file, "*.npy"))
        if not npy_files:
            npy_files = glob.glob(os.path.join(dp_file, "*/*.npy"))

        with open(type_map_raw, 'r') as f:
            type_map = f.read().splitlines()
        _atom_type = [ELEMENTTABLE[atom] for atom in type_map]
        
        with open(type_raw, 'r') as f:
            type = f.read().splitlines()
        atom_nums = len(type)
        atom_types_image = np.array([_atom_type[int(atom)] for atom in type])
        sc = Counter(atom_types_image)
        atom_type = np.array(list(sc.keys()))
        atom_type_num = list(sc.values())
        # atom_type_num = [atom_types_image.count(atom) for atom in set(atom_types_image)]

        box, coord, energy, force, virial, image_nums = self.load_npy(npy_files, atom_nums)

        for i in range(image_nums):
            virial_image = virial[i] if virial is not None else None
            image = Image(lattice=box[i], position=coord[i], force=force[i], Ep=energy[i], virial=virial_image,
                          atom_type=atom_type, atom_nums=atom_nums, atom_types_image=atom_types_image, atom_type_num=None,
                          cartesian=True, image_nums=i)
            atomic_energy, _, _, _ = np.linalg.lstsq([atom_type_num], np.array([image.Ep]), rcond=1e-3)
            atomic_energy = np.repeat(atomic_energy, atom_type_num)
            image.atomic_energy = to_numpy_array(atomic_energy.tolist())
            self.image_list.append(image)
        
    def load_npy(self, npy_files, atom_nums):
        virial = None
        for npy_file in tqdm(npy_files, desc="Loading data"):
            npy_file_name = os.path.basename(npy_file)
            if "box" in npy_file_name:
                box = np.load(npy_file).reshape(-1, 3, 3).astype(np.float64)
            elif "coord" in npy_file_name:
                coord = np.load(npy_file).reshape(-1, atom_nums, 3)
            elif "energy" in npy_file_name:
                energy = np.load(npy_file)
            elif "force" in npy_file_name:
                force = np.load(npy_file).reshape(-1, atom_nums, 3)
            elif "virial" in npy_file_name:
                virial = np.load(npy_file).reshape(-1, 3, 3)

        image_nums = len(box)
        print("Load data %s successfully! \t\t\t\t Image nums: %d" % (npy_files, image_nums))
        return box, coord, energy, force, virial, image_nums
        
            
class DPRAW(object):
    def __init__(self, dp_file):
        self.image_list:list[Image] = []
        self.load_dp_file(dp_file)

        assert len(self.image_list) > 0, "No data loaded!"

    def get(self):
        return self.image_list
    
    def load_dp_file(self, dp_file):
        type_map_raw = os.path.join(dp_file, "type_map.raw")
        type_raw = os.path.join(dp_file, "type.raw")

        # Search for .raw files in the current directory
        raw_files = glob.glob(os.path.join(dp_file, "*.raw"))
        raw_files.remove(type_map_raw)
        raw_files.remove(type_raw)

        with open(type_map_raw, 'r') as f:
            type_map = f.read().splitlines()
        _atom_type = [ELEMENTTABLE[atom] for atom in type_map]
        
        with open(type_raw, 'r') as f:
            type = f.read().splitlines()
        atom_nums = len(type)
        atom_types_image = [_atom_type[int(atom)] for atom in type]
        sc = Counter(atom_types_image)
        atom_type = list(sc.keys())
        atom_type_num = list(sc.values())
        # atom_type_num = [atom_types_image.count(atom) for atom in set(atom_types_image)]

        box, coord, energy, force, virial, image_nums = self.load_raw(raw_files, atom_nums)

        for i in range(image_nums):
            virial_image = virial[i] if virial is not None else None
            image = Image(lattice=box[i], position=coord[i], force=force[i], Ep=energy[i], virial=virial_image,
                          atom_type=atom_type, atom_nums=atom_nums, atom_types_image=atom_types_image, atom_type_num=atom_type_num,
                          cartesian=True, image_nums=i)
            atomic_energy, _, _, _ = np.linalg.lstsq([atom_type_num], np.array([image.Ep]), rcond=1e-3)
            atomic_energy = np.repeat(atomic_energy, atom_type_num)
            image.atomic_energy = to_numpy_array(atomic_energy.tolist())
            self.image_list.append(image)

    def load_raw(self, raw_files, atom_nums):
        file_keys_to_load = {
            "box": (process_line, (-1, 3, 3)),
            "coord": (process_line, (-1, atom_nums, 3)),
            "force": (process_line, (-1, atom_nums, 3)),
            "energy": (process_single_line, None),
            "virial": (process_line, (-1, 3, 3))
        }

        data = {}
        for raw_file in tqdm(raw_files, desc="Loading data"):
            with open(raw_file, 'r') as f:
                lines = f.read().splitlines()
            
            for key, (func, shape) in file_keys_to_load.items():
                if key in raw_file:
                    if shape is None:
                        data[key] = func(lines)
                    else:
                        data[key] = func(lines, shape)

        image_nums = len(data['box'])
        print("Load data %s successfully! \t\t\t\t Image nums: %d" % (raw_files, image_nums))
        virial = None if 'virial' not in data.keys() else data['force']
        return data['box'], data['coord'], data['energy'], data['force'], virial, image_nums
                                          
def process_line(line, shape):
    return np.array([list(map(float, line.split())) for line in line]).reshape(*shape)

def process_single_line(line):
    return np.array([float(line) for line in line])
    