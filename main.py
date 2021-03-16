import ctypes
import platform
import logging
import os
import yaml
from gaminopad.app import Notepad


def get_app_config():
    return yaml.load(open('config/config.yml', 'r'),
                           Loader=yaml.FullLoader)

def setup_error_logging():
    if not os.path.isdir('logs'):
        os.mkdir('logs')

    logging.basicConfig(filename='logs/error.log',
                        encoding='utf-8',
                        level=logging.ERROR)

def make_dpi_aware():
    if int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)


if __name__ == '__main__':
    setup_error_logging()
    try:
        make_dpi_aware()
        config = get_app_config()
        app = Notepad(config)
        app.start()
    except Exception as e:
        logging.error(e)
