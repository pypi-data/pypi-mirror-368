OK = 'OK'
NULL = 'NULL'
ERROR = '{api}-错误: {msg}.'

SUCCESS = 200
FAILURE = 500


def success(data=None):
    """
    系统响应消息
    :param code:
    :param msg:
    :param data:
    :return:
    """
    return info(SUCCESS, OK, data)


def failure(msg: str, data=None):
    """
    系统响应消息
    :param code:
    :param msg:
    :param data:
    :return:
    """
    return info(FAILURE, msg, data)


def info(code: int, msg: str, data):
    """
    系统响应消息
    :param code:
    :param msg:
    :param data:
    :return:
    """
    return {'code': code, 'message': msg, 'data': data}
