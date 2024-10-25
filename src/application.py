import sys
import os
import requests
import json
import websocket
import threading
from PyQt5 import QtCore, QtWidgets, QtGui

SERVER="http://45.66.228.76:8888"
global_username=""
security_token=""

# Главное окно
class MainApp():
    def __init__(self):
        self.Window = QtWidgets.QMainWindow()
        self.Window.setWindowTitle("Quetzalcoatl")

        central_widget = QtWidgets.QWidget()
        self.Window.setCentralWidget(central_widget)

        self.TextMsg = QtWidgets.QTextEdit()
        self.TextMsg.setFont(QtGui.QFont("Arial", 12))

        self.PushMsg = QtWidgets.QPushButton(">")
        self.PushMsg.setFont(QtGui.QFont("Arial", 14))

        self.Chat = QtWidgets.QTextBrowser()
        self.Chat.setFont(QtGui.QFont("Arial", 14))

        self.ListContact = QtWidgets.QListWidget()
        self.ListContact.setFont(QtGui.QFont("Arial", 11))

        self.menubar = QtWidgets.QMenuBar()
        self.menubar.setGeometry(QtCore.QRect(0, 0, 218, 26))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(self.menubar)
        self.menu_2.setObjectName("menu_2")
        self.Window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar()
        self.statusbar.setObjectName("statusbar")
        self.Window.setStatusBar(self.statusbar)
        self.action = QtWidgets.QAction()
        self.action.setObjectName("action")
        self.action_2 = QtWidgets.QAction()
        self.action_2.setObjectName("action_2")
        self.menu.addAction(self.action)
        self.menu.addAction(self.action_2)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())

        self.retranslateUi(self.Window)
        QtCore.QMetaObject.connectSlotsByName(self.Window)

        bl = QtWidgets.QHBoxLayout()

        ChatAndSendLayout = QtWidgets.QVBoxLayout()
        ContactsLayout = QtWidgets.QVBoxLayout()
        MSGLayout = QtWidgets.QHBoxLayout()

        ContactsLayout.addWidget(self.ListContact, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        ChatAndSendLayout.addWidget(self.Chat)
        MSGLayout.addWidget(self.TextMsg, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
        MSGLayout.addWidget(self.PushMsg)

        ChatAndSendLayout.addLayout(MSGLayout)
        bl.addLayout(ContactsLayout)
        bl.addLayout(ChatAndSendLayout)

        central_widget.setLayout(bl)

        self.Window.resize(1080, 560)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menu.setTitle(_translate("MainWindow", "Аккаунт"))
        self.menu_2.setTitle(_translate("MainWindow", "Справка"))
        self.action.setText(_translate("MainWindow", "Добавить контакт"))
        self.action_2.setText(_translate("MainWindow", "Выйти"))
    
    def Run(self, data, us):
        self.Window.show()
        self.Carray = []
        self.data = data
        self.username = us
        self.cnt = ""

        if data["messages"] != None:
            for i in data["messages"]:

                if i["sender"] in self.Carray or i["sender"] == us:
                    continue
                else:
                    item = QtWidgets.QListWidgetItem(i["sender"])  
                    item.setIcon(QtGui.QIcon("style/user.svg"))
                    self.ListContact.addItem(item)
                    self.Carray.append(i["sender"])

                if i["receiver"] in self.Carray or i["receiver"] == us:
                    continue
                else:
                    item = QtWidgets.QListWidgetItem(i["receiver"])
                    item.setIcon(QtGui.QIcon("style/user.svg"))
                    self.ListContact.addItem(item)
                    self.Carray.append(i["receiver"])

        self.ListContact.itemClicked.connect(self.clickContactInList)
        self.PushMsg.clicked.connect(self.SendMessage)
        # self.Chat.setText(json.dumps(data))

    def clickContactInList(self, item):
        self.cnt = item.text()
        self.Chat.clear()
        for i in self.data["messages"]:
            if i["sender"] == self.cnt or i["receiver"] == self.cnt:
                if i["sender"] == self.cnt:
                    self.Chat.append(f'<div><p style="color:red;font-size:11;">{i["sender"]}</p>\n{i["text"]}<br></div>')
                    QtCore.QTimer.singleShot(0, self.scroll_to_bottom)
                else:
                    self.Chat.append(f'<div><p style="color:blue;font-size:11;">{i["sender"]}</p>\n{i["text"]}<br></div>')
                    QtCore.QTimer.singleShot(0, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        # Прокручиваем вниз
        self.Chat.verticalScrollBar().setValue(self.Chat.verticalScrollBar().maximum())
    
    def SendMessage(self):
        with open("token.txt", "r") as file:
            token = file.read()

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

    def AppendMessage(self, msg):
        if msg["sender"] == self.cnt or (msg["sender"] == self.username and msg["receiver"] == self.cnt):
            if msg["sender"] == self.cnt:
                self.Chat.append(f'<div><p style="color:red;font-size:11;">{msg["sender"]}</p>\n{msg["text"]}<br></div>')
                QtCore.QTimer.singleShot(0, self.scroll_to_bottom)
            else:
                self.Chat.append(f'<div><p style="color:blue;font-size:11;">{msg["sender"]}</p>\n{msg["text"]}<br></div>')
                QtCore.QTimer.singleShot(0, self.scroll_to_bottom)
        self.data["messages"].append(msg)
        print(self.data)

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

# Служба сообщений на WebSocket
class ChatService():
    def __init__(self, username):
        with open("token.txt", "r") as file:
            tokenF = file.read()

        self.ws = websocket.WebSocketApp(f"ws://45.66.228.76:8888/ws?id={username}&token={tokenF}")
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
    service = ChatService(global_username)
    service.ws.run_forever()

# Запуск приложения
if __name__ == "__main__":
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