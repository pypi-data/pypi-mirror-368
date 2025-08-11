'''
Author: error: error: git config user.name & please set dead value or install git && error: git config user.email & please set dead value or install git & please set dead value or install git
Date: 2025-03-16 11:22:36
LastEditors: error: error: git config user.name & please set dead value or install git && error: git config user.email & please set dead value or install git & please set dead value or install git
LastEditTime: 2025-03-16 11:26:59
FilePath: /pwdata_dev/pwdata/test/matrcan2lmdb.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
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
    mat_file = "/data/home/wuxingxing/datas/PWMLFF_library_data/matpes-rscan/MatPES-R2SCAN-2025.1.json"
    save_file = "/data/home/wuxingxing/datas/PWMLFF_library_data/matpes-rscan/MatPES-R2SCAN-2025.1.aselmdb"
    matjson = json.load(open(mat_file))
    db = LMDBDatabase(filename=save_file, readonly=False)
    for i, val in tqdm(enumerate(matjson), total=len(matjson), desc="mat.json to aselmdb"):
        _atomrow, data = cvt_matdict_2_atomrow(val)
        data["idx"] = "{} MatPES-R2SCAN-2025.1.json".format(i)
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
if __name__=="__main__":
    MPjson2lmdb()

	
