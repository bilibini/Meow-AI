import re,json,torch
from tqdm import tqdm
from rwkv.utils import PIPELINE, PIPELINE_ARGS
from typing import List,Dict,Mapping,Union,Callable,Any,Tuple

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

    def chat(self,messages:List[Mapping[str,str]],prev_state:torch.Tensor=None,callback:Callable[[str],Any]=None)->Tuple[str,torch.Tensor]:
        '''
        messages=[
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
        out_tokens = []
        out_len = 0
        out_str = ""
        occurrence = {}
        state = prev_state
        input_text = "\n\n".join([f"{text['role']}:{self.purr(text['content'])}" for text in messages])
        if state:
            input_text = f"\n\n{input_text}\n\nAnswerer:"
        else:
            input_text = f"Answerer:{self.purr(self.character.persona)}\n\n{input_text}\n\nAnswerer:"
        for i in tqdm(range(self.max_tokens),desc=f"tokens",leave=False):
            if self.stop:break
            if i == 0:
                out, state = self.model.model.forward(self.model.encode(input_text), state)
            else:
                out, state = self.model.model.forward([token], state)
            for n in occurrence:
                out[n] -= (
                    self.character.alpha_frequency + occurrence[n] * self.character.alpha_presence
                )

            token = self.model.sample_logits(out, temperature=self.character.temperature, top_p=self.character.top_p)
            if token == 0:break
            out_tokens += [token]

            for n in occurrence:
                occurrence[n] *= self.character.alpha_decay
            occurrence[token] = 1 + (occurrence[token] if token in occurrence else 0)

            tmp = self.model.decode(out_tokens[out_len:])
            out_str += tmp
            # self.chat_state=state
            if ("\ufffd" not in tmp) and ( not tmp.endswith("\n") ):
                out_len = i + 1
            elif "\n\n" in tmp:
                break
            if callback and not self.stop: callback(tmp)
        print(out_str.strip())
        return out_str.strip(),state
    
    def talk(self,input_text:str,prev_state:torch.Tensor=None,callback:Callable[[str],Any]=None)->Tuple[str,torch.Tensor]:
        out_tokens = []
        out_len = 0
        out_str = ""
        occurrence = {}
        state = prev_state
        for i in tqdm(range(self.max_tokens),desc=f"tokens",leave=False):
            if i == 0:
                out, state = self.model.model.forward(self.model.encode(input_text), state)
            else:
                out, state = self.model.model.forward([token], state)
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
            # self.talk_state=state
            if callback: callback(tmp)
            out_len = i + 1
            if self.stop:break
        print(out_str)
        return out_str,state
    
from flask import Flask, render_template
from flask_socketio import SocketIO
import webbrowser
from extensions import register_extensions

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
        register_extensions(self.app,self.socketio,self.meowAI)

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/extension/')
        def extension():
            return render_template('extension.html')

        @self.socketio.on('emit')
        def emit(news:Dict[str,Union[int,float]]):
            '''
            news={'code':1,'msg':'XX错误'}
            '''
            self.socketio.emit('emit', json.dumps(news))

        @self.socketio.on('stop')
        def stop(status:bool=True):
            self.socketio.emit('stop', status)
            self.meowAI.stop=status

        @self.socketio.on('character')
        def handle_character(character:Dict[str,Union[int,float]]):
            self.meowAI.character = Character(**character)
            print(character)
            
        @self.socketio.on('chat')
        def handle_chat(message:Mapping[str,Union[str,List[Dict[str,str]]]]):
            try:
                self.meowAI.stop=False
                self.meowAI.chat(message,None,lambda x:self.socketio.emit('chat',x[0]))
            except Exception as e:
                emit({'code':1,'msg':f'生成错误Error:{e}'})
            finally:
                stop(True)
        
        @self.socketio.on('talk')
        def handle_talk(prompt):
            try:
                self.meowAI.stop=False
                self.meowAI.talk(prompt,None,lambda x:self.socketio.emit('talk',x[0]))
            except Exception as e:
                emit({'code':1,'msg':f'生成错误Error:{e}'})
            finally:
                stop(True)

    def run(self):
        if self.autoOpen:webbrowser.open(f'http://{self.host}:{self.port}')
        self.socketio.run(self.app,host=self.host,port=self.port,debug=self.debug,use_reloader=self.use_reloader)