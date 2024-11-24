import sys
import os
import requests
import json
import websocket
import threading
import plyer
import re
import hnt
from PyQt5 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets

global_username=""
security_token=""

# Главное окно
class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        with open("style/style", "r") as s:
            style = s.read()

        self.lastmsg_by = {}
        self.data={"messages":""}
        self.lastMsgSenders = {}

        self.setStyleSheet(style)
        self.setWindowIcon(QtGui.QIcon("style/Quetzalcoatl.svg"))

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        self.TextMsg = NewKeysTextEdit()
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
                ::-webkit-scrollbar-thumb {
                    background: #FF9800; /* Цвет ползунка */
                    border-radius: 6px; /* Закругление углов */
                }
                ::-webkit-scrollbar-track {
                    background: #2E2E2E; /* Цвет фона полосы прокрутки */
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
        ac = ContactAddWindow()
        ac.exec_()

    def checkActive(self):
        if self.isActiveWindow():
            return True
        else:
            return False

    def hnt(self):
        w = hnt.Hentai()
        w.exec_()
    
    def Run(self, data, us):
        self.show()
        self.data = data
        self.username = us
        self.cnt = ""

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
        # QtCore.QTimer.singleShot(100, self.scroll_chat)
        
    def scroll_chat(self):
        js_code = "window.scrollTo(0, document.body.scrollHeight);"
        self.Chat.page().runJavaScript(js_code)

    def on_chat_load_finished(self):
        for i in range(len(self.data["messages"])-1):
            try:
                if self.data["messages"][i]["sender"] == self.data["messages"][i-1]["sender"]:
                    self.appendMSG(self.data["messages"][i], False)
                else:
                    self.appendMSG(self.data["messages"][i], True)
            except:
                self.appendMSG(self.data["messages"][i], True)
        QtCore.QTimer.singleShot(350, self.scroll_chat)
            

    def appendMSG(self, msg, Last=True):
        self.lastmsg_by = msg
        if msg["sender"] == self.cnt or (msg["sender"] == self.username and msg["receiver"] == self.cnt):
            color = "red" if msg["sender"] == self.cnt else "blue"
            links = self.extract_links(msg["text"])
            links_img = self.filter_image_links(links)
            img = str()
            if len(links_img) > 0:
                for i in links_img:
                    img += f"i = {json.dumps(i)};img = document.createElement('img');img.src = i;div.appendChild(img);"
            if Last:
                js_code = f"""
                    i = {json.dumps(msg)};
                    div = document.createElement('div');
                    p = document.createElement('p');
                    p.style.color = '{color}';
                    p.style.fontSize = '20px';
                    p.textContent = i.sender;
                    div.appendChild(p);
                    br = document.createElement('br');
                    textNode = document.createTextNode(i.text);
                    div.style.fontSize = '20px';
                    div.appendChild(textNode);
                    div.appendChild(br);
                    {img}
                    document.getElementById('chat').appendChild(div);
                    window.scrollTo(0, document.body.scrollHeight);
                """
            else:
                js_code = f"""
                    i = {json.dumps(msg)};
                    div = document.createElement('div');
                    br = document.createElement('br');
                    textNode = document.createTextNode(i.text);
                    div.style.fontSize = '20px';
                    div.appendChild(textNode);
                    div.appendChild(br);
                    {img}
                    document.getElementById('chat').appendChild(div);
                    window.scrollTo(0, document.body.scrollHeight);
                """
            self.lastMsgSenders[f"{self.cnt}"] = msg["sender"]
            self.Chat.page().runJavaScript(js_code)
    
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
            r = requests.post(f"{SERVER}/getmsg", json=q)
            if r.status_code == 200:
                print("Congratulations!!!")
                service.send_message(q)
            else:
                print("error get msg")

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Return:
            self.SendMessage()

    def AppendMessage(self, msg):
        self.lastmsg_by = msg
        if msg["sender"] == self.lastMsgSenders[self.cnt]:
            self.appendMSG(msg, False)
        else:
            self.appendMSG(msg)
        QtCore.QTimer.singleShot(250, self.scroll_chat)
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

# Модифицированный текст едит
class NewKeysTextEdit(QtWidgets.QTextEdit):
    def __init__(self):
        super().__init__()

    def keyPressEvent(self, e):
        key = e.key()
        if key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            mp.SendMessage()
        super().keyPressEvent(e)

# Окно для регистрации и входа
class LoginRegisterWindow():
    def __init__(self):
        self.window = QtWidgets.QWidget()
        self.window.setWindowTitle("Register")

        self.FirstName = QtWidgets.QLabel("Имя:")
        self.FirstNameEdit = QtWidgets.QLineEdit()

        self.LastName = QtWidgets.QLabel("Фамилия:")
        self.LastNameEdit = QtWidgets.QLineEdit()

        self.Username = QtWidgets.QLabel("Имя пользователя:")
        self.UsernameEdit = QtWidgets.QLineEdit()

        self.Password1 = QtWidgets.QLabel("Введите пароль:")
        self.Password1Edit = QtWidgets.QLineEdit()

        self.Password2 = QtWidgets.QLabel("Введите пароль ещё раз:")
        self.Password2Edit = QtWidgets.QLineEdit()

        self.Login = QtWidgets.QPushButton("Уже есть аккаунт")
        self.Login.setFont(QtGui.QFont("Arial", 14))

        self.Enter = QtWidgets.QPushButton("Зарегестрироваться")
        self.Enter.setFont(QtGui.QFont("Arial", 14))

        self.boss = QtWidgets.QVBoxLayout()

        self.fl = QtWidgets.QVBoxLayout()
        self.fl.addWidget(self.FirstName)
        self.fl.addWidget(self.FirstNameEdit)

        self.fl.addWidget(self.LastName)
        self.fl.addWidget(self.LastNameEdit)

        self.fl.addWidget(self.Username)
        self.fl.addWidget(self.UsernameEdit)

        self.fl.addWidget(self.Password1)
        self.fl.addWidget(self.Password1Edit)

        self.fl.addWidget(self.Password2)
        self.fl.addWidget(self.Password2Edit)

        self.bl = QtWidgets.QHBoxLayout()
        self.bl.addWidget(self.Login)
        self.bl.addWidget(self.Enter)

        self.boss.addLayout(self.fl)
        self.boss.addLayout(self.bl)

        self.Enter.clicked.connect(self.Reg)
        self.Login.clicked.connect(self.SetLogin)

        self.window.setLayout(self.boss)

    # Запуск
    def Run(self):
        self.window.show()

    # Приостановка
    def Stop(self):
        self.window.hide()

    # Смена на форму фхода
    def SetLogin(self):
        self.window.setWindowTitle("Login")

        self.FirstName.hide()
        self.FirstNameEdit.hide()
        self.LastName.hide()
        self.LastNameEdit.hide()
        self.Username.hide()
        self.UsernameEdit.hide()
        self.Password1.hide()
        self.Password1Edit.hide()
        self.Password2.hide()
        self.Password2Edit.hide()
        self.Login.hide()
        self.Enter.hide()
        
        self.LoginUsername = QtWidgets.QLabel("Имя пользователя:")
        self.LoginUsernameEdit = QtWidgets.QLineEdit()

        self.LoginPassword = QtWidgets.QLabel("Пароль:")
        self.LoginPasswordEdit = QtWidgets.QLineEdit()

        self.EnterLogin = QtWidgets.QPushButton("Войти")
        self.EnterLogin.setFont(QtGui.QFont("Arial", 14))

        self.SetRegisterBTN = QtWidgets.QPushButton("Нет аккаунта")
        self.SetRegisterBTN.setFont(QtGui.QFont("Arial", 14))

        self.fl.addWidget(self.LoginUsername)
        self.fl.addWidget(self.LoginUsernameEdit)

        self.fl.addWidget(self.LoginPassword)
        self.fl.addWidget(self.LoginPasswordEdit)

        self.bl.addWidget(self.SetRegisterBTN)
        self.bl.addWidget(self.EnterLogin)

        self.window.adjustSize()

        self.SetRegisterBTN.clicked.connect(self.SetRegister)
        self.EnterLogin.clicked.connect(self.Log)

    # Смена на форму регистрации
    def SetRegister(self):
        self.LoginUsername.hide()
        self.LoginUsernameEdit.hide()

        self.LoginPassword.hide()
        self.LoginPasswordEdit.hide()
        
        self.EnterLogin.hide()
        self.SetRegisterBTN.hide()

        self.window.setWindowTitle("Register")

        self.FirstName.show()
        self.FirstNameEdit.show()
        self.LastName.show()
        self.LastNameEdit.show()
        self.Username.show()
        self.UsernameEdit.show()
        self.Password1.show()
        self.Password1Edit.show()
        self.Password2.show()
        self.Password2Edit.show()
        self.Login.show()
        self.Enter.show()

        self.window.adjustSize()

    # Запрос на регистрацию
    def Reg(self):
        data = {
            "first_name": self.FirstNameEdit.text(),
            "last_name": self.LastNameEdit.text(),
            "username": self.UsernameEdit.text(),
            "password_1": self.Password1Edit.text(),
            "password_2": self.Password2Edit.text(),
        }

        r = requests.post(f"{SERVER}/reg", json=data)

        if r.status_code == 200:
            QtWidgets.QMessageBox.information(None, "Успешно!", "Вы зарегестрировались! Закройте это окно и войдите в аккаунт.")
            self.SetLogin()
        else:
            QtWidgets.QMessageBox.warning(None, "Ошибка", "Ошибка регистрации, проверьте введенные данные")
    
    # Запрос авторизации получения токена
    def Log(self):
        data = {
            "username": self.LoginUsernameEdit.text(),
            "password": self.LoginPasswordEdit.text(),
        }
        
        r = requests.get(f"{SERVER}/login", json=data)
        if r.status_code != 200:
            QtWidgets.QMessageBox.warning(None, "Ошибка", "Ошибка входа в аккаунт, проверьте введенные данные")
            return

        R_tocken = r.json()
        security_token = R_tocken["token"]
        print(security_token)

        r = requests.get(f"{SERVER}/msgs", json=R_tocken)
        if r.status_code == 200:
            with open("config.json", "w+") as file:
                q = {
                    "username": self.LoginUsernameEdit.text(),
                    "password": self.LoginPasswordEdit.text()
                }
                username = q["username"]
                q = json.dumps(q)
                file.write(q)
                self.window.close()

            global_username = username

            with open("token.txt", "w+") as file:
                file.write(R_tocken["token"])

            thread = threading.Thread(target=RunWS)
            thread.start()
            print("Websocket start")

            mp.Run(r.json(), username)
        else:
            QtWidgets.QMessageBox.warning(None, "Ошибка", "Ошибка входа в аккаунт, проверьте введенные данные")

# Добавление контакта
class ContactAddWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавление контакта")

        self.Label = QtWidgets.QLabel("Введите ник пользователя")
        self.Label.setFont(QtGui.QFont("Arial", 12))

        self.US = QtWidgets.QLineEdit()
        self.US.setFont(QtGui.QFont("Arial", 12))

        self.Send = QtWidgets.QPushButton("Отправить")
        self.Send.setFont(QtGui.QFont("Arial", 12))

        self.l = QtWidgets.QVBoxLayout()
        self.l.addWidget(self.Label)
        self.l.addWidget(self.US)
        self.l.addWidget(self.Send)

        self.setLayout(self.l)

        self.Send.clicked.connect(self.ReqAddContact)

    def ReqAddContact(self):
        with open("token.txt", "r") as file:
            token = file.read()

        q = {
            "option": self.US.text(),
            "token": token,
        }

        r = requests.post(f"{SERVER}/addcontact", json=q)
        if r.status_code == 200:
            print("Congratulations!!!")
            if mp.data["contacts"] == None:
                mp.data["contacts"] = []
            mp.data["contacts"].append({"name":mp.username, "contact":q["option"]})
            item = QtWidgets.QListWidgetItem(q["option"])  
            item.setIcon(QtGui.QIcon("style/user.svg"))
            mp.ListContact.addItem(item)
            self.hide()
            QtWidgets.QMessageBox.information(None, "Успешно", "Контакт добавлен")
        else:
            print("error add contact")
            QtWidgets.QMessageBox.warning(None, "Ошибка", "Контакт не добавлен")


# Служба сообщений на WebSocket
class ChatService():
    def __init__(self, username):
        with open("token.txt", "r") as file:
            tokenF = file.read()

        self.ws = websocket.WebSocketApp(f"{WS_SERVER}/ws?id={username}&token={tokenF}")
        self.ws.on_open = self.on_open
        self.ws.on_message = self.on_message
        self.ws.on_error = self.on_error
        self.ws.on_close = self.on_close

    def on_open(self, ws):
        print("WebSocket connection opened")

    def on_message(self, ws, message):
        print("Getting message", message)
        msg = json.loads(message)
        mp.AppendMessage(msg)
        with open("config.json", "r") as file:
            data = json.loads(file.read())
            username = data["username"]
        if msg["sender"] != username and mp.cnt != msg["sender"]:
            plyer.notification.notify( 
                message=f'{msg["text"]}',
                app_name='Quetzalcoatl',
                title=f'Новое сообщение от {msg["sender"]}', )

    def on_error(self, ws, error):
        print("WebSocket error:", error)

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed")

    def send_message(self, q):
        message = q
        if message:
            self.ws.send(json.dumps(message))
            mp.TextMsg.clear()

def RunWS():
    global service
    with open("config.json", "r") as file:
        data = json.loads(file.read())
        username = data["username"]
    service = ChatService(username)
    service.ws.run_forever()

# Запуск приложения
if __name__ == "__main__":
    with open("server_config.json", "r") as file:
        cng = json.loads(file.read())
        ADDR=cng["addr"]
        PROTO=cng["proto"]
        SERVER=f"{PROTO}://{ADDR}"
        WS_SERVER=f"ws://{ADDR}"

    app = QtWidgets.QApplication(sys.argv)

    global mp
    mp = MainApp()

    print("Client app is start")

    try: 
        with open("config.json", "r") as file:
            i = file.read()
            print(i)
        data = json.loads(i)

        r = requests.get(f"{SERVER}/login", json=data)

        R_tocken = r.json()
        security_token = R_tocken["token"]
        print(security_token)

        r = requests.get(f"{SERVER}/msgs", json=R_tocken)
        print(r.json())

        if r.status_code == 200:
            print("OK")
        else:
            print("Error get messages from server")

        global_username = data["username"]

        with open("token.txt", "w+") as file:
            file.write(R_tocken["token"])

        thread = threading.Thread(target=RunWS)
        thread.start()
        print("Websocket start")

        
        mp.Run(r.json(), data["username"])

    except FileNotFoundError:
        regForm = LoginRegisterWindow()
        regForm.Run()

    sys.exit(app.exec_())