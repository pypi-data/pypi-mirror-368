import configparser
import os

CONFIG = configparser.ConfigParser()

if os.path.exists('config.ini'):
    os.remove('config.ini')

IP = '10.157.1.249'
# IP = '10.10.5.179'

# CONFIG CONTENT
CONFIG['BASE'] = {}
CONFIG['BASE']['url'] = 'http://{}:8888/'.format(IP)
CONFIG['BASE']['api'] = 'api'
CONFIG['BASE']['manual'] = 'manual'


CONFIG['API'] = {}
CONFIG['API']['tcc'] = 'tcc'
CONFIG['API']['pro'] = 'pro'
CONFIG['API']['em'] = 'em'
CONFIG['API']['mm'] = 'mm'
CONFIG['API']['db'] = 'db'
CONFIG['API']['udm'] = 'udm'
CONFIG['API']['build_in'] = 'build_in'
CONFIG['API']['pdh'] = 'pdh'
CONFIG['API']['msg'] = 'msg'

CONFIG['RABBITMQ'] = {}
CONFIG['RABBITMQ']['host'] = IP
CONFIG['RABBITMQ']['port'] = '5672'
CONFIG['RABBITMQ']['username'] = 'admin'
CONFIG['RABBITMQ']['password'] = 'auto@T0001'


CONFIG['REDIS'] = {}
CONFIG['REDIS']['host'] = IP
CONFIG['REDIS']['password'] = 'auto@T0001'
CONFIG['REDIS']['encoding'] = 'utf-8'
CONFIG['REDIS']['db'] = '0'
CONFIG['REDIS']['max_conn'] = '20'


CONFIG['DB'] = {}
CONFIG['DB']['mysql'] = 'mysql+pymysql://root:autoTT0001@{}:3306/autotest'.format(IP)


with open('config.ini', 'w') as file:
    CONFIG.write(file)