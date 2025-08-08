"""
    协议栈
"""
from ats_base.base import req, entrance
from ats_base.config.configure import CONFIG
from ats_base.common import func

pro = entrance.api(CONFIG.get(func.SERVICE, 'pro'))


def manual(protocol: str, operation: str, mode: str = None, security: str = None):
    result = req.get('{}/{}'.format(pro, 'manual'),
                     params=func.to_dict(protocol=protocol, operation=operation, mode=mode, security=security))
    if result['code'] == 500:
        raise Exception(result['message'])

    return result['data']


def encode(data: dict):
    result = req.post('{}/{}'.format(pro, 'encode'), jsons=data)
    if result['code'] == 500:
        raise Exception(result['message'])

    return result['data']


def decode(data: dict):
    result = req.post('{}/{}'.format(pro, 'decode'), jsons=data)
    if result['code'] == 500:
        raise Exception(result['message'])

    return result['data']
