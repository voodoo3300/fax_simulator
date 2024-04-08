import subprocess
import platform

def print_pdf(file_path):
    if platform.system() == 'Linux':
        subprocess.run(['lp', file_path])
    else:
        print('Ducken geht nur unter Linux')