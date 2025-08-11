'''
description: 
Convert MPtraj JSON file to aselmdb format
'''
import os
import json
from pwdata.fairchem.datasets.ase_datasets import LMDBDatabase
from ase import Atoms
from ase.db.row import AtomsRow
from pwdata.utils.constant import get_atomic_number_from_name
from tqdm import tqdm
import numpy as np

def MPjson2lmdb():
    mat_file = "/data/home/wuxingxing/datas/PWMLFF_library_data/mat/MatPES-PBE-2025.1.json"
    save_file = "/data/home/wuxingxing/datas/PWMLFF_library_data/mat/MatPES-PBE-2025.1.aselmdb"
    matjson = json.load(open(mat_file))
    db = LMDBDatabase(filename=save_file, readonly=False)
    for i, v in tqdm(enumerate(matjson), total=len(matjson.keys())):
        _atomrow, data = cvt_matdict_2_atomrow(v)
        data["idx"] = "{} MatPES-PBE-2025.1.json".format(i)
        db._write(_atomrow, key_value_pairs={}, data=data)
    db.close()

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
    stress = read_from_dict('stress', config, require=True)
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

if __name__=="__main__":
    MPjson2lmdb()

	
