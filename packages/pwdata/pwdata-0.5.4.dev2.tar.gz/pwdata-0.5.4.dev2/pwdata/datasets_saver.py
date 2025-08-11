import numpy as np
import os
from collections import Counter
from math import ceil
from collections import defaultdict
from pwdata.calculators.const import elements
from pwdata.utils.constant import get_atomic_name_from_number, FORMAT
from pwdata.image import Image
from pwdata.utils.format_change import to_numpy_array
def save_to_dataset(image_data: list, data_path = "./", random = False, seed = None, retain_raw = False, data_name = "PWdata", write_patthen="w"):
    """ Get and process the data from the input file. """
    # sort atom order
    for image in image_data:
        image.sort_by_atomtype()
    image_dict = split_image_by_atomtype_nums(image_data)
    for key, image_datas in image_dict.items():
        save_image(image_datas, data_path = data_path, random = random, seed = seed, retain_raw = retain_raw, data_name = data_name, write_patthen=write_patthen)

def save_image(image_data: list, data_path = None, random = False, seed = None, retain_raw = False, data_name = "PWdata", write_patthen="w"):
    lattice, position, energies, ei, forces, virials, atom_type, atom_types_image, image_nums = get_pw(image_data)

    sc = Counter(atom_types_image)  # a list sc of (symbol, count) pairs
    temp_atom_name = ''.join([elements[key] + str(count) for key, count in sc.items()])
    atom_name = temp_atom_name
    suffix = 0
    while os.path.exists(os.path.join(data_path, atom_name)):
        suffix += 1
        atom_name = temp_atom_name + "_" + str(suffix)

    labels_path = os.path.join(data_path, data_name, atom_name)
    if not os.path.exists(data_path):
        os.makedirs(data_path, exist_ok=True)
    if not os.path.exists(labels_path):
        os.makedirs(labels_path, exist_ok=True)
    
    if seed is not None:
        np.random.seed(seed)
    indices = np.arange(image_nums)    # 0, 1, 2, ..., image_nums-1
    if random:
        np.random.shuffle(indices)              # shuffle the indices

    # image_nums = [image_nums]
    atom_types_image = atom_types_image.reshape(1, -1)

    train_data = [lattice[indices], position[indices], energies[indices],
                    forces[indices], atom_types_image, atom_type,
                    ei[indices]]
    
    if len(virials) != 0:
        train_data.append(virials[indices])
    else:
        train_data.append([])

    if not os.path.exists(labels_path):
        os.makedirs(labels_path)
    if retain_raw:
        save_to_raw(train_data, labels_path)
    save_to_npy(train_data, labels_path)

def save_to_raw(data, directory):
    filenames = ["lattice.dat", "position.dat", "energies.dat", "forces.dat", "image_type.dat", "atom_type.dat", "ei.dat", "virials.dat"]
    formats = ["%.8f", "%.16f", "%.8f", "%.16f", "%d", "%d", "%.8f", "%.8f"]
    # for i in tqdm(range(len(data)), desc="Saving to raw files"):
    for i in range(len(data)):
        if i != 7 or (i == 7 and len(data[7]) != 0):
            np.savetxt(os.path.join(directory, filenames[i]), data[i], fmt=formats[i])

def save_to_npy(data, directory):
    filenames = ["lattice.npy", "position.npy", "energies.npy", "forces.npy", "image_type.npy", "atom_type.npy", "ei.npy", "virials.npy"]
    # for i in tqdm(range(len(data)), desc="Saving to npy files"):
    for i in range(len(data)):
        if i != 7 or (i == 7 and len(data[7]) != 0):
            np.save(os.path.join(directory, filenames[i]), data[i])

def get_pw(image_data):
    # Initialize variables to store data
    all_lattices = []
    all_postions = []
    all_energies = []
    all_ei = []
    all_forces = []
    all_virials = []
    for image in image_data:
        if image.cartesian:
            image.position = image.get_scaled_positions(wrap=False)     # get the positions in direct coordinates, because the positions in direct coordinates are used in the MLFF model (find_neighbore)
            image.cartesian = False
        all_lattices.append(image.lattice)
        all_postions.append(image.position)
        all_energies.append(image.Ep)
        all_forces.append(image.force)
        all_ei.append(image.atomic_energy)
        if image.virial is not None and len(image.virial) != 0:
            all_virials.append(image.virial)
        else:
            all_virials.append(np.full((3, 3), -1e5))
    image_nums = len(image_data)
    atom_type = to_numpy_array(image.atom_type)
    atom_types_image = to_numpy_array(image.atom_types_image)
    all_lattices = np.array(all_lattices).reshape(image_nums, 9)
    all_postions = np.array(all_postions).reshape(image_nums, -1)
    all_energies = np.array(all_energies).reshape(image_nums, 1)
    all_forces = np.array(all_forces).reshape(image_nums, -1)
    all_ei = np.array(all_ei).reshape(image_nums, -1)
    if len(all_virials) != 0:
        all_virials = np.array(all_virials).reshape(image_nums, -1)
    return all_lattices, all_postions, all_energies, all_ei, all_forces, all_virials, atom_type, atom_types_image, image_nums

def split_image_by_atomtype_nums(image_data:list[Image]):
    key_dict = {}
    for idx, image in enumerate(image_data):
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
        for atom, num in zip(atom_list, type_nums):
            new_key.append(atom)
            new_key.append(num)
        new_key = "".join(new_key)
        new_split[new_key] = key_dict[key]
    return new_split