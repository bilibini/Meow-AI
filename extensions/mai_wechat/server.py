from .wxauto import WeChat,elements
from .install import init
from flask import Flask,Blueprint,render_template
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
        self.app.route('/')
        def index():
            return render_template('mai_wechat/index.html')
        self.app.route('/start')
        def start():
            try:
                self.wx = WeChat()
                self.stop_event.clear()
                thread = Thread(target=self.run, args=('bilibini',))
                thread.start()
                return json.dumps({'code': 0, 'msg': f'启动成功，获取到已登录窗口：{self.wx.nickname}'})
            except:
                return json.dumps({'code': 1, 'msg': '启动失败，请检查是否已经打开并登录微信'})
        self.app.route('/stop')
        def stop():
            self.stop_event.set()
            return json.dumps({'code': 0, 'msg': '微信自动对话停止成功'})
        
        self.meowAPP.register_blueprint(self.app)
        self.index=index
        self.start=start
        self.stop=stop
    
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
        self.chats.append({"role": "User", "content": msg})
        if len(self.chats)<1:
            input_text = "\n\n".join([f"{text['role']}: {self.meowAI.purr(text['content'])}" for text in self.chats['messages']])
            input_text = f"Answerer: {self.meowAI.purr(self.character.persona)}\n\n{input_text}\n\nAnswerer:"
        else:
            input_text = f"\n\nUser:{self.meowAI.purr(msg)}\n\nAnswerer:"
        reply,self.prev_state=self.meowAI.chat(input_text,self.prev_state,lambda x:print(x[0],end=''))
        self.chats.append({"role": "Assistant", "content": reply})
        return reply

    def run(self,name:str,get_chat_history:bool=False):
        wx=self.wx
        wx.ChatWith(who=name)
        if get_chat_history:
            wx.LoadMoreMessage()
            wx.GetAllMessage()
        wx.AddListenChat(who=name)
        while not self.stop_event.is_set():
            try:
                chats = wx.GetListenMessage()
                for chat in filter(lambda x:x.who==name,chats):
                    msgs=chats.get(chat)
                    for msg in filter(lambda x:x.type=='friend',msgs):
                        reply=self.reply(msg.content,chat)
                        chat.SendMsg(reply)
            except:
                self.meowSIO.emit('emit',{'code':1,'msg':'微信监听失败'})
                self.stop()
            time.sleep(0.5)        
                    


def main(meowAPP:Flask,meowSIO:SocketIO,meowAI:MA):
    init()
    WeChatServer(meowAPP,meowSIO,meowAI)