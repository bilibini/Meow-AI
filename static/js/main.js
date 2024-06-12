const app = Vue.createApp({
    data() {
        return {
            users: {
                you: {
                    name: 'you',
                    avatar: '/static/img/bilibini.png',
                },
                other: {
                    name: 'MeowAI',
                    avatar: '/static/img/ai.png',
                }
            },
            coordinate: { x: 25, y: 35, isPC: true },
            persona: '主人你好呀！我是你的可爱猫娘，喵~',
            messages: [],
            //{type: 'you',content: '聊天内容',editMode: false,editedContent:'编辑内容'}
            socket: null,
            currentMessage: '',
            partialMessage: '',
            isDragging: false,//是否正在拖拽
            showStopButton: false,
            showContextMenu: false,
            showMoreSetup: -1,
            contextMenuIndex: -1,
            contextMenuPosition: { x: 0, y: 0 },
        };
    },
    mounted() {
        this.socket = io.connect('http://' + document.domain + ':' + location.port);
        this.socket.on('chat', (data) => {
            if (this.partialMessage != '') {
                this.messages.pop();
            }
            this.partialMessage += data;
            this.messages.push({ type: 'other', content: this.partialMessage, editMode: false, editedContent: '' });

            const endOfMessageIndex = this.partialMessage.indexOf('\n\n');
            if (endOfMessageIndex !== -1) {
                this.partialMessage = '';
                this.scrollToBottom();
                this.stopReply();
            }
        });
        this.socket.on('stop', (data) => {
            if (data == 'True' || data == true) {
                this.partialMessage = '';
                this.showStopButton = false;
            }
        });


    },
    computed: {
        messagesInfo() {
            const messagesInfo = {
                "Answerer": "Assistant",
                "messages": []
            };
            for (let message of this.messages) {
                messagesInfo.messages.push({
                    "role": message.type=='you'?"User":"Assistant",
                    "content": message.content,
                })
            }

            return messagesInfo;
        },
        characters() {
            if (!this.coordinate) {
                console.error("Coordinate is not defined!");
                return {"sense":1.1,"pizzazz":0.5};
            }
            
            let pizzazz = this.coordinate.x || 0.01;//top_p
            let sense = this.coordinate.y || 0.01;//temperature
            
            pizzazz=pizzazz<=50?pizzazz/50:(pizzazz-50)/5;
            sense=sense<=50?sense/50:(sense-50)/5;

            if (this.coordinate.isPC) {
                if (sense>=2&&pizzazz<=2){
                    pizzazz=pizzazz>1?pizzazz*0.2:pizzazz*0.5;
                }else if(pizzazz>=2&&sense<=2){
                    sense=sense>1?sense*0.2:sense*0.5;
                }else{
                    pizzazz=pizzazz>1?pizzazz*0.2:pizzazz*0.5;
                    sense=sense>1?sense*0.2:sense*0.5;
                }
                sense=sense*0.5;
                pizzazz=pizzazz*0.5;
            }

            console.log(this.coordinate.isPC, "pizzazz(top_p):",pizzazz,"sense(temperature):",sense);
            return { sense, pizzazz };
        },
    },
    methods: {
        sendMessage() {
            //发送消息
            const message = this.currentMessage.trim();
            if (message != '') {
                this.showStopButton = true;
                this.messages.push({ type: 'you', content: message, editMode: false, editedContent: '' });

                this.currentMessage = '';
                this.partialMessage = '';
                this.scrollToBottom();

                this.socket.emit('chat', this.messagesInfo);
                console.log(this.messagesInfo)
            }
        },
        setCharacter() {
            //设置性格
            this.socket.emit('character', {
                "persona": this.persona,
                "temperature": this.characters.sense,
                "top_p": this.characters.pizzazz,
            });
        },
        scrollToBottom() {
            //滚动到聊天消息底部
            const messagesContainer = document.getElementById('chat-messages');
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        },
        stopReply() {
            //停止对话
            this.socket.emit('stop', true);
        },
        resetReply() {
            //重新对话
            this.showStopButton = true;
            this.messages.pop();
            this.socket.emit('chat', this.messagesInfo);
            console.log(this.messagesInfo)
        },
        cutParagraphs(text) {
            //切断落
            return text.split('\n')
        },
        showContextMenuFun(index, event) {
            // 显示菜单
            this.showContextMenu = true;
            this.contextMenuIndex = index;
            this.contextMenuPosition = { x: event.offsetX + 55, y: event.offsetY };
        },
        hideContextMenuFun() {
            // 隐藏菜单
            this.showContextMenu = false;
            this.contextMenuIndex = -1;
        },
        copyMessage(index) {
            // 复制消息
            this.showContextMenu = false;
            navigator.clipboard.writeText(this.messages[index].content);
        },
        editMessage(index, event) {
            // 编辑消息
            this.messages[index].editMode = true;
            this.messages[index].editedContent = this.messages[index].content;
        },
        deleteMessage(index) {
            // 删除消息
            this.messages.splice(index, 1);
        },
        confirmEdit(index) {
            // 确认编辑
            this.messages[index].content = this.messages[index].editedContent;
            this.messages[index].editMode = false;
        },
        cancelEdit(index) {
            // 取消编辑
            this.messages[index].editMode = false;
        },
        autoResize(event) {
            //更新编辑框高度
            event.target.style.height = (event.target.scrollHeight - 20) + "px";
        },
        clickAvatarBox(typeAvatar) {
            //更换头像
            if (typeAvatar == 'you') {
                this.$refs.youAvatarToUpload.click();
            } else {
                this.$refs.otherAvatarToUpload.click();
            }
        },
        changeAvatarFile(typeAvatar) {
            //上传头像
            let file = typeAvatar == 'you' ? this.$refs.youAvatarToUpload.files[0] : this.$refs.otherAvatarToUpload.files[0];
            let thisf = this;
            if (file && file instanceof Blob) {
                const reader = new FileReader();
                reader.onloadend = function () {
                    const base64DataUrl = reader.result; // 获取到图片文件的Base64编码数据URL
                    typeAvatar == 'you' ? thisf.users.you.avatar = base64DataUrl + window.btoa('abc') : thisf.users.other.avatar = base64DataUrl;
                };
                reader.readAsDataURL(file); // 开始读取图片文件并转换成Base64格式
            } else {
                console.error("无效的图片文件");
            }
        },
        clickDownloadConfig() {
            //下载配置
            let config = {
                "persona": this.persona,
                "coordinate": this.coordinate,
                "characters": this.characters,
                "messages": this.messages,
                "users": this.users,
            }

            let file = new File([JSON.stringify(config)], 'meowAI.json', { type: 'text/plain' });
            this.$refs.downloadConfig.download = 'meowAI.json';
            this.$refs.downloadConfig.href = URL.createObjectURL(file);
            this.$refs.downloadConfig.click();
        },
        changeUploadConfig() {
            //上传配置
            let file = this.$refs.uploadConfig.files[0];
            let thisf = this;
            if (file && file instanceof Blob) {
                const reader = new FileReader();
                reader.onloadend = function () {
                    let configData = reader.result; // 获取到配置文件内容
                    configData = JSON.parse(configData);
                    thisf.persona = configData.persona;
                    thisf.coordinate = configData.coordinate;
                    thisf.messages = configData.messages;
                    thisf.users = configData.users;
                    thisf.showMoreSetup = -1;
                };
                reader.readAsText(file); // 开始读取配置文件
            } else {
                console.error("无效的配置文件");
            }
        },
        clickUploadConfig() {
            this.$refs.uploadConfig.click();
        },
        mousemoveCoordinate(e) {
            //拖动坐标
            const coordinateSystem = this.$refs.coordinateSystem;
            const draggablePoint = this.$refs.draggablePoint;
            if (this.isDragging) {
                const x = e.clientX - coordinateSystem.getBoundingClientRect().left - 10;
                const y = e.clientY - coordinateSystem.getBoundingClientRect().top - 10;
                const maxX = coordinateSystem.clientWidth - draggablePoint.clientWidth;
                const maxY = coordinateSystem.clientHeight - draggablePoint.clientHeight;
                const clampedX = Math.min(Math.max(0, x), maxX);
                const clampedY = Math.min(Math.max(0, y), maxY);

                this.coordinate.y = clampedY;
                this.coordinate.x = clampedX;
                // console.log(`X: ${clampedX}, Y: ${clampedY}`);
            }
        },
    },
});

app.mount('#app');