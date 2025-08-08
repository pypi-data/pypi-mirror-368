import os
import re
import json
import time
import random
import requests

class Fakemail:
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
        })
    
    def email(self):
        '''
        Return:
        example@fakemail.my.id
        '''
        response = self.session.get('https://fakemail.my.id/api/email/generate').json()
        if response.get('success'):
            return response.get('email')
        return None
    
    def inbox(self, email: str):
        '''
        Return:
        {
          "count": 1,
          "inbox": [
            {
              "uid": 12345,
              "subject": "Welcome!",
              "from_name": "Fakemail Team",
              "from_email": "noreply@fakemail.my.id",
              "date": "2024-06-08 10:15:00",
              "is_seen": false
            }
          ]
        }
        '''
        response = self.session.get(f'https://fakemail.my.id/api/email/inbox?email={email}').json()
        return {
            'count': response.get('count', 0),
            'inbox': response.get('messages', [])
        } if response.get('success') else {}
    
    def inbox_show(self, email: str, inbox: str):
        '''
        Return:
        {
          "success": true,
          "uid": 12345,
          "subject": "Welcome!",
          "from_name": "Fakemail Team",
          "from_email": "noreply@fakemail.my.id",
          "to": ["user12345@fakemail.my.id"],
          "date": "2024-06-08 10:15:00",
          "body": "Selamat datang...",
          "body_html": "<p>Selamat datang...</p>",
          "attachments": [],
          "is_seen": true
        }
        '''
        response = self.session.get(f'https://fakemail.my.id/api/email/show?email={email}&uid={inbox}').json()
        return response
    
    def inbox_delete(self, email: str, inbox: str):
        '''
        Return:
        True or False
        '''
        response = self.session.get(f'https://fakemail.my.id/api/email/delete?email={email}&uid={inbox}').json()
        return response.get('success') == True