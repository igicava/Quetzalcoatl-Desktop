# Эксперементальная функция с хентаем
import sys
from PyQt5 import QtWidgets, QtCore, QtGui, QtWebEngineWidgets
import requests

class CustomWebEngineView(QtWebEngineWidgets.QWebEngineView):
    def createWindow(self, type):
        new_window = CustomWebEngineView()
        new_window.show()  # Показываем новое окно
        return new_window

class Hentai(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        self.search = QtWidgets.QLineEdit()
        self.list = QtWidgets.QListWidget()
        self.browser = CustomWebEngineView()
        self.browser.setUrl(QtCore.QUrl("https://hentaimood.me/219057-boku-wa-kiwi-no-sayber-ya-tvoy-seyber.html"))

        self.l = QtWidgets.QHBoxLayout()
        self.l.addWidget(self.browser)

        self.setLayout(self.l)
        self.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    w = Hentai()
    sys.exit(app.exec_())

        