from .wxauto import WeChat,elements
from .install import init
from flask import Flask,Blueprint,render_template,request
from flask_socketio import SocketIO
from threading import Thread, Event
import json,time
from meowServer import MeowAI as MA

class WeChatServer():
    def __init__(self,meowAPP:Flask,meowSIO:SocketIO, meowAI: MA):
        self.meowAI=meowAI
        self.meowAPP=meowAPP
        self.meowSIO=meowSIO
        self.stop_event = Event()
        self.app = Blueprint('wechat', __name__,static_folder='static',template_folder='templates',url_prefix='/wechat')
        self.wx=None
        self.prev_state=None
        self.chats=[]
        @self.app.route('/')
        def index():
            return render_template('mai_wechat/index.html')
        @self.app.route('/start',methods=['POST'])
        def start():
            try:
                self.wx = WeChat()
                self.stop_event.clear()
                data = request.get_json()
                thread = Thread(target=self.run, args=(data['name'],data['chatHistory']))
                thread.start()
                return json.dumps({'code': 0, 'msg': f'启动成功，获取到已登录窗口：{self.wx.nickname}'})
            except:
                return json.dumps({'code': 1, 'msg': '启动失败，请检查是否已经打开并登录微信'})
        @self.app.route('/stop',methods=['POST','GET'])
        def stop():
            self.stop_event.set()
            self.prev_state=None
            return json.dumps({'code': 0, 'msg': '微信自动对话停止成功'})
        
        self.meowAPP.register_blueprint(self.app)
        self.index=index

    
    def reply(self,msg:str,chat:elements.ChatWnd)->str:
        '''
        self.chats=[
            {
                "role": "User",
                "content": "What is the meaning of life?"
            },
            {
                "role": "Assistant",
                "content": "The meaning of life is to live a happy and fulfilling life."
            },
            {
                "role": "User",
                "content": "How do cats call?"
            },
        ]
        '''
        self.chats.append({"role": "User", "content": self.meowAI.purr(msg)})
        if self.prev_state:
            messages=self.chats[len(self.chats)-2:]
        else:
            messages=self.chats
        print(messages)
        reply,self.prev_state=self.meowAI.chat(messages,self.prev_state,lambda x:print(x[0],end=''))
        self.chats.append({"role": "Assistant", "content": reply})
        return reply

    def run(self,name:str,chat_history:bool=False):
        try:
            wx=self.wx
            wx.ChatWith(who=name)
            if chat_history:
                wx.LoadMoreMessage()
                for chat in wx.GetAllMessage():
                    if chat[0]=='SYS':pass
                    elif chat[0]=='Self':
                        self.chats.append({"role": "Assistant", "content": chat[1]})
                    else:
                        self.chats.append({"role": "User", "content": chat[1]})
                print(self.chats)
            wx.AddListenChat(who=name)
            while not self.stop_event.is_set():
                chats = wx.GetListenMessage()
                for chat in filter(lambda x:x.who==name,chats):
                    msgs=chats.get(chat)
                    for msg in filter(lambda x:x.type=='friend',msgs):
                        reply=self.reply(msg.content,chat)
                        chat.SendMsg(reply)
                time.sleep(0.5)
        except Exception as e:
            self.meowSIO.emit('emit',{'code':1,'msg':'微信监听失败:'+str(e)})
            self.stop_event.set()
            self.prev_state=None
            self.meowSIO.emit('wechat_stop','微信监听失败:'+str(e))
            print('错误：',e)


def main(meowAPP:Flask,meowSIO:SocketIO,meowAI:MA):
    init()
    WeChatServer(meowAPP,meowSIO,meowAI)