"""
    结果分析计算验证服务
"""
from ats_base.base import req, entrance
from ats_base.common import func
from ats_base.config.configure import CONFIG

udm = entrance.api(CONFIG.get(func.SERVICE, 'udm'))


def handle(module: str, function: str, data, debug_url: str = None):
    """
    数据验证
    :param module:
    :param function:
    :param data:
    :param debug_url:
    :return:
    """
    if debug_url is not None and func.is_valid_url(debug_url):
        result = req.post('{}/{}/{}'.format(debug_url, module, function), jsons=data)
    else:
        result = req.post('{}/{}/{}'.format(udm, module, function), jsons=data)

    if result['code'] == 500:
        raise Exception(result['message'])

    return result['data']
