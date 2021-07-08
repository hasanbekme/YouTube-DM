from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QGraphicsDropShadowEffect

from Resources.Designs import about_dialog


class AboutDialog(QDialog, about_dialog.Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.pushButton.pressed.connect(self.close)
