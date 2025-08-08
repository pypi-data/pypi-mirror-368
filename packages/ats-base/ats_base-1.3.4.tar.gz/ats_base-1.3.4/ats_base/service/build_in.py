"""
    内置函数
"""
from ats_base.base import req, entrance
from ats_base.common import func
from ats_base.config.configure import CONFIG

build_in = entrance.api(CONFIG.get(func.SERVICE, 'build_in'))


def handle(function: str, data, debug_url: str = None):
    """
    内置函数
    :param function:
    :param data:
    :param debug_url:
    :return:
    """
    if debug_url is not None and func.is_valid_url(debug_url):
        result = req.post('{}/{}'.format(debug_url, function), jsons=data)
    else:
        result = req.post('{}/{}'.format(build_in, function), jsons=data)

    if result['code'] == 500:
        raise Exception(result['message'])

    return result['data']


