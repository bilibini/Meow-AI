from flask import Flask
from flask_socketio import SocketIO
import extensions.mai_wechat.server
from meowServer import MeowAI as MA

def register_extensions(meowAPP:Flask,meowSIO:SocketIO,meowAI:MA):
    extensions.mai_wechat.server.main(meowAPP,meowSIO,meowAI)
    