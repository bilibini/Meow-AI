import torch,os
from transformers import AutoModelForCausalLM, AutoTokenizer

def generate_prompt(instruction, input=""):
    instruction = instruction.strip().replace('\r\n','\n').replace('\n\n','\n')
    input = input.strip().replace('\r\n','\n').replace('\n\n','\n')
    if input:
        return f"""Instruction: {instruction}\n\nInput: {input}\n\nResponse:"""
    else:
        return f"""User: hi\n\nAssistant: Hi. I am your assistant and I will provide expert full response in full details. Please feel free to ask any question and I will always answer it.\n\nUser: {instruction}\n\nAssistant:"""

output_folder=os.path.join(os.path.dirname(__file__),'model','rwkv-4-world-430m')
model = AutoModelForCausalLM.from_pretrained(output_folder, trust_remote_code=True).to(torch.float32)
tokenizer = AutoTokenizer.from_pretrained(output_folder, trust_remote_code=True)


from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.jinja_env.variable_start_string = '{['
app.jinja_env.variable_end_string = ']}'
socketio = SocketIO(app)
terminate=False

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(message):
    global terminate
    terminate=False
    messages=message
    prompt = ''
    if len(messages)>1:
        prompt+=f"""User: hi\n\nAssistant: Hi. I am your assistant and I will provide expert full response in full details. Please feel free to ask any question and I will always answer it.\n\n"""
        for mess in messages:
            prompt+=f"""{'User' if mess['type']=='you' else 'Assistant'}: {mess['content']}\n\n"""
        prompt+=f"""Assistant:"""
    else:
        prompt = generate_prompt(messages[0]['content'])

    print(prompt)
    inputs = tokenizer(prompt, return_tensors="pt")
    promptnew=prompt
    while True:
        if terminate:
            socketio.emit('terminate', True)
            return
        output = model.generate(inputs["input_ids"], max_new_tokens=1, do_sample=True, temperature=1.0, top_p=0.3, top_k=0, )
        inputs=tokenizer.decode(output[0].tolist(), skip_special_tokens=True)
        words=inputs.replace(promptnew,'')
        promptnew=inputs
        print(promptnew.replace(prompt,''))
        if promptnew.replace(prompt,'').count('\n\n')>0 or words=='' or terminate:
            socketio.emit('terminate', True)
            return
        socketio.emit('message', words)
        inputs = tokenizer(promptnew, return_tensors="pt")

@socketio.on('terminate')
def handle_terminate(message):
    global terminate
    terminate=True
    print('接收到停止命令',terminate,message)

if __name__ == '__main__':
    socketio.run(app, debug=True)
