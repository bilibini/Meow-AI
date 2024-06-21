# Meow-AI
“Meow-AI”是基于RWKV的本地轻量级聊天AI

## 环境配置
推荐Python版本 3.9.18  
需要模块numpy、tokenizers、prompt_toolkit、flask、flask-socketio、torch、subprocess  
`pip3 install numpy tokenizers prompt_toolkit flask flask-socketio torch subprocess` 

## 运行要求
最低4G运行内存（CPU+4G内存，可以运行430m的小模型）  
最高不限（最高可运行14b的大模型，聊天质量和效果更加好）  

## 运行设置
根据自己电脑配置在模型网站（[https://huggingface.co/BlinkDL](https://huggingface.co/BlinkDL)）下载合适的模型 （[镜像网址](https://hf-mirror.com/BlinkDL)） 
下载的所有文件放在models文件夹内，并修改config.json中的“modelFile”，将'RWKV-x060-World-1B6-v2-20240208-ctx4096'修改为自己下载的模型名  
运行main.py，在浏览器中打开http://172.0.0.1:5000 即可开始对话  

## 功能更新
- 2024-01-05：支持手动停止对话  
- 2024-01-19：支持编辑对话实现简单的手动微调  
- 2024-01-23：支持配置导入/导出，支持自定义AI性格人设
- 2024-03-01：完全使用RWKV架构，实现更小的模型体积，降低运行内存和CPU占用
- 2024-04-26：优化整体架构
- 2024-06-21：支持扩展功能，支持微信自动聊天  

## 演示效果
### 1. 持续对话
该演示环境为GPU+8G，使用'RWKV-5-World-3B-v2-20231118-ctx16k'模型  
![image](https://img.z4a.net/images/2024/06/12/9067bcfab67bb37a3c012ccca84b39be.png)
### 2. 手动调整对话
~注：手动添加修改更多的自己预设的对话，对后续的实现自己想要的聊天效果有很大帮助~  
![image](https://img.z4a.net/images/2024/06/12/c21bbf309e8836a2f420a2e9aa430805.png)
### 3. 配置导入导出
可以导入导出对话以及配置信息  
![image](https://img.z4a.net/images/2024/06/12/827ad26b2bfd9c31897b75081133d307.png)
### 4. 调教AI人设性格
可以自定义设置MeowAI人设性格，让MeowAI更加符合自己的喜好  
![image](https://img.z4a.net/images/2024/06/12/Meow.gif)
### 4. 扩展功能
支持添加自定义扩展功能，目前已完成“微信自动聊天”  
![image](https://img.z4a.net/images/2024/06/12/Meow.gif)

## 未来展望
1. 完成更多扩展功能
2. 实现本地一键 懒人包，不用配置环境一键启动即可运行  
3. 待续……    


## Star History
[![Star History Chart](https://api.star-history.com/svg?repos=bilibini/Meow-AI&type=Date)](https://star-history.com/#bilibini/Meow-AI&Date)

