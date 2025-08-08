import configparser
import os

CONFIG = configparser.ConfigParser()

cur_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(cur_path, 'config.ini')

if os.path.exists(config_path):
    CONFIG.read(config_path)


