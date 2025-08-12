from django.utils import timezone

from datetime import datetime, timedelta
import json
import threading
import websocket
import time
import requests
from lms_geotool.tools.projected import mercator_to_lonlat

from .models import Product, Tag, Anchor, Map, Config
from .utils import APIClient


def check_api_param():
    try:
        host = Config.objects.get(name="HOST", is_valid=True).value
        account = Config.objects.get(name="ACCOUNT", is_valid=True).value
        password = Config.objects.get(name="PASSWORD", is_valid=True).value
    except Config.DoesNotExist as e:
        raise e
    except Exception as e:
        raise e
    return host, account, password


def get_map():
    host, account, password = check_api_param()
    api_client = APIClient(host, account, password)
    result = api_client.get_map()
    for each in result:
        cfg = each.get("cfgMap")
        floor = 0
        matrix = ""
        if cfg:
            for every in json.loads(cfg):
                if every["key"] == "cfg_floor":
                    floor = int(every.get("value"))
                elif every["key"] == "cfg_result_trans_matrix":
                    matrix = json.loads(every.get("value", {}))
        Map.objects.update_or_create(
            id=each.get("id"),
            defaults={
                "name": each.get("cname", "未命名地图"),
                "floor": floor,
                "matrix": matrix,
                "cfg": json.loads(cfg) if cfg else None,
            }
        )
    return


def get_product():
    host, account, password = check_api_param()
    api_client = APIClient(host, account, password)
    result_tag = api_client.get_product("tag")
    for each in result_tag:
        Product.objects.update_or_create(
            id=str(each.get("id")),
            defaults={
                "product_type": "TAG",
                "name": each.get("cname", ""),
                "desc": each.get("description", ""),
            }
        )

    result_anchor = api_client.get_product("anchor")
    for each in result_anchor:
        Product.objects.update_or_create(
            id=str(each.get("id")),
            defaults={
                "product_type": "ANCHOR",
                "name": each.get("cname", ""),
                "desc": each.get("description", ""),
            }
        )
    return


def get_tag():
    host, account, password = check_api_param()
    api_client = APIClient(host, account, password)
    result = api_client.get_tag()
    for each in result:
        product = Product.objects.get(id=each.get("productId"))

        Tag.objects.update_or_create(
            mac=str(each.get("mac")),
            defaults={
                "product": product,
                "is_online": True if each.get("status") == "online" else False,
                "is_hold_position": each.get("isHoldPosition", ""),
                "switch_distance": each.get("switchDistance", ""),
                "sleep_wait": each.get("sleepWait", ""),
                "is_hold_ble": each.get("isHoldBle", ""),
                "is_hold_uart": each.get("isHoldUart", ""),
                "wake_period": each.get("wakePeriod", ""),
                "max_power": each.get("maxPower", ""),
                "percent": each.get("percent") if each.get("percent") else None,
                "ota_cfg": json.loads(each.get("cat1_Ota_Cfg")) if each.get("cat1_Ota_Cfg") else None,
                "power": int(each.get("power")) if each.get("power") else None,
                "ip": each.get("ip", ""),
                "pos_anchor": each.get("posAnchor", ""),
                "imei": each.get("IMEI", ""),
                "iccid": each.get("ICCID", ""),
                "time": datetime.fromtimestamp(
                    int(each.get("time")) / 1000, tz=timezone.get_current_timezone()
                ) if each.get("time") else None,
                "online_time": datetime.fromtimestamp(
                    int(each.get("onlineTime")) / 1000, tz=timezone.get_current_timezone()
                ) if each.get("onlineTime") else None
            }
        )
    return


def get_anchor():
    host, account, password = check_api_param()
    api_client = APIClient(host, account, password)
    result = api_client.get_anchor()
    for each in result:
        try:
            product = Product.objects.get(id=each.get("productId"))
        except Product.DoesNotExist:
            product = None
        try:
            map = Map.objects.get(id=each.get("mapId"))
        except Map.DoesNotExist:
            map = None

        Anchor.objects.update_or_create(
            mac=str(each.get("mac")),
            defaults={
                "name": each.get("alias", "未命名基站"),
                "product": product,
                "map": map,
                "is_master": each.get("isMaster", 0),
                "master_list": each.get("masterList", ""),
                "is_online": True if each.get("status") == "online" else False,
                "x": each.get("x", 0),
                "y": each.get("y", 0),
                "lon": each.get("lon", 0),
                "lat": each.get("lat", 0),

                "cfg": json.loads(each.get("cfg")) if each.get("cfg") else None,
                "thresholds": json.loads(each.get("thresholds")) if each.get("thresholds") else None,
                "ip": each.get("localIp", ""),
                "online_time": datetime.fromtimestamp(
                    int(each.get("onlineTime")) / 1000, tz=timezone.get_current_timezone()
                ) if each.get("onlineTime") else None
            }
        )


def check_ws_param():
    try:
        http_url = Config.objects.get(name="HTTP_URL", is_valid=True).value
        heart_beat = Config.objects.get(name="HEART_BEAT", is_valid=True).value
        project_code = Config.objects.get(name="PROJECT_CODE", is_valid=True).value
    except Config.DoesNotExist as e:
        raise e
    except Exception as e:
        raise e
    return http_url, heart_beat, project_code


class ServiceManager:
    _instance = None
    websocket_running = False
    websocket_thread = None
    logs = []
    websocket_app = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def start_websocket(self):
        if self.websocket_running:
            return False

        # 初始化上次执行时间
        self.last_execution_time = datetime.now()
        self.execution_interval = timedelta(minutes=20)

        self.websocket_running = True

        self.host, account, password = check_api_param()
        self.http_url, self.heart_beat, self.project_code = check_ws_param()
        self.api_client = APIClient(self.host, account, password)
        self.api_token = self.api_client.get_token()

        self.websocket_thread = threading.Thread(
            target=self._websocket_worker,
            daemon=True
        )
        self.websocket_thread.start()
        self.log("WebSocket服务已启动")
        return True

    def stop_websocket(self):
        if not self.websocket_running:
            return False

        self.websocket_running = False

        # 主动关闭WebSocket连接
        if self.websocket_app:
            self.websocket_app.close()

        self.log("WebSocket服务已停止")
        return True

    def log(self, message):
        """添加日志并打印到控制台"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)

        # 限制日志数量
        if len(self.logs) > 500:
            self.logs.pop(0)

    def get_logs(self, count=50):
        """获取最近的日志"""
        return self.logs[-count:]

    # 新增：实际WebSocket回调函数
    def _on_message(self, ws, message):

        current_time = datetime.now()
        if current_time - self.last_execution_time >= self.execution_interval:
            get_tag()
            self.last_execution_time = current_time  # 更新上次执行时间

        result = json.loads(message)

        # 从标签和地图列表获取缓存的数据
        mac = result.get("code")
        device_type = Tag.objects.get(mac=mac).product.name
        floor = Map.objects.get(id=result.get("mapId")).floor
        percent = Tag.objects.get(mac=mac).percent

        data = {
            "deviceId": mac,
            "deviceType": device_type,
            "tag": "indoor",
            "baseFloor": floor,
            "heartbeatInterval": self.heart_beat,
            "timestamp": result.get("time"),
            "angle": 0,
            "qoe": percent,
            "note": ""
        }
        if result.get("msgType") == "coord":
            lon, lat = mercator_to_lonlat(result.get("tx", 0), result.get("ty", 0))

            data.update({
                "longitude": lon,
                "latitude": lat,
                "altitude": float(result.get("altitude", 0)),
                "x": result.get("tx", 0),
                "y": result.get("ty", 0),
                "z": result.get("tz", 0),
                "speed": result.get("rate", 0),
                "other": {
                    "sos": False
                },
            })
            requests.post(url=self.http_url, json=data, timeout=3)
        elif result.get("msgType") == "sos":
            # 单查返回值注意数据格式转换
            data.update({
                "other": {
                    "sos": True,
                    "uhbi": 1
                },
            })
            requests.post(url=self.http_url, json=data, timeout=3)
        elif result.get("msgType") == "imu":
            data.update({
                "other": {
                    "uhbi": 1
                },
            })
            requests.post(url=self.http_url, json=data, timeout=3)
        elif result.get("msgType") == "power":
            pass
        elif result.get("msgType") == "gpsSignal":
            pass
        elif result.get("msgType") == "powerAlert":
            pass
        elif result.get("msgType") == "fenceInOut":
            pass
        elif result.get("msgType") == "sosAlert":
            pass
        else:
            self.log(result)

    def _on_error(self, ws, error):
        self.log(f"WebSocket错误: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        self.log(f"连接关闭: code={close_status_code}, msg={close_msg}")

    def _on_open(self, ws):
        self.log("WebSocket连接已建立")

    def _on_reconnect(self, ws):
        self.log("正在尝试重新连接...")

    def _websocket_worker(self):
        """实际WebSocket工作线程"""
        self.log("正在启动WebSocket服务...")

        # 构建连接URL - 使用你的实际参数
        url = (
            f"ws://{self.host}/websocket/"
            f"{self.project_code}_0_2D"
            f"{self.api_token}"
        )

        try:
            self.websocket_app = websocket.WebSocketApp(
                url=url,
                on_open=self._on_open,
                on_reconnect=self._on_reconnect,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )

            # 运行WebSocket客户端（带自动重连）
            self.websocket_app.run_forever(reconnect=5)

        except Exception as e:
            self.log(f"WebSocket启动失败: {str(e)}")
        finally:
            self.websocket_running = False
            self.log("WebSocket工作线程已退出")


# 全局服务管理器实例
service_manager = ServiceManager()
