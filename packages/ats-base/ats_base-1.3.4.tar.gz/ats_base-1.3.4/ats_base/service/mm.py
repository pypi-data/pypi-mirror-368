"""
    缓存服务 - redis
    - 缓存测试用例运行过程中产生的数据 - 方便调用
"""
from ats_base.base import req, entrance
from ats_base.common import func
from ats_base.config.configure import CONFIG

mm = entrance.api(CONFIG.get(func.SERVICE, 'mm'))


class Dict:
    """
        字典
    """
    url = mm + '/dict'

    @classmethod
    def get(cls, name: str, key: str):
        result = req.get('{}/{}/{}'.format(Dict.url, name, key))
        if result['code'] == 500:
            raise Exception(result['message'])

        return result['data']

    @classmethod
    def put(cls, name: str, key: str, data):
        if type(data) is dict or type(data) is list:
            result = req.post('{}/{}/{}'.format(Dict.url, name, key), jsons=data)
        else:
            result = req.post('{}/{}/{}/{}'.format(Dict.url, name, key, data))

        if result['code'] == 500:
            raise Exception(result['message'])

        return result['data']

    @classmethod
    def delete(cls, name: str, key: str):
        result = req.delete('{}/{}/{}'.format(Dict.url, name, key))
        if result['code'] == 500:
            raise Exception(result['message'])

        return result['message']


class Queue:
    """
        队列
    """
    url = mm + '/queue'

    @classmethod
    def get(cls, name: str):
        result = req.get('{}/{}'.format(Queue.url, name))
        if result['code'] == 500:
            raise Exception(result['message'])

        return result['data']

    @classmethod
    def put(cls, name: str, data):
        if type(data) is dict or type(data) is list:
            result = req.post('{}/{}'.format(Queue.url, name), jsons=data)
        else:
            result = req.post('{}/{}/{}'.format(Queue.url, name, data))

        if result['code'] == 500:
            raise Exception(result['message'])

        return result['data']

    @classmethod
    def delete(cls, name: str, start: int, end: int):
        result = req.delete('{}/{}/{}/{}'.format(Dict.url, name, start, end))
        if result['code'] == 500:
            raise Exception(result['message'])

        return result['message']


class Set:
    """
        集合
    """
    url = mm + '/set'

    @classmethod
    def get(cls, name: str):
        result = req.get('{}/{}'.format(Set.url, name))
        if result['code'] == 500:
            raise Exception(result['message'])

        return result['data']

    @classmethod
    def put(cls, name: str, data):
        result = req.post('{}/{}/{}'.format(Set.url, name, data))
        if result['code'] == 500:
            raise Exception(result['message'])

        return result['message']

    @classmethod
    def delete(cls, name: str, data):
        result = req.delete('{}/{}/{}'.format(Set.url, name, data))
        if result['code'] == 500:
            raise Exception(result['message'])

        return result['message']


def get(key: str):
    result = req.get('{}/{}'.format(mm, key))
    if result['code'] == 500:
        raise Exception(result['message'])

    return result['data']


def put(key: str, data):
    if type(data) is dict or type(data) is list:
        result = req.post('{}/{}'.format(mm, key), jsons=data)
    else:
        result = req.post('{}/{}/{}'.format(mm, key, data))
        
    if result['code'] == 500:
        raise Exception(result['message'])

    return result['message']


def delete(key: str):
    result = req.delete('{}/{}'.format(mm, key))
    if result['code'] == 500:
        raise Exception(result['message'])

    return result['message']


if __name__ == '__main__':
    METER_COMM = {
        "step_id": "*STEP_ID",
        "todo": {
            "meter:comm": {
                "msg": "#MESSAGE",
                "channel": '#CHANNEL',
                "frame": "#FRAME"
            }
        }
    }

    APP_Show = {
        "step_id": "*STEP_ID",
        "todo": {
            "app:show": {
                "msg": "#MESSAGE"
            }
        }
    }

    BENCH_POWER_OFF = {
        "step_id": "*STEP_ID",
        "todo": {
            "bench:power_off": {
                "msg": "#MESSAGE",
                "Dev_Port": "#DEV_PORT"
            }
        }
    }

    BENCH_POWER_ON = {
        "step_id": "*STEP_ID",
        "todo": {
            "bench:power_on": {
                "msg": "#MESSAGE",
                "Phase": "#PHASE",
                "Rated_Volt": "#RATED_VOLTAGE",
                "Rated_Curr": "#RATED_CURRENT",
                "Rated_Freq": "#RATED_FREQUENT",
                "PhaseSequence": "#PH_SEQUENCE",
                "Revers": "#REVERS",
                "Volt_Per": "#VOLTAGE_PERCENT",
                "Curr_Per": "#CURRENT_PERCENT",
                "IABC": "#IABC",
                "CosP": "#COSP",
                "SModel": "#SMODEL",
                "Dev_Port": "#DEV_PORT"
            }
        }
    }

    BENCH_ADJUST = {
        "step_id": "*STEP_ID",
        "todo": {
            "bench:adjust": {
                "msg": "#MESSAGE",
                "Phase": "#PHASE",
                "Rated_Volt": "#RATED_VOLTAGE",
                "Rated_Curr": "#RATED_CURRENT",
                "Rated_Freq": "#RATED_FREQUENT",
                "PhaseSequence": "#PH_SEQUENCE",
                "Revers": "#REVERS",
                "Volt_Per": "#VOLTAGE_PERCENT",
                "Curr_Per": "#CURRENT_PERCENT",
                "IABC": "#IABC",
                "CosP": "#COSP",
                "SModel": "#SMODEL",
                "Dev_Port": "#DEV_PORT"
            }
        }
    }

    BENCH_ADJUST_CUST = {
        "step_id": "*STEP_ID",
        "todo": {
            "bench:adjust_cust": {
                "msg": "#MESSAGE",
                "Phase": "#PHASE",
                "Rated_Freq": "#RATED_FREQUENT",
                "Volt1": "#VOLTAGE1",
                "Volt2": "#VOLTAGE2",
                "Volt3": "#VOLTAGE3",
                "Curr1": "#CURRENT1",
                "Curr2": "#CURRENT2",
                "Curr3": "#CURRENT3",
                "Uab": "#UAB",
                "Uac": "#UAC",
                "Ang1": "#ANGLE1",
                "Ang2": "#ANGLE2",
                "Ang3": "#ANGLE3",
                "SModel": "#SMODEL",
                "Dev_Port": "#DEV_PORT"
            }
        }
    }

    BENCH_ADJUST_UI2 = {
        "step_id": "*STEP_ID",
        "todo": {
            "bench:adjust_ui2": {
                "msg": "#MESSAGE",
                "Phase": "#PHASE",
                "Rated_Volt": "#RATED_VOLTAGE",
                "Rated_Curr": "#RATED_CURRENT",
                "Rated_Freq": "#RATED_FREQUENT",
                "PhaseSequence": "#PHASE_SEQUENCE",
                "Revers": "#REVERS",
                "Volt1_Per": "#VOLTAGE1_PERCENT",
                "Volt2_Per": "#VOLTAGE2_PERCENT",
                "Volt3_Per": "#VOLTAGE3_PERCENT",
                "Curr1_Per": "#CURRENT1_PERCENT",
                "Curr2_Per": "#CURRENT2_PERCENT",
                "Curr3_Per": "#CURRENT3_PERCENT",
                "IABC": "#IABC",
                "CosP": "#COSP",
                "SModel": "#SMODEL",
                "Dev_Port": "#DEV_PORT"
            }
        }
    }

    BENCH_READ = {
        "step_id": "*STEP_ID",
        "todo": {
            "bench:read": {
                "msg": "#MESSAGE",
                "SModel": "#SMODEL",
                "Dev_Port": "#DEV_PORT"
            }
        }
    }

    Dict.put('app:manual', 'meter:comm', METER_COMM)
    Dict.put('app:manual', 'app:show', APP_Show)
    Dict.put('app:manual', 'bench:power_on', BENCH_POWER_ON)
    Dict.put('app:manual', 'bench:adjust', BENCH_ADJUST)
    Dict.put('app:manual', 'bench:adjust_cust', BENCH_ADJUST_CUST)
    Dict.put('app:manual', 'bench:adjust_ui2', BENCH_ADJUST_UI2)
    Dict.put('app:manual', 'bench:power_off', BENCH_POWER_OFF)
    Dict.put('app:manual', 'bench:read', BENCH_READ)

    # API Service URL
    Dict.put("API", 'TCC', 'http://10.10.5.108:8000/tcc')
    Dict.put("API", 'PRO', 'http://10.10.5.108:8001/pro')
    Dict.put("API", 'MM', 'http://10.10.5.108:8007/mm')
    Dict.put("API", 'DB', 'http://10.10.5.108:8008/db')
    Dict.put("API", 'DVS', 'http://10.10.5.108:8020/dvs')
    Dict.put("API", 'GW698', 'http://10.10.5.108:8010/pro/gw698')
    Dict.put("API", 'DLMS', 'http://10.10.5.108:8011/pro/dlms')
    Dict.put("API", 'DLT645', 'http://10.10.5.108:8012/pro/dlt645')

    # client.getConn().hset("MANUAL:API", 'TCC', {})
