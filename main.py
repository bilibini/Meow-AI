import torch,os,json,webbrowser
from rwkv.model import RWKV
from rwkv.utils import PIPELINE, PIPELINE_ARGS

os.environ['RWKV_JIT_ON'] = '1'
os.environ["RWKV_CUDA_ON"] = '0'

is_available='cuda fp16' if torch.cuda.is_available() else 'cpu fp32'
config=None
modelsFolder=""
modelFile=""
autoOpen=True

with open(os.path.join(os.path.dirname(__file__),'config.json'),'r') as f:
    config = json.load(f)
modelsFolder=os.path.join(os.path.dirname(__file__),config["modelsFolder"]) if ":" not in config["modelsFolder"] else config["modelsFolder"]
modelFile=os.path.join(modelsFolder,config["modelFile"])
autoOpen=config["autoOpen"]

model = RWKV(model=modelFile, strategy=is_available)
pipeline = PIPELINE(model, "rwkv_vocab_v20230424")


def generate_prompt(instruction, persona=""):
    instruction = instruction.strip().replace('\r\n','\n').replace('\n\n','\n')
    persona = persona.strip().replace('\r\n','\n').replace('\n\n','\n')
    if persona:
        return f"""User: 你是？\n\nAssistant: {persona}\n\nUser: {instruction}\n\nAssistant:"""
    else:
        return f"""User: hi\n\nAssistant: Hi. I am your assistant and I will provide expert full response in full details. Please feel free to ask any question and I will always answer it.\n\nUser: {instruction}\n\nAssistant:"""


from flask import Flask, render_template
from flask_socketio import SocketIO
import socket
app = Flask(__name__)
app.jinja_env.variable_start_string = '{['
app.jinja_env.variable_end_string = ']}'
socketio = SocketIO(app)
terminate=False
promptnew=""

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(message):
    global terminate,promptnew
    promptnew=""
    def emitCTX(ctx):
        global terminate,promptnew
        if terminate:
            socketio.emit('terminate', True)
            return True
        promptnew=promptnew+ctx
        if promptnew.count('\n\n')>0 or ctx=='' or terminate:
            socketio.emit('terminate', True)
            return True
        socketio.emit('message', ctx)
        print(ctx,end='')
        return False
        
    terminate=False
    messages=message['messages']
    persona=message['persona']
    characters=message['characters']
    temperature=float(characters['sense'])
    top_p=float(characters['pizzazz'])
    prompt = ''
    if len(messages)>1:
        prompt+=f"""User: 你是？\n\nAssistant: {persona}\n\n"""
        for mess in messages:
            prompt+=f"""{'User' if mess['type']=='you' else 'Assistant'}: {mess['content']}\n\n"""
        prompt+=f"""Assistant:"""
    else:
        prompt = generate_prompt(messages[0]['content'],persona)
    args = PIPELINE_ARGS(temperature = temperature, top_p = top_p, top_k = 100,alpha_frequency = 0.25,alpha_presence = 0.25,alpha_decay = 0.996,token_ban = [0],token_stop = [],chunk_len = 256)
    #top_p严谨->活泼 0->10 性格
    # 更小的top_p → 更准确的答案，但会增加输出重复内容的概率
    #temperature 理性->感性 0->2 认知
    #改变模型输出分布的随机性，温度越高 → 输出随机性越大，文采斐然，但更容易偏题、脱轨
    print(prompt,end="")
    pipeline.generate(prompt, token_count=4096, args=args, callback=emitCTX)
    print('\n')

@socketio.on('terminate')
def handle_terminate(message):
    global terminate
    terminate=True
    print('接收到停止命令',terminate,message)

if __name__ == '__main__':
    if autoOpen:webbrowser.open('http://127.0.0.1:5000')
    socketio.run(app, debug=True,use_reloader=False)
    
