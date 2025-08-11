class FORMAT:
    pwmat_config="pwmat/config"
    pwmat_config_name="atom.config"
    pwmat_movement="pwmat/movement"
    pwmat_movement_name="MOVEMENT"
    vasp_poscar="vasp/poscar"
    vasp_poscar_name="POSCAR"
    vasp_outcar="vasp/outcar"
    vasp_outcar_name="OUTCAR"
    vasp_potcar="vasp/potcar"
    vasp_potcar_name="POTCAR"
    lammps_lmp="lammps/lmp"
    lammps_lmp_name="lammps.lmp"
    lammps_dump="lammps/dump"
    cp2k_md="cp2k/md"
    cp2k_scf="cp2k/scf"
    pwmlff_npy="pwmlff/npy"
    pwmlff_npy_name="PWdata"
    deepmd_npy="deepmd/npy"
    deepmd_raw="deepmd/raw"
    extxyz="extxyz"
    extxyz_name="extxyz.xyz"
    meta = "meta"
    traj = "traj"
    
    support_config_format = [pwmat_config, vasp_poscar, lammps_lmp, cp2k_scf]
    support_images_format = [pwmat_movement, vasp_outcar, lammps_dump, cp2k_md, pwmlff_npy, deepmd_npy, deepmd_raw, extxyz, meta]

    @staticmethod
    def get_filename_by_format(input_format:str):
        input_format = input_format.lower()
        if input_format == FORMAT.pwmat_config:
            return FORMAT.pwmat_config_name
        elif input_format==FORMAT.pwmat_movement:
            return FORMAT.pwmat_movement_name
        elif input_format == FORMAT.vasp_poscar:
            return FORMAT.vasp_poscar_name
        elif input_format == FORMAT.vasp_outcar:
            return FORMAT.vasp_outcar_name
        elif input_format == FORMAT.vasp_potcar:
            return FORMAT.vasp_potcar_name
        elif input_format == FORMAT.lammps_lmp:
            return FORMAT.lammps_lmp_name
        elif input_format == FORMAT.pwmlff_npy:
            return FORMAT.pwmlff_npy_name
        elif input_format == FORMAT.extxyz:
            return FORMAT.extxyz_name
        else:
            raise ValueError("Unknown format: {}".format(input_format))

    @staticmethod
    def check_format(input_format:str, support_format:list[str]=None):
        input_format = input_format.lower()
        if support_format is None:
            if input_format in [FORMAT.pwmat_config, FORMAT.pwmat_movement, FORMAT.vasp_poscar, FORMAT.vasp_outcar, FORMAT.vasp_potcar, FORMAT.lammps_lmp, FORMAT.pwmlff_npy, FORMAT.extxyz]:
                return True
            else:
                raise Exception("the input format is not supported, please check the input format {}, the supported format as:\n{}".format(input_format, [FORMAT.pwmat_config, FORMAT.pwmat_movement, FORMAT.vasp_poscar, FORMAT.vasp_outcar, FORMAT.vasp_potcar, FORMAT.lammps_lmp, FORMAT.pwmlff_npy, FORMAT.extxyz]))
        else:
            if input_format in support_format:
                return True
            else:
                raise Exception("the input format is not supported, please check the input format {}, the supported format as:\n{}".format(input_format, support_format))


ELEMENTTABLE={'H': 1,
    'He': 2,  'Li': 3,  'Be': 4,  'B': 5,   'C': 6,   'N': 7,   'O': 8,   'F': 9,   'Ne': 10,  'Na': 11,
    'Mg': 12, 'Al': 13, 'Si': 14, 'P': 15,  'S': 16,  'Cl': 17, 'Ar': 18, 'K': 19,  'Ca': 20,  'Sc': 21,
    'Ti': 22, 'V': 23,  'Cr': 24, 'Mn': 25, 'Fe': 26, 'Co': 27, 'Ni': 28, 'Cu': 29, 'Zn': 30,  'Ga': 31,
    'Ge': 32, 'As': 33, 'Se': 34, 'Br': 35, 'Kr': 36, 'Rb': 37, 'Sr': 38, 'Y': 39,  'Zr': 40,  'Nb': 41, 
    'Mo': 42, 'Tc': 43, 'Ru': 44, 'Rh': 45, 'Pd': 46, 'Ag': 47, 'Cd': 48, 'In': 49, 'Sn': 50,  'Sb': 51, 
    'Te': 52, 'I': 53,  'Xe': 54, 'Cs': 55, 'Ba': 56, 'La': 57, 'Ce': 58, 'Pr': 59, 'Nd': 60,  'Pm': 61,
    'Sm': 62, 'Eu': 63, 'Gd': 64, 'Tb': 65, 'Dy': 66, 'Ho': 67, 'Er': 68, 'Tm': 69, 'Yb': 70,  'Lu': 71, 
    'Hf': 72, 'Ta': 73, 'W': 74,  'Re': 75, 'Os': 76, 'Ir': 77, 'Pt': 78, 'Au': 79, 'Hg': 80,  'Tl': 81, 
    'Pb': 82, 'Bi': 83, 'Po': 84, 'At': 85, 'Rn': 86, 'Fr': 87, 'Ra': 88, 'Ac': 89, 'Th': 90,  'Pa': 91, 
    'U': 92,  'Np': 93, 'Pu': 94, 'Am': 95, 'Cm': 96, 'Bk': 97, 'Cf': 98, 'Es': 99, 'Fm': 100, 'Md': 101,
    'No': 102,'Lr': 103,'Rf': 104,'Db': 105,'Sg': 106,'Bh': 107,'Hs': 108,'Mt': 109,'Ds': 110,'Rg': 111,
    'Uub': 112
    }

ELEMENTTABLE_2 = {1: 'H', 
    2: 'He',     3: 'Li',   4: 'Be',   5: 'B',    6: 'C',    7: 'N',   8: 'O',     9: 'F',   10: 'Ne',  11: 'Na', 
    12: 'Mg',   13: 'Al',  14: 'Si',  15: 'P',   16: 'S',   17: 'Cl',  18: 'Ar',  19: 'K',   20: 'Ca',  21: 'Sc', 
    22: 'Ti',   23: 'V',   24: 'Cr',  25: 'Mn',  26: 'Fe',  27: 'Co',  28: 'Ni',  29: 'Cu',  30: 'Zn',  31: 'Ga', 
    32: 'Ge',   33: 'As',  34: 'Se',  35: 'Br',  36: 'Kr',  37: 'Rb',  38: 'Sr',  39: 'Y',   40: 'Zr',  41: 'Nb', 
    42: 'Mo',   43: 'Tc',  44: 'Ru',  45: 'Rh',  46: 'Pd',  47: 'Ag',  48: 'Cd',  49: 'In',  50: 'Sn',  51: 'Sb', 
    52: 'Te',   53: 'I',   54: 'Xe',  55: 'Cs',  56: 'Ba',  57: 'La',  58: 'Ce',  59: 'Pr',  60: 'Nd',  61: 'Pm', 
    62: 'Sm',   63: 'Eu',  64: 'Gd',  65: 'Tb',  66: 'Dy',  67: 'Ho',  68: 'Er',  69: 'Tm',  70: 'Yb',  71: 'Lu', 
    72: 'Hf',   73: 'Ta',  74:  'W',  75: 'Re',  76: 'Os',  77: 'Ir',  78: 'Pt',  79: 'Au',  80: 'Hg',  81: 'Tl', 
    82: 'Pb',   83: 'Bi',  84: 'Po',  85: 'At',  86: 'Rn',  87: 'Fr',  88: 'Ra',  89: 'Ac',  90: 'Th',  91: 'Pa', 
    92: 'U',    93: 'Np',  94: 'Pu',  95: 'Am',  96: 'Cm',  97: 'Bk',  98: 'Cf',  99: 'Es', 100: 'Fm', 101: 'Md', 
    102: 'No', 103: 'Lr', 104: 'Rf', 105: 'Db', 106: 'Sg', 107: 'Bh', 108: 'Hs', 109: 'Mt', 110: 'Ds', 111: 'Rg', 
    112: 'Uub'
    }

ELEMENTMASSTABLE={  1:1.007,2:4.002,3:6.941,4:9.012,5:10.811,6:12.011,
                            7:14.007,8:15.999,9:18.998,10:20.18,11:22.99,12:24.305,
                            13:26.982,14:28.086,15:30.974,16:32.065,17:35.453,
                            18:39.948,19:39.098,20:40.078,21:44.956,22:47.867,
                            23:50.942,24:51.996,25:54.938,26:55.845,27:58.933,
                            28:58.693,29:63.546,30:65.38,31:69.723,32:72.64,33:74.922,
                            34:78.96,35:79.904,36:83.798,37:85.468,38:87.62,39:88.906,
                            40:91.224,41:92.906,42:95.96,43:98,44:101.07,45:102.906,46:106.42,
                            47:107.868,48:112.411,49:114.818,50:118.71,51:121.76,52:127.6,
                            53:126.904,54:131.293,55:132.905,56:137.327,57:138.905,58:140.116,
                            59:140.908,60:144.242,61:145,62:150.36,63:151.964,64:157.25,65:158.925,
                            66:162.5,67:164.93,68:167.259,69:168.934,70:173.054,71:174.967,72:178.49,
                            73:180.948,74:183.84,75:186.207,76:190.23,77:192.217,78:195.084,
                            79:196.967,80:200.59,81:204.383,82:207.2,83:208.98,84:210,85:210,86:222,
                            87:223,88:226,89:227,90:232.038,91:231.036,92:238.029,93:237,94:244,
                            95:243,96:247,97:247,98:251,99:252,100:257,101:258,102:259,103:262,104:261,105:262,106:266}

def get_atomic_number_from_name(atomic_names:list[str]):
    res = []
    for name in atomic_names:
        res.append(ELEMENTTABLE[name])
    return res

def get_atomic_name_from_number(atomic_number:list[int]):
    res = []
    for number in atomic_number:
        res.append(ELEMENTTABLE_2[int(number)])
    return res

def get_atomic_name_from_str(atom_strs):
    try:
        return [int(_) for _ in atom_strs]
    except ValueError:
        return get_atomic_number_from_name(atom_strs)

def check_atom_type_name(atom_types:list[str]):
    return all([_ in ELEMENTTABLE.keys() for _ in atom_types])