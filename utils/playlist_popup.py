from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from db_functions import *



class PlaylistDialog(QtWidgets.QDialog):
    def __init__(self, data, title, parent=None):
        super().__init__(parent)
        self.data = data
        self.title = title

        self.setWindowTitle(f"Songs in {self.title}")
        self.setGeometry(550, 200, 500, 300)
        self.setMinimumSize(QtCore.QSize(500, 300))
        self.setMaximumSize(QtCore.QSize(500, 300))

        self.playlist_widget = QtWidgets.QListWidget(self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.playlist_widget)
        for song in self.data:
            self.playlist_widget.addItem(song)


        # Customize the popup
        # Hide Scrollbars
        self.playlist_widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.playlist_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Customize the font
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(120)
        self.playlist_widget.setFont(font)


        # Change Window Colors
        self.setStyleSheet(
            "background-color: rgb(10, 25, 47);"
        )
        self.playlist_widget.setStyleSheet(
            "color: rgb(86, 227, 194);\n"
            "background-color: rgba(0, 0, 0, 100);\n"
            "selection-background-color: rgb(255,255,255);\n"
            "selection-color: rgb(22, 16, 182);\n"
            "padding: 10px;\n"
        )


