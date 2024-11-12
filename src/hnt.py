# Эксперементальная функция с хентаем
from PyQt5 import QtWidgets, QtCore, QtGui


class Hentai(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.search = QtWidgets.QLineEdit()
        self.list = QtWidgets.QListWidget()
        