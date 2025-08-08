"""
    数据库服务
"""
from ats_base.base import req, entrance
from ats_base.common import func
from ats_base.config.configure import CONFIG

db = entrance.api(CONFIG.get(func.SERVICE, 'db'))


def query(table: str, **condition):
    """
    查询
    :param table:
    :param condition:
    :return:
    """
    con = func.to_dict(condition=condition)
    result = req.post('{}/{}'.format(db, table), jsons=con)
    if result['code'] == 500:
        raise Exception(result['message'])

    if type(result['data']) is list and len(result['data']) == 1:
        return result['data'].pop()
    else:
        return result['data']


def save(table: str, **data):
    """
    保存
    :param table:
    :param data:
    :return:
    """
    td = func.to_dict(data=data)
    result = req.post('{}/{}'.format(db, table), jsons=td)
    if result['code'] == 500:
        raise Exception(result['message'])

    return result['data']


def update(table: str, condition: dict, **data):
    """
    更新
    :param table:
    :param condition:
    :param data:
    :return:
    """
    td = func.to_dict(condition=condition, data=data)
    result = req.put('{}/{}'.format(db, table), jsons=td)
    if result['code'] == 500:
        raise Exception(result['message'])

    return result['data']


def delete(table: str, **condition):
    """
    删除
    :param table:
    :param condition:
    :return:
    """
    con = func.to_dict(condition=condition)
    result = req.delete('{}/{}'.format(db, table), jsons=con)
    if result['code'] == 500:
        raise Exception(result['message'])

    return result['data']
