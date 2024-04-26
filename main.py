from rwkv.model import RWKV
from rwkv.utils import PIPELINE
from server import MeowAIServer,Character,MeowAI
from typing import List,Dict,Mapping,Union,Callable,Any
import torch,os,json

os.environ['RWKV_JIT_ON'] = '1'
os.environ["RWKV_CUDA_ON"] = '0'

is_available='cuda fp16' if torch.cuda.is_available() else 'cpu fp32'
config=None
modelsFolder=""
modelFile=""

def getModelsList(modelsFolder:str)->List[Dict[str,str]]:
    modelInfoList=[]
    for dirname, dirnames, filenames in os.walk(modelsFolder):
        for filename in filenames:
            if '.pth' in filename:
                modelInfo={'name':filename.replace('.pth',''),'path':os.path.join(dirname, filename)}
                modelInfoList.append(modelInfo)
    return modelInfoList

if not os.path.exists(os.path.join(os.path.dirname(__file__),'config.json')):raise FileNotFoundError(f"读取config.json失败,没有找到默认配置文件!\n请在项目根目录下创建config.json文件,并参照config.json.example文件填写配置项!\n配置文件路径:{os.path.join(os.path.dirname(__file__),'config.json')}")
with open(os.path.join(os.path.dirname(__file__),'config.json'),'r') as f:config = json.load(f)
modelsFolder=os.path.abspath(config['modelsFolder'])
modelFile=os.path.join(modelsFolder,config['modelFile'])
modelInfoList=getModelsList(modelsFolder)


if not os.path.exists(modelFile+'.pth'):
    print(f"模型文件不存在，请先下载{config['modelFile']}模型\n将自动使用{modelInfoList[0]['name']}模型")
    modelFile=modelInfoList[0]['path']
    config["modelFile"]=modelInfoList[0]['name']

model = RWKV(model=modelFile, strategy=is_available)
pipeline = PIPELINE(model, "rwkv_vocab_v20230424")

meowAI=MeowAI(pipeline)
meowAIServer=MeowAIServer(meowAI,host=config['host'],port=config['port'],autoOpen=config['autoOpen'])


if __name__ == '__main__':
    meowAIServer.run()

