"""
    加密机
"""
from ats_base.base import req, entrance
from ats_base.config.configure import CONFIG
from ats_base.common import func

em = entrance.api(CONFIG.get(func.SERVICE, 'em'))


def handle(protocol: str, function: str, data):
    result = req.post('{}/{}/{}'.format(em, protocol, function), jsons=data)
    if result['code'] == 500:
        raise Exception(result['message'])

    return result['data']