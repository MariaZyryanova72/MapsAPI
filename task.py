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
        self.type_map = "map"
        self.search_flag = False
        uic.loadUi('untitled.ui', self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Отображение карты')

        self.label_error.setStyleSheet('color: red')
        self.radioButton_map.setChecked(True)
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.radioButton_map)
        self.button_group.addButton(self.radioButton_sat)
        self.button_group.addButton(self.radioButton_satskl)

        self.button_group.buttonClicked.connect(self.on_radio_button_clicked)
        self.pull_button.clicked.connect(self.setImage)
        self.button_obj.clicked.connect(self.onClickSearch)

    def on_radio_button_clicked(self, button):
        if button.text() == "Схема":
            self.type_map = "map"
            self.map_file = "map.png"
        elif button.text() == "Спутник":
            self.type_map = "sat"
            self.map_file = "map.jpg"
        elif button.text() == "Гибрид":
            self.type_map = "sat,skl"
            self.map_file = "map.jpg"
        self.setImage()

    def getObj(self):
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": self.lineEdit_obj.text(),
            "format": "json"
        }
        response = requests.get(geocoder_api_server, params=geocoder_params)
        if not response:
            pass

        json_response = response.json()

        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"]
        if len(toponym) != 0:
            toponym_coodrinates = toponym[0]["GeoObject"]["Point"]["pos"]
            toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
            map_params = {
                "ll": f"{toponym_longitude},{toponym_lattitude}",
                "l": self.type_map,
                "spn": f"{self.lineEdit_spn.text()},{self.lineEdit_spn.text()}",
                "pt": f"{toponym_longitude},{toponym_lattitude},pm2al"
            }

            return map_params
        return ''

    def onClickSearch(self):
        self.search_flag = self.lineEdit_obj.text() != ''
        self.setImage()

    def getMap(self):
        self.check_pos()
        if self.lineEdit_x.text() and self.lineEdit_y.text():
            map_params = {
                "ll": f"{self.lineEdit_x.text()},{self.lineEdit_y.text()}",
                "l": self.type_map,
                "spn": f"{self.lineEdit_spn.text()},{self.lineEdit_spn.text()}"
            }
            return map_params

    def setImage(self):
        if self.error():
            return
        if self.search_flag:
            map_params = self.getObj()
            if map_params == '':
                self.label_error.setText('Объект не найден!')
                return
        else:
            map_params = self.getMap()
        self.label_error.setText('')
        response = requests.get("http://static-maps.yandex.ru/1.x/", params=map_params)

        if not response:
            print("Ошибка выполнения запроса:")
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
            self.setImage()
        elif event.key() == Qt.Key_PageDown:
            self.lineEdit_spn.setText(str(round(float(self.lineEdit_spn.text()) - 0.01, 6)))
            self.setImage()
        elif event.key() == Qt.Key_Up:
            self.lineEdit_y.setText(str(round(float(self.lineEdit_y.text())
                                              + 1.6 * float(self.lineEdit_spn.text()), 6)))
            self.setImage()
        elif event.key() == Qt.Key_Down:
            self.lineEdit_y.setText(str(round(float(self.lineEdit_y.text())
                                              - 1.6 * float(self.lineEdit_spn.text()), 6)))
            self.setImage()
        elif event.key() == Qt.Key_Left:
            self.lineEdit_x.setText(str(round(float(self.lineEdit_x.text())
                                              - 4 * float(self.lineEdit_spn.text()), 6)))
            self.setImage()
        elif event.key() == Qt.Key_Right:
            self.lineEdit_x.setText(str(round(float(self.lineEdit_x.text())
                                              + 4 * float(self.lineEdit_spn.text()), 6)))
            self.setImage()

    def check_pos(self):
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

    def error(self):
        try:
            float(self.lineEdit_x.text())
            float(self.lineEdit_y.text())
            float(self.lineEdit_spn.text())
        except Exception as e:
            print(e)
            self.label_error.setText('Координаты или масштаб введены неверно!')
            return True
        return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    map_api = MapApi()
    map_api.show()
    sys.exit(app.exec())
