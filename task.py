import os
import sys

from PyQt5 import uic
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QButtonGroup


class MapApi(QWidget):
    def __init__(self):
        super().__init__()
        self.map_file = "map.png"
        uic.loadUi('untitled.ui', self)
        self.initUI()


    def initUI(self):
        self.setWindowTitle('Отображение карты')
        self.pull_button.clicked.connect(self.getImage)
        self.label_error.setStyleSheet('color: red')
        self.radioButton_map.setChecked(True)
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.radioButton_map)
        self.button_group.addButton(self.radioButton_sat)
        self.button_group.addButton(self.radioButton_satskl)

        self.button_group.buttonClicked.connect(self._on_radio_button_clicked)

    def _on_radio_button_clicked(self, button):
        if button.text() == "Схема":
            self.type_map = "map"
            self.map_file = "map.png"
        elif button.text() == "Спутник":
            self.type_map = "sat"
            self.map_file = "map.jpg"
        elif button.text() == "Гибрид":
            self.type_map = "sat,skl"
            self.map_file = "map.jpg"
        self.getImage()

    def getImage(self):
        if self.error():
            return
        if self.lineEdit_x.text() and self.lineEdit_y.text():
            if float(self.lineEdit_spn.text()) > 1:
                self.lineEdit_spn.setText('1')
            elif float(self.lineEdit_spn.text()) < 0.001:
                self.lineEdit_spn.setText('0.001')

            if float(self.lineEdit_x.text()) > 180.0:
                self.lineEdit_x.setText('-179.999')
            elif float(self.lineEdit_x.text()) < -180.0:
                self.lineEdit_x.setText('179.999')

            if float(self.lineEdit_y.text()) > 85.0:
                self.lineEdit_y.setText('85.0')
            elif float(self.lineEdit_y.text()) < -85.0:
                self.lineEdit_y.setText('-85.0')

            map_request = f"http://static-maps.yandex.ru/1.x/?ll={self.lineEdit_x.text()}," \
                          f"{self.lineEdit_y.text()}&spn={self.lineEdit_spn.text()}," \
                          f"{self.lineEdit_spn.text()}&l={self.type_map}"
            response = requests.get(map_request)

            if not response:
                print("Ошибка выполнения запроса:")
                print(map_request)
                print("Http статус:", response.status_code, "(", response.reason, ")")
                sys.exit(1)

            # Запишем полученное изображение в файл.

            with open(self.map_file, "wb") as file:
                file.write(response.content)
            print(self.map_file)
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
        elif event.key() == Qt.Key_Up:
            self.lineEdit_y.setText(str(round(float(self.lineEdit_y.text())
                                              + 1.6 * float(self.lineEdit_spn.text()), 6)))
            self.getImage()
        elif event.key() == Qt.Key_Down:
            self.lineEdit_y.setText(str(round(float(self.lineEdit_y.text())
                                              - 1.6 * float(self.lineEdit_spn.text()), 6)))
            self.getImage()
        elif event.key() == Qt.Key_Left:
            self.lineEdit_x.setText(str(round(float(self.lineEdit_x.text())
                                              - 4 * float(self.lineEdit_spn.text()), 6)))
            self.getImage()
        elif event.key() == Qt.Key_Right:
            self.lineEdit_x.setText(str(round(float(self.lineEdit_x.text())
                                              + 4 * float(self.lineEdit_spn.text()), 6)))
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
