import subprocess
import platform

def run_calc():
    """Opens calculator if on Windows."""
    if platform.system() == "Windows":
        subprocess.Popen(["calc.exe"])
    else:
        print("This script only works on Windows.")
