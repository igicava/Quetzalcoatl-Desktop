# Эксперементальная функция с хентаем
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import requests

class Hentai(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        r = requests.get("http://hentasis1.top/982-iribitari-gal-ni-manko.html")
        self.search = QtWidgets.QLineEdit()
        self.list = QtWidgets.QListWidget()
        self.browser = QtWidgets.QTextBrowser()
        self.browser.setText(r.text)

        self.l = QtWidgets.QHBoxLayout()
        self.l.addWidget(self.browser)

        self.setLayout(self.l)
        self.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    w = Hentai()
    sys.exit(app.exec_())

        