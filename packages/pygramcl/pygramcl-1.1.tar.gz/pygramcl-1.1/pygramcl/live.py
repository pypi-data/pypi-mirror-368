from .client import Client
from .parser import Parser
from .video import Video

import os
import time
import threading
import subprocess

class Live:
    
    def __init__(self, cookies: str):
        self.client = Client(cookies)
        self.live_user = self.user()
        self.live_time = int(time.time())
        self.live_info = {
            'broadcast_id': None,
            'viewer_count': 0,
            'comment_count': 0,
            'comment_users': []
        }
        self.live_loop = None
        self.live_started = False
        self.live_process = None
    
    def user(self):
        try:
            user = self.client.account_info()
            return user.to_dict() if user and user.username else None
        except Exception:
            return None
    
    def info(self):
        try:
            broadcast_id = self.live_info['broadcast_id']
            viewer = self.client.web_request(method='post', endpoint=f'/api/v1/live/{broadcast_id}/heartbeat_and_get_viewer_count/?hl=en').json()
            comment = self.client.web_request(method='get', endpoint=f'/api/v1/live/{broadcast_id}/get_comment/?last_comment_ts={self.live_time}&hl=en').json()
            viewer_count = viewer.get('viewer_count', 0)
            comment_count = len(comment.get('comments'))
            self.live_info['viewer_count'] = int(viewer_count)
            self.live_info['comment_count'] += int(comment_count)
            for user in comment.get('comments', [{}]):
                self.live_info['comment_users'].append({
                    'user': user.get('user', {}).get('username', 'unknown'),
                    'text': user.get('text', ''),
                    'time': time.strftime('%H:%M:%S')
                })
            if self.live_info['comment_users']:
                self.live_time = int(time.time())
            return self.live_info
        except Exception:
            return None
    
    def start(self, video: str, title: str = None, hours: int = 0, minutes: int = 0, seconds: int = 0):
        try:
            html = self.client.web_request(method='get', endpoint='?hl=en')
            data = Parser.data(html.text)
            response = self.client.web_request(
                data={
                    'broadcast_message': title or 'LIVE',
                    'internal_only': 'false',
                    'source_type': '203',
                    'visibility': '0',
                    'jazoest': data.get('jazoest')
                },
                method='post',
                endpoint='/api/v1/live/create/?hl=en'
            )
            response_json = response.json()
            broadcast_id = response_json.get('broadcast_id')
            stream_url = response_json.get('upload_url')
            start = self.client.web_request(method='post', endpoint=f'/api/v1/live/{broadcast_id}/start/?hl=en')
            self.live_info['broadcast_id'] = broadcast_id
            duration = (hours * 3600) + (minutes * 60) + seconds
            if duration > 0:
                self.live_loop = Video.loop(video, hours, minutes, seconds)
                video = self.live_loop
            self.live_process = Video.stream(video, stream_url)
            self.live_started = True
            return True
        except Exception:
            return False
    
    def stop(self):
        if self.live_loop:
            if os.path.isfile(self.live_loop):
                os.remove(self.live_loop)
        if self.live_process:
            try:
                self.live_process.terminate()
            except:
                self.live_process.kill()
        self.live_process = None
        self.live_started = False
        self.live_info['broadcast_id'] = None
        self.live_info['viewer_count'] = 0
        self.live_info['comment_count'] = 0
        self.live_info['comment_users'] = []
        return True