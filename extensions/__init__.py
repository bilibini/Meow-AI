from flask import Flask,json
from flask_socketio import SocketIO
from meowServer import MeowAI as MA
from typing import List,Dict,Mapping,Union,Callable,Any
from pathlib import Path
from importlib.metadata import version
import packaging.version as pv
import importlib
import subprocess
import sys

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

def load_extensions(meowAPP:Flask,meowSIO:SocketIO,meowAI:MA)->List[Path]:
    extensions_path = Path(__file__).parent
    extension_dirs = [extension_dir for extension_dir in extensions_path.iterdir() if (extension_dir / '__init__.py').exists()]
    print(extension_dirs)
    extension_infoList = []
    for extension_dir in extension_dirs:
        requirementsPath=extension_dir.joinpath('requirements.txt')
        try:
            install_requirements(requirementsPath)
        except Exception as e:
            print(f'Error installing requirements for {extension_dir.name}: {e}')
            continue
        
        module_name = f'extensions.{extension_dir.name}'
        module = importlib.import_module(module_name)
        if hasattr(module, 'init_app'):
            module.init_app(meowAPP,meowSIO,meowAI)
        extension_info=extension_dir.joinpath('static/info.json')
        if extension_info.exists():
            with open(extension_info,'r',encoding='UTF-8') as f:extension_infoList.append(json.load(f))
            
    
    @meowAPP.route('/extension/infoList.json')
    def get_extension_infoList():
        print(extension_infoList)
        return json.dumps(extension_infoList)
    
    return extension_dirs
