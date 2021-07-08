import os
import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator, QSettings, QCoreApplication

import Handlers as hs
import res_rc


class Main_window(hs.main_window.MainWindow):
    def __init__(self):
        super().__init__()


def check_folders():
    if not os.path.isdir(str(Path.home() / "Downloads/YouTube")):
        os.mkdir(str(Path.home() / "Downloads/YouTube"))
    if not os.path.isdir(os.getenv('APPDATA') + '\\Youtube DM'):
        os.mkdir(os.getenv('APPDATA') + '\\Youtube DM')
    if not os.path.isdir(os.getenv('APPDATA') + '\\Youtube DM\\temp'):
        os.mkdir(os.getenv('APPDATA') + '\\Youtube DM\\temp')


def get_language():
    settings = QSettings('YouTube DM', 'Configs')
    if not (settings.contains('save_path')):
        settings.setValue('save_path', str(Path.home() / "Downloads/YouTube"))
    if settings.contains('language'):
        return settings.value('language')
    else:
        settings.setValue('language', 'UZ')
        return 'UZ'


def restart():
    os.execv(sys.executable, ['python'] + sys.argv)


if __name__ == '__main__':
    try:
        check_folders()
        app = QApplication(sys.argv)
        lan = get_language()
        tr = QTranslator()
        if lan == 'RU':
            tr.load(":/mw_icons/ru.qm")
        app.installTranslator(tr)
        window = Main_window()
        window.showMaximized()
        window.restart.connect(restart)
        app.setStyle('Fusion')
        sys.exit(app.exec_())
    except Exception as er:
        with open("error.txt", "w+") as f:
            f.write(str(er))
