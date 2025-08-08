"""
    智能终端APP
"""
from ats_base.base import req


def send(url: str, data: dict):
    """
    发送 -> APP
    :param url:
    :param data:
    :return:
    """
    return req.post(url, jsons=data)

