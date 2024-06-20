from flask import Flask
from flask_socketio import SocketIO
from meowServer import MeowAI as MA
from pathlib import Path
import importlib


def load_extensions(meowAPP:Flask,meowSIO:SocketIO,meowAI:MA)->list[Path]:
    extensions_path = Path(__file__).parent
    extension_dirs = filter(lambda p: (p / '__init__.py').exists(), extensions_path.iterdir())
    for extension_dir in extension_dirs:
        module_name = f'extensions.{extension_dir.name}'
        module = importlib.import_module(module_name)
        if hasattr(module, 'init_app'):
            module.init_app(meowAPP,meowSIO,meowAI)
    return [i for i in extension_dirs]
