import json
import requests

from typing import Any, Dict, Union, Optional
from .utils import Generator
from .parser import Parser
from .types import Account

class Guest:
    
    @staticmethod
    def request(method: str, endpoint: str, **kwargs):
        domain = 'https://z-p3.www.instagram.com/'
        session = requests.Session()
        session.headers.update({
            'authority': 'z-p3.www.instagram.com',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'cache-control': 'max-age=0',
            'pragma': 'no-cache',
            'origin': 'https://z-p3.www.instagram.com',
            'referer': f'https://z-p3.www.instagram.com/',
            'sec-ch-prefers-color-scheme': 'light',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6788.76 Safari/537.36',
            'x-ig-app-id': '936619743392459',
            'x-bloks-version-id': '446750d9733aca29094b1f0c8494a768d5742385af7ba20c3e67c9afb91391d8',
            'x-csrftoken': Generator.csrftoken(),
            'x-asbd-id': '359341',
            'x-mid': Generator.machine_id()
        })
        session.headers.update(kwargs.pop('headers', {}))
        session.cookies.update(kwargs.pop('cookies', {}))
        if method.upper() == 'POST':
            if kwargs.get('data') and 'content-length' not in session.headers:
                session.headers.update({'content-length': str(len(kwargs.get('data')))})
        response = session.request(
            url=(domain if endpoint.startswith('https') else domain + endpoint.lstrip('/')),
            method=method.upper(),
            **kwargs
        )
        return response
    
    @staticmethod
    def posts(username: str, max_results: Optional[int] = None):
        max_results = max_results if max_results is not None else 35
        count = max_results if max_results <= 35 else 35
        results = []
        next_max_id = ''
        more_available = True
        while more_available:
            try:
                response = Guest.request(
                    method='get',
                    endpoint=f'/api/v1/feed/user/{username}/username/?count={count}&max_id={next_max_id}&nocache={Generator.timestamp()}',
                    headers={'referer': f'https://z-p3.www.instagram.com/{username}/'
                })
                response_json = response.json()
                userpost = Parser.media(response_json)
                if isinstance(userpost, list):
                    for post in userpost:
                        results.append(post)
                else:
                    if userpost:
                        results.append(userpost)
                if len(results) >= max_results: break
                next_max_id = response_json.get('next_max_id', None)
                more_available = response_json.get('more_available', False)
            except Exception:
                break
        return results[:max_results]
    
    @staticmethod
    def username_info(username: str):
        try:
            response = Guest.request(method='get', endpoint=f'/api/v1/users/web_profile_info/?username={username}&nocache={Generator.timestamp()}')
            response.raise_for_status()
            user = response.json()['data']['user']
            info = {
                'id': user.get('id'),
                'type': user.get('account_type', ''),
                'email': user.get('public_email', ''),
                'gender': Parser.gender_map.get(user.get('gender'), ''),
                'private': user.get('is_private'),
                'verified': user.get('is_verified'),
                'username': user.get('username'),
                'fullname': user.get('full_name'),
                'followers': str(user.get('edge_followed_by', {}).get('count', 0)),
                'following': str(user.get('edge_follow', {}).get('count', 0)),
                'bio': user.get('biography',''),
                'bio_links': [item.get('url') for item in user.get('bio_links', [{}])],
                'posts': str(user.get('edge_owner_to_timeline_media', {}).get('count', 0)),
                'reels': str(user.get('edge_owner_to_timeline_clips', {}).get('count', 0)),
                'external_url': user.get('external_url', ''),
                'phone_number': user.get('public_phone_number', ''),
                'profile_picture': user.get('profile_pic_url_hd', '')
            }
            return Account.from_dict(info)
        except Exception:
            return None