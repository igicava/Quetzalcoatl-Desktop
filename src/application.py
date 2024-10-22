import sys
import os
import requests
import json
import websocket
import threading
from PyQt5 import QtCore, QtWidgets, QtGui

SERVER="http://127.0.0.1:8888"
global_username=""
security_token=""

# Главное окно
class MainApp():
    def __init__(self):
        self.Window = QtWidgets.QWidget()
        self.Window.setWindowTitle("Quetzalcoatl")

        self.TextMsg = QtWidgets.QTextEdit()
        self.PushMsg = QtWidgets.QPushButton("Отправить сообщение")
        self.PushMsg.setFont(QtGui.QFont("Arial", 14))

        self.Chat = QtWidgets.QTextBrowser()
        self.ListContact = QtWidgets.QListWidget()

        bl = QtWidgets.QHBoxLayout()

        InputLayout = QtWidgets.QVBoxLayout()
        OutputLayout = QtWidgets.QVBoxLayout()
        ContactsLayout = QtWidgets.QVBoxLayout()

        InputLayout.addWidget(self.TextMsg)
        InputLayout.addWidget(self.PushMsg)

        OutputLayout.addWidget(self.Chat)

        ContactsLayout.addWidget(self.ListContact)

        bl.addLayout(InputLayout)
        bl.addLayout(OutputLayout)
        bl.addLayout(ContactsLayout)

        self.Window.setLayout(bl)
    
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
                    self.Carray.append(i["sender"])
                    self.ListContact.addItem(i["sender"])

                if i["receiver"] in self.Carray or i["receiver"] == us:
                    continue
                else:
                    self.Carray.append(i["receiver"])
                    self.ListContact.addItem(i["receiver"])

        self.ListContact.itemClicked.connect(self.clickContactInList)
        self.PushMsg.clicked.connect(self.SendMessage)
        # self.Chat.setText(json.dumps(data))

    def clickContactInList(self, item):
        self.cnt = item.text()
        self.Chat.clear()
        for i in self.data["messages"]:
            if i["sender"] == self.cnt or i["receiver"] == self.cnt:
                self.Chat.append(i["text"])
    
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
            self.Chat.append(msg["text"])
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

        self.ws = websocket.WebSocketApp(f"ws://localhost:8888/ws?id={username}&token={tokenF}")
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