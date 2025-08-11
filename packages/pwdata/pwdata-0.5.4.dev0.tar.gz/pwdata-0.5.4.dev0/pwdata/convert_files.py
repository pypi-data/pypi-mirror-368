import os
import sys
import glob
import numpy as np
from pwdata.config import Config
from pwdata.build.supercells import make_supercell
from pwdata.pertub.perturbation import perturb_structure
from pwdata.pertub.scale import scale_cell
from pwdata.utils.constant import FORMAT, ELEMENTTABLE, get_atomic_name_from_number
from pwdata.image import Image
from collections import Counter
from ase.db.row import AtomsRow
from pwdata.fairchem.datasets.ase_datasets import AseDBDataset
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
from tqdm import tqdm
def do_convert_config(input_file:str, 
                    input_format:str = None, 
                    atom_types:list[str] = None,
                    savename:str = None, 
                    output_format:str = None, 
                    direct:bool = True): # True: save as fractional coordinates, False for cartesian coordinates
    image = Config(data_path=input_file, format=input_format, atom_names=atom_types)
    if output_format is None:
        output_format = FORMAT.pwmat_config if image.format == FORMAT.cp2k_scf else image.format
    if savename is None:
        savename = FORMAT.get_filename_by_format(output_format)

    image.to(data_path = os.path.dirname(os.path.abspath(savename)),
          data_name = os.path.basename(savename),
          format = output_format,
          direct = direct,
          sort = True)
    return os.path.abspath(savename)

def do_scale_cell(input_file:str, 
                    input_format:str = None,
                    atom_types:list[str] = None,
                    savename:str = None, 
                    output_format:str = None, 
                    scale_factor:list[float] = None,
                    direct:bool = True): # True: save as fractional coordinates, False for cartesian coordinates
    # for pwamt/movement movement or MLMD.OUT files
    if not isinstance(scale_factor, list):
        scale_factor = [scale_factor]
    image = Config(data_path=input_file, format=input_format, atom_names=atom_types)
    if output_format is None:
        output_format = FORMAT.pwmat_config if image.format == FORMAT.cp2k_scf else image.format
    if savename is None:
        savename = FORMAT.get_filename_by_format(image.format)
    for idx, factor in enumerate(scale_factor):
        scaled_structs = scale_cell(image, factor)
        scaled_structs.to(data_path = os.path.dirname(os.path.abspath(savename)),
            data_name = "{}_{}".format(factor, os.path.basename(savename)),
            format = output_format,
            direct = direct,
            sort = True)
    return os.path.abspath(savename)

def do_super_cell(input_file:str, 
                    input_format:str = None, 
                    atom_types:list[str] = None,
                    savename:str = None, 
                    output_format:str = None, 
                    supercell_matrix:list[int] = None,
                    direct:bool = True,
                    pbc:list =[1, 1, 1],
                    wrap=True, 
                    tol=1e-5
                    ): # True: save as fractional coordinates, False for cartesian coordinates
    # for pwamt/movement movement or MLMD.OUT files
    image = Config(data_path=input_file, format=input_format, atom_names=atom_types)
    scaled_structs = make_supercell(image, supercell_matrix, pbc=pbc, wrap=wrap, tol=tol)
    if output_format is None:
        output_format = FORMAT.pwmat_config if image.format == FORMAT.cp2k_scf else image.format
    if savename is None:
        savename = FORMAT.get_filename_by_format(image.format)
    scaled_structs.to(data_path = os.path.dirname(os.path.abspath(savename)),
          data_name = os.path.basename(savename),
          format = output_format,
          direct = direct,
          sort = True)
    return os.path.abspath(savename)

def do_perturb(input_file:str, 
                    input_format:str = None, 
                    atom_types:list[str] = None,
                    save_path:str = None, 
                    save_name_prefix:str = None,
                    output_format:str = None, 
                    cell_pert_fraction:float = None,
                    atom_pert_distance:float = None,
                    pert_num:int = None,
                    direct:bool = True
                    ): # True: save as fractional coordinates, False for cartesian coordinates
    # for pwamt/movement movement or MLMD.OUT files
    image = Config(data_path=input_file, format=input_format, atom_names=atom_types)
    save_path = os.path.abspath(save_path)
    perturbed_structs = perturb_structure(
            image_data = image,
            pert_num = pert_num,
            cell_pert_fraction = cell_pert_fraction,
            atom_pert_distance = atom_pert_distance)

    perturb_files = []
    if output_format is None:
        output_format = FORMAT.pwmat_config if image.format == FORMAT.cp2k_scf else image.format
    for tmp_perturbed_idx, tmp_pertubed_struct in enumerate(perturbed_structs):
        tmp_pertubed_struct.to(data_path = save_path,
                                data_name = "{}_{}".format(tmp_perturbed_idx, save_name_prefix),
                                format = output_format,
                                direct = direct,
                                sort = True)
        perturb_files.append("{}_{}".format(tmp_perturbed_idx, save_name_prefix))
    return perturb_files, perturbed_structs

def do_convert_images(
    input:list[str],
    input_format:str = None, 
    savepath = None, #'the/path/pwmlff-datas'
    output_format = None, 
    data_shuffle = None, 
    gap = None,
    atom_types:list[str]=None,
    query:str=None,
    cpu_nums:int=None,
    merge:bool=True
):
    data_files = search_images(input, input_format)
    image_data = load_files(data_files, input_format, atom_types=atom_types, query=query, cpu_nums=cpu_nums)
    save_images(savepath, image_data, output_format, data_shuffle, merge)

def do_count_images(
    input:list[str],
    input_format:str = None, 
    atom_types:list[str]=None,
    query:str=None,
    cpu_nums:int=None
):
    data_files = search_images(input, input_format)
    image_data = load_files(data_files, input_format, atom_types=atom_types, query=query, cpu_nums=cpu_nums)
    print("\n\n******The number of configs is {}******\n\n".format(len(image_data.images)))
    return len(image_data.images)

'''
description: 
    save the image_datas to pwmlff/npy or extxyz format
    for pwmlff/npy, the images will save to subdir accordding to the atom types and atom nums of each type, such as Pb20Te30, Pb21Te30, ... 
    for extxyz, the images will save to subdir accordding to the atom types, such as PbTe, PbTeG
param {*} savepath
param {*} image_data
param {*} output_format
param {*} train_valid_ratio
param {*} data_shuffle
return {*}
author: wuxingxing
'''
def save_images(savepath, image_data, output_format, data_shuffle=False, merge=True):
    if merge is True and output_format == FORMAT.extxyz:
        save_dir = savepath
        image_data.to(
                        data_path=save_dir,
                        format=output_format,
                        random=data_shuffle,
                        seed = 2024, 
                        retain_raw = False,
                        write_patthen="a"
                        )
    elif merge is False and output_format == FORMAT.extxyz:
        save_dict = split_image_by_atomtype_nums(image_data, format=output_format)
        for key, images in save_dict.items():
            save_dir = os.path.join(savepath, key)
            image_data.images = images
            image_data.to(
                        data_path=save_dir,
                        format=output_format,
                        random=data_shuffle,
                        seed = 2024, 
                        retain_raw = False,
                        write_patthen="a"
                        )
    else: # for pwmlff/mpy
        image_data.to(
                    data_path=savepath,
                    format=output_format,
                    random=data_shuffle,
                    seed = 2024, 
                    retain_raw = False,
                    write_patthen="a"
                    )

def search_images(input_list:list[str], input_format:str = None):
    data_path = {}
    data_path[FORMAT.pwmlff_npy] = []
    data_path[FORMAT.extxyz] = []
    data_path[FORMAT.deepmd_npy] = []
    data_path[FORMAT.deepmd_raw] = []
    data_path[FORMAT.meta] = []
    data_path[FORMAT.traj] = []
    for workDir in input_list:
        workDir = os.path.abspath(workDir)
        if os.path.isfile(workDir) and '.xyz' not in os.path.basename(workDir) and '.aselmdb' not in os.path.basename(workDir):#traj files
            data_path[FORMAT.traj].append(workDir)
        else:
            if input_format is not None:
                _data_list = search_by_format(workDir, input_format)
                if len(_data_list) > 0:
                    data_path[input_format].extend(search_by_format(workDir, input_format))
            else:
                for _format in [FORMAT.pwmlff_npy, FORMAT.extxyz, FORMAT.deepmd_npy, FORMAT.deepmd_raw, FORMAT.meta]:
                    _data_list = search_by_format(workDir, _format)
                    if len(_data_list) > 0:
                        data_path[_format].extend(_data_list)

    format_count = 0
    match_format = []
    for key, value in data_path.items():
        if len(value) > 0:
            match_format.append(key)
            format_count += 1
    if format_count >= 2:
        match_str = " ".join(match_format)
        error_info = "WARNING! Multiple formats '{}' of data have been matched in the input data directory. All matched data will be loaded!".format(match_str)
        print(error_info)
    return data_path

def search_by_format(workDir, format):
    data_path = {}
    data_path[FORMAT.pwmlff_npy] = []
    data_path[FORMAT.extxyz] = []
    data_path[FORMAT.deepmd_npy] = []
    data_path[FORMAT.deepmd_raw] = []
    data_path[FORMAT.meta] = []
    if '.xyz' in os.path.basename(workDir):
        data_path[FORMAT.extxyz].append(workDir)
    elif '.aselmdb' in os.path.basename(workDir):
        data_path[FORMAT.meta].append(workDir)
    else:
        if format == FORMAT.pwmlff_npy:    
            for root, dirs, files in os.walk(workDir):
                if 'energies.npy' in files:
                    data_path[FORMAT.pwmlff_npy].append(root)
                    # if "train" in os.path.basename(root):
                    #     data_path[FORMAT.pwmlff_npy].append(os.path.dirname(root))
                    # elif "valid" in os.path.basename(root):
                    #     data_path[FORMAT.pwmlff_npy].append(os.path.dirname(root))

        if format == FORMAT.extxyz:
            for path, dirList, fileList in os.walk(workDir):
                for _ in fileList:
                    if ".xyz" in _:
                        data_path[FORMAT.extxyz].append(os.path.join(path, _))
        
        if format == FORMAT.deepmd_npy:
            for root, dirs, files in os.walk(workDir):
                if 'energy.npy' in files:
                    data_path[FORMAT.deepmd_npy].append(os.path.dirname(root))

        if format == FORMAT.deepmd_raw:
            for root, dirs, files in os.walk(workDir):
                if 'energy.raw' in files:
                    if len(glob.glob(os.path.join(root, "*/energy.npy"))) == 0: # 
                        data_path[FORMAT.deepmd_raw].append(os.path.dirname(root)) #If both npy and raw format data exist, only load npy format
        if format == FORMAT.meta:
            for root, dirs, files in os.walk(workDir):
                for file in files:
                    _, ext = os.path.splitext(file)
                    if '.aselmdb' == ext:
                        data_path[FORMAT.meta].append(os.path.join(root, file))
                        # break
        
    return data_path[format]


def load_files(input_dict:dict, input_format:str=None, atom_types:list[str]=None, query:str=None, cpu_nums=None):
    image_data = None
    if input_format is not None:
        if input_format == FORMAT.meta:
            chunk_size = 100
            lmdb_nums = len(input_dict[FORMAT.meta])
            metadatas = [input_dict[FORMAT.meta][i:i + chunk_size] for i in range(0, lmdb_nums, chunk_size)]
            for idx, metapaths in enumerate(tqdm(metadatas, total=lmdb_nums // chunk_size)):
                if image_data is None:
                    image_data = Config(input_format, metapaths, atom_names=atom_types, query=query, cpu_nums=cpu_nums)
                    if not isinstance(image_data.images, list): # for the first pwmlff/npy dir only has one picture
                        image_data.images = [image_data.images]
                else:
                    tmp_image_data = Config(input_format, metapaths, atom_names=atom_types, query=query, cpu_nums=cpu_nums)
                    image_data.images.extend(tmp_image_data.images)
                # print("There are a total of {} aselmdb, and the current progress has been loaded {} %".format(lmdb_nums, np.round(idx*chunk_size/lmdb_nums, 2)))
        else:
            if len(input_dict[FORMAT.traj]) > 0:# the input is traj files
                for data_path in  tqdm(input_dict[FORMAT.traj], total=len(input_dict[FORMAT.traj])):
                    if image_data is None:
                        image_data = Config(input_format, data_path, atom_names=atom_types, query=query, cpu_nums=cpu_nums)
                        if not isinstance(image_data.images, list): # for the first pwmlff/npy dir only has one picture
                            image_data.images = [image_data.images]
                    else:
                        tmp_image_data = Config(input_format, data_path, atom_names=atom_types, query=query, cpu_nums=cpu_nums)
                        image_data.images.extend(tmp_image_data.images)
            else:
                for data_path in tqdm(input_dict[input_format], total=len(input_dict[input_format])): 
                    if image_data is None:
                        image_data = Config(input_format, data_path, atom_names=atom_types, query=query, cpu_nums=cpu_nums)
                        if not isinstance(image_data.images, list): # for the first pwmlff/npy dir only has one picture
                            image_data.images = [image_data.images]
                    else:
                        tmp_image_data = Config(input_format, data_path, atom_names=atom_types, query=query, cpu_nums=cpu_nums)
                        image_data.images.extend(tmp_image_data.images)
        return image_data

    else:
        for format, data_list in input_dict.items():
            if len(data_list) == 0:
                continue
            if format == FORMAT.meta:
                chunk_size = 500
                lmdb_nums = len(input_dict[FORMAT.meta])
                metadatas = [input_dict[FORMAT.meta][i:i + chunk_size] for i in range(0, lmdb_nums, chunk_size)]
                for idx, metapaths in enumerate(tqdm(metadatas, total=lmdb_nums // chunk_size)):
                    if image_data is None:
                        image_data = Config(input_format, metapaths, atom_names=atom_types, query=query, cpu_nums=cpu_nums)
                        if not isinstance(image_data.images, list): # for the first pwmlff/npy dir only has one picture
                            image_data.images = [image_data.images]
                    else:
                        tmp_image_data = Config(input_format, metapaths, atom_names=atom_types, query=query, cpu_nums=cpu_nums)
                        image_data.images.extend(tmp_image_data.images)
                    # print("There are a total of {} aselmdb, and the current progress has been loaded {} %".format(lmdb_nums, np.round(idx*chunk_size/lmdb_nums, 2)))
            else:
                for data_path in tqdm(data_list, total=len(data_list)):
                    if image_data is None:
                        image_data = Config(None, data_path, atom_names=atom_types, query=query, cpu_nums=cpu_nums)
                        if not isinstance(image_data.images, list): # for the first pwmlff/npy dir only has one picture
                            image_data.images = [image_data.images]
                    else:
                        tmp_image_data = Config(None, data_path, atom_names=atom_types, query=query, cpu_nums=cpu_nums)
                        image_data.images.extend(tmp_image_data.images)
        return image_data

'''
description: 
this function only used for extxyz format
param {*} image_data
param {*} format
return {*}
author: wuxingxing
'''
def split_image_by_atomtype_nums(image_data, format=None):
    key_dict = {}
    for idx, image in enumerate(image_data.images):
        element_counts = Counter(image.atom_types_image)
        atom_type = list(element_counts.keys())
        counts = list(element_counts.values())
        tmp_key = ""
        for element, count in zip(atom_type, counts):
            tmp_key += "{}_{}_".format(element, count)
        if tmp_key not in key_dict:
            key_dict[tmp_key] = [image]
        else:
            key_dict[tmp_key].append(image)

    new_split = {}
    for key in key_dict.keys():
        elements = key.split('_')[:-1]
        new_array = [int(elements[i]) for i in range(0, len(elements), 2)]
        type_nums = elements[1::2]
        atom_list = get_atomic_name_from_number(new_array)
        new_key = []
        if format == FORMAT.extxyz:
            new_key = "".join(atom_list)
            if new_key not in new_split:
                new_split[new_key] = key_dict[key]
            else:
                new_split[new_key].extend(key_dict[key])
        else: # for pwmlff/npy
            for atom, num in zip(atom_list, type_nums):
                new_key.append(atom)
                new_key.append(num)
            new_key = "".join(new_key)
            new_split[new_key] = key_dict[key]
    return new_split
