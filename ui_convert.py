import argparse
import os

my_parser = argparse.ArgumentParser()
my_parser.add_argument('name', type=str)

name = my_parser.parse_args().name

command_ui = f"pyuic5 -x Resources/UI/{name}.ui -o Resources/Designs/{name}.py"
command_res = "pyrcc5 -o ./res_rc.py Resources/Icons/res.qrc"

os.system(command_ui)
os.system(command_res)
