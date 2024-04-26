import re
from rwkv.utils import PIPELINE, PIPELINE_ARGS
from typing import List,Dict,Mapping,Union,Callable,Any

class Character(PIPELINE_ARGS):
    def __init__(self,persona:str='主人你好呀！我是你的可爱猫娘，喵~', temperature:float=1.1,top_p:float=0.7, top_k:float=0, alpha_frequency:float=0.2, alpha_presence:float=0.2, alpha_decay:float=0.996, token_ban:list=[], token_stop:list=[], chunk_len=256):
        super().__init__(temperature, top_p, top_k, alpha_frequency, alpha_presence, alpha_decay, token_ban, token_stop, chunk_len)
        self.persona=persona


class MeowAI:
    def __init__(self,model:PIPELINE, character:Character=Character(),max_tokens:int=2048 ):
        self.model=model
        self.character=character
        self.max_tokens=max_tokens
        self.stop=False
        self.chat_state=None
        self.talk_state=None

    def purr(self,txt:str)->str:
        return re.sub(r'\r*\n{2,}', '\n', txt.strip())

    def chat(self,message:Mapping[str,Union[str,List[Dict[str,str]]]],prev_state:bool=False,callback:Callable[[str],Any]=None)->str:
        '''
        message={
            "Answerer": "Answerer",
            "messages": [
                {
                    "role": "user",
                    "content": "What is the meaning of life?"
                },
                {
                    "role": "assistant",
                    "content": "The meaning of life is to live a happy and fulfilling life."
                },
                {
                    "role": "user",
                    "content": "How do cats call?"
                },
            ]
        }
        '''
        out_tokens = []
        out_len = 0
        out_str = ""
        occurrence = {}
        state = self.chat_state if prev_state else None
        input_text = "\n\n".join([f"{text['role']}: {self.purr(text['content'])}" for text in message['messages']])
        input_text = f"{message['Answerer']}: {self.purr(self.character.persona)}\n\n"+input_text+f"\n\n{message['Answerer']}: "
        for i in range(self.max_tokens):
            if i == 0:
                out, state = self.model.forward(self.model.encode(input_text), state)
            else:
                out, state = self.model.forward([token], state)
            for n in occurrence:
                out[n] -= (
                    self.character.alpha_frequency + occurrence[n] * self.character.persona
                )

            token = self.model.sample_logits(out, temperature=self.character.temperature, top_p=self.character.top_p)

            if token == 0:break
            out_tokens += [token]

            for n in occurrence:
                occurrence[n] *= self.character.alpha_decay
            occurrence[token] = 1 + (occurrence[token] if token in occurrence else 0)

            tmp = self.model.decode(out_tokens[out_len:])
            out_str += tmp
            self.prev_state=state
            print(tmp, end="", flush=True)
            if callback: callback(tmp)
            if ("\ufffd" not in tmp) and ( not tmp.endswith("\n") ):
                out_len = i + 1
            elif "\n\n" in tmp or self.stop:
                break
        return out_str.strip()
    
    def talk(self,input_text:str,prev_state:bool=False,callback:Callable[[str],Any]=None)->str:
        out_tokens = []
        out_len = 0
        out_str = ""
        occurrence = {}
        state = self.chat_state if prev_state else None
        for i in range(self.max_tokens):
            if i == 0:
                out, state = self.model.forward(self.model.encode(input_text), state)
            else:
                out, state = self.model.forward([token], state)
            for n in occurrence:
                out[n] -= (
                    self.character.alpha_frequency + occurrence[n] * self.character.persona
                )
            token = self.model.sample_logits( out, temperature=self.character.temperature, top_p=self.character.top_p)

            out_tokens += [token]

            for n in occurrence:
                occurrence[n] *= self.character.alpha_decay
            occurrence[token] = 1 + (occurrence[token] if token in occurrence else 0)

            tmp = self.model.decode(out_tokens[out_len:])
            out_str += tmp
            self.prev_state=state
            print(tmp, end="", flush=True)
            if callback: callback(tmp)
            out_len = i + 1
            if self.stop:
                break
        return out_str
    
from flask import Flask, render_template
from flask_socketio import SocketIO
import webbrowser

class MeowAIServer():
    def __init__(self, meowAI:MeowAI, host:str="0.0.0.0", port:int=5000, debug:bool=False,use_reloader:bool=False,autoOpen:bool=True):
        if not meowAI:raise Exception("meowAI is not defined")
        self.meowAI = meowAI
        self.host=host
        self.port=port
        self.debug=debug
        self.use_reloader=use_reloader
        self.autoOpen=autoOpen

        self.app = Flask(__name__)
        self.app.jinja_env.variable_start_string = '{['
        self.app.jinja_env.variable_end_string = ']}'
        self.socketio = SocketIO(self.app)

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.socketio.on('stop')
        def stop(status:bool=True):
            self.socketio.emit('stop', status)
            self.meowAI.stop=status

        @self.socketio.on('chat')
        def handle_chat(message:Mapping[str,Union[str,List[Dict[str,str]]]]):
            self.meowAI.stop=False
            self.meowAI.chat(message,True,lambda x:self.socketio.emit('chat',x))
            stop(True)
        
        @self.socketio.on('talk')
        def handle_talk(prompt):
            self.meowAI.stop=False
            self.meowAI.talk(prompt,False,lambda x:self.socketio.emit('talk',x))
            stop(True)

    def run(self):
        if self.autoOpen:webbrowser.open(f'http://{self.host}:{self.port}')
        self.socketio.run(self.app,host=self.host,port=self.port,debug=self.debug,use_reloader=self.use_reloader)