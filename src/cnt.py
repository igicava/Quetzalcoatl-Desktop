import requests
from PySide6 import QtWidgets, QtGui
import mdl

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

        r = requests.post(f"{mdl.SERVER}/addcontact", json=q)
        if r.status_code == 200:
            print("Congratulations!!!")
            if mdl.mp.data["contacts"] == None:
                mdl.mp.data["contacts"] = []
            mdl.mp.data["contacts"].append({"name":mdl.mp.username, "contact":q["option"]})
            item = QtWidgets.QListWidgetItem(q["option"])  
            item.setIcon(QtGui.QIcon("style/user.svg"))
            mdl.mp.ListContact.addItem(item)
            self.hide()
            QtWidgets.QMessageBox.information(None, "Успешно", "Контакт добавлен")
        else:
            print("error add contact")
            QtWidgets.QMessageBox.warning(None, "Ошибка", "Контакт не добавлен")

