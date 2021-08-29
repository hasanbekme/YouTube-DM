import requests
from PyQt5.QtCore import QThread, pyqtSignal
from pget import Downloader

from .utils import *


class VideoDownloader(QThread):
    data = pyqtSignal(dict)

    def __init__(self, val):
        super(VideoDownloader, self).__init__()
        self.filename = val['filename']
        self.v = prepare_temp() + '\\video.mp4'
        self.a = prepare_temp() + '\\audio.webm'
        self.dr = Downloader(val['url_v'], self.v, 8)
        self.md = Downloader(val['url_a'], self.a, 8)
        self.status = 0

    def terminate(self):
        self.dr.stop()
        self.md.stop()
        super(VideoDownloader, self).terminate()

    def run(self):
        self.dr.start()
        self.md.start()
        self.dr.subscribe(self.call_back)
        self.dr.wait_for_finish()
        self.md.wait_for_finish()
        self.merge_data()
        self.status = 1
        self.call_back(1, 2, 3)

    def call_back(self, *args):
        res = {'total_downloaded': self.dr.total_downloaded, 'speed': self.dr.speed, 'status': self.status}
        self.data.emit(res)

    def merge_data(self):
        print("Filename: "+self.filename)
        print("Video stream: "+self.v)
        print("Audio Stream: "+self.a)
        command = f"""ffmpeg\\nt\\bin\\ffmpeg.exe -i  "{self.v}" -i "{self.a}" -c:v copy -c:a aac "{self.filename}" """
        #command = f"""ffmpeg -i  "{self.v}" -i "{self.a}" -c:v copy -c:a copy "{self.filename}" """
        os.system(command)


class AudioDownloader(QThread):
    data = pyqtSignal(dict)

    def __init__(self, val):
        super(AudioDownloader, self).__init__()
        self.dr = Downloader(val['url_a'], val['filename'], 8)
        self.status = 0

    def terminate(self):
        self.dr.stop()
        super(AudioDownloader, self).terminate()

    def run(self):
        self.dr.start()
        self.dr.subscribe(self.call_back)
        self.dr.wait_for_finish()
        self.status = 1
        self.call_back(1, 2, 3)

    def call_back(self, *args):
        res = {'total_downloaded': self.dr.total_downloaded, 'speed': self.dr.speed, 'status': self.status}
        self.data.emit(res)


class LoadThread(QThread):
    data = pyqtSignal(dict)

    def __init__(self, mv):
        super(LoadThread, self).__init__()
        self.v = mv

    def get_video_streams(self):
        m_s = self.m_s
        v_1080 = m_s.filter(resolution='1080p', mime_type='video/mp4')
        v_720 = m_s.filter(resolution='720p', mime_type='video/mp4')
        v_480 = m_s.filter(resolution='480p', mime_type='video/mp4')
        v_360 = m_s.filter(resolution='360p', mime_type='video/mp4')
        res = {}
        if v_1080:
            res['1080p'] = v_1080[0]
        if v_720:
            res['720p'] = v_720[0]
        if v_480:
            res['480p'] = v_480[0]
        if v_360:
            res['360p'] = v_360[0]
        return res

    def get_audio_stream(self):
        m_a = self.m_s.filter(mime_type='audio/webm')
        if m_a:
            return m_a[0]
        else:
            return None

    def run(self):
        self.m_s = self.v.streams
        thumbnail = requests.get(self.v.thumbnail_url).content
        res = {'title': self.v.title, 'thumbnail': thumbnail, 'v_s': self.get_video_streams(),
               'a_s': self.get_audio_stream()}
        self.data.emit(res)
