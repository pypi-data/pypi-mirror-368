from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any

import json

class Data:
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: Optional[int] = 4) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)

    @classmethod
    def from_json(cls, data: str):
        return cls(**json.loads(data))

    def __repr__(self):
        return f'{self.__class__.__name__}({self.to_dict()})'

@dataclass
class User(Data):
    id: str = ''
    private: bool = False
    verified: bool = False
    username: str = ''
    fullname: str = ''
    profile_picture: str = ''

@dataclass
class File(Data):
    file: str = ''
    size: str = ''

@dataclass
class Post(Data):
    id: str = ''
    code: str = ''

@dataclass
class Photo(Data):
    size: float = (0,0)
    mode: str = ''
    width: int = 0
    height: int = 0

@dataclass
class Video(Data):
    size: float = (0,0)
    width: int = 0
    height: int = 0
    duration: float = (0,0)

@dataclass
class Device(Data):
    android_manufacturer: str = ''
    android_resolution: str = ''
    android_language: str = ''
    android_release: str = ''
    android_model: str = ''
    android_board: str = ''
    android_cpu: str = ''
    android_sdk: str = ''
    android_dpi: str = ''
    instagram_code: str = ''
    instagram_version: str = ''

@dataclass
class Setting(Data):
    user_id: str = ''
    csrftoken: str = ''
    device_id: str = ''
    android_id: str = ''
    machine_id: str = ''
    family_device_id: str = ''
    client_session_id: str = ''
    pigeon_session_id: str = ''
    web_session_id: str = ''
    x_ig_www_claim: str = '0'
    authorization: str = ''
    user_agent: str = ''

@dataclass
class Account(Data):
    id: str = ''
    type: str = ''
    email: str = ''
    gender: str = ''
    private: bool = False
    verified: bool = False
    username: str = ''
    fullname: str = ''
    followers: str = '0'
    following: str = '0'
    bio: str = ''
    bio_links: List[str] = field(default_factory=list)
    posts: str = '0'
    reels: str = '0'
    birthday: str = ''
    external_url: str = ''
    phone_number: str = ''
    profile_picture: str = ''

@dataclass
class Notif(Data):
    id: str = ''
    new: bool = False
    name: str = ''
    date: str = ''
    text: str = ''
    user: User = field(default_factory=dict)
    ndid: str = ''
    tuuid: str = ''
    media: Post = field(default_factory=dict)

@dataclass
class Media(Data):
    id: str = ''
    type: str = ''
    code: str = ''
    date: str = ''
    like: str = '0'
    comment: str = '0'
    caption: str = ''
    location: Dict[str, Any] = field(default_factory=dict)
    usertags: List[str] = field(default_factory=list)
    can_save: bool = False
    can_share: bool = False
    can_comment: bool = False
    has_liked: bool = False
    music: str = ''
    url: List[str] = field(default_factory=list)

@dataclass
class Likers(Data):
    id: str = ''
    private: bool = False
    verified: bool = False
    username: str = ''
    fullname: str = ''
    profile_picture: str = ''

@dataclass
class Comments(Data):
    id: str = ''
    date: str = ''
    text: str = ''
    like: str = '0'
    user: User = field(default_factory=dict)
    child: str = '0'
    has_liked: bool = False
    has_translation: bool = False

@dataclass
class Followers(Data):
    id: str = ''
    private: bool = False
    verified: bool = False
    username: str = ''
    fullname: str = ''
    has_follow: bool = False
    has_request: bool = False
    profile_picture: str = ''

@dataclass
class Following(Data):
    id: str = ''
    private: bool = False
    verified: bool = False
    username: str = ''
    fullname: str = ''
    has_follow: bool = False
    has_request: bool = False
    profile_picture: str = ''