import io
import os
import re
import time
import json
import random
import requests
import subprocess

from .utils import Bearer, Cookie, Generator, Useragent
from typing import Any, Dict, Union, Optional
from .download import Download
from .parser import Parser
from .photo import Photo
from .video import Video

class Client:
    
    def __init__(self, cookies: Union[str, Dict[str, str]], user_agent: Optional[str] = None):
        if not Cookie.validate(cookies):
            return ValueError(f'Can\'t find ds_user_id and sessionid: {cookies}')
        if not isinstance(cookies, str):
            cookies = Cookie.to_str(cookies)
        if user_agent is not None:
            devices = Useragent.parser(user_agent)
        else:
            devices = None
    
        self.cookies = cookies
        self.devices = self.get_devices(devices)
        self.user_id = Cookie.parser('ds_user_id', self.cookies)
        self.setting = self.get_setting()
        self.session = requests.Session()
    
    def get_devices(self, devices: Optional[Dict[str, str]] = None):
        if not devices:
            devices = Useragent.USER_AGENT_DEVICE
        return Parser.devices(devices)
    
    def get_setting(self):
        return Parser.setting({
            'user_id': self.user_id,
            'csrftoken': Cookie.parser('csrftoken', self.cookies, Generator.csrftoken()),
            'device_id': Generator.device_id(Cookie.parser('ig_did', self.cookies)),
            'android_id': Generator.android_id(self.user_id),
            'machine_id': Cookie.parser('mid', self.cookies, Generator.machine_id()),
            'family_device_id': Generator.family_device_id(),
            'client_session_id': Generator.uuid(),
            'pigeon_session_id': Generator.pigeon_session_id(),
            'web_session_id': Generator.web_session_id(),
            'x_ig_www_claim': Generator.hmac(),
            'authorization': Bearer.encrypt(self.cookies),
            'user_agent': Useragent.instagram(self.devices.to_dict())
        })
    
    def api_request(self, method: str, endpoint: str, headers: Optional[Dict[str, Any]] = None, data: Union[str, Dict[str, Any]] = None, with_signature: Optional[bool] = False, **kwargs):
        api_domain = 'https://i.instagram.com/api/v1/'
        api_method = method.upper()
        api_payload = data
        api_headers = {
            'user-agent': Useragent.instagram(self.devices),
            'accept-encoding': 'gzip, deflate',
            'x-ig-app-locale': self.devices.android_language,
            'x-ig-device-locale': self.devices.android_language,
            'x-ig-mapped-locale': self.devices.android_language,
            'x-pigeon-session-id': self.setting.pigeon_session_id,
            'x-pigeon-rawclienttime': Generator.pigeon_rawclienttime(),
            'x-ig-bandwidth-speed-kbps': str(Generator.speed_kbps()),
            'x-ig-bandwidth-totalbytes-b': str(Generator.total_bytes_b()),
            'x-ig-bandwidth-totaltime-ms': str(Generator.total_time_ms()),
            'x-ig-app-startup-country': self.devices.android_language.split('_')[1].upper(),
            'x-bloks-version-id': '9fc6a7a4a577456e492c189810755fe22a6300efc23e4532268bca150fe3e27a',
            'x-ig-www-claim': self.setting.x_ig_www_claim,
            'x-bloks-is-prism-enabled': 'true',
            'x-bloks-prism-button-version': '0',
            'x-bloks-is-layout-rtl': 'false',
            'x-ig-device-id': self.setting.device_id,
            'x-ig-family-device-id': self.setting.family_device_id,
            'x-ig-android-id': self.setting.android_id,
            'x-ig-timezone-offset': str(Generator.timezone_offset()),
            'x-fb-connection-type': 'WIFI',
            'x-ig-connection-type': 'WIFI',
            'x-ig-capabilities': '3brTv10=',
            'x-ig-app-id': '567067343352427',
            'priority': 'u=3',
            'accept': '*/*',
            'accept-language': f'{self.devices.android_language.replace("_","-")}, en-US',
            'authorization': self.setting.authorization,
            'x-mid': self.setting.machine_id,
            'ig-u-ds-user-id': self.setting.user_id,
            'ig-u-rur': f'EAG,{self.setting.user_id},{int(Generator.timestamp()) + 31536000}:01fe5b0d5777d056cfc0d00d5709baeca9e0fc6df763aa64b06c73ad58ade8878fcba77c',
            'ig-intended-user-id': self.setting.user_id,
            'x-fb-http-engine': 'Liger',
            'x-fb-client-ip': 'True',
            'x-fb-server-cluster': 'True'
        }
        api_headers.update(headers if headers else {})
        if api_method == 'POST':
            if 'content-type' not in api_headers:
                api_headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            if api_payload:
                if 'content-length' not in api_headers:
                    api_headers['content-length'] = str(len(api_payload))
                if with_signature and 'signed_body' not in api_payload:
                    api_payload = {'signed_body': f'SIGNATURE.{json.dumps(api_payload, separators=(",",":"))}'}
        return self.session.request(
            url=(api_domain + endpoint.lstrip('/') if 'https' not in endpoint else endpoint),
            data=api_payload,
            method=api_method,
            headers=api_headers,
            **kwargs
        )
    
    def web_request(self, method: str, endpoint: str, headers: Optional[Dict[str, Any]] = None, data: Union[str, Dict[str, Any]] = None, **kwargs):
        web_domain = 'https://www.instagram.com/'
        web_method = method.upper()
        web_payload = data
        web_headers = {
            'authority': 'www.instagram.com',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'cookie': self.cookies,
            'sec-ch-prefers-color-scheme': 'light',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="133", "Google Chrome";v="133"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.6831.68 Safari/537.36',
            'x-asbd-id': '359341',
            'x-csrftoken': self.setting.csrftoken,
            'x-ig-app-id': '936619743392459',
            'x-ig-www-claim': self.setting.x_ig_www_claim,
            'x-requested-with': 'XMLHttpRequest',
            'x-web-session-id': self.setting.web_session_id
        }
        web_headers.update(headers if headers else {})
        if web_method == 'POST':
            if 'content-type' not in web_headers:
                web_headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            if web_payload:
                if 'content-length' not in web_headers:
                    web_headers['content-length'] = str(len(web_payload))
        return self.session.request(
            url=(web_domain + endpoint.lstrip('/') if 'https' not in endpoint else endpoint),
            data=web_payload,
            method=web_method,
            headers=web_headers,
            **kwargs
        )
    
    def notif_info(self):
        try:
            html = self.web_request(method='get', endpoint='?hl=en')
            data = Parser.data(html.text)
            response = self.web_request(
                data=data,
                method='post',
                endpoint='/api/v1/news/inbox/'
            )
            response_json = response.json()
            return Parser.notif(response_json)
        except Exception:
            return None
    
    def media_info(self, url: Union[str, int]):
        try:
            media_id = Generator.media_id(url)
            response = self.api_request(method='get', endpoint=f'/media/{media_id}/info/')
            response_json = response.json()
            if response_json['status'] == 'ok':
                return Parser.media(response_json)
        except Exception:
            return None
    
    def account_info(self):
        try:
            user = self.api_request(method='get', endpoint='/accounts/current_user/?edit=true')
            info = self.api_request(method='get', endpoint=f'/users/{self.user_id}/info/')
            response_json = {**user.json(), **info.json()}
            if response_json['status'] == 'ok':
                return Parser.account(response_json)
        except Exception:
            return None
    
    def username_info(self, user: Union[str, int]):
        try:
            endpoint = f'/users/{user}/info/' if str(user).isdigit() else f'/users/{user}/usernameinfo/'
            response = self.api_request(method='get', endpoint=endpoint)
            response_json = response.json()
            if response_json['status'] == 'ok':
                return Parser.account(response_json)
        except Exception:
            return None
    
    def like(self, url: str):
        media = self.media_info(url)
        if not media or not media.like:
            return None
        try:
            response = self.web_request(
                method='post',
                endpoint=f'/api/v1/web/likes/{media.id}/like/'
            )
            return response.status_code == 200
        except Exception:
            return None
    
    def unlike(self, url: str):
        media = self.media_info(url)
        if not media or not media.like:
            return None
        try:
            response = self.web_request(
                method='post',
                endpoint=f'/api/v1/web/likes/{media.id}/unlike/'
            )
            return response.status_code == 200
        except Exception:
            return None
    
    def comment(self, url: str, text: Optional[str] = None):
        media = self.media_info(url)
        if not media or not media.like:
            return None
        try:
            data = {'comment_text': text if text is not None else ''}
            response = self.web_request(
                data=data,
                method='post',
                endpoint=f'/api/v1/web/comments/{media.id}/add/'
            )
            return response.status_code == 200
        except Exception:
            return None
    
    def follow(self, user: Union[str, int]) -> bool:
        user = self.username_info(user)
        if not user or not user.id:
            return None
        try:
            data = {
                'container_module': 'profile',
                'nav_chain': 'PolarisProfileNestedContentRoot:profilePage:1:via_cold_start',
                'user_id': user.id
            }
            response = self.web_request(
                data=data,
                method='post',
                endpoint=f'/api/v1/friendships/create/{user.id}/'
            )
            return response.status_code == 200
        except Exception:
            return None
    
    def unfollow(self, user: Union[str, int]) -> bool:
        user = self.username_info(user)
        if not user or not user.id:
            return None
        try:
            data = {
                'container_module': 'profile',
                'nav_chain': 'PolarisProfileNestedContentRoot:profilePage:1:via_cold_start',
                'user_id': user.id
            }
            response = self.web_request(
                data=data,
                method='post',
                endpoint=f'/api/v1/friendships/destroy/{user.id}/'
            )
            return response.status_code == 200
        except Exception:
            return None
    
    def posts(self, user: Union[str, int], max_results: Optional[int] = None):
        user = self.username_info(user)
        if not user or not user.posts:
            return None
        if max_results is None:
            max_results = int(user.posts)
        results = []
        next_max_id = None
        more_available = True
        while more_available and len(results) < max_results:
            try:
                params = {
                    'count': 12,
                    'min_timestamp': None,
                    'rank_token': f'{user.id}_{Generator.uuid()}',
                    'ranked_content': True
                }
                if next_max_id:
                    params['max_id'] = next_max_id
                response = self.api_request(
                    method='get',
                    params=params,
                    endpoint=f'/feed/user/{user.id}/'
                )
                response_json = response.json()
                userpost = Parser.media(response_json)
                if isinstance(userpost, list):
                    results.extend(userpost)
                elif userpost:
                    results.append(userpost)
                more_available = response_json.get('more_available', False)
                next_max_id = response_json.get('next_max_id')
            except Exception:
                break
        return results[:max_results]
    
    def search(self, query: str, max_results: Optional[int] = None):
        if max_results is None:
            max_results = 10
        results = []
        has_more = True
        next_max_id = None
        while has_more:
            try:
                params = {
                    'enable_metadata': True,
                    'query': query,
                    'search_session_id': Generator.uuid()
                }
                if next_max_id:
                    params['max_id'] = next_max_id
                response = self.web_request(
                    method='get',
                    params=params,
                    endpoint='/api/v1/fbsearch/web/top_serp/'
                )
                response_json = response.json()
                for section in response_json.get('media_grid', {}).get('sections', [{}]):
                    for media in section.get('layout_content', {}).get('medias', [{}]):
                        items = Parser.media(media)
                        if isinstance(items, list):
                            for item in items:
                                results.append(item)
                        else:
                            if items:
                                results.append(items)
                if len(results) >= max_results: break
                next_max_id = response_json.get('next_max_id')
                has_more = response_json.get('has_more', False)
            except Exception:
                break
        return results[:max_results]
    
    def explore(self, max_results: Optional[int] = None):
        if max_results is None:
            max_results = 10
        results = []
        next_max_id = None
        more_available = True
        while more_available:
            try:
                params = {
                    'include_fixed_destinations': 'true',
                    'is_nonpersonalized_explore': 'false',
                    'is_prefetch': 'false',
                    'omit_cover_media': 'false',
                    'module': 'explore_popular'
                }
                if next_max_id:
                    params['max_id'] = next_max_id
                response = self.web_request(
                    method='get',
                    params=params,
                    endpoint='/api/v1/discover/web/explore_grid/'
                )
                response_json = response.json()
                for section in response_json.get('sectional_items', [{}]):
                    for media in section.get('layout_content', {}).get('fill_items', [{}]):
                        items = Parser.media(media)
                        if isinstance(items, list):
                            for item in items:
                                results.append(item)
                        else:
                            if items:
                                results.append(items)
                if len(results) >= max_results: break
                next_max_id = response_json.get('next_max_id', None)
                more_available = response_json.get('more_available', False)
            except Exception:
                break
        return results[:max_results]
    
    def likers(self, url: str, max_results: Optional[int] = None):
        media = self.media_info(url)
        if not media or not media.like:
            return None
        if max_results is None:
            max_results = int(media.like)
        results = []
        next_min_id = None
        while True:
            try:
                params = {
                    'can_support_threading': True
                }
                if next_min_id:
                    params['min_id'] = next_min_id
                response = self.web_request(
                    method='get',
                    params=params,
                    endpoint=f'/api/v1/media/{media.id}/likers/'
                )
                response_json = response.json()
                likers = Parser.likers(response_json)
                if isinstance(likers, list):
                    for liker in likers:
                        results.append(liker)
                else:
                    if likers:
                        results.append(likers)
                if len(results) >= max_results: break
                next_min_id = response_json.get('next_min_id', None)
                if not next_min_id: break
            except Exception:
                break
        return results[:max_results]
    
    def comments(self, url: str, max_results: Optional[int] = None):
        media = self.media_info(url)
        if not media or not media.comment:
            return None
        if max_results is None:
            max_results = int(media.comment)
        results = []
        next_min_id = ''
        has_more_headload_comments = True
        while has_more_headload_comments:
            try:
                params = {
                    'can_support_threading': True,
                    'sort_order': 'popular'
                }
                if next_min_id:
                    params['min_id'] = next_min_id
                response = self.web_request(
                    method='get',
                    params=params,
                    endpoint=f'/api/v1/media/{media.id}/comments/'
                )
                response_json = response.json()
                comments = Parser.comments(response_json)
                if isinstance(comments, list):
                    for comment in comments:
                        results.append(comment)
                else:
                    if comments:
                        results.append(comments)
                if len(results) >= max_results: break
                has_more_headload_comments = response_json.get('has_more_headload_comments', False)
                next_min_id = response_json.get('next_min_id', None)
            except Exception:
                break
        return results[:max_results]
    
    def followers(self, user: Union[str, int], max_results: Optional[int] = None):
        user = self.username_info(user)
        if not user or not user.followers:
            return None
        if max_results is None:
            max_results = int(user.followers)
        results = []
        end_cursor = None
        has_next_page = True
        while has_next_page:
            try:
                params = {
                    'query_hash': 'c76146de99bb02f6415203be841dd25a',
                    'id': user.id,
                    'first': 24
                }
                if end_cursor:
                    params['after'] = end_cursor
                response = self.web_request(
                    method='get',
                    params=params,
                    headers={'referer': f'https://www.instagram.com/{user.username}/followers/'},
                    endpoint='/graphql/query/'
                )
                response_json = response.json()
                followers = Parser.followers(response_json)
                if followers and followers.id: results.append(followers)
                if len(results) >= max_results: break
                page_info = response_json.get('data', {}).get('user', {}).get('edge_followed_by', {}).get('page_info', {})
                end_cursor = page_info.get('end_cursor', None)
                has_next_page = page_info.get('has_next_page', False)
            except Exception:
                break
        return results[:max_results]
    
    def following(self, user: Union[str, int], max_results: Optional[int] = None):
        user = self.username_info(user)
        if not user or not user.followers:
            return None
        if max_results is None:
            max_results = int(user.followers)
        results = []
        end_cursor = None
        has_next_page = True
        while has_next_page:
            try:
                params = {
                    'query_hash': 'd04b0a864b4b54837c0d870b0e77e076',
                    'id': user.id,
                    'first': 24
                }
                if end_cursor:
                    params['after'] = end_cursor
                response = self.web_request(
                    method='get',
                    params=params,
                    headers={'referer': f'https://www.instagram.com/{user.username}/following/'},
                    endpoint='/graphql/query/'
                )
                response_json = response.json()
                following = Parser.following(response_json)
                if following and following.id: results.append(following)
                if len(results) >= max_results: break
                page_info = response_json.get('data', {}).get('user', {}).get('edge_follow', {}).get('page_info', {})
                end_cursor = page_info.get('end_cursor', None)
                has_next_page = page_info.get('has_next_page', False)
            except KeyError:
                break
        return results[:max_results]
    
    def post_delete(self, url: str):
        try:
            media_id = Generator.media_id(url)
            response = self.web_request(
                method='post',
                headers={
                    'content-type': 'application/x-www-form-urlencoded',
                    'content-length': '0'
                },
                endpoint=f'/api/v1/web/create/{media_id}/delete/'
            )
            return response.status_code == 200
        except Exception:
            return None
    
    def post_photo_rupload(self, upload_id: str, upload_photo: str):
        try:
            photo_mode = None
            photo_file = upload_photo
            photo_name = f'fb_uploader_{upload_id}'
            photo_info = Photo.info(photo_file)
            if photo_info.mode != 'RGB':
                photo_mode = Photo.rgb(photo_file)
                photo_file = photo_mode
                photo_info = Photo.info(photo_file)
            with open(photo_file, 'rb') as file:
                photo_data = file.read()
                photo_size = len(photo_data)
            if photo_mode:
                os.remove(photo_file)
            self.web_request(
                method='options',
                headers={
                    'access-control-request-headers': 'content-type,offset,x-asbd-id,x-entity-length,x-entity-name,x-entity-type,x-ig-app-id,x-instagram-rupload-params,x-web-session-id',
                    'access-control-request-method': 'POST',
                    'origin': 'https://www.instagram.com',
                    'referer': 'https://www.instagram.com/'
                },
                endpoint=f'/rupload_igphoto/{photo_name}'
            )
            headers = {
                'content-type': 'image/jpeg',
                'content-length': str(photo_size),
                'offset': '0',
                'origin': 'https://www.instagram.com',
                'referer': 'https://www.instagram.com/',
                'x-entity-length': str(photo_size),
                'x-entity-name': photo_name,
                'x-entity-type': 'image/jpeg',
                'x-instagram-rupload-params': json.dumps({
                    'media_type': 1,
                    'upload_id': upload_id,
                    'upload_media_height': photo_info.height,
                    'upload_media_width': photo_info.width
                })
            }
            response = self.web_request(
                data=photo_data,
                method='post',
                headers=headers,
                endpoint=f'/rupload_igphoto/{photo_name}'
            )
            return response.status_code == 200
        except Exception:
            return None
    
    def post_photo(self, photo: str, ratio: Optional[str] = None, caption: Optional[str] = None, usertags: Optional[list] = None):
        if not os.path.isfile(photo):
            raise FileNotFoundError(photo)
        if ratio and not ratio in ('square', 'portrait', 'landscape'):
            raise ValueError('Ratio must be square, portrait or landscape')
        try:
            html = self.web_request(method='get', endpoint='?hl=en')
            data = Parser.data(html.text)
            crop = False
            photo_file = photo
            if ratio:
                crop = True
                photo_crop = Photo.crop(photo_file, ratio)
                photo_file = photo_crop
            upload_id = str(Generator.timestamp() * 1000)
            rupload = self.post_photo_rupload(upload_id, photo_file)
            if crop:
                os.remove(photo_file)
            if not rupload:
                return None
            configure_data = {
                'archive_only': 'false',
                'caption': caption or '',
                'clips_share_preview_to_feed': '1',
                'disable_comments': '0',
                'disable_oa_reuse': 'false',
                'igtv_share_preview_to_feed': '1',
                'is_meta_only_post': '0',
                'is_unified_video': '1',
                'like_and_view_counts_disabled': '0',
                'media_share_flow': 'creation_flow',
                'share_to_facebook': '',
                'share_to_fb_destination_type': 'USER',
                'source_type': 'library',
                'upload_id': str(upload_id),
                'video_subtitles_enabled': '0',
                'jazoest': data.get('jazoest', Generator.jazoest())
            }
            if usertags:
                if not isinstance(usertags, list):
                    usertags = [usertags]
                user_ids = []
                for user in usertags:
                    if str(user).isdigit():
                        user_ids.append(str(user))
                    else:
                        info = self.username_info(user)
                        if info and info.id:
                            user_ids.append(str(info.id))
                if user_ids:
                    configure_data['invite_coauthor_user_ids_string'] = json.dumps(user_ids)
                    configure_data['usertags'] = json.dumps({
                        'in': [
                            {
                                'user_id': user_id,
                                'position': [
                                    round(random.uniform(0.1, 0.9), 3),
                                    round(random.uniform(0.1, 0.9), 3)
                                ]
                            } for user_id in user_ids
                        ]
                    })
            configure_headers = {
                'content-type': 'application/x-www-form-urlencoded',
                'content-length': str(len(configure_data)),
                'origin': 'https://www.instagram.com',
                'referer': 'https://www.instagram.com/'
            }
            response = self.web_request(
                data=configure_data,
                method='post',
                headers=configure_headers,
                endpoint='/api/v1/media/configure/'
            )
            return response.status_code == 200
        except Exception:
            return None
    
    def post_video_rupload(self, upload_id: str, upload_video: str):
        try:
            video_file = upload_video
            video_info = Video.info(video_file)
            video_name = f'fb_uploader_{upload_id}'
            with open(video_file, 'rb') as file:
                video_data = file.read()
                video_size = len(video_data)
            self.web_request(
                method='options',
                headers={
                    'access-control-request-headers': 'content-type,offset,x-asbd-id,x-entity-length,x-entity-name,x-entity-type,x-ig-app-id,x-instagram-rupload-params,x-web-session-id',
                    'access-control-request-method': 'POST',
                    'origin': 'https://www.instagram.com',
                    'referer': 'https://www.instagram.com/'
                },
                endpoint=f'/rupload_igvideo/{video_name}'
            )
            headers = {
                'content-type': 'video/mp4',
                'content-length': str(video_size),
                'offset': '0',
                'origin': 'https://www.instagram.com',
                'referer': 'https://www.instagram.com/',
                'x-entity-length': str(video_size),
                'x-entity-name': video_name,
                'x-instagram-rupload-params': json.dumps({
                    'client-passthrough': '1',
                    'is_clips_video': '1',
                    'is_sidecar': '0',
                    'media_type': 2,
                    'for_album': False,
                    'video_format': '',
                    'upload_id': upload_id,
                    'upload_media_duration_ms': video_info.duration * 1000,
                    'upload_media_height': video_info.height,
                    'upload_media_width': video_info.width,
                    'video_transform': None,
                    'video_edit_params': {
                        'crop_height': video_info.height,
                        'crop_width': video_info.width,
                        'crop_x1': 0,
                        'crop_y1': 0,
                        'mute': False,
                        'trim_end': video_info.duration,
                        'trim_start': 0
                    }
                })
            }
            response = self.web_request(
                data=video_data,
                method='post',
                headers=headers,
                endpoint=f'/rupload_igvideo/{video_name}'
            )
            return response.status_code == 200
        except Exception:
            return None
    
    def post_video(self, video: str, ratio: Optional[str] = None, caption: Optional[str] = None, usertags: Optional[list] = None, thumbnail: Optional[str] = None, retry_delay: Optional[int] = 3, max_retries: Optional[int] = 10):
        if not os.path.isfile(video):
            raise FileNotFoundError(video)
        if ratio and not ratio in ('square', 'portrait', 'landscape'):
            raise ValueError('Ratio must be square, portrait or landscape')
        try:
            html = self.web_request(method='get', endpoint='?hl=en')
            data = Parser.data(html.text)
            crop = False
            video_file = video
            thumb_file = thumbnail
            if not thumbnail or not os.path.isfile(thumbnail):
                thumb_file = Video.thumbnail(video_file)
                if ratio:
                    thumb_crop = Photo.crop(thumb_file, ratio)
                    if thumb_crop:
                        os.remove(thumb_file)
                    thumb_file = thumb_crop
            if ratio:
                crop = True
                video_crop = Video.crop(video_file, ratio)
                video_file = video_crop
            upload_id = str(Generator.timestamp() * 1000)
            rupload = self.post_video_rupload(upload_id, video_file)
            if crop:
                os.remove(video_file)
            if not rupload:
                return None
            rupload = self.post_photo_rupload(upload_id, thumb_file)
            if not rupload:
                return None
            if not thumbnail:
                os.remove(thumb_file)
            configure_data = {
                'archive_only': 'false',
                'caption': caption or '',
                'clips_share_preview_to_feed': '1',
                'disable_comments': '0',
                'disable_oa_reuse': 'false',
                'igtv_share_preview_to_feed': '1',
                'is_meta_only_post': '0',
                'is_unified_video': '1',
                'like_and_view_counts_disabled': '0',
                'media_share_flow': 'creation_flow',
                'share_to_facebook': '',
                'share_to_fb_destination_type': 'USER',
                'source_type': 'library',
                'upload_id': upload_id,
                'video_subtitles_enabled': '0',
                'jazoest': data.get('jazoest')
            }
            if usertags:
                if not isinstance(usertags, list):
                    usertags = [usertags]
                user_ids = []
                for user in usertags:
                    if str(user).isdigit():
                        user_ids.append(str(user))
                    else:
                        info = self.username_info(user)
                        if info and info.id:
                            user_ids.append(str(info.id))
                if user_ids:
                    configure_data['usertags'] = json.dumps({
                        'in': [
                            {
                                'user_id': user_id,
                                'position': [
                                    round(random.uniform(0.1, 0.9), 3),
                                    round(random.uniform(0.1, 0.9), 3)
                                ]
                            } for user_id in user_ids
                        ]
                    })
            
            configure_headers = {
                'content-type': 'application/x-www-form-urlencoded',
                'content-length': str(len(configure_data)),
                'origin': 'https://www.instagram.com',
                'referer': 'https://www.instagram.com/'
            }
            for attempt in range(max_retries):
                response = self.web_request(
                    data=configure_data,
                    method='post',
                    headers=configure_headers,
                    endpoint='/api/v1/media/configure_to_clips/'
                )
                response_json = response.json()
                if response_json.get('status') != 'fail' or 'Transcode not finished yet' not in response_json.get('message', ''):
                    return response.status_code == 200
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
            return False
        except Exception:
            return None
    
    def repost(self, url: str, caption: Optional[str] = None, usertags: Optional[list] = None):
        media_info = self.media_info(url)
        if not media_info or not media_info.id:
            return None
        media_link = media_info.url[0]
        media_save = Download.from_url(media_link)
        if not media_save:
            return None
        media_file = media_save.file
        if not caption:
            caption = media_info.caption
        if media_info.type == 'video':
            response = self.post_video(video=media_file, caption=caption)
        else:
            response = self.post_photo(photo=media_file, caption=caption)
        if os.path.isfile(media_file):
            os.remove(media_file)
        return response
    
    def post(self, media: str, ratio: Optional[str] = None, caption: Optional[str] = None, usertags: Optional[list] = None, thumbnail: Optional[str] = None):
        if not os.path.isfile(media):
            raise FileNotFoundError(media)
        if ratio and not ratio in ('square', 'portrait', 'landscape'):
            raise ValueError('Ratio must be square, portrait or landscape')
        extension = os.path.splitext(media)[1]
        if extension in ('.png', '.jpg', '.jpeg', '.webp', '.heic'):
            response = self.post_photo(photo=media, ratio=ratio, caption=caption, usertags=usertags)
        elif extension in ('.mov', '.mkv', '.mp4', '.webm'):
            response = self.post_video(video=media, ratio=ratio, caption=caption, usertags=usertags, thumbnail=thumbnail)
        else:
            raise ValueError('Media must be photo or video with valid format')
        return response