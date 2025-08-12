import hashlib
import hmac
import base64
import time
import uuid
import requests
import json
from urllib.parse import urljoin
from django.core.cache import cache
from django.db import DatabaseError
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
"""
正常情况下不会改变的常量，用于生成签名
"""
METHOD = "POST"
ARTEMIS = "artemis"

from .models import Camera, Config


def get_config_value(name, default=""):
    """
    动态获取配置参数，从数据库或缓存中获取
    :param name: 配置名
    :param default: 默认值
    :return:
    """

    value = cache.get(f'config_{name}')
    if value is not None:
        return value
    try:
        config = Config.objects.get(name=name, is_valid=True)
        # 缓存1小时（3600秒），根据需求调整
        cache.set(f'config_{name}', config.value, 3600)
        return config.value
    except Config.DoesNotExist:
        return default
    except DatabaseError as e:
        # 处理数据库不可用的情况
        print(f"Database error fetching config {name}: {str(e)}")
        return default


def create_signature(api: str) -> dict:
    """
    获取签名并放入请求头
    :param app_key: 应用标识
    :param app_secret: 密钥凭证
    :param api: 接口地址
    :return: 请求头
    """

    # 动态获取当前配置
    app_key = get_config_value("APP_KEY")
    app_secret = get_config_value("APP_SECRET")

    # 毫秒时间戳
    timestamp = str(round(time.time() * 1000))
    # uuid
    nonce = str(uuid.uuid1())
    # signature
    secret = str(app_secret).encode('utf-8')
    message = (
        f"{METHOD}\n*/*\napplication/json\n"
        f"x-ca-key:{app_key}\n"
        f"x-ca-nonce:{nonce}\n"
        f"x-ca-timestamp:{timestamp}\n"
        f"/{ARTEMIS}{api}"
    ).encode('utf-8')
    signature = base64.b64encode(
        hmac.new(secret, message, digestmod=hashlib.sha256).digest()
    )
    return {
        'Accept': '*/*',
        'Content-Type': 'application/json',
        'X-Ca-Key': app_key,
        'X-Ca-Signature': signature,
        'X-Ca-timestamp': timestamp,
        'X-Ca-nonce': nonce,
        'X-Ca-Signature-Headers': 'x-ca-key,x-ca-nonce,x-ca-timestamp'
    }


def get_cameras_list():
    """
    获取摄像头列表
    :return:
    """
    api = "/api/resource/v2/camera/search"
    payload = {"pageNo": 1, "pageSize": 1000}
    header_dict = create_signature(api)
    host = get_config_value("HOST")
    response = requests.post(url=urljoin(host, ARTEMIS + api), headers=header_dict, json=payload, verify=False, timeout=5)
    res = response.json()
    return res.get("data", {}).get("list", [])


def get_camera_preview(index_code):
    """
    获取websocket视频流地址
    :param index_code: 摄像头唯一编码
    :return: 视频流地址
    """
    api = "/api/video/v2/cameras/previewURLs"
    payload = {"pageNo": 1, "pageSize": 1000, "cameraIndexCode": index_code, "protocol": "ws"}
    header_dict = create_signature(api)
    host = get_config_value("HOST")
    try:
        response = requests.post(url=urljoin(host, ARTEMIS + api), headers=header_dict, json=payload, verify=False, timeout=5)
        res = response.json()
        if res["code"] == "0":
            return res.get("data", {}).get("url")
        else:
            print(f"错误码：{res['code']}\n详情：{res['msg']}")
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
    except json.JSONDecodeError:
        print("响应解析失败")


def get_camera_online():
    api = "/api/nms/v1/online/camera/get"
    payload = {"pageNo": 1, "pageSize": 1000}
    header_dict = create_signature(api)
    host = get_config_value("HOST")
    response = requests.post(url=urljoin(host, ARTEMIS + api), headers=header_dict, json=payload, verify=False, timeout=5)
    res = response.json()
    return res.get("data", {}).get("list", [])


def get_camera_history_status(index_code):
    api = "/api/nms/v1/online/history_status"
    payload = {"indexCode": index_code, "resourceType": "camera"}
    header_dict = create_signature(api)
    host = get_config_value("HOST")
    response = requests.post(url=urljoin(host, ARTEMIS + api), headers=header_dict, json=payload, verify=False, timeout=5)
    res = response.json()
    return res.get("data", {}).get("list", [])


def control_camera(camera_index_code, action, command, speed=50):
    api = "/api/video/v1/ptzs/controlling"
    payload = {"cameraIndexCode": camera_index_code, "action": action, "command": command, "speed": speed}
    header_dict = create_signature(api)
    host = get_config_value("HOST")
    try:
        response = requests.post(url=urljoin(host, ARTEMIS + api), headers=header_dict, json=payload, verify=False, timeout=5)
        res = response.json()
        return res
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
    except json.JSONDecodeError:
        print("响应解析失败")


def get_camera_playback(index_code: str, begin_time, end_time):
    api = "/api/video/v2/cameras/playbackURLs"
    payload = {"cameraIndexCode": index_code, "beginTime": begin_time, "endTime": end_time, "protocol": "ws"}
    header_dict = create_signature(api)
    host = get_config_value("HOST")
    try:
        response = requests.post(url=urljoin(host, ARTEMIS + api), headers=header_dict, json=payload, verify=False, timeout=5)
        res = response.json()
        return res.get("data", {}).get("url")
    except Exception as e:
        return ""


if __name__ == '__main__':
    payload = {"pageNo": 1, "pageSize": 1000, "cameraIndexCode": "2ed4491f79174f82bd6c685c06a8d175", "protocol": "ws"}
    header_dict = create_signature("/api/video/v2/cameras/previewURLs")
    r = requests.post("https://172.25.31.1/artemis/api/video/v2/cameras/previewURLs", headers=header_dict, json=payload, verify=False)
    res = r.content.decode('utf-8')
    a = json.loads(res)["data"]
    print(a)
