import requests
import json

_timeout_ = 90
_method_ = 'get'


def get(url, params: dict = None):
    """
    请求方式 - get
    :param url:
    :param params:
    :return:
    """
    try:
        res = requests.get(url=url, params=params, timeout=_timeout_)
        try:
            return json.loads(res.text)
        except Exception as e:
            return res.text
    except Exception as e:
        raise e


def post(url, params: dict = None, jsons: dict = None):
    """
    请求方式 - post
    :param url:
    :param params:
    :param jsons:
    :return:
    """
    try:
        res = requests.post(url=url, params=params, json=jsons, timeout=_timeout_)
        try:
            return json.loads(res.text)
        except Exception as e:
            return res.text
    except Exception as e:
        raise e


def put(url, params: dict = None, jsons: dict = None):
    """
    请求方式 - put
    :param url:
    :param params:
    :param jsons:
    :return:
    """
    try:
        res = requests.put(url=url, params=params, json=jsons, timeout=_timeout_)
        try:
            return json.loads(res.text)
        except Exception as e:
            return res.text
    except Exception as e:
        raise e


def delete(url, params: dict = None, jsons: dict = None):
    """
    请求方式 - delete
    :param url:
    :param params:
    :param jsons:
    :return:
    """
    try:
        res = requests.delete(url=url, params=params, json=jsons, timeout=_timeout_)
        try:
            return json.loads(res.text)
        except Exception as e:
            return res.text
    except Exception as e:
        raise e




