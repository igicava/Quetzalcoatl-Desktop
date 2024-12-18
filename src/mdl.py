import app
import json
import sys
from PySide6 import QtCore, QtWidgets, QtWebEngineWidgets
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
    global service_ws
    with open("config.json", "r") as file:
        data = json.loads(file.read())
        username = data["username"]
    service_ws = service.ChatService(username)
    service_ws.message_received.connect(mp.AppendMessage)
    service_ws.ws.run_forever()