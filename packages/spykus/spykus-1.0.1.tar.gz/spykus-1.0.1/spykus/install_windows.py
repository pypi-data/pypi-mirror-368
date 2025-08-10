import os
import subprocess

def apply_reg():
    reg_file = os.path.join(os.path.dirname(__file__), "spykus.reg")
    subprocess.run(["regedit", "/s", reg_file], shell=True)

apply_reg()
