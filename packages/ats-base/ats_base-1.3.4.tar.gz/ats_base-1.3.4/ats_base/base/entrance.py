from ats_base.base import req
from ats_base.config.configure import CONFIG


api_entrance = CONFIG.get('BASE', 'url') + CONFIG.get('BASE', 'api')
manual_entrance = CONFIG.get('BASE', 'url') + CONFIG.get('BASE', 'manual')


def api(service: str):
    """
    获取服务api访问url地址
    :param service:
    :return:
    """
    url = '{}/{}'.format(api_entrance, service)

    result = req.get(url)
    if result['code'] == 500:
        raise Exception(result['message'])

    return result['data']


def manual(name: str, key: str):
    """
    获取 - 参数格式
    :param name:
    :param key:
    :param params:
    :return:
    """
    url = '{}/{}/{}'.format(manual_entrance, name, key)

    result = req.get(url)
    if result['code'] == 500:
        raise Exception(result['message'])

    return result['data']
