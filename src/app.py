import re
import json
import requests
from PyQt5 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets
import cnt
import hnt
import mdl

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        with open("style/style", "r") as s:
            style = s.read()

        self.data={"messages":""}
        # self.lastMsgSenders = {}

        self.setStyleSheet(style)
        self.setWindowIcon(QtGui.QIcon("style/Quetzalcoatl.svg"))

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        self.TextMsg = mdl.NewKeysTextEdit()
        # keyboard.on_press_key('enter', self.SendMessage)
        self.TextMsg.setFont(QtGui.QFont("Arial", 12))

        self.PleaseSelectContact = QtWidgets.QLabel("Выбирай контакт с боку или добавляй новый!")
        self.PleaseSelectContact.setFont(QtGui.QFont("Arial", 12))

        self.PushMsg = QtWidgets.QPushButton("\n>\n")
        self.PushMsg.setFont(QtGui.QFont("Arial", 14))

        self.Chat = QtWebEngineWidgets.QWebEngineView()
        self.Chat.loadFinished.connect(self.on_chat_load_finished)
        self.html = '''
        <html>
        <head>
            <style>
                body {
                    scrollbar-width: thin;
                    scrollbar-color: #2E2E2E black;
                }
            </style>
        </head>
        <body id="chat" style="background-color:#2E2E2E;color:white"></body>
        </html>
        '''
        base_i = "let i;let div;let p;let br;let textNode"
        self.Chat.page().runJavaScript(base_i)
        self.Chat.setHtml(self.html)
        # self.Chat.textChanged.connect(self.scroll_to_bottom_update)

        self.ListContact = QtWidgets.QListWidget()
        self.ListContact.setFont(QtGui.QFont("Arial", 14))

        self.menubar = QtWidgets.QMenuBar()
        self.menubar.setGeometry(QtCore.QRect(0, 0, 218, 26))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(self.menubar)
        self.menu_2.setObjectName("menu_2")
        self.menu_3 = QtWidgets.QMenu(self.menubar)
        self.menu_3.setObjectName("menu_3")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar()
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.action = QtWidgets.QAction()
        self.action.setObjectName("action")
        self.action_2 = QtWidgets.QAction()
        self.action_2.setObjectName("action_2")
        self.action_3 = QtWidgets.QAction()
        self.setObjectName("action_3")
        self.menu.addAction(self.action)
        self.menu.addAction(self.action_2)
        self.menu_3.addAction(self.action_3)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())
        self.menubar.addAction(self.menu_3.menuAction())

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        bl = QtWidgets.QHBoxLayout()

        ChatAndSendLayout = QtWidgets.QVBoxLayout()
        ContactsLayout = QtWidgets.QVBoxLayout()
        MSGLayout = QtWidgets.QHBoxLayout()

        ContactsLayout.addWidget(self.ListContact, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        ChatAndSendLayout.addWidget(self.PleaseSelectContact, alignment=QtCore.Qt.AlignmentFlag.AlignVCenter)
        ChatAndSendLayout.addWidget(self.Chat)
        MSGLayout.addWidget(self.TextMsg, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
        MSGLayout.addWidget(self.PushMsg)
        self.Chat.hide()
        self.TextMsg.hide()
        self.PushMsg.hide()

        ChatAndSendLayout.addLayout(MSGLayout)
        bl.addLayout(ContactsLayout)
        bl.addLayout(ChatAndSendLayout)

        self.action.triggered.connect(self.AddContact)
        self.action_3.triggered.connect(self.hnt)
        self.addAction(self.action)
        self.addAction(self.action_3)

        central_widget.setLayout(bl)

        self.resize(1080, 560)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.menu.setTitle(_translate("MainWindow", "Аккаунт"))
        self.menu_2.setTitle(_translate("MainWindow", "Справка"))
        self.action.setText(_translate("MainWindow", "Добавить контакт"))
        self.action_2.setText(_translate("MainWindow", "Выйти"))
        self.menu_3.setTitle(_translate("MainWindow", "Экспирементальные функции"))
        self.action_3.setText(_translate("MainWindow", "Хентай манга и додзинси"))

    def AddContact(self):
        ac = cnt.ContactAddWindow()
        ac.exec_()

    def hnt(self):
        w = hnt.Hentai()
        w.exec_()
    
    def Run(self, data, us):
        self.show()
        self.data = data
        self.username = us
        self.cnt = "none"

        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", f"Quetzalcoatl - {self.username}"))

        if data["contacts"] != None:
            for i in data["contacts"]:
                item = QtWidgets.QListWidgetItem(i["contact"])  
                item.setIcon(QtGui.QIcon("style/user.svg"))
                self.ListContact.addItem(item)

        if data["messages"] != None:
            self.lastmsg_by = data["messages"][(len(data["messages"])-1)]

        self.ListContact.itemClicked.connect(self.clickContactInList)
        self.PushMsg.clicked.connect(self.SendMessage)
        # self.Chat.setText(json.dumps(data))

    def extract_links(self, text):
        """
        Извлекает ссылки из текста и возвращает их в виде списка.
        
        :param text: строка, содержащая текст с возможными ссылками
        :return: список ссылок
        """
        # Регулярное выражение для поиска URL
        url_pattern = r'https?://[^\s]+'
        # Находим все совпадения
        links = re.findall(url_pattern, text)
        return links
    
    def filter_image_links(self, links):
        """
        Фильтрует ссылки, указывающие на изображения, включая ссылки с параметрами.
        
        :param links: список ссылок
        :return: список ссылок, ведущих на изображения
        """
        # Регулярное выражение для поиска файлов изображений с учетом параметров
        image_pattern = r'\.(jpg|jpeg|png|gif|bmp|webp|tiff)(\?.*)?$'
        
        # Фильтруем ссылки, которые содержат расширения изображений
        image_links = [link for link in links if re.search(image_pattern, link, re.IGNORECASE)]
        
        return image_links

    def clickContactInList(self, item):
        self.cnt = item.text()
        self.Chat.setHtml(self.html)
        self.PleaseSelectContact.hide()
        self.Chat.show()
        self.TextMsg.show()
        self.PushMsg.show()
        if self.data["messages"] != None:
            for i in self.data["messages"]:
                self.appendMSG(i)
        
    def scroll_chat(self):
        js_code = "window.scrollTo(0, document.body.scrollHeight);"
        self.Chat.page().runJavaScript(js_code)

    def on_chat_load_finished(self):
        if self.data["messages"] != None:
            for i in self.data["messages"]:
                self.appendMSG(i)
            
    def append_images_msg(self, links):
        for i in links:
            js_code = f"""
            i = {json.dumps(i)}
            img = document.createElement('img');img.src = i;document.getElementById('chat').appendChild(img);
            window.scrollTo(0, window.outerHeight);
            """
            self.Chat.page().runJavaScript(js_code)

    def appendMSG(self, msg):
        self.lastmsg_by = msg
        if msg["sender"] == self.cnt or (msg["sender"] == self.username and msg["receiver"] == self.cnt):
            color = "red" if msg["sender"] == self.cnt else "blue"
            js_code = f"""
                i = {json.dumps(msg)};
                div = document.createElement('div');
                p = document.createElement('p');
                p.style.color = '{color}';
                p.style.fontSize = '20px';
                p.textContent = i.sender;
                div.appendChild(p);
                br = document.createElement('br');
                div.appendChild(br);
                textNode = document.createTextNode(i.text);
                div.style.fontSize = '20px';
                div.appendChild(textNode);
                div.appendChild(br);
                document.getElementById('chat').appendChild(div);
                window.scrollTo(0, document.body.scrollHeight);
            """
            self.Chat.page().runJavaScript(js_code)
            links = self.extract_links(msg["text"])
            links_img = self.filter_image_links(links)
            if len(links_img) > 0:
                self.append_images_msg(links_img)
    
    def SendMessage(self):
        with open("token.txt", "r") as file:
            token = file.read()

        if len(self.TextMsg.toPlainText().strip()) > 0:
            q = {
                "receiver": self.cnt,
                "sender": self.username,
                "text": self.TextMsg.toPlainText(),
                "token": token,
            }
            r = requests.post(f"{mdl.SERVER}/getmsg", json=q)
            if r.status_code == 200:
                print("Congratulations!!!")
                mdl.service.send_message(q)
            else:
                print("error get msg")

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Return:
            self.SendMessage()

    def AppendMessage(self, msg):
        self.lastmsg_by = msg
        self.appendMSG(msg)
        if self.data["contacts"] == None:
            self.data["contacts"] = []
        if {"name":self.username, "contact":msg["sender"]} in self.data["contacts"] or msg["sender"] == self.username:
            pass
        else:
            self.data["contacts"].append({"name":self.username, "contact":msg["sender"]})
            item = QtWidgets.QListWidgetItem(msg["sender"])  
            item.setIcon(QtGui.QIcon("style/user.svg"))
            self.ListContact.addItem(item)

        if self.data["messages"] == None:
            self.data["messages"] = []
        self.data["messages"].append(msg)

        print(self.data)
