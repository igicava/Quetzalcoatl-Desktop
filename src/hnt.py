# Эксперементальная функция с хентаем
from PyQt5 import QtWidgets, QtCore, QtGui, QtWebEngineWidgets
import mdl

class Hentai(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        
        self.setWindowIcon(QtGui.QIcon("style/Quetzalcoatl.svg"))
        self.setWindowTitle("Quetzalcoatl")
        self.search = QtWidgets.QLineEdit()
        self.list = QtWidgets.QListWidget()
        self.browser = mdl.CustomWebEngineView()
        self.browser.setUrl(QtCore.QUrl("https://hentaimood.me"))

        self.l = QtWidgets.QHBoxLayout()
        self.l.addWidget(self.browser)

        self.setLayout(self.l)
        self.show()


        