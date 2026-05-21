import json
import ssl
import urllib.error
import urllib.request

from utils.logger import Logger

logger = Logger.get_logger("HttpClient")

_SSL_CONTEXT = ssl.create_default_context()
_SSL_CONTEXT.check_hostname = False
_SSL_CONTEXT.verify_mode = ssl.CERT_NONE


class HttpClient:
    @staticmethod
    def post(url: str, headers: dict[str, str], timeout: int = 10) -> dict | None:
        req = urllib.request.Request(url, data=b"", method="POST")
        for key, value in headers.items():
            req.add_header(key, value)
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CONTEXT) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body) if body.strip() else None
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            logger.warning(f"HTTP {e.code} from {url}: {body[:300]}")
            return None
        except Exception as e:
            logger.warning(f"Request to {url} failed: {e}")
            return None
