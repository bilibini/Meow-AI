from flask import Flask
from flask_socketio import SocketIO
from meowServer import MeowAI as MA
from .setupButler import SetupButler

def init_app(meowAPP:Flask,meowSIO:SocketIO,meowAI:MA):
    SetupButler(meowAPP,meowSIO,meowAI).run()