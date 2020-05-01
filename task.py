import os
import sys

from PyQt5 import uic
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel


class MapApi(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('untitled.ui', self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Отображение карты')
        self.pull_button.clicked.connect(self.getImage)
        self.label_error.setStyleSheet('color: red')

    def getImage(self):
        if self.error():
            return
        if self.lineEdit_x.text() and self.lineEdit_y.text():
            if float(self.lineEdit_spn.text()) > 1:
                self.lineEdit_spn.setText('1')
            elif float(self.lineEdit_spn.text()) < 0.001:
                self.lineEdit_spn.setText('0.001')

            map_request = f"http://static-maps.yandex.ru/1.x/?ll={self.lineEdit_x.text()}," \
                          f"{self.lineEdit_y.text()}&spn={self.lineEdit_spn.text()}," \
                          f"{self.lineEdit_spn.text()}&l=map"
            response = requests.get(map_request)

            if not response:
                print("Ошибка выполнения запроса:")
                print(map_request)
                print("Http статус:", response.status_code, "(", response.reason, ")")
                sys.exit(1)

            # Запишем полученное изображение в файл.
            self.map_file = "map.png"
            with open(self.map_file, "wb") as file:
                file.write(response.content)
            self.pixmap = QPixmap(self.map_file)
            self.image.setPixmap(self.pixmap)

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)

    def keyPressEvent(self, event):
        if self.error():
            return
        if event.key() == Qt.Key_PageUp:
            self.lineEdit_spn.setText(str(round(float(self.lineEdit_spn.text()) + 0.01, 6)))
            self.getImage()
        elif event.key() == Qt.Key_PageDown:
            self.lineEdit_spn.setText(str(round(float(self.lineEdit_spn.text()) - 0.01, 6)))
            self.getImage()

    def error(self):
        try:
            float(self.lineEdit_x.text())
            float(self.lineEdit_y.text())
            float(self.lineEdit_spn.text())
        except Exception as e:
            print(e)
            self.label_error.setText('Координаты или масштаб введены неверно!')
            return True
        self.label_error.setText('')
        return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    map_api = MapApi()
    map_api.show()
    sys.exit(app.exec())
