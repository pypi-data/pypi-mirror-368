from pwdata import META_OMol, Molecule, read_oMol_data

if __name__ == "__main__":
    file_list = [
        "/data/home/wuxingxing/codespace/pwdata_dev/examples/omol_data"
    ]

    atom_names = ["C", "H"]
    query = None
    cpu_nums = 3

    omol_data = read_oMol_data(file_list, atom_names, query, cpu_nums)
    print(len(omol_data.image_list))
