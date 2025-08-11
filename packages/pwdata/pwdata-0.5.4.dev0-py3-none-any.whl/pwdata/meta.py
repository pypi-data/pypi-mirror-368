import numpy as np
import os, glob
from tqdm import tqdm
from pwdata.image import Image
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
from collections import Counter
from functools import partial
from pwdata.fairchem.datasets.ase_datasets import AseDBDataset
from pwdata.utils.format_change import to_numpy_array, to_integer, to_float

class META(object):
    def __init__(self, files: list[str], atom_names: list[str] = None, query: str = None, cpu_nums: int=None):
        self.image_list:list[Image] = []
        self.load_files_cpus(files, atom_names, query, cpu_nums)
        if len(self.image_list) < 1:
            print("Warining! No data loaded!")
        # self.load_files(files, atom_names, query, cpu_nums) used to debug on one cpu

    def get(self):
        return self.image_list
    
    def load_files(self, input:list[str], atom_types: list[str] = None, query: str = None, cpu_nums: int=None):
        def query_fun(row, elements:list[str]=None):
            if elements is None:
                return True
            return sorted(set(row.symbols)) == elements

        search_dict = {'src': input}
        dataset = AseDBDataset(config=search_dict)
        if atom_types is not None:
            filter_with_elements = partial(query_fun, elements=sorted(atom_types))
        for ids, dbs in enumerate(dataset.dbs):
            if query is None and atom_types is None:
                atom_list = list(dbs.select())
            elif query is None and atom_types is not None:
                atom_list = list(dbs.select("".join(atom_types), filter=filter_with_elements))
            elif query is not None and atom_types is not None:
                atom_list = list(dbs.select(query, filter=filter_with_elements))
            else:# query is not None and atom_types is None:
                atom_list = list(dbs.select(query))
            for Atoms in atom_list:
                image = to_image(Atoms)
                self.image_list.append(image)

    def load_files_cpus(self, input: list[str], atom_types: list[str] = None, query: str = None, cpu_nums: int = None):
        # 设置查询过滤器
        filter_with_elements = partial(query_fun, elements=sorted(atom_types)) if atom_types is not None else None
        if cpu_nums is None:
            cpu_nums = 1
        else:
            cpu_nums = min(cpu_nums, multiprocessing.cpu_count())
        if isinstance(input, str):
            input = [input]
        atom_lists = []
        # single cpu debug
        if cpu_nums == 1:
            for i, _ in enumerate(input):
                _atom_lists = load_and_query_db(_, atom_types, query, filter_with_elements)
                # for _ in _atom_lists:
                #     print(_.formula)
                atom_lists.append(_atom_lists)
        else:
            # 使用多进程并行加载和查询数据库
            with ProcessPoolExecutor(max_workers=cpu_nums) as executor:
                futures = []
                for db_address in input:
                    futures.append(executor.submit(load_and_query_db, db_address, atom_types, query, filter_with_elements))
                
                # 收集查询结果
                atom_lists = []
                for future in as_completed(futures):
                    atom_lists.append(future.result())

        # 处理所有结果
        for atom_list in atom_lists:
            if len(atom_list) > 0:
                # for _ in atom_list:
                #     print(_.formula)
                self.image_list.extend([to_image(Atoms) for Atoms in atom_list])

    @staticmethod
    def process_atoms(self, atom_list):
        """处理每个 atom_list 并转换为对象列表"""
        return [to_image(Atoms) for Atoms in atom_list]

def load_and_query_db(db_address, atom_types, query, filter_with_elements):
    # 加载数据库
    try:
        dataset = AseDBDataset(config={'src': db_address})
    except Exception as e:
        if "No valid ase data found" in e.args[0]:
            return []
        else:
            return e
    atom_list = []
    for dbs in dataset.dbs:
        if query is None and atom_types is None:
            atom_list.extend(list(dbs.select()))
        elif query is None and atom_types is not None:
            atom_list.extend(list(dbs.select("".join(atom_types), filter=filter_with_elements)))
        elif query is not None and atom_types is not None:
            atom_list.extend(list(dbs.select(query, filter=filter_with_elements)))
        else:  # query is not None and atom_types is None
            atom_list.extend(list(dbs.select(query)))
    return atom_list

def query_fun(row, elements):
    if elements is None:
        return True
    return sorted(set(row.symbols)) == elements

def to_image(Atoms):
    image = Image()
    image.formula = Atoms.formula
    image.pbc = to_numpy_array(Atoms.pbc)
    image.atom_nums = Atoms.natoms
    type_nums_dict = Counter(Atoms.numbers)
    image.atom_type = to_numpy_array(list(type_nums_dict.keys()))
    image.atom_type_num = to_numpy_array(list(type_nums_dict.values()))
    image.atom_types_image = to_numpy_array(Atoms.numbers)
    image.lattice = to_numpy_array(Atoms.cell).reshape(3, 3)
    image.position = to_numpy_array(Atoms.positions)
    image.cartesian = True
    image.force = to_numpy_array(Atoms.forces)
    image.Ep = to_float(Atoms.energy)
    # 计算 Atomic-Energy
    # atomic_energy, _, _, _ = np.linalg.lstsq([image.atom_type_num], np.array([image.Ep]), rcond=1e-3)
    # atomic_energy = np.repeat(atomic_energy, image.atom_type_num)
    # image.atomic_energy = atomic_energy.tolist()

    if hasattr(Atoms, 'virial') is False and hasattr(Atoms, 'stress'):
        vol = Atoms.volume
        virial = (-np.array(Atoms.stress) * vol)
        image.virial = np.array([
            [virial[0], virial[5], virial[4]],
            [virial[5], virial[1], virial[3]],
            [virial[4], virial[3], virial[2]]
        ])
        # print(image.virial)
    image.format = 'metadata'
    return image