'''
description: 
Convert various trajectory files ('pwmat/movement','vasp/outcar','cp2k/md', or 'lammps/dump')
    to a single structure format ('pwmat/config', 'vasp/poscar', 'lammps/lmp')
'''

from pwdata import Config
from pwdata.utils.constant import FORMAT
from pwdata.config import string2index
def trajs2config():
    atom_types = ["Hf", "O"] # for lammps
    input_file = "/data/home/wuxingxing/datas/pwmat_mlff_workdir/hfo2/lmps_test/jit_cpu/traj/0.lammpstrj"
    save_dir = "/data/home/wuxingxing/datas/pwmat_mlff_workdir/hfo2/lmps_test/jit_cpu/traj/"
    input_format="lammps/dump"
    save_format = "pwmat/config"
    index_str=":" #'start:stop:step' -> '0:10' is '0:10:1' 
    image = Config(data_path=input_file, format=input_format, index=index_str, atom_names=atom_types)
    tmp_image_data = image.images
    indexs = string2index(index_str)
    if isinstance(indexs, slice):
        start = 0 if indexs.start is None else indexs.start
        end   = len(tmp_image_data) if indexs.stop is None else indexs.stop
        step  = 1 if indexs.step is  None else indexs.step
        save_list = list(range(start, end, step))
        for id, config in enumerate(tmp_image_data):
            savename = "{}_{}".format(save_list[id], FORMAT.get_filename_by_format(save_format))
            image.iamges = [config]
            image.to(output_path = save_dir,
                data_name = savename,
                save_format = save_format,
                sort = True)
    else:
        savename = "{}_{}".format(indexs, FORMAT.get_filename_by_format(save_format))
        image.to(output_path = save_dir,
            data_name = savename,
            save_format = save_format,
            sort = True)

if __name__=="__main__":
    trajs2config()

	
