import threading
import json
from PySide6 import QtWidgets, QtGui
import requests
import mdl

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

        r = requests.post(f"{mdl.SERVER}/reg", json=data)

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
        
        r = requests.get(f"{mdl.SERVER}/login", json=data)
        if r.status_code != 200:
            QtWidgets.QMessageBox.warning(None, "Ошибка", "Ошибка входа в аккаунт, проверьте введенные данные")
            return

        R_tocken = r.json()
        security_token = R_tocken["token"]
        print(security_token)

        r = requests.get(f"{mdl.SERVER}/msgs", json=R_tocken)
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

            thread = threading.Thread(target=mdl.RunWS)
            thread.start()
            print("Websocket start")

            mdl.mp.Run(r.json(), username)
        else:
            QtWidgets.QMessageBox.warning(None, "Ошибка", "Ошибка входа в аккаунт, проверьте введенные данные")
