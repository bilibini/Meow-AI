# AbaAba-AI
“阿巴阿巴AI”是基于RWKV的本地轻量级聊天AI

## 环境配置
推荐Python版本 3.9.18  
需要模块numpy、tokenizers、prompt_toolkit、transformers、flask、flask-socketio、torch  
`pip3 install numpy tokenizers prompt_toolkit transformers flask flask-socketio torch` 

## 运行要求
最低4G运行内存（CPU+4G内存，可以运行430m的小模型）  
最高不限（最高可运行14b的大模型，聊天质量和效果更加好）  

## 运行设置
根据自己电脑配置在模型网站（[https://huggingface.co/RWKV](https://huggingface.co/RWKV)）下载合适的模型 
下载的所有文件放在model文件夹内，并修改main.py第12行代码，将'rwkv-4-world-430m'修改为自己下载的模型文件夹  
运行main.py，在浏览器中打开http://172.0.0.1:5000 即可开始对话  

## 功能更新
- 2024-01-05：支持手动停止对话  
- 2024-01-19：支持编辑对话实现简单的手动微调  

## 演示效果
### 1. 普通对话聊天
该演示环境为CPU+4G运行内存，使用'rwkv-4-world-430m'模型  
![image](https://picshack.net/ib/JmNDSYUKX6.gif)
### 2. 持续对话聊天
该演示环境为CPU+28G运行内存，使用'rwkv-5-world-1b5'模型  
![image](https://picshack.net/ib/7c1jDPPjHO.gif)
### 3. 手动微调
该演示环境为CPU+28G运行内存，使用'rwkv-5-world-1b5'模型  
~注：手动添加修改更多的自己预设的对话，对后续的实现自己想要的聊天效果有很大帮助~  
![image](https://picshack.net/ib/pzpp41XVCG.gif)




## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=bilibini/AbaAba-AI&type=Date)](https://star-history.com/#bilibini/AbaAba-AI&Date)
