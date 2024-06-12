from rwkv.model import RWKV
from rwkv.utils import PIPELINE
from meowServer import MeowAIServer,Character,MeowAI
from typing import List,Dict,Mapping,Union,Callable,Any
import torch,os,json
from pathlib import Path

os.environ['RWKV_JIT_ON'] = '1'
os.environ["RWKV_CUDA_ON"] = '0'

is_available='cuda fp16' if torch.cuda.is_available() else 'cpu fp32'
config=None
modelsFolder=""
modelFile=""
rootPath=Path(__file__).parent
configPath=rootPath.joinpath('config.json')

def getModelsList(modelsFolder:Path)->List[dict[str,str]]:
    modelInfoList=[]
    for file in modelsFolder.rglob('*.pth'):
        modelsinfo={
            "name":file.name.replace('.pth',''),
            "path":str(file.absolute()).replace('.pth','')
        }
        modelInfoList.append(modelsinfo)
    return modelInfoList

if not configPath.exists():raise FileNotFoundError(f"读取config.json失败,没有找到默认配置文件!\n请在项目根目录下创建config.json文件,并参照config.json.example文件填写配置项!\n配置文件路径:{configPath}")
with open(configPath,'r') as f:config = json.load(f)
modelsFolder=Path(config['modelsFolder'])
if not modelsFolder.exists():raise FileNotFoundError(f"读取models文件夹失败,没有找到models文件夹!\n请在项目根目录下创建models文件夹,并放入模型文件!\n配置文件路径:{modelsFolder}")
modelFile=modelsFolder.joinpath(config['modelFile'])
modelInfoList=getModelsList(modelsFolder)


if not os.path.exists(str(modelFile)+'.pth'):
    if len(modelInfoList)==0:raise FileNotFoundError(f"没有找到模型文件!\n请在项目根目录下创建models文件夹,并放入模型文件!\n配置文件路径:{modelsFolder}")
    print(f"模型文件不存在，请先下载{config['modelFile']}模型\n现将自动使用{modelInfoList[0]['name']}模型")
    modelFile=modelInfoList[0]['path']
    config["modelFile"]=modelInfoList[0]['name']

model = RWKV(model=str(modelFile), strategy=is_available)
pipeline = PIPELINE(model, "rwkv_vocab_v20230424")

meowAI=MeowAI(pipeline)
meowAIServer=MeowAIServer(meowAI,host=config['host'],port=config['port'],autoOpen=config['autoOpen'],debug=True)


if __name__ == '__main__':
    meowAIServer.run()

