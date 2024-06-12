from importlib.metadata import version
import packaging.version as pv
import subprocess
from pathlib import Path
import sys

rootPath = Path(__file__).parent
pipPath = Path(sys.executable).parent.joinpath("Scripts\pip.exe")
requirementsPath = rootPath.joinpath("requirements.txt")


def get_installed_version(package: str) -> pv.Version:
    try:
        return pv.parse(version(package))
    except Exception:
        return pv.parse("0")

def install_requirements(requirements:Path):
    with open(requirements) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '==' in line:
                package, version = line.split('==')
                if get_installed_version(package) != pv.parse(version):
                    print(f'Installing {package}=={version}')
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', line])
            elif '>=' in line:
                package, version = line.split('>=')
                if get_installed_version(package) < pv.parse(version):
                    print(f'Installing {package}=={version}')
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', line])
            elif get_installed_version(line)==pv.parse("0"):
                print(f'Installing {line}')
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', line])
            else:
                print(f'{line} is already installed')

def init():
    install_requirements(requirementsPath)
                


