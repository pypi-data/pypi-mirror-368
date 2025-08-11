from ase.io import read, write
import os
import glob

"""
xyz_file = "/data/home/wuxingxing/codespace/EDM/outputs/edm_qm9/bk_eval/stabel_pwmat/0/molecule_stable_000.xyz"
atoms = read(xyz_file)
atoms.center(vacuum=8)
# 获取原子符号列表，并排序
symbols = atoms.get_chemical_symbols()
sorted_indices = sorted(range(len(symbols)), key=lambda i: symbols[i])

# 按排序后的索引重新排列原子
atoms_sorted = atoms[sorted_indices]

save_file = "/data/home/wuxingxing/codespace/EDM/outputs/edm_qm9/bk_eval/stabel_pwmat/0/sort.0.POSCAR"
write(filename=save_file, images=atoms_sorted, format="vasp")
"""

pseudo = ["/data/home/wuxingxing/codespace/EDM/outputs/edm_qm9/bk_eval/stabel_pwmat/F.SG15.PBE.UPF",
        "/data/home/wuxingxing/codespace/EDM/outputs/edm_qm9/bk_eval/stabel_pwmat/N.SG15.PBE.UPF",
        "/data/home/wuxingxing/codespace/EDM/outputs/edm_qm9/bk_eval/stabel_pwmat/C.SG15.PBE.UPF",
        "/data/home/wuxingxing/codespace/EDM/outputs/edm_qm9/bk_eval/stabel_pwmat/H.SG15.PBE.UPF",
        "/data/home/wuxingxing/codespace/EDM/outputs/edm_qm9/bk_eval/stabel_pwmat/O.SG15.PBE.UPF",
        "/data/home/wuxingxing/codespace/EDM/outputs/edm_qm9/bk_eval/stabel_pwmat/etot.input",
        "/data/home/wuxingxing/codespace/EDM/outputs/edm_qm9/bk_eval/stabel_pwmat/run.sh"]

def set_path():
    xyz_path = "/data/home/wuxingxing/codespace/EDM/outputs/edm_qm9/bk_eval/molecules"
    save_path= "/data/home/wuxingxing/codespace/EDM/outputs/edm_qm9/bk_eval/stabel_pwmat"
    xyz_files = glob.glob(os.path.join(xyz_path, "molecule_stable_*.xyz"))
    for xyz_file in xyz_files:
        if "molecule_stable_000.xyz" in os.path.basename(xyz_file):
            pass
        atoms = read(xyz_file)
        atoms.center(vacuum=8)
        # 获取原子符号列表，并排序
        symbols = atoms.get_chemical_symbols()
        sorted_indices = sorted(range(len(symbols)), key=lambda i: symbols[i])

        # 按排序后的索引重新排列原子
        atoms_sorted = atoms[sorted_indices]
        idx = int(xyz_file.split("/")[-1].split("_")[-1].split(".")[0])
        save_dir = os.path.join(save_path, "{}".format(idx))
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        save_file = os.path.join(save_dir, "POSCAR")
        write(filename=save_file, images=atoms_sorted, format="vasp")

        for _tmp in pseudo:
            os.system(f"cp {_tmp} {save_dir}")

        cwd = os.getcwd()
        os.chdir(save_dir)
        os.system("pwdata cvt_config -i POSCAR -f vasp/poscar -o pwmat/config")
        os.chdir(cwd)

if __name__ == "__main__":
    set_path() # pwmat
