import os
import re
import time


def prepare_temp():
    folder = os.getenv('APPDATA') + "\\Youtube DM\\temp"
    print(folder)
    try:
        if os.path.isfile(folder + "\\video.mp4"):
            os.unlink(folder + "\\video.mp4")
        if os.path.isfile(folder + "\\audio.webm"):
            os.unlink(folder + "\\audio.webm")
    except Exception as e:
        print('Failed to delete. Reason: %s' % e)
    return folder


def youtube_url_validation(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return True
    return False


def format_time(n):
    if n >= 3600:
        return time.strftime('%H:%M:%S', time.gmtime(n))
    else:
        return time.strftime('%M:%S', time.gmtime(n))


def format_size(size):
    if size < 1024 ** 2:
        return f'{round(size / 1024, 1)} KB'
    elif 1024 ** 2 < size < 1024 ** 3:
        return f'{round(size / 1024 ** 2, 1)} MB'
    else:
        return f'{round(size / 1024 ** 3, 1)} GB'


def clear_name(name):
    characters = """\<>*?/!":|"""
    new_name = ''
    for i in name:
        if i not in characters:
            new_name += i
    return new_name
