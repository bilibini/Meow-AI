from flask import Flask
from flask_socketio import SocketIO
from meowServer import MeowAI as MA
from .server import main

def init_app(meowAPP:Flask,meowSIO:SocketIO,meowAI:MA):
    main(meowAPP,meowSIO,meowAI)