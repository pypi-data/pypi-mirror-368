import numpy as np
import os, sys, glob
from math import ceil
from typing import (List, Union, Optional)
# import time
# os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pwdata.image import Image
from pwdata.movement import MOVEMENT
from pwdata.outcar import OUTCAR
from pwdata.poscar import POSCAR
from pwdata.atomconfig import CONFIG
from pwdata.dump import DUMP
from pwdata.lammpsdata import LMP
from pwdata.cp2kdata import CP2KMD, CP2KSCF
from pwdata.deepmd import DPNPY, DPRAW
from pwdata.pwmlff import PWNPY
from pwdata.movement_saver import save_to_movement
from pwdata.extendedxyz import EXTXYZ, save_to_extxyz
from pwdata.datasets_saver import save_to_dataset, get_pw, save_to_raw, save_to_npy
from pwdata.build.write_struc import write_config, write_vasp, write_lammps
from pwdata.meta import META
from pwdata.utils.constant import FORMAT

class Save_Data(object):
    def __init__(self, data_path, datasets_path = "./PWdata", train_data_path = "train", valid_data_path = "valid", 
                 train_ratio = None, random = True, seed = 2024, format = None, retain_raw = False, atom_names:list[str] = None) -> None:
        if format.lower() == "pwmat/config":
            self.image_data = CONFIG(data_path)
        elif format.lower() == "vasp/poscar":
            self.image_data = POSCAR(data_path)
        elif format.lower() == "lammps/dump":
            self.image_data = DUMP(data_path, atom_names)
        elif format.lower() == "lammps/lmp":
            self.image_data = LMP(data_path)
        else:
            assert train_ratio is not None, "train_ratio must be set when format is not config or poscar (inference)"
            self.data_name = os.path.basename(data_path)
            self.labels_path = os.path.join(datasets_path, self.data_name)
            if os.path.exists(datasets_path) is False:
                os.makedirs(datasets_path, exist_ok=True)
            if not os.path.exists(self.labels_path):
                os.makedirs(self.labels_path, exist_ok=True)
            if len(glob.glob(os.path.join(self.labels_path, train_data_path, "*.npy"))) > 0:
                print("Data %s has been processed!" % self.data_name)
                return
            if format.lower() == "pwmat/movement":
                self.image_data = MOVEMENT(data_path)
            elif format.lower() == "vasp/outcar":
                self.image_data = OUTCAR(data_path)
            elif format.lower() == "extxyz":
                self.image_data = EXTXYZ(data_path)
            elif format.lower() == "vasp/xml":
                pass
            elif format.lower() == 'cp2k/md':
                self.image_data = CP2KMD(data_path)
            elif format.lower() == 'cp2k/scf':
                self.image_data = CP2KSCF(data_path)
            elif format.lower() == 'deepmd/npy':
                self.image_data = DPNPY(data_path)
            elif format.lower() == 'deepmd/raw':
                self.image_data = DPRAW(data_path)
            elif format.lower() == 'pwmlff/npy':
                self.image_data = PWNPY(data_path)
        self.lattice, self.position, self.energies, self.ei, self.forces, self.virials, self.atom_type, self.atom_types_image, self.image_nums = get_pw(self.image_data.get())

        if train_ratio is not None:  # inference 时不存数据
            self.train_ratio = train_ratio        
            self.split_and_save_data(seed, random, self.labels_path, train_data_path, valid_data_path, retain_raw)
    
    def split_and_save_data(self, seed, random, labels_path, train_path, val_path, retain_raw):
        if seed:
            np.random.seed(seed)
        indices = np.arange(self.image_nums)    # 0, 1, 2, ..., image_nums-1
        if random:
            np.random.shuffle(indices)              # shuffle the indices
        train_size = ceil(self.image_nums * self.train_ratio)
        train_indices = indices[:train_size]
        val_indices = indices[train_size:]
        # image_nums = [self.image_nums]
        atom_types_image = self.atom_types_image.reshape(1, -1)

        train_data = [self.lattice[train_indices], self.position[train_indices], self.energies[train_indices], 
                      self.forces[train_indices], atom_types_image, self.atom_type,
                      self.ei[train_indices]]
        val_data = [self.lattice[val_indices], self.position[val_indices], self.energies[val_indices], 
                    self.forces[val_indices], atom_types_image, self.atom_type,
                    self.ei[val_indices]]

        if len(self.virials) != 0:
            train_data.append(self.virials[train_indices])
            val_data.append(self.virials[val_indices])
        else:
            train_data.append([])
            val_data.append([])

        if self.train_ratio == 1.0 or len(val_indices) == 0:
            labels_path = os.path.join(labels_path, train_path)
            if not os.path.exists(labels_path):
                os.makedirs(labels_path)
            if retain_raw:
                save_to_raw(train_data, train_path)
            save_to_npy(train_data, labels_path)
        else:
            train_path = os.path.join(labels_path, train_path) 
            val_path = os.path.join(labels_path, val_path)
            if not os.path.exists(train_path):
                os.makedirs(train_path)
            if not os.path.exists(val_path):
                os.makedirs(val_path)
            if retain_raw:
                save_to_raw(train_data, train_path)
                save_to_raw(val_data, val_path)
            save_to_npy(train_data, train_path)
            save_to_npy(val_data, val_path)
                
                
class Config(object):
    def __init__(self, format: str = None, data_path: str = None, pbc = None, atom_names = None, index = ':', **kwargs):
        self.format = format
        self.data_path = data_path
        self.pbc = pbc
        self.atom_names = atom_names
        self.index = index
        self.kwargs = kwargs
        if data_path is not None:
            self.images = self._read()
        else:
            self.images = []

    def _read(self):
        images, format = Config.read(self.format, self.data_path, self.pbc, self.atom_names, self.index, **self.kwargs)
        self.format = format # if the input format is None
        return images
    
    def append(self, images_obj):
        if not hasattr(self, 'images'):
            self.images = []
        if not isinstance(self.images, list):
            self.images = [self.images]
        if not isinstance(images_obj.images, list):
            images_obj.images = [images_obj.images]
        self.images += images_obj.images
        
    @staticmethod
    def read(format: str = None, data_path: str = None, pbc = None, atom_names = None, index = ':', **kwargs):
        """ Read the data from the input file. 
            index: int, slice or str
            The last configuration will be returned by default.  Examples:

            * ``index=0``: first configuration
            * ``index=-2``: second to last
            * ``index=':'`` or ``index=slice(None)``: all
            * ``index='-3:'`` or ``index=slice(-3, None)``: three last
            * ``index='::2'`` or ``index=slice(0, None, 2)``: even
            * ``index='1::2'`` or ``index=slice(1, None, 2)``: odd

            kwargs: dict
            Additional keyword arguments for reading the input file.
            unit: str, optional. for lammps, the unit of the input file. Default is 'metal'.
            style: str, optional. for lammps, the style of the input file. Default is 'atomic'.
            sort_by_id: bool, optional. for lammps, whether to sort the atoms by id. Default is True.

        """
        if isinstance(index, str):
            try:
                index = string2index(index)
            except ValueError:
                pass
        if format is None:
            image, format = infer_format(data_path, pbc, atom_names, index, **kwargs)
            print("infer the input data format is {}".format(format))
        else:
            if format.lower() == "pwmat/config":
                image = CONFIG(data_path, pbc).image_list
            elif format.lower() == "vasp/poscar":
                image = POSCAR(data_path, pbc).image_list
            elif format.lower() == "lammps/dump":
                assert atom_names is not None, "atom_names must be set when format is dump"
                image = DUMP(data_path, atom_names).image_list[index]
            elif format.lower() == "lammps/lmp":
                image = LMP(data_path, atom_names, **kwargs).image_list
            elif format.lower() == "pwmat/movement":
                image = MOVEMENT(data_path).image_list[index]
            elif format.lower() == "vasp/outcar":
                image = OUTCAR(data_path).image_list[index]
            elif format.lower() == "extxyz":
                image = EXTXYZ(data_path, index).image_list[index]
            elif format.lower() == "vasp/xml":
                image = None
            elif format.lower() == 'cp2k/md':
                image = CP2KMD(data_path).image_list[index]
            elif format.lower() == 'cp2k/scf':
                image = CP2KSCF(data_path).image_list
            elif format.lower() == 'deepmd/npy':
                image = DPNPY(data_path).image_list[index]
            elif format.lower() == 'deepmd/raw':
                image = DPRAW(data_path).image_list[index]
            elif format.lower() == 'pwmlff/npy':
                image = PWNPY(data_path).image_list[index]
            elif format.lower() == 'meta':
                image = META(data_path, atom_names, **kwargs).image_list[index]
            else:
                raise Exception("Error! The format of the input file is not supported!")
        if not isinstance(image, list):
            image = [image]
        return image, format.lower()
    
    def to(self, data_path, format = None, **kwargs):
        """
        Write all images (>= 1) object to a new file.

        Note: Set sort to False for CP2K, because data from CP2K is already sorted!!!. It will result in a wrong order if sort again.

        Args:
        data_path (str): Required. The path to save the file.
        format (str): Required. The format of the file. Default is None.

        Kwargs:

        Additional keyword arguments for image or multi_image format. (e.g. 'pwmat/config', 'vasp/poscar', 'lammps/lmp', 'pwmat/movement', 'extxyz')

            * data_name (str): Save name of the configuration file.
            * sort (bool): Whether to sort the atoms by atomic number. Default is False.
            * wrap (bool): Whether to wrap the atoms into the simulation box (for pbc). Default is False.
            * direct (bool): The coordinates of the atoms are in fractional coordinates or cartesian coordinates. (0 0 0) -> (1 1 1)


        Additional keyword arguments for 'pwmlff/npy' format.

            * data_name (str): Save name of the dataset folder.
            * train_ratio (float): Required. The ratio of the training dataset. Default is None. 
            * train_data_path (str): Save path of the training dataset. Default is "train". ("./output_path/train")
            * valid_data_path (str): Save path of the validation dataset. Default is "valid". ("./output_path/valid")
            * random (bool): Whether to shuffle the raw data and then split the data into the training and validation datasets. Default is True.
            * seed (int): Random seed. Default is 2024.
            * retain_raw (bool): Whether to retain the raw data. Default is False.

        """
        assert format is not None, "output file format is not specified"
        if not os.path.exists(data_path):
            os.makedirs(data_path)

        if format in FORMAT.support_config_format:
            self.write_image(self.images[0], data_path, format, **kwargs)
        else:
            self.multi_to(self.images, data_path, format, **kwargs)
        
    def multi_to(self, images, data_path, format, **kwargs):
        """
        Write multiple images to new files.
        """
        if format.lower() in ['pwmat/config', 'vasp/poscar', 'lammps/lmp']:
            data_name = kwargs['data_name']
            for i, image in enumerate(images):
                kwargs['data_name'] = data_name + "_{0}".format(i)
                self.write_image(image, data_path, format, **kwargs)
        else:
            self.write_image(images, data_path, format, **kwargs)

    def write_image(self, image, data_path, format, **kwargs):
        if format.lower() == 'pwmat/config':
            write_config(image, data_path, **kwargs)
        elif format.lower() == 'vasp/poscar':
            write_vasp(image, data_path, **kwargs)
        elif format.lower() == "lammps/lmp":
            write_lammps(image, data_path, **kwargs)
        elif format.lower() == "pwmat/movement":
            save_to_movement(image, data_path, **kwargs)
        elif format.lower() == "extxyz":
            save_to_extxyz(image, data_path, **kwargs)
        elif format.lower() == "pwmlff/npy":
            save_to_dataset(image, data_path=data_path, **kwargs)
        else:
            raise RuntimeError('Unknown file format')

def string2index(string: str) -> Union[int, slice, str]:
    """Convert index string to either int or slice"""
    string = string.replace(" ", "")
    if ':' not in string:
        # may contain database accessor
        try:
            return int(string)
        except ValueError:
            return string
    i: List[Optional[int]] = []
    for s in string.split(':'):
        if s == '':
            i.append(None)
        else:
            i.append(int(s))
    i += (3 - len(i)) * [None]
    return slice(*i)

def infer_format(data_path: str, pbc = None, atom_names = None, index = ':', **kwargs):  
    try:
        image = MOVEMENT(data_path).image_list[index]
        return image, FORMAT.pwmat_movement
    except Exception as e:
        pass
    try:
        image = OUTCAR(data_path).image_list[index]
        return image, FORMAT.vasp_outcar
    except Exception as e:
        pass    
    try:
        image = EXTXYZ(data_path, index).image_list[index]
        return image, FORMAT.extxyz
    except Exception as e:
        pass
    try:
        image = CP2KMD(data_path).image_list[index]
        return image, FORMAT.cp2k_md
    except Exception as e:
        pass
    try:
        image = DPNPY(data_path).image_list[index]
        return image, FORMAT.deepmd_npy
    except Exception as e:
        pass    
    try:
        image = DPRAW(data_path).image_list[index]
        return image, FORMAT.deepmd_raw
    except Exception as e:
        pass    
    try:
        image = PWNPY(data_path).image_list[index]
        return image, FORMAT.pwmlff_npy
    except Exception as e:
        pass    
    try:
        image = META(data_path, atom_names, **kwargs).image_list[index]
        if len(image) == 0:
            pass
        else:
            return image, FORMAT.meta
    except Exception as e:
        pass
    try:
        image = DUMP(data_path, atom_names).image_list[index]
        return image, FORMAT.lammps_dump
    except Exception as e:
        pass
    try:
        image = CONFIG(data_path, pbc).image_list #
        return image, FORMAT.pwmat_config
    except Exception as e:
        pass  
    try:
        image = POSCAR(data_path, pbc).image_list
        return image, FORMAT.vasp_poscar
    except Exception as e:
        pass
    try:
        image = CP2KSCF(data_path).image_list
        return image, FORMAT.cp2k_scf
    except Exception as e:
        pass
    try:
        image = LMP(data_path, atom_names, **kwargs).image_list
        return image, FORMAT.lammps_lmp
    except Exception as e:
        pass
    error_info = "ERROR! Speculation on input data format failed, please explicitly specify the input format. For lammps/dump files, please also specify the element type."
    raise Exception(error_info)
