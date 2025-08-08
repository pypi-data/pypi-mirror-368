from instagram.types import User, File, Post, Photo, Video, Device, Setting, Account, Notif, Media, Likers, Comments, Followers, Following
from typing import Optional, Union, List, Dict, Any
from instagram.utils import Generator

import re

class Parser:
    
    gender_map: dict = {1: 'male', 2: 'female', 3: 'non-binary'}
    media_type_map: dict = {1: 'image', 2: 'video'}
    account_type_map: dict = {1: 'personal', 2: 'business', 3: 'creator'}
    
    @staticmethod
    def data(html: str):
        try:
            data = {
                'av': re.search(r'"actorID":"(\d+)",', html).group(1),
                '__d': 'www',
                '__user': '0',
                '__a': '1',
                '__req': '2c',
                '__hs': re.search(r'"haste_session":"(.*?)",', html).group(1),
                'dpr': '3',
                '__ccg': re.search(r'"connectionClass":"(.*?)"}', html).group(1),
                '__rev': re.search(r'"client_revision":(\d+),', html).group(1),
                '__hsi': re.search(r'"hsi":"(.*?)",', html).group(1),
                '__comet_req': '7',
                'fb_dtsg': re.search(r'{"dtsg":{"token":"(.*?)",', html).group(1),
                'jazoest': re.search(r'jazoest=(\d+)",', html).group(1),
                'lsd': re.search(r'"LSD",\[\],\{"token":"(.*?)"\}', html).group(1),
                '__spin_r': re.search(r'"__spin_r":(\d+),', html).group(1),
                '__spin_b': re.search(r'"__spin_b":"(.*?)",', html).group(1),
                '__spin_t': re.search(r'"__spin_t":(\d+),', html).group(1)
            }
            return data
        except Exception:
            return {}
    @staticmethod
    def file(response: Dict[str, Any]):
        return File.from_dict(response)
    
    @staticmethod
    def photo(response: Dict[str, Any]):
        return Photo.from_dict(response)
    
    @staticmethod
    def video(response: Dict[str, Any]):
        return Video.from_dict(response)
    
    @staticmethod
    def devices(response: Dict[str, Any]):
        return Device.from_dict(response)
    
    @staticmethod
    def setting(response: Dict[str, Any]):
        return Setting.from_dict(response)
    
    @staticmethod
    def account(response: Dict[str, Any]):
        user = response.get('user', {})
        return Account(
            id=user.get('pk_id', ''),
            type=Parser.account_type_map.get(user.get('account_type'), ''),
            email=user.get('email', ''),
            gender=Parser.gender_map.get(user.get('gender'), ''),
            private=user.get('is_private', False),
            verified=user.get('is_verified', False),
            username=user.get('username', ''),
            fullname=user.get('full_name', ''),
            followers=str(user.get('follower_count', 0)),
            following=str(user.get('following_count', 0)),
            bio=user.get('biography', ''),
            bio_links=[item.get('url') for item in user.get('bio_links', [{}])],
            posts=str(user.get('media_count', 0)),
            reels=str(user.get('total_clips_count', 0)),
            birthday=user.get('birthday', ''),
            external_url=user.get('external_url', ''),
            phone_number=user.get('phone_number', ''),
            profile_picture=user.get('hd_profile_pic_url_info', {}).get('url', '')
        )
    
    @staticmethod
    def media(response: Dict[str, Any]):
        medias = []
        if isinstance(response.get('items'), list):
            medias = response.get('items', [])
        elif isinstance(response.get('media'), dict):
            medias = [response.get('media')]
        elif isinstance(response, dict) and response.get('pk'):
            medias = [response]

        results = []
        for media in medias:
            music_info = (((media or {}).get('music_metadata') or {}).get('music_info') or {}).get('music_asset_info') or {}
            music = '{} - {}'.format(music_info.get('title', ''), music_info.get('display_artist', ''))
            caption = media.get('caption', {}).get('text', '') if media.get('caption') else ''
            loc = media.get('location') or {}
            maps = f"https://www.google.com/maps/search/?api=1&query={loc.get('lat', '0')},{loc.get('lng', '0')}"
            location = {
                'id': loc.get('facebook_places_id', ''),
                'name': loc.get('name', ''),
                'address': loc.get('address', ''),
                'google_maps': maps
            } if loc else {}

            usertags = []
            for tag in ((media.get('usertags') or {}).get('in') or []):
                username = (tag.get('user') or {}).get('username')
                if username:
                    usertags.append(username)

            media_type = Parser.media_type_map.get(media.get('media_type'), 'carousel')
            media_url = []

            if media_type == 'image':
                media_url.append(media.get('image_versions2', {}).get('candidates', [{}])[0].get('url', ''))
            elif media_type == 'video':
                media_url.append(media.get('video_versions', [{}])[0].get('url', ''))
            elif media_type == 'carousel':
                for carousel in media.get('carousel_media', []):
                    ctype = Parser.media_type_map.get(carousel.get('media_type'))
                    if ctype == 'image':
                        media_url.append(carousel.get('image_versions2', {}).get('candidates', [{}])[0].get('url', ''))
                    elif ctype == 'video':
                        media_url.append(carousel.get('video_versions', [{}])[0].get('url', ''))

            results.append(Media(
                id=str(media.get('pk')),
                type=media_type,
                code=media.get('code'),
                date=Generator.timestring(media.get('taken_at')),
                like=str(media.get('like_count', 0)),
                comment=str(media.get('comment_count', 0)),
                caption=caption,
                location=location,
                usertags=usertags,
                can_save=media.get('can_viewer_save', False),
                can_share=media.get('can_viewer_reshare', False),
                can_comment=media.get('has_more_comments', False),
                has_liked=media.get('has_liked', False),
                music=music if len(music) > 10 else '',
                url=media_url
            ))
        return results[0] if len(results) == 1 else results
    
    @staticmethod
    def notif(response: Dict[str, Any]):
        results = []
        for item in (response.get('new_stories') or [{}]):
            if not item.get('pk'):
                continue
            args = item.get('args', {})
            results.append(Notif(
                id=item.get('pk', ''),
                new=True,
                name=item.get('notif_name', ''),
                date=Generator.timestring(args.get('timestamp', 0)),
                text=args.get('text', ''),
                user=User(
                    id=args.get('profile_id', ''),
                    username=args.get('profile_name', ''),
                    profile_picture=args.get('profile_image', ''),
                ),
                ndid=item.get('ndid', ''),
                tuuid=args.get('tuuid', ''),
                media=Post(
                    id=args.get('media', [{}])[0].get('id', '').split('_')[0],
                    code=args.get('media', [{}])[0].get('shortcode', '')
                )
            ))
        for item in (response.get('old_stories') or [{}]):
            if not item.get('pk'):
                continue
            args = item.get('args', {})
            results.append(Notif(
                id=item.get('pk', ''),
                new=False,
                name=item.get('notif_name', ''),
                date=Generator.timestring(args.get('timestamp', 0)),
                text=args.get('text', ''),
                user=User(
                    id=args.get('profile_id', ''),
                    username=args.get('profile_name', ''),
                    profile_picture=args.get('profile_image', '')
                ),
                ndid=item.get('ndid', ''),
                tuuid=args.get('tuuid', ''),
                media=Post(
                    id=args.get('media', [{}])[0].get('id', '').split('_')[0],
                    code=args.get('media', [{}])[0].get('shortcode', '')
                )
            ))
        return results
    
    @staticmethod
    def likers(response: Dict[str, Any]):
        results = []
        for user in response.get('users', [{}]):
            results.append(Likers(
                id=user.get('id', ''),
                private=user.get('is_private', False),
                verified=user.get('is_verified', False),
                username=user.get('username', ''),
                fullname=user.get('full_name', ''),
                profile_picture=user.get('profile_pic_url', '')
            ))
        return results
    
    @staticmethod
    def comments(response: Dict[str, Any]):
        results = []
        for comment in response.get('comments', [{}]):
            results.append(Comments(
                id=comment.get('pk', ''),
                date=Generator.timestring(comment.get('created_at', 0)),
                text=comment.get('text', ''),
                like=str(comment.get('comment_like_count', 0)),
                user=User(
                    id=comment.get('user', {}).get('id', ''),
                    username=comment.get('user', {}).get('username', ''),
                    fullname=comment.get('user', {}).get('full_name', ''),
                    profile_picture=comment.get('user', {}).get('profile_pic_url', '')
                ),
                child=str(comment.get('child_comment_count', 0)),
                has_liked=comment.get('has_liked_comment', False),
                has_translation=comment.get('has_translation', False)
            ))
        return results
    
    @staticmethod
    def followers(response: Dict[str, Any]):
        user = response.get('data', {}).get('user', {}).get('edge_followed_by', {})
        for edge in user.get('edges', [{}]):
            node = edge.get('node', {})
            return Followers(
                id=str(node.get('id', '')),
                private=node.get('is_private', False),
                verified=node.get('is_verified', False),
                username=node.get('username', ''),
                fullname=node.get('full_name', ''),
                has_follow=node.get('followed_by_viewer', False),
                has_request=node.get('requested_by_viewer', False),
                profile_picture=node.get('profile_pic_url', '')
            )
    
    @staticmethod
    def following(response: Dict[str, Any]):
        user = response.get('data', {}).get('user', {}).get('edge_follow', {})
        for edge in user.get('edges', [{}]):
            node = edge.get('node', {})
            return Following(
                id=str(node.get('id', '')),
                private=node.get('is_private', False),
                verified=node.get('is_verified', False),
                username=node.get('username', ''),
                fullname=node.get('full_name', ''),
                has_follow=node.get('followed_by_viewer', False),
                has_request=node.get('requested_by_viewer', False),
                profile_picture=node.get('profile_pic_url', '')
            )