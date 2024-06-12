from flask import Flask
from extensions.mai_wechat.server import wechatAPP
from meowServer import MeowAIServer as MS

def register_extensions(app: Flask,meowAIServer:MS):
    app.register_blueprint(wechatAPP)
    