def print_cmd():
    cmd_infos()

def cmd_infos():
    info = ""
    info += "In functional development, please refer to the link\n\t\thttp://doc.lonxun.com/PWMLFF/Appendix-2/\n"
    
    info += "scale_cell or scale:\n"
    info += "\tScaling the structural lattice, the command example:\n"
    info += "\tscale_cell -r 0.98 0.99 0.97 0.95 -i lisi_atom.config -f pwmat/config -s scale_atom.config -o pwmat/config\n"
    info += "\t\nYou can also use 'pwdata scale_cell -h' to obtain a more detailed parameter list\n\n"
    
    info += "super_cell or super:\n"
    info += "\tConstruct a supercell based on the input original structure and supercell matrix, the command example:\n"
    info += "\tpwdata super_cell -i input_file -f input_file_format -n output_format_name -o output_format\n"
    info += "\tYou can also use 'pwdata super_cell -h' to obtain a more detailed parameter list\n\n"
    
    info += "perturb:\n"
    info += "\tDisturb the atomic positions and unit cells of the structure, the command example:\n"
    info += "\tpwdata perturb -e 0.01 -d 0.04 -n 20 -i LiSi_POSCAR -f vasp/poscar -s perturb_lammps -o lammps/lmp -c\n\n"
    info += "\tYou can also use 'pwdata perturb -h' to obtain a more detailed parameter list\n\n"
    
    info += "convert_config or cvt_config:\n"
    info += "\tTransferring structural files between different apps(PWmat\VASP\CP2K\Lammps), the command example:\n"
    info += "\tpwdata cvt_config -i LiSi_POSCAR -f vasp/poscar -s cvtcnf_lammps.lmp -o lammps/lmp -c\n\n"
    info += "\tYou can also use 'pwdata convert_config -h' to obtain a more detailed parameter list\n\n"
    
    info += "convert_configs or cvt_configs:\n"
    info += "\tExtract various trajectory files(movement of PWmat, outcar of Vasp, lammps/dump of Lammps, cp2k-mdfile of CP2K) or data sets (deepmd/npy, deepmd/raw, extxyz, meta aselmdb) into pwmlff/npy or extxyz format, the command example:\n"
    info += "\tpwdata convert_images -i input_file1 input_file2 ... input_filen -f input_file_format -n output_format_name -o output_format\n\n"

    info += "count or count_configs:\n"
    info += "\tThis command is used to count the number of input structures, the command example:\n"
    info += "\tpwdata count -i input_file1 input_file2 ... input_filen -f input_file_format\n\n"

    info += "format suppport\n"
    info += "__________________________________________________________________________________________|\n"
    info += "| Software          | file             | multi-Image | label | format                     |\n"
    info += "| ----------------- | ---------------- | ----------- | ----- | -------------------------- |\n"
    info += "| PWmat             | MOVEMENT         | True        | True  | 'pwmat/movement'           |\n"
    info += "| PWmat             | OUT.MLMD         | False       | True  | 'pwmat/movement'           |\n"
    info += "| PWmat             | atom.config      | False       | False | 'pwmat/config'             |\n"
    info += "| VASP              | OUTCAR           | True        | True  | 'vasp/outcar'              |\n"
    info += "| VASP              | poscar           | False       | False | 'vasp/poscar'              |\n"
    info += "| LAMMPS            | lmp.init         | False       | False | 'lammps/lmp'               |\n"
    info += "| LAMMPS            | dump             | True        | False | 'lammps/dump'              |\n"
    info += "| CP2K              | stdout, xyz, pdb | True        | True  | 'cp2k/md'                  |\n"
    info += "| CP2K              | stdout           | False       | True  | 'cp2k/scf'                 |\n"
    info += "| PWMLFF            | \*.npy           | True        | True  | 'pwmlff/npy'               |\n"
    info += "| DeepMD (read)     | \*.npy, \*.raw   | True        | True  | 'deepmd/npy', 'deepmd/raw' |\n"
    info += "| \* (extended xyz) | \*.xyz           | True        | True  | 'extxyz'                   |\n"
    info += "| \* (meta aselmdb) | \*.aselmdb       | True        | True  | 'meta'                     |\n"
    info += "__________________________________________________________________________________________|\n\n"

    print(info)

def comm_info():
    print("\n" + "=" * 50) 
    print("         PWDATA Basic Information")
    print("=" * 50) 
    print("Version: 0.5.2")
    print("support pwact: >= 0.3.0")
    print("support MatPL: >= 2025.3")
    print("Contact: support@pwmat.com")
    print("Citation: https://github.com/LonxunQuantum/MatPL")
    print("Manual online: http://doc.lonxun.com/PWMLFF/")
    print("=" * 50)  
    print("\n\n")
