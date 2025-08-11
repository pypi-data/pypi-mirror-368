import os
import numpy as np
import numpy.linalg as LA

def save_to_movement(image_data_all: list, data_path: str, data_name: str = "toMOVEMENT"):
    data_name = open(os.path.join(data_path, data_name), 'w')
    for i in range(len(image_data_all)):
        image_data = image_data_all[i]
        if image_data.cartesian:
            image_data._set_fractional()
        # with open(os.path.join(output_path, data_name), 'a') as wf:
        scf = image_data.scf if image_data.scf is not None else 0
        data_name.write(" %d atoms,Iteration (fs) = %16.10E, Etot,Ep,Ek (eV) = %16.10E  %16.10E   %16.10E, SCF = %d\n"\
                            % (image_data.atom_nums, 0.0, image_data.Ep, image_data.Ep, 0.0, scf))
        data_name.write(" MD_INFO: METHOD(1-VV,2-NH,3-LV,4-LVPR,5-NHRP) TIME(fs) TEMP(K) DESIRED_TEMP(K) AVE_TEMP(K) TIME_INTERVAL(fs) TOT_TEMP(K) \n")
        data_name.write("          *    ************   ********   ********   ********    ********    ********\n")
        data_name.write("     TOTAL MOMENTUM\n")
        data_name.write("     ********    ********    ********\n")
        data_name.write(" MD_VV_INFO: Basic Velocity Verlet Dynamics (NVE), Initialized total energy(Hartree)\n")
        data_name.write("          *******              \n")
        data_name.write("Lattice vector (Angstrom)\n")
        for j in range(3):
            if image_data.virial is not None:
                virial = image_data.get_virial()
                data_name.write("  %16.10E    %16.10E    %16.10E     stress (eV): %16.10E    %16.10E    %16.10E\n" % (image_data.lattice[j][0], image_data.lattice[j][1], image_data.lattice[j][2], virial[j][0], virial[j][1], virial[j][2]))
            else:
                data_name.write("  %16.10E    %16.10E    %16.10E\n" % (image_data.lattice[j][0], image_data.lattice[j][1], image_data.lattice[j][2]))
        data_name.write("  Position (normalized), move_x, move_y, move_z\n")
        for j in range(image_data.atom_nums):
            data_name.write(" %4d    %20.15F    %20.15F    %20.15F    1 1 1\n"\
                                % (image_data.atom_types_image[j], image_data.position[j][0], image_data.position[j][1], image_data.position[j][2]))
        data_name.write("  Force (-force, eV/Angstrom)\n")
        for j in range(image_data.atom_nums):
            data_name.write(" %4d    %20.15F    %20.15F    %20.15F\n"\
                                % (image_data.atom_types_image[j], -image_data.force[j][0], -image_data.force[j][1], -image_data.force[j][2]))
        data_name.write(" -------------------------------------\n")
    data_name.close()
    # print("Convert to %s successfully!" % data_name)