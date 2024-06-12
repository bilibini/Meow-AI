from .wxauto import WeChat
from flask import Blueprint,render_template
from flask_socketio import SocketIO
import json
from meowServer import MeowAIServer as MS

wechatAPP = Blueprint('wechat', __name__,static_folder='static',template_folder='templates',url_prefix='/wechat')
wx=None
meowAIServer=None

def init(meowAIser:MS):
    global meowAIServer
    meowAIServer=meowAIser

@wechatAPP.route('/')
def index():
    return render_template('mai_wechat/index.html')

@wechatAPP.route('/start')
def start():
    global wx
    try:
        wx = WeChat()
        return '666'
    except:
        return json.dumps({'code': 1, 'msg': '启动失败，请检查是否已经打开并登录微信'})

