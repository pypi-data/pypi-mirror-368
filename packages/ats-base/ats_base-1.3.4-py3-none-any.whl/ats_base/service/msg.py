"""
    消息服务
"""
from ats_base.base import req, entrance
from ats_base.config.configure import CONFIG
from ats_base.common import func

msg = entrance.api(CONFIG.get(func.SERVICE, 'msg'))


def send(chat_tool: str, data):
    result = req.post('{}/{}'.format(msg, chat_tool), jsons=data)
    if result['code'] == 500:
        raise Exception(result['message'])

    return result['data']