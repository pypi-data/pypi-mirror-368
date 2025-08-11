import os
import glob
from ase import Atoms
from ase.db.row import AtomsRow
from pwdata.utils.constant import get_atomic_number_from_name
from tqdm import tqdm
import numpy as np
import torch
from pwdata.fairchem.datasets.ase_datasets import LMDBDatabase

atomic_number_to_symbol = {
    1: 'H', 2: 'He', 3: 'Li', 4: 'Be', 5: 'B', 6: 'C', 7: 'N', 8: 'O', 9: 'F', 10: 'Ne',
    11: 'Na', 12: 'Mg', 13: 'Al', 14: 'Si', 15: 'P', 16: 'S', 17: 'Cl', 18: 'Ar', 19: 'K', 20: 'Ca',
    21: 'Sc', 22: 'Ti', 23: 'V', 24: 'Cr', 25: 'Mn', 26: 'Fe', 27: 'Co', 28: 'Ni', 29: 'Cu', 30: 'Zn',
    31: 'Ga', 32: 'Ge', 33: 'As', 34: 'Se', 35: 'Br', 36: 'Kr', 37: 'Rb', 38: 'Sr', 39: 'Y', 40: 'Zr',
    41: 'Nb', 42: 'Mo', 43: 'Tc', 44: 'Ru', 45: 'Rh', 46: 'Pd', 47: 'Ag', 48: 'Cd', 49: 'In', 50: 'Sn',
    51: 'Sb', 52: 'Te', 53: 'I', 54: 'Xe', 55: 'Cs', 56: 'Ba', 57: 'La', 58: 'Ce', 59: 'Pr', 60: 'Nd',
    61: 'Pm', 62: 'Sm', 63: 'Eu', 64: 'Gd', 65: 'Tb', 66: 'Dy', 67: 'Ho', 68: 'Er', 69: 'Tm', 70: 'Yb',
    71: 'Lu', 72: 'Hf', 73: 'Ta', 74: 'W', 75: 'Re', 76: 'Os', 77: 'Ir', 78: 'Pt', 79: 'Au', 80: 'Hg',
    81: 'Tl', 82: 'Pb', 83: 'Bi', 84: 'Po', 85: 'At', 86: 'Rn', 87: 'Fr', 88: 'Ra', 89: 'Ac', 90: 'Th',
    91: 'Pa', 92: 'U', 93: 'Np', 94: 'Pu', 95: 'Am', 96: 'Cm', 97: 'Bk', 98: 'Cf', 99: 'Es', 100: 'Fm',
    101: 'Md', 102: 'No', 103: 'Lr', 104: 'Rf', 105: 'Db', 106: 'Sg', 107: 'Bh', 108: 'Hs', 109: 'Mt',
    110: 'Ds', 111: 'Rg', 112: 'Cn', 113: 'Nh', 114: 'Fl', 115: 'Mc', 116: 'Lv', 117: 'Ts', 118: 'Og'
}

def cvt_matdict_2_atomrow(config:dict):
    cell = read_from_dict('matrix', config['structure']['lattice'], require=True)
    atom_type_list = get_atomic_number_from_name([_['label'] for _ in config['structure']['sites']])
    position = [_['xyz'] for _ in config['structure']['sites']]
    magmom = [_['properties']['magmom'] for _ in config['structure']['sites']]
    # magmom = read_from_dict('magmom', config, require=True)
    atom = Atoms(positions=position,
                numbers=atom_type_list,
                magmoms=magmom,
                cell=cell)

    atom_rows = AtomsRow(atom)
    atom_rows.pbc = np.ones(3, bool)
    # read stress -> xx, yy, zz, yz, xz, xy
    virial = read_from_dict('stress', config, require=True) # this is vrial and the order is xx, yy, zz, yz, xz, xy
    stress = -np.array(virial) / config['volume']
    atom_rows.stress = [stress[0],stress[1],stress[2],stress[3],stress[4],stress[5]]
    force = read_from_dict('forces', config, require=True) #mat is s
    energy = read_from_dict('energy', config, require=True)
    atom_rows.__setattr__('force',  force)
    atom_rows.__setattr__('forces',  force)
    atom_rows.__setattr__('energy', energy)
    data = {}
    return atom_rows, data

def read_from_dict(key:str, config:dict, default=None, require=False):
    if key in config:
        return config[key]
    else:
        if require:
            raise ValueError("key {} not found in config".format(key))
        else:
            return default

def atom_type_to_symbol(atom_type):
    return atomic_number_to_symbol.get(int(atom_type), 'X')  # Default to 'X' for unknown types

def atom_types_to_symbol(atom_types):
    return [atom_type_to_symbol(atom) for atom in atom_types]

# xyz_file = "/data/home/wuxingxing/codespace/EDM/outputs/edm_qm9/eval/stabel_pwmat/0/molecule_stable_000.xyz"
# atoms = read(xyz_file)
# atoms.center(vacuum=8)
# # 获取原子符号列表，并排序
# symbols = atoms.get_chemical_symbols()
# sorted_indices = sorted(range(len(symbols)), key=lambda i: symbols[i])

# # 按排序后的索引重新排列原子
# atoms_sorted = atoms[sorted_indices]

# save_file = "/data/home/wuxingxing/codespace/EDM/outputs/edm_qm9/bk_eval/stabel_pwmat/0/sort.0.POSCAR"
# write(filename=save_file, images=atoms_sorted, format="vasp")

def read2atoms(pt_file, db, prefix):
    atom_row_list = []
    val = torch.load(pt_file, map_location="cpu")
    # Get the necessary tensors
    cumsum_atom = val['cumsum_atom'].numpy()  # Convert to numpy for easier handling
    positions = val['pos'].numpy()            # Shape: [410945, 3]
    atom_types = val['atom_types'].numpy()    # Shape: [410945]
    forces     = val['forces'].numpy()
    charges    = val['charge'].numpy()
    for id, i in tqdm(enumerate(range(len(cumsum_atom) - 1)), total=len(cumsum_atom) - 1, desc="bamboo ptfile to aselmdb"):
        start_idx = cumsum_atom[i]
        end_idx = cumsum_atom[i + 1]
        energy = val['energy'][id].item()
        # Get positions and atom types for the current structure
        struct_pos = positions[start_idx:end_idx]
        struct_types = atom_types[start_idx:end_idx]
        force        = forces[start_idx:end_idx]
        charge      = charges[start_idx:end_idx]
        symbol = atom_types_to_symbol(struct_types)
        atom = Atoms(symbols=symbol, 
                    positions=struct_pos,
                    charges=charge,
                    pbc=False)
        atom.center(vacuum=5)
        atom_rows = AtomsRow(atom)
        atom_rows.__setattr__('force',  force)
        atom_rows.__setattr__('forces',  force)
        atom_rows.__setattr__('energy', energy)
        data = {}
        data['total_charge'] = val['total_charge'][id].item()
        data['dipole'] = list(val['dipole'][id].numpy())
        data['quadrupole'] = list(val['quadrupole'][id].numpy())
        data["idx"] = f"{id}-{prefix}"
        db._write(atom_rows, key_value_pairs={}, data=data)
        atom_row_list.append(atom_rows)
    db.close()

def cvtbamboo(pt_dir, save_dir, prefix):
    pt_list = glob.glob(os.path.join(pt_dir, "*.pt"))
    for pt in pt_list:
        save_path = os.path.join(save_dir, os.path.basename(pt).replace('.pt', '.aselmdb'))
        db = LMDBDatabase(filename=save_path, readonly=False)
        atom_row_list = read2atoms(pt, db, prefix)


if __name__=="__main__":
    pt_dir="/share/public/PWMLFF_test_data/bamboo/mini"
    save_dir="/share/public/PWMLFF_test_data/bamboo/mini_aselmdb"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    prefix = "bamboo-mini"
    cvtbamboo(pt_dir, save_dir, prefix)
