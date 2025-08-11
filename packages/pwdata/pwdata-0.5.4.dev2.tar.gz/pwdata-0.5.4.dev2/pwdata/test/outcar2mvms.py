import os, sys
from pwdata import Config

import argparse

def run_convert_configs(cmd_list:list[str]):
    parser = argparse.ArgumentParser(description='This command is used for transferring structural files between different apps. For extxyz format, all configs will save to one file, \nFor pwmlff/npy, configs with same atom types and atom nums in each type will save to one dir.\n')

    parser.add_argument('-i', '--input',         type=str, required=True,  help="The directory or file path of the datas.\nYou can also use JSON file to list all file paths in 'datapath': [], such as 'pwdata/test/meta_data.json'")
    parser.add_argument('-s', '--savepath',      type=str, required=False, default="MOVEMENT", help="The output dir path, if not provided, the current dir will be used")
    args = parser.parse_args(cmd_list)
    image = Config(data_path=args.input, format="vasp/outcar")
    image.to(format="pwmat/movement", data_path=args.savepath)
    print("covert outcar to movement done!")

if __name__=="__main__":
    print(sys.argv)
    run_convert_configs(cmd_list = sys.argv[1:])