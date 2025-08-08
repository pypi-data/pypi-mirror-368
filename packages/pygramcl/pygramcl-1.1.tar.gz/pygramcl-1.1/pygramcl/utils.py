import re
import json
import uuid
import base64
import random
import string
import hashlib

from typing import Any, Dict, Union, Optional
from datetime import datetime, timezone

class Bearer:

    @staticmethod
    def encrypt(cookie: Dict[str, Any]) -> Optional[str]:
        if not Cookie.validate(cookie):
            return None
        if not isinstance(cookie, dict):
            cookie = Cookie.to_dict(cookie)
        try:
            data = {
                'ds_user_id': Cookie.parser('ds_user_id', cookie),
                'sessionid': Cookie.parser('sessionid', cookie)
            }
            bearer = base64.b64encode(json.dumps(data, separators=(',', ':')).encode('utf-8')).decode('utf-8')
            return f'Bearer IGT:2:{bearer}'
        except Exception:
            return None

    @staticmethod
    def decrypt(bearer: str) -> Optional[str]:
        try:
            encoded = bearer.split(':', 2)[-1]
            decoded = base64.urlsafe_b64decode(encoded).decode('utf-8')
            data = json.loads(decoded)
            data.pop('should_use_header_over_cookies', None)
            return Cookie.to_str(data)
        except Exception:
            return None

class Cookie:

    @staticmethod
    def to_str(cookie_dict: Dict[str, Any]) -> str:
        if not isinstance(cookie_dict, dict):
            return cookie_dict if isinstance(cookie_dict, str) else None
        return '; '.join(f'{k}={v}' for k, v in cookie_dict.items())

    @staticmethod
    def to_dict(cookie_str: str) -> Dict[str, Any]:
        return dict(
            item.strip().split('=', 1)
            for item in cookie_str.split(';') if '=' in item
        )

    @staticmethod
    def parser(key: str, cookie: Union[str, Dict[str, any]], default: Optional[Any] = None) -> Dict[str, Any]:
        if isinstance(cookie, str):
            cookie = Cookie.to_dict(cookie)
        return cookie.get(key, default)

    @staticmethod
    def validate(cookie: Union[str, Dict[str, Any]]) -> bool:
        if 'ds_user_id' not in cookie or 'sessionid' not in cookie:
            return False
        return True

class Generator:

    @staticmethod
    def uuid(heex: Optional[bool] = False, seed: Union[str, Dict[str, Any]] = None, uppercase: Optional[bool] = False) -> str:
        if seed and isinstance(seed, (str, Dict[str, Any])):
            hash = hashlib.md5()
            hash.update(str(seed).encode('utf-8'))
            _uid = uuid.UUID(hash.hexdigest())
        else:
            _uid = uuid.uuid4()
        uid_ = _uid.hex if heex else str(_uid)
        return uid_.upper() if uppercase else uid_

    @staticmethod
    def hmac():
        return f'hmac.AR0{Generator.string(45)}'

    @staticmethod
    def nonce(seed: Optional[str] = None) -> str:
        seed = seed or Generator.uuid()
        return base64.b64encode(hashlib.sha256(seed.encode('utf-8')).digest()).decode('utf-8')

    @staticmethod
    def digit(size: Optional[int] = 12) -> str:
        return ''.join(random.choices(string.digits, k=size))

    @staticmethod
    def string(size: Optional[int] = 12, char: Optional[bool] = False) -> str:
        base = string.ascii_letters + string.digits
        return ''.join(random.choices(base + '_-' if char else base, k=size))

    @staticmethod
    def jazoest(seed: Optional[str] = None) -> str:
        seed = seed or Generator.android_id()
        return f'2{sum(ord(c) for c in seed)}'

    @staticmethod
    def upload_id() -> int:
        return str(Generator.timestamp() * 1000)

    @staticmethod
    def android_id(device_id: Optional[str] = None) -> str:
        seed = str(device_id if device_id else Generator.uuid()).replace('-', '')
        return f'android-{hashlib.sha256(seed.encode()).hexdigest()[:16]}'

    @staticmethod
    def csrftoken(size: Optional[int] = 32, char: Optional[bool] = False) -> str:
        return Generator.string(size, char)

    @staticmethod
    def machine_id(size: Optional[int] = 28, char: Optional[bool] = False) -> str:
        return Generator.string(size, char)

    @staticmethod
    def device_id(ig_did: Optional[str] = None) -> str:
        if ig_did:
            try:
                return str(uuid.UUID(ig_did))
            except:
                pass
        return Generator.uuid()

    @staticmethod
    def family_device_id(uppercase: Optional[bool] = False) -> str:
        return Generator.uuid(uppercase=uppercase)

    @staticmethod
    def web_session_id():
        return '{}:{}:{}'.format(Generator.string(6), Generator.string(6), Generator.string(6))

    @staticmethod
    def pigeon_session_id() -> str:
        return 'UFS-' + Generator.uuid(False) + '-' + str(random.randint(1,50))

    @staticmethod
    def pigeon_rawclienttime() -> str:
        return str(round(Generator.timestamp(), 3))

    @staticmethod
    def timestamp() -> Optional[float]:
        return int(datetime.now(timezone.utc).timestamp())

    @staticmethod
    def timestring(timestamp: Union[float, Any] = None) -> str:
        return datetime.fromtimestamp(timestamp if timestamp is not None else Generator.timestamp()).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def timezone_offset() -> str:
        offset = datetime.now().astimezone().utcoffset()
        return str(int(offset.total_seconds()) if offset else 0)

    @staticmethod
    def speed_kbps(total_bytes_b: Union[str, int, float] = None, total_time_ms: Union[str, int] = None) -> str:
        total_bytes_b = total_bytes_b or Generator.total_bytes_b()
        total_time_ms = total_time_ms or Generator.total_time_ms()
        speed = (float(total_bytes_b) * 8) / int(total_time_ms) / 1000
        return f'{speed:.3f}'

    @staticmethod
    def total_bytes_b() -> Union[int, float]:
        return random.randint(2_000_000, 8_000_000)

    @staticmethod
    def total_time_ms() -> int:
        return random.randint(1000, 4000)
    
    @staticmethod
    def media_id(url: str) -> str:
        try:
            if not url.startswith('https://'):
                if url.isdigit():
                    return url
            basestr = string.ascii_uppercase + string.ascii_lowercase + string.digits + '-_'
            mapping = {value: key for key, value in enumerate(basestr)}
            pattern = r'/(?:p|reel|story)/([A-Za-z0-9_-]+)'
            matches = re.search(pattern, url).group(1)
            media_id = 0
            for chars in matches:
                media_id = (media_id * 64) + mapping[chars]
            return media_id
        except Exception:
            return None

class Useragent:

    USER_AGENT_DEVICE = {
        'instagram_version': '309.1.0.41.113',
        'android_sdk': '31',
        'android_release': '12',
        'android_dpi': '440dpi',
        'android_resolution': '1080x2254',
        'android_manufacturer': 'Xiaomi/Redmi',
        'android_model': 'Redmi Note 9 Pro',
        'android_board': 'joyeuse',
        'android_cpu': 'qcom',
        'android_language': 'in_ID',
        'instagram_code': '541635890'
    }

    USER_AGENT_FORMAT = (
        'Instagram {instagram_version} Android ({android_sdk}/{android_release}; '
        '{android_dpi}; {android_resolution}; {android_manufacturer}; {android_model}; '
        '{android_board}; {android_cpu}; {android_language}; {instagram_code})'
    )

    USER_AGENT_PARSER = re.compile(
        r'Instagram\s(?P<instagram_version>[\d\.]+)\sAndroid\s\('
        r'(?P<android_sdk>\d+)/(?P<android_release>[\d\.]+);'
        r'\s*(?P<android_dpi>\d+dpi);'
        r'\s*(?P<android_resolution>\d+x\d+);'
        r'\s*(?P<android_manufacturer>[^;]+);'
        r'\s*(?P<android_model>[^;]+);'
        r'\s*(?P<android_board>[^;]+);'
        r'\s*(?P<android_cpu>[^;]+);'
        r'\s*(?P<android_language>[^;]+);'
        r'\s*(?P<instagram_code>\d+)\)'
    )

    @classmethod
    def parser(cls, user_agent: str) -> Optional[dict]:
        match = cls.USER_AGENT_PARSER.search(user_agent)
        return match.groupdict() if match else None

    @classmethod
    def instagram(cls, device: Optional[Dict[str, str]] = None, instagram_version: Optional[str] = None, instagram_code: Optional[str] = None) -> str:
        default_device = cls.USER_AGENT_DEVICE.copy()
        device = device if isinstance(device, dict) and set(default_device.keys()).issubset(device.keys()) else default_device
        if instagram_version:
            device['instagram_version'] = instagram_version
        if instagram_code:
            device['instagram_code'] = instagram_code
        return cls.USER_AGENT_FORMAT.format(**device)

__all__ = ['Bearer', 'Cookie', 'Generator', 'Useragent']