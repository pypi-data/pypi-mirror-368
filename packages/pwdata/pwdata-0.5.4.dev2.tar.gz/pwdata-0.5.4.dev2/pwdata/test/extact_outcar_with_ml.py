import os
import sys
import argparse
import numpy as np
import re
from tqdm import tqdm
from collections import Counter
from pwdata import Config
from pwdata.image import Image, elements_to_order
from pwdata.utils.format_change import to_numpy_array, to_integer, to_float

class OUTCAR(object):
    def __init__(self, outcar_file) -> None:
        self.image_list:list[Image] = []
        self.number_pattern = re.compile(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
        self.load_outcar_file(outcar_file)

    def get(self):
        return self.image_list

    def load_outcar_file(self, outcar_file):
        # seperate content to image contents
        with open(outcar_file, 'r') as rf:
            outcar_contents = rf.readlines()

        atom_names = []
        atom_type_num = None
        nelm = None
        for idx, ii in enumerate(outcar_contents):
            if "POTCAR" in ii:
                # get atom names from POTCAR info, tested only for PAW_PBE ...
                _ii = ii.split()[2]
                if '_' in _ii:
                    # atom_names.append(_ii.split('_')[0])
                    atom_name = _ii.split('_')[0]
                    if atom_name not in atom_names:
                        atom_names.append(atom_name)
                else:
                    atom_name = _ii
                    if atom_name not in atom_names:
                        atom_names.append(atom_name)
            elif 'ions per type' in ii:
                atom_type_num_ = [int(s) for s in ii.split()[4:]]
                if atom_type_num is None:
                    atom_type_num = atom_type_num_
                else:
                    assert (atom_type_num == atom_type_num_), "inconsistent number of atoms in OUTCAR"
            elif 'NELM   =' in ii:
                nelm = int(ii.split()[2][:-1])
                break
        assert (nelm is not None), "cannot find maximum steps for each SC iteration"
        assert (atom_type_num is not None), "cannot find ion type info in OUTCAR"
        atom_names = atom_names[:len(atom_type_num)]
        atom_types_image = []
        for idx, ii in enumerate(atom_type_num) :
            for _ in range(ii) :
                atom_types_image.append(idx+1)
        atom_nums = sum(atom_type_num)
        atom_types_image = elements_to_order(atom_names, atom_types_image, atom_nums)

        max_scf_idx = 0
        prev_idx = 0
        converged_images = []
        max_insw = -1
        for idx, ii in tqdm(enumerate(outcar_contents), total=len(outcar_contents), desc="Processing data"):
            if "Ionic step" in ii:
                if prev_idx == 0:
                    prev_idx = idx
                else:
                    if max_insw < nelm:
                        converged_images.append(outcar_contents[max_scf_idx:idx])
                max_insw = 0
            if "Iteration" in ii:
                scf_index = int(ii.split()[3][:-1])
                if scf_index == 1 and prev_idx != 0:
                    if max_insw < nelm:
                        converged_images.append(outcar_contents[max_scf_idx:idx])
                    max_insw = 0
                if scf_index > max_insw:
                    max_insw = scf_index
                    max_scf_idx = idx
                prev_idx = idx
            if "Elapsed time (sec):" in ii:
                if max_insw < nelm:
                    converged_images.append(outcar_contents[max_scf_idx:idx])

        for converged_image in tqdm(converged_images, total=len(converged_images), desc="Loading converged data"):
            is_ionic = False
            for idx, line in enumerate(converged_image):
                if "Iteration" in line or "Ionic step" in line:

                    image = Image()
                    if "Iteration" in line:
                        image.scf = int(line.split()[3][:-1])
                    elif "Ionic step" in line:
                        is_ionic = True
                        image.scf = int(line.split()[3])
                elif "in kB" in line:
                    virial_info = self.parse_virial_info(converged_image[idx - 1])
                    image.virial = to_numpy_array(virial_info["virial"]).reshape(3, 3)
                elif "VOLUME and BASIS" in line:
                    lattice_info = self.parse_lattice(converged_image[idx+5:idx+8])
                    image.lattice = to_numpy_array(lattice_info["lattice"])
                elif is_ionic and "volume of cell" in line:
                    lattice_info = self.parse_lattice(converged_image[idx+2:idx+5])
                    image.lattice = to_numpy_array(lattice_info["lattice"])                    
                elif "TOTAL-FORCE" in line:
                    force_info = self.parse_force(converged_image[idx+2:idx+2+atom_nums])
                    image.force = to_numpy_array(force_info["force"])
                    image.position = to_numpy_array(force_info["position"]) 
                    image.cartesian = True            
                elif "free  energy   TOTEN" in line or "free  energy ML TOTEN" in line:
                    energy_info = self.parse_energy_info(line)
                    image.Ep = to_float(energy_info["Etot"])
            if image.Ep is None or abs(image.Ep) < 1e-8:
                continue
            image.atom_nums = atom_nums
            image.atom_types_image = to_numpy_array(atom_types_image)
            image.atom_type = to_numpy_array(list(Counter(atom_types_image).keys()))
            image.atom_type_num = to_numpy_array(atom_type_num)
            # If Atomic-Energy is not in the file, calculate it from the Ep
            if image is not None and image.atomic_energy is None and image.atom_type_num is not None:
                atomic_energy, _, _, _ = np.linalg.lstsq([image.atom_type_num], np.array([image.Ep]), rcond=1e-3)
                atomic_energy = np.repeat(atomic_energy, image.atom_type_num)
                image.atomic_energy = to_numpy_array(atomic_energy.tolist())
            self.image_list.append(image)
            
        # atom_type_num = list(counter.values())
        image.image_nums = len(self.image_list)
        print("Load data %s successfully! \t\t\t\t Image nums: %d" % (outcar_file, image.image_nums))
        
    def parse_virial_info(self, virial_content):
        numbers = self.number_pattern.findall(virial_content)
        tmp_virial = [float(_) for _ in numbers]
        virial = np.zeros(9)
        virial[0] = tmp_virial[0]     # xx
        virial[4] = tmp_virial[1]     # yy
        virial[8] = tmp_virial[2]     # zz
        virial[1] = tmp_virial[3]     # xy
        virial[3] = tmp_virial[3]     # yx
        virial[5] = tmp_virial[4]     # yz
        virial[7] = tmp_virial[4]     # zy
        virial[2] = tmp_virial[5]     # xz
        virial[6] = tmp_virial[5]     # zx
        return {"virial": virial}
    
    def parse_lattice(self, lattice_content):
        lattice1 = [float(_) for _ in self.number_pattern.findall(lattice_content[0])]
        lattice2 = [float(_) for _ in self.number_pattern.findall(lattice_content[1])]
        lattice3 = [float(_) for _ in self.number_pattern.findall(lattice_content[2])]
        lattice = [lattice1[:3], lattice2[:3], lattice3[:3]]
        return {"lattice": lattice}
    
    def parse_force(self, force_content):
        force = []
        position = []
        for i in range(0, len(force_content)):
            numbers = self.number_pattern.findall(force_content[i])
            position.append([float(_) for _ in numbers[:3]])
            force.append([float(_) for _ in numbers[3:6]])
        return {"position": position, "force": force}
    
    def parse_energy_info(self, energy_content):
        numbers = self.number_pattern.findall(energy_content)
        Etot = float(numbers[0])
        return {"Etot": Etot}

def extract_outcar_with_ml(data_path, savepath, savename, output_format, gap):
    image_data = Config()
    for outcar_file in data_path:
        tmp_image_data = OUTCAR(outcar_file).image_list
        image_data.images.extend(tmp_image_data[::gap])
    image_data.to(data_path=savepath, data_name=savename, format=output_format)
    return image_data

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Extract OUTCAR traj containing ml data.\n')

    parser.add_argument('-i', '--input',         type=str, required=True, nargs='+', help="The path of outcar files")
    parser.add_argument('-s', '--savename',      type=str, required=False, help="Output file name, if it is in the format of 'extxyz', the output file is 'savename.xyz', if it is 'pwmlff/npy', the output is in the directory 'savename'", default="outcar2xyz.xyz")
    parser.add_argument('-o', '--output_format', type=str, required=False, default='extxyz', help="the output file format, only support the format ['pwmlff/npy','extxyz'], if not provided, the 'extxyz' format be used. ")
    parser.add_argument('-g', '--gap', help='Set the number of steps to take a frame trajectory, default is 1', type=int, default=1)
    
    args = parser.parse_args(sys.argv[1:])

    file_lists = args.input
    savename = args.savename
    output_format = args.output_format
    gap = args.gap

    # os.chdir("/data/home/wuxingxing/datas/debugs/czy")
    # file_lists = ["/data/home/wuxingxing/datas/debugs/czy/tmp.OUTCAR", "/data/home/wuxingxing/datas/debugs/czy/Si_OUTCAR"]
    # savename = "outcar2xyz.xyz"
    # output_format = "extxyz"
    # gap = 1

    if format == "extxyz" and '.xyz' not in savename:
        savename = savename + ".xyz"
    if isinstance(file_lists, str):
        file_lists = [file_lists]
    if output_format not in ['pwmlff/npy', 'extxyz']:
        raise ValueError("The output format must be in ['pwmlff/npy', 'extxyz']")
    savepath = os.getcwd()
    extract_outcar_with_ml(file_lists, savepath, savename, output_format, gap)
    print("Done!")
