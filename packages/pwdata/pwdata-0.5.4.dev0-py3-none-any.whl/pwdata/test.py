import os
from main import main
import json
from pwdata.utils.constant import FORMAT
from pwdata.convert_files import search_images

# scale_cell super_cell pertub convert_config convert_images
def test_convert_config():
    res_list = []
    configs = json.load(open("./config.json"))["convert_image"]
    save_dir = "./test_workdir"
    for config in configs:
        config_file = config["input_file"]
        config_format= config["input_format"]
        if "atom_types" in config.keys():
            atom_types = config["atom_types"]
        else:
            atom_types = None
        for format in ["pwmat/config","vasp/poscar","lammps/lmp"]:
            cmd_list = ["", "cvt_config", "-i", config_file, "-f", config_format, "-s", os.path.join(save_dir, "{}_{}".format("cvtcnf", FORMAT.get_filename_by_format(format))), "-o", format, "-c"]
            if atom_types is not None:
                cmd_list.append("-t")
                cmd_list.extend(atom_types)
            main(cmd_list)
            res_list.append(cmd_list)
    return res_list

def test_scale_cell():
    res_list = []
    configs = json.load(open("./config.json"))["convert_image"]
    save_dir = "./test_workdir"
    for idi, config in enumerate(configs):
        config_file = config["input_file"]
        config_format= config["input_format"]
        if "atom_types" in config.keys():
            atom_types = config["atom_types"]
        else:
            atom_types = None
        for idj, format in enumerate(["pwmat/config","vasp/poscar","lammps/lmp"]):
            save_path =  os.path.join(save_dir, "scale_{}_{}_{}".format(idi, idj, FORMAT.get_filename_by_format(format)))
            cmd_list = ["", "scale_cell", "-r", "1.2", "1.1", "1.0", "0.99", "0.98",  "-i", config_file, "-s", save_path, "-o", format, "-c"]#"-f", config_format, 
            if atom_types is not None:
                cmd_list.append("-t")
                cmd_list.extend(atom_types)
            main(cmd_list)
            res_list.append(cmd_list)
    return res_list

def test_super_cell():
    res_list = []
    configs = json.load(open("./config.json"))["convert_image"]
    save_dir = "./test_workdir"
    for idi, config in enumerate(configs):
        config_file = config["input_file"]
        config_format= config["input_format"]
        if "atom_types" in config.keys():
            atom_types = config["atom_types"]
        else:
            atom_types = None
        for idj, format in enumerate(["pwmat/config","vasp/poscar","lammps/lmp"]):
            save_path =  os.path.join(save_dir, "super_{}_{}_{}".format(idi, idj, FORMAT.get_filename_by_format(format)))
            cmd_list = ["", "super_cell", "-m", "2", "3", "4",  "-i", config_file, "-s", save_path, "-o", format, "-c"]# "-f", config_format, 
            if atom_types is not None:
                cmd_list.append("-t")
                cmd_list.extend(atom_types)
            main(cmd_list)
            res_list.append(cmd_list)
    return res_list

def test_pertub():
    res_list = []
    configs = json.load(open("./config.json"))["convert_image"]
    save_dir = "./test_workdir"
    for idi, config in enumerate(configs):
        config_file = config["input_file"]
        config_format= config["input_format"]
        if "atom_types" in config.keys():
            atom_types = config["atom_types"]
        else:
            atom_types = None
        for idj, format in enumerate(["pwmat/config","vasp/poscar","lammps/lmp"]):
            save_path =  os.path.join(save_dir, "perturb_{}_{}_{}".format(idi, idj, FORMAT.get_filename_by_format(format).split('.')[0]))
            cmd_list = ["", "perturb", "-e", "0.01", "-d", "0.04", "-n", "20", "-i", config_file, "-s", save_path, "-o", format, "-c"]#"-f", config_format, 
            if atom_types is not None:
                cmd_list.append("-t")
                cmd_list.extend(atom_types)
            main(cmd_list)
            res_list.append(cmd_list)
    return res_list

def test_convert_configs():
    res_list = []
    configs = json.load(open("./config.json"))["convert_configs"]
    save_dir = "./test_workdir"
    for idi, config in enumerate(configs):
        config_file = config["input_file"]
        if isinstance(config_file, str):
            config_file = [config_file]
        
        for _ in config_file:
            if not os.path.exists(_):
                print("{} not exists".format(_))
        config_format= config["input_format"]
        if "atom_types" in config.keys():
            atom_types = config["atom_types"]
        else:
            atom_types = None

        # res = search_images(config_file, config_format)
        # print(res)
        # if config_format == FORMAT.meta:
        #     print()
        for idj, format in enumerate([FORMAT.pwmlff_npy, FORMAT.extxyz]):
            save_path =  os.path.join(save_dir, "{}_{}_{}_{}".format(idi, idj, config_format.replace('/','_'), FORMAT.get_filename_by_format(format).split('.')[0]))
            cmd_list = ["", "convert_configs"]
            cmd_list.append("-i")
            cmd_list.extend(config_file)
            cmd_list.extend([  "-s", save_path, "-o", format, "-r", "-g", "1", "-m", '1'])#"-f", config_format,
            if atom_types is not None:
                cmd_list.append("-t")
                cmd_list.extend(atom_types)
            main(cmd_list)
            res_list.append(cmd_list)
    return res_list


def test_count_configs():
    res_list = []
    configs = json.load(open("./config.json"))["convert_configs"]
    for idi, config in enumerate(configs):
        config_file = config["input_file"]
        if isinstance(config_file, str):
            config_file = [config_file]
        
        for _ in config_file:
            if not os.path.exists(_):
                print("{} not exists".format(_))
        if "atom_types" in config.keys():
            atom_types = config["atom_types"]
        else:
            atom_types = None
        for idj, format in enumerate([FORMAT.pwmlff_npy, FORMAT.extxyz]):
            cmd_list = ["", "count"]
            cmd_list.append("-i")
            cmd_list.extend(config_file)
            if atom_types is not None:
                cmd_list.append("-t")
                cmd_list.extend(atom_types)
            main(cmd_list)
            res_list.append(cmd_list)
    return res_list

def test_meata_data():
    res_list = []
    # res = search_images(config_file, config_format)
    # print(res)
    atom_types = ["Pt", "Ge"]
    save_dir = "./test_workdir"
    for idj, format in enumerate([FORMAT.extxyz]):
        save_path =  os.path.join(save_dir, "test_{}_meta_{}".format(idj, FORMAT.get_filename_by_format(format).split('.')[0]))
        cmd_list = ["", "convert_configs"]
        cmd_list.append("-i")
        cmd_list.append("./meta_data.json")
        cmd_list.extend([ "-s", save_path, "-o", format, "-p", "0.8", "-r"])#, "-c", "10" , "-q", "HfGeH" "-f", "meta", 
        if atom_types is not None:
            cmd_list.append("-t")
            cmd_list.extend(atom_types)
        main(cmd_list)
        res_list.append(cmd_list)
    for res in res_list:
        print(" ".join(res))

if __name__ == "__main__":
    # run_cmd(["", "-h"])
    # run_cmd(["", "cvt_config", "-h"])
    # run_cmd(["", "scale_cell", "-h"])
    # run_cmd(["", "super_cell", "-h"])
    # run_cmd(["", "perturb", "-h"])
    # run_cmd(["", "cvt_configs", "-h"])
    os.chdir(os.path.join(os.path.dirname(os.path.dirname(__file__)), "examples"))
    cmd_list = []
    cmd_list.extend(test_scale_cell())
    cmd_list.extend(test_super_cell())
    cmd_list.extend(test_pertub())
    cmd_list.extend(test_convert_config())
    cmd_list.extend(test_convert_configs())
    cmd_list.extend(test_count_configs())

    for cmd in cmd_list:
        print(" ".join(cmd))
    
    # test_meata_data()
