from flask import Flask,Blueprint,render_template,request
from typing import List,Dict,Mapping,Union,Callable,Any
from flask_socketio import SocketIO
from meowServer import MeowAI as MA
from rwkv.model import RWKV
from rwkv.utils import PIPELINE
from pathlib import Path
import json,gc,torch,time


rootPath = Path(__file__).parent.parent.parent
configPath=rootPath.joinpath('config.json')

class SetupButler():
    def __init__(self,meowAPP:Flask,meowSIO:SocketIO,meowAI:MA):
        self.meowAI=meowAI
        self.meowAPP=meowAPP
        self.meowSIO=meowSIO
        self.app = Blueprint('setupButler', __name__,static_folder='static',template_folder='templates',url_prefix='/extension/setupButler')
        self.config={}
        with open(configPath,'r') as f:
            self.config = json.load(f)
        
    def run(self):
        modelsFolder=rootPath.joinpath(self.config['modelsFolder'])
        print(modelsFolder)
        @self.app.route('/config.json')
        def get_config():
            print(modelsFolder)
            config={
                'host':self.config['host'],
                'port':self.config['port'],
                'model':str(modelsFolder.joinpath(self.config['modelFile'])),
                'modelList':self.getModelsList(modelsFolder),
                'strategy':self.config['strategy'],
                'autoOpen':self.config['autoOpen']
            }
            return json.dumps(config)
       
        @self.app.route('/setup',methods=['POST'])
        def setup():
            data = request.get_json()
            self.config['host']=data['host']
            self.config['port']=data['port']
            self.config['autoOpen']=data['autoOpen']
            model=Path(data['model']).name
            self.config['modelFile']=model
            self.config['strategy']=data['strategy']
            with open(configPath,'w') as f:f.write(json.dumps(self.config,indent=4))
            return json.dumps({'code': 0, 'msg': '设置成功，请重新启动服务'})
            if model!=self.config['modelFile'] or data['strategy']!=self.config['strategy']:
                del self.meowAI.model.model
                del self.meowAI.model
                gc.collect()
                if 'cuda' in self.config['strategy']:
                    torch.cuda.empty_cache()
                self.config['modelFile']=model
                self.config['strategy']=data['strategy']

                model = RWKV(model=str(data['model']), strategy=data['strategy'])
                pipeline = PIPELINE(model, "rwkv_vocab_v20230424")
                self.meowAI.model=pipeline
            with open(configPath,'w') as f:f.write(json.dumps(self.config,indent=4))
            return json.dumps({'code': 0, 'msg': '模型重新载入成功'})

        @self.app.route('/')
        def index():
            return render_template('mai_setupButler/index.html')
        
        self.meowAPP.register_blueprint(self.app)
    
    def getModelsList(self,modelsFolder:Path)->List[Dict[str,str]]:
        modelInfoList=[]
        for file in modelsFolder.rglob('*.pth'):
            modelsinfo={
                "name":file.name.replace('.pth',''),
                "path":str(file.absolute()).replace('.pth','')
            }
            modelInfoList.append(modelsinfo)
        return modelInfoList

