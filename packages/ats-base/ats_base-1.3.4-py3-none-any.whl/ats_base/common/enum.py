from enum import Enum


class ProClazz(Enum):
    GW698 = 'GW698'
    DLT645 = 'DLT645'
    DLMS = 'DLMS'
    CJT188 = 'CJT188'


class Payload(Enum):
    NORMAL = 'NORMAL'
    WARN = 'WARN'
    ERROR = 'ERROR'
