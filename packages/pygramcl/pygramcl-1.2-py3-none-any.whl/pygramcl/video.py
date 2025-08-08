from typing import Optional
from .parser import Parser

import subprocess
import json
import os

class Video:
    
    @staticmethod
    def info(file: str):
        try:
            video_stream = None
            command = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', file]
            results = subprocess.run(command, capture_output=True, text=True, check=True)
            data = json.loads(results.stdout)
            for stream in data['streams']:
                if stream['codec_type'] == 'video':
                    video_stream = stream
                    break
            return Parser.video({
                'size': (video_stream['width'], video_stream['height']),
                'width': int(video_stream['width']),
                'height': int(video_stream['height']),
                'duration': float(data['format']['duration'])
            })
        except IOError:
            return None
    
    @staticmethod
    def loop(file: str, hours: Optional[int] = 0, minutes: Optional[int] = 0, seconds: Optional[int] = 0):
        try:
            name,ext = os.path.splitext(file)
            duration = (hours * 3600) + (minutes * 60) + seconds
            filename = f'{name}_loop_{duration}{ext}'
            command = [
                'ffmpeg', '-y',
                '-stream_loop', '-1',
                '-i', file,
                '-c', 'copy'
            ]
            if duration > 0:
                command.extend([
                    '-t', f'{hours:02d}:{minutes:02d}:{seconds:02d}',
                    filename
                ])
            else:
                command.extend([
                    '-t', f'{hours:02d}:10:{seconds:02d}',
                    filename
                ])
            subprocess.run(command, check=True, capture_output=True)
            return filename
        except Exception:
            return None
    
    @staticmethod
    def crop(file: str, ratio: Optional[str] = None, faster: bool = True):
        if not ratio or not ratio.lower() in ('square', 'portrait', 'landscape'):
            raise ValueError('Ratio must be square, portrait or landscape')
        target_ratio = {
            'square': (1080, 1080),
            'portrait': (1080, 1920),
            'landscape': (1920, 1080)
        }
        try:
            info = Video.info(file)
            width = info.width
            height = info.height
            ratio_key = ratio.lower()
            target_w, target_h = target_ratio[ratio_key]
            current_aspect = width / height
            target_aspect = target_w / target_h
            if ratio_key == 'square':
                size = min(width, height)
                crop_width = size
                crop_height = size
                x = (width - size) // 2
                y = (height - size) // 2
            else:
                if current_aspect > target_aspect:
                    crop_height = height
                    crop_width = height * target_w // target_h
                    x = (width - crop_width) // 2
                    y = 0
                else:
                    crop_width = width
                    crop_height = width * target_h // target_w
                    x = 0
                    y = (height - crop_height) // 2
            name, ext = os.path.splitext(file)
            filename = f'{name}_{ratio.lower()}{ext}'
            if faster:
                command = [
                    'ffmpeg', '-i', file,
                    '-filter:v', f'crop={crop_width}:{crop_height}:{x}:{y}',
                    '-c:a', 'copy',
                    '-c:v', 'libx264',
                    '-crf', '18',
                    '-preset', 'faster',
                    '-y',
                    filename
                ]
            else:
                command = [
                    'ffmpeg', '-i', file,
                    '-filter:v', f'crop={crop_width}:{crop_height}:{x}:{y}',
                    '-c:a', 'copy',
                    '-c:v', 'libx264',
                    '-crf', '18',
                    '-preset', 'slow',
                    '-y',
                    filename
                ]
            subprocess.run(command, check=True, capture_output=True)
            return filename
        except subprocess.CalledProcessError:
            return None
        except Exception:
            return None
    
    @staticmethod
    def scale(file: str, factor: float = None, faster: bool = True):
        if not factor or not isinstance(factor, (int, float)):
            raise ValueError('Factor must be a number (example: 2.0)')
        if factor <= 0:
            raise ValueError('Factor must be greater than 0')
        try:
            info = Video.info(file)
            if not info:
                return None
            width = info.width
            height = info.height
            new_width = int(width * factor)
            new_height = int(height * factor)
            if new_width % 2 != 0:
                new_width += 1
            if new_height % 2 != 0:
                new_height += 1
            name, ext = os.path.splitext(file)
            filename = f'{name}_scaled_{factor}{ext}'
            if faster:
                command = [
                    'ffmpeg', '-i', file,
                    '-filter:v', f'scale={new_width}:{new_height}:flags=lanczos',
                    '-c:a', 'copy',
                    '-c:v', 'libx264',
                    '-crf', '18',
                    '-preset', 'faster',
                    '-y',
                    filename
                ]
            else:
                command = [
                    'ffmpeg', '-i', file,
                    '-filter:v', f'scale={new_width}:{new_height}:flags=lanczos',
                    '-c:a', 'copy',
                    '-c:v', 'libx264',
                    '-crf', '18',
                    '-preset', 'slow',
                    '-y',
                    filename
                ]
            subprocess.run(command, check=True, capture_output=True)
            return filename
        except subprocess.CalledProcessError:
            return None
        except Exception:
            return None
    
    @staticmethod
    def stream(file: str, link: str):
        command = [
            'ffmpeg', '-re',
            '-i', file,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-b:v', '2500k',
            '-maxrate', '2500k',
            '-bufsize', '5000k',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-ar', '44100',
            '-ac', '2',
            '-f', 'flv',
            link
        ]
        return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    @staticmethod
    def thumbnail(file: str):
        try:
            duration = Video.info(file).duration
            midpoint = duration / 2
            name,ext = os.path.splitext(file)
            filename = f'{name}_thumbnail.png'
            subprocess.run([
                'ffmpeg', '-y', '-i', file,
                '-ss', str(midpoint),
                '-vframes', '1',
                '-q:v', '2',
                filename
            ], check=True, capture_output=True)
            return filename
        except Exception:
            return None