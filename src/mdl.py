import app
import json
import sys
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets
import service

class NewKeysTextEdit(QtWidgets.QTextEdit):
    def __init__(self):
        super().__init__()

    def keyPressEvent(self, e):
        key = e.key()
        if key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            mp.SendMessage()
        super().keyPressEvent(e)

class CustomWebEngineView(QtWebEngineWidgets.QWebEngineView):
    def createWindow(self, type):
        new_window = CustomWebEngineView()
        new_window.show()  # Показываем новое окно
        return new_window

global application
application = QtWidgets.QApplication(sys.argv)

global mp
mp = app.MainApp()

def RunWS():
    global service
    with open("config.json", "r") as file:
        data = json.loads(file.read())
        username = data["username"]
    service = service.ChatService(username)
    service.ws.run_forever()