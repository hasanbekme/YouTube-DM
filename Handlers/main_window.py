import os
import webbrowser
from PyQt5 import QtCore
from PyQt5.QtCore import QUrl, QCoreApplication, QSettings, pyqtSignal, QTranslator
from PyQt5.QtGui import QMovie, QIcon
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QApplication
from PyQt5.QtWidgets import QTableWidgetItem as ti
from pytube import YouTube

from Resources import Designs as ds
from models import Media
from .download_dialog import DownloadDialog
from .about_dialog import AboutDialog
from .utils import format_time, youtube_url_validation

lang = {'RU': 'Русский', 'UZ': "O'zbekcha"}
re_lang = {'Русский': 'RU', "O'zbekcha": "UZ"}


class MainWindow(QMainWindow, ds.main_window.Ui_MainWindow):
    restart = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.translator = QCoreApplication.translate
        self.trans = QtCore.QTranslator(self)
        self.settings = QSettings('YouTube DM', 'Configs')
        self.setupUi(self)
        self.resizeTables()

        self.setButtonEvents()
        self.load_browser()
        self.load_window_data()
        self.load_settings()
        self.setDownloadIcon()

    def show_about_dialog(self):
        self.ad = AboutDialog(self)
        self.ad.exec()

    def load_settings(self):
        self.default_path.setText(self.settings.value('save_path', type=str))
        self.languages.setCurrentText(lang[self.settings.value('language', type=str)])

    def change_language(self):
        if self.languages.currentText() != lang[self.settings.value('language')]:
            reply = QMessageBox.question(self, "YouTube DM", self.tr("Dastur tilini o'zgartirmoqchimisiz?"),
                                         QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.No:
                self.languages.setCurrentText(lang[self.settings.value('language', type=str)])
            else:
                self.settings.setValue('language', re_lang[self.languages.currentText()])
                self.restart.emit()

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.LanguageChange:
            self.retranslateUi(self)
        super(MainWindow, self).changeEvent(event)

    def tr(self, text):
        return self.translator('MainWindow', text)

    def open_media(self):
        if self.tw.item(self.tw.currentRow(), 0) is not None:
            path = self.tw.item(self.tw.currentRow(), 1).text()
            name = self.tw.item(self.tw.currentRow(), 2).text()
            total = '"' + path + '/' + name + '"'
            try:
                os.startfile(total, 'open')
            except:
                QMessageBox.warning(self, self.tr("Xatolik"), self.tr("Bu fayl mavjud emas!"))
                Media.delete_by_id(self.tw.item(self.tw.currentRow(), 0).text())
                self.load_window_data()

    def remove_pr(self):
        if self.tw.item(self.tw.currentRow(), 0) is not None:
            id = self.tw.item(self.tw.currentRow(), 0).text()
            obj = Media.get(Media.id == id)
            obj.delete_instance()
            self.load_window_data()

    def open_in_folder_pr(self):
        if self.tw.item(self.tw.currentRow(), 0) is not None:
            path = self.tw.item(self.tw.currentRow(), 1).text()
            
            if os.name == 'nt':
                os.system('explorer ' + path.replace('/', '\\'))
            elif os.name == 'posix':
                os.system('explorer ' + path)

    def setDownloadIcon(self):
        self.dm = QMovie(':/mw_icons/download.gif')
        self.download_button.setIcon(QIcon(self.dm.currentPixmap()))
        self.dm.frameChanged.connect(lambda x: self.download_button.setIcon(QIcon(self.dm.currentPixmap())))

    def load_browser(self):
        self.browser.urlChanged.connect(self.changed)
        self.browser.load(QUrl("https://youtube.com/"))

    def return_home(self):
        self.browser.load(QUrl("https://youtube.com/"))

    def resizeTables(self):
        self.tw.setColumnHidden(0, True)
        self.tw.setColumnHidden(1, True)
        self.tw.setColumnWidth(2, 280)
        self.tw.setColumnWidth(3, 140)
        self.tw.setColumnWidth(4, 180)
        self.tw.setColumnWidth(5, 140)
        self.tw.setColumnWidth(6, 140)
        self.tw.setColumnWidth(7, 220)

    def open_download_dialog(self):
        try:
            self.v = YouTube(self.youtube_link.text())
            self.download_dialog = DownloadDialog(self.v, self)
            self.download_dialog.accepted.connect(self.load_window_data)
            self.download_dialog.exec_()
        except Exception as er:
            pass

    def setButtonEvents(self):
        self.feedback.pressed.connect(lambda: webbrowser.open("https://t.me/MR_prgmr"))
        self.about.pressed.connect(self.show_about_dialog)
        self.languages.currentTextChanged.connect(self.change_language)
        self.play.pressed.connect(self.open_media)
        self.remove.clicked.connect(self.remove_pr)
        self.open_in_folder.pressed.connect(self.open_in_folder_pr)
        self.exit.triggered.connect(self.close)
        self.web_back.pressed.connect(self.browser.back)
        self.web_forward.pressed.connect(self.browser.forward)
        self.link_direct.pressed.connect(self.set_vid_link)
        self.youtube_link.editingFinished.connect(self.set_vid_link)
        self.open_folder.pressed.connect(self.changeDefaultPath)
        self.bg.buttonClicked.connect(self.tab_events)
        self.bg2.buttonClicked.connect(self.load_window_data)
        self.download_button.pressed.connect(self.open_download_dialog)
        self.web_home.pressed.connect(self.return_home)

    def set_vid_link(self):
        if youtube_url_validation(self.youtube_link.text()):
            self.browser.setUrl(QUrl(self.youtube_link.text()))

    def closeEvent(self, e):
        reply = QMessageBox.question(self, "YouTube DM", self.tr("Dasturdan chiqishni hoxlaysizmi?"),
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
        else:
            e.ignore()

    def tab_events(self):
        tab_name = self.bg.checkedButton().objectName()
        if tab_name == 'youtube_tab':
            self.tabw.setCurrentIndex(0)
        elif tab_name == 'downloads_tab':
            self.tabw.setCurrentIndex(1)
        elif tab_name == 'settings_tab':
            self.tabw.setCurrentIndex(2)

    def changeDefaultPath(self):
        self.save_dir = QFileDialog.getExistingDirectory(self, self.tr("Manzilni tanlash"), './')
        if self.save_dir:
            self.default_path.setText(self.save_dir)
            self.settings.setValue('save_path', self.save_dir)

    def changed(self):
        self.youtube_link.setText(self.browser.url().toString())
        if youtube_url_validation(self.browser.url().toString()):
            self.dm.start()
        else:
            self.download_button.setIcon(QIcon())
            self.dm.stop()

    def write_data_tw(self, data):
        self.tw.setRowCount(0)
        for row in data:
            rc = self.tw.rowCount()
            self.tw.insertRow(rc)
            self.tw.setItem(rc, 0, ti(str(row.id)))
            self.tw.setItem(rc, 1, ti(row.Path))
            self.tw.setItem(rc, 2, ti(row.Name))
            self.tw.setItem(rc, 3, ti(f'{round(row.Size / 1024 ** 2, 1)} MB'))
            self.tw.setItem(rc, 4, ti(f'{format_time(row.Duration)}'))
            self.tw.setItem(rc, 5, ti(row.Type))
            self.tw.setItem(rc, 6, ti(row.Format))
            self.tw.setItem(rc, 7, ti(row.Date.strftime("%Y-%m-%d, %H:%M:%S")))

    def load_window_data(self):
        media_type = self.bg2.checkedButton().objectName()
        if media_type == 'video_audio':
            data = Media.select().order_by(Media.Date)
        elif media_type == 'only_video':
            data = Media.select().order_by(Media.Date).where(Media.Type == 'Video')
        else:
            data = Media.select().order_by(Media.Date).where(Media.Type == 'Audio')
        self.write_data_tw(data)
