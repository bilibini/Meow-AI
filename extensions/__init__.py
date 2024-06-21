from flask import Flask,json
from flask_socketio import SocketIO
from meowServer import MeowAI as MA
from pathlib import Path
import importlib


def load_extensions(meowAPP:Flask,meowSIO:SocketIO,meowAI:MA)->list[Path]:
    extensions_path = Path(__file__).parent
    extension_dirs = [extension_dir for extension_dir in extensions_path.iterdir() if (extension_dir / '__init__.py').exists()]
    extension_infoList = []
    for extension_dir in extension_dirs:
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
