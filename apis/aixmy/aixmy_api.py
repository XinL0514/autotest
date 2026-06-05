import json

from utils.http_client import HttpClient
from utils.logger import Logger


class AixmyApiClient:
    _END_CLASS_API = "https://maliang.miaobi.cn/api/v2/classroom/over/course"

    def __init__(self, page, room_key: str | None = None, cached_token: str | None = None):
        self.page = page
        self.room_key = room_key
        self._cached_token = cached_token
        self.logger = Logger.get_logger("AixmyApiClient")

    def get_auth_token(self) -> str | None:
        if self._cached_token:
            return self._cached_token
        self._cached_token = self._load_token_from_env() or self._read_token_from_localStorage()
        return self._cached_token

    def _load_token_from_env(self) -> str | None:
        from fixtures.business_auth import _get_auth_value
        user_json = _get_auth_value("AUTOTEST_AUTH_USER_JSON")
        if user_json:
            try:
                user = json.loads(user_json)
                token = user.get("token") or user.get("accessToken")
                if token:
                    self.logger.info("auth token loaded from env AUTOTEST_AUTH_USER_JSON")
                    return token
            except Exception:
                pass
        return None

    def _read_token_from_localStorage(self) -> str | None:
        try:
            user_json = self.page.evaluate("() => localStorage.getItem('user')")
            if user_json:
                user = json.loads(user_json)
                token = user.get("token") or user.get("accessToken")
                if token:
                    self.logger.info("auth token cached from localStorage")
                    return token
        except Exception:
            pass
        return None

    def _get_device_id(self) -> str:
        try:
            val = self.page.evaluate(
                "() => localStorage.getItem('deviceId') || localStorage.getItem('device_id')"
            )
            if val:
                return val
        except Exception:
            pass
        return "device_autotest"

    def end_class(self) -> bool:
        if not self.room_key:
            self.logger.warning("end_class: roomKey 未捕获，跳过")
            return False

        token = self.get_auth_token()
        if not token:
            self.logger.warning("end_class: 未获取到 auth token，跳过")
            return False

        url = f"{self._END_CLASS_API}?roomKey={self.room_key}"
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN",
            "appversion": "1.0.0",
            "authorization": f"Bearer {token}",
            "content-length": "0",
            "deviceid": self._get_device_id(),
            "devicetype": "pc",
            "imappid": "1600079439",
            "origin": "https://aixmy.miaobi.cn",
            "referer": "https://aixmy.miaobi.cn/",
        }
        result = HttpClient.post(url, headers)
        if result is not None:
            self.logger.info(f"end_class: 下课成功 roomKey={self.room_key} resp={result}")
            return True
        self.logger.warning(f"end_class: 下课接口调用失败 roomKey={self.room_key}")
        return False
