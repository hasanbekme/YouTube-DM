from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import Qt, QCoreApplication, QSettings
from PyQt5.QtGui import QPixmap, QMovie, QIcon
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox

from Resources.Designs import download_dialog
from models import Media
from .threads import *
from .utils import *


class DownloadDialog(QDialog, download_dialog.Ui_Dialog):
    def __init__(self, mv, parent=None):
        super().__init__(parent)
        self.v = mv
        self.lth = LoadThread(mv)
        self.downloading = QMovie(':/mw_icons/downloading.gif')
        self.translator = QCoreApplication.translate
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.load_path()
        self.load_data()
        self.download_button.pressed.connect(self.download_clicked)
        self.open_folder.pressed.connect(self.select_folder)

    def tr(self, text):
        return self.translator('Dialog', text)

    def download_clicked(self):
        if self.download_button.text() == self.tr('Yuklash'):
            s_f = self.a_f.currentText().split(',')[0]
            if s_f in ['360p', '480p', '720p', '1080p']:
                filename = self.save_path.text() + '\\' + clear_name(self.title.text()) + ' ' + s_f + '.mp4'
                self.file_size = self.res['v_s'][s_f].filesize
                self.media_type = 'Video'
            else:
                self.media_type = 'Audio'
                filename = self.save_path.text() + '\\' + clear_name(self.title.text()) + '.mp3'
                self.file_size = self.res['a_s'].filesize
            self.file_name = filename

            self.download_button.setIcon(QIcon(self.downloading.currentPixmap()))
            self.downloading.frameChanged.connect(
                lambda x: self.download_button.setIcon(QIcon(self.downloading.currentPixmap())))
            self.downloading.start()
            self.download_button.setText(self.tr("Yuklanmoqda"))

            self.size_l.setText(f"{self.tr('Hajmi')}:  {format_size(self.file_size)}")
            self.progressBar.setHidden(False)
            self.a_f.setDisabled(True)
            self.download_button.setDisabled(True)
            self.open_folder.setDisabled(True)
            if self.media_type == 'Video':
                req = {'url_v': self.res['v_s'][s_f].url, 'url_a': self.res['a_s'].url, 'filename': filename}
                self.d_class = VideoDownloader(req)
            else:
                req = {'url_v': None, 'url_a': self.res['a_s'].url, 'filename': filename}
                self.d_class = AudioDownloader(req)
            self.d_class.data.connect(self.call_back)
            self.d_class.start()

        elif self.download_button.text() == self.tr('Ochish'):
            os.system("explorer " + self.save_path.text().replace('/', '\\'))

    def call_back(self, data):
        v = int(round(data['total_downloaded'] / self.file_size * 100))
        self.progressBar.setValue(v)
        self.downloaded_l.setText(f"{self.tr('Yuklandi')}:  {format_size(data['total_downloaded'])}, {v}%")
        self.speed_l.setText(F"{self.tr('Tezlik')}:  {format_size(data['speed'])}/s")
        if self.d_class.status == 1:
            self.downloading.stop()
            self.download_button.setIcon(QIcon(":/mw_icons/open.png"))
            self.download_button.setText(self.tr("Ochish"))
            self.download_button.setDisabled(False)
            try:
                Media.create(Name=self.file_name.split("\\")[-1], Path=self.save_path.text(), Duration=self.v.length,
                             Size=self.file_size, Type=self.media_type, Format=self.a_f.currentText().split(',')[0],
                             Date=datetime.now())
            except:
                pass

    def closeEvent(self, e):
        try:
            if self.lth.isRunning():
                self.lth.terminate()
        except:
            pass
        try:
            if self.d_class.isRunning():
                reply = QMessageBox.question(self, self.tr("Ogohlantirish"), self.tr("Yuklashni bekor qilasizmi?"),
                                             QMessageBox.Yes, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.d_class.dr.stop()
                    self.d_class.terminate()
                    e.accept()
                else:
                    e.ignore()
                    return None
        except:
            pass
        self.accept()

    def load_data(self):
        self.title.setHidden(True)
        self.progressBar.setHidden(True)
        self.setMaximumHeight(209)
        self.loading = QMovie(":/mw_icons/loading.gif")
        self.thumbnail.setMovie(self.loading)
        self.loading.start()
        self.lth.data.connect(self.write_data)
        self.lth.start()

    def write_data(self, res):
        self.res = res
        self.title.setText(res['title'])
        self.length_l.setText(f"{self.tr('Davomiyligi')}: {format_time(self.v.length)}")
        v_thumbnail = QPixmap()
        v_thumbnail.loadFromData(res['thumbnail'])
        self.thumbnail.setPixmap(v_thumbnail)
        v_icon = QIcon(':/mw_icons/video_format.png')
        a_icon = QIcon(':/mw_icons/audio_format.png')
        d = 1024 ** 2
        for i, v in res['v_s'].items():
            self.a_f.addItem(v_icon, f"{i}, {format_size(v.filesize + res['a_s'].filesize)}")
        if res['a_s'] is not None:
            self.a_f.addItem(a_icon, f"Audio, {round(res['a_s'].filesize / d, 2)} MB")
        self.title.setHidden(False)
        self.loading.stop()

    def load_path(self):
        settings = QSettings('YouTube DM', 'Configs')
        self.save_path.setText(settings.value('save_path', type=str))

    def select_folder(self):
        self.save_dir = QFileDialog.getExistingDirectory(self, self.tr("Manzilni tanlash"), './')
        if self.save_dir:
            self.save_path.setText(self.save_dir)
