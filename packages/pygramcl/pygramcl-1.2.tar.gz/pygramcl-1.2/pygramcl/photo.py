from PIL import Image, ImageDraw, ImageFont
from typing import Union, Optional
from .parser import Parser
from enum import Enum

import os

class Photo:
    
    @staticmethod
    def rgb(file: str):
        try:
            with Image.open(file) as img:
                rgb = img.convert('RGB')
                name,ext = os.path.splitext(file)
                filename = f'{name}_rgb{ext}'
                rgb.save(filename)
                return filename
        except Exception:
            return None
    
    @staticmethod
    def info(file: str):
        try:
            with Image.open(file) as img:
                return Parser.photo({
                    'size': img.size,
                    'mode': img.mode,
                    'width': img.width,
                    'height': img.height
                })
        except Exception:
            return None
    
    @staticmethod
    def crop(file: str, ratio: Optional[str] = None):
        if not ratio or not ratio.lower() in ('square', 'portrait', 'landscape'):
            return ValueError('Ratio must be square, portrait or landscape')
        target_sizes = {
            'square': (1080, 1080),
            'portrait': (1080, 1920),
            'landscape': (1920, 1080)
        }
        try:
            if not os.path.exists(file):
                return None
            with Image.open(file) as img:
                if img.mode not in ('RGB'):
                    img = img.convert('RGB')
                data = list(img.getdata())
                clean_img = Image.new(img.mode, img.size)
                clean_img.putdata(data)
                img = clean_img
                width, height = img.size
                target_width, target_height = target_sizes[ratio.lower()]
                target_aspect = target_width / target_height
                current_aspect = width / height
                if ratio.lower() == 'square':
                    size = min(width, height)
                    left = (width - size) // 2
                    top = (height - size) // 2
                    right = left + size
                    bottom = top + size
                elif ratio.lower() == 'portrait':
                    if current_aspect > target_aspect:
                        new_width = int(height * target_aspect)
                        left = (width - new_width) // 2
                        top = 0
                        right = left + new_width
                        bottom = height
                    else:
                        new_height = int(width / target_aspect)
                        left = 0
                        top = (height - new_height) // 2
                        right = width
                        bottom = top + new_height
                elif ratio.lower() == 'landscape':
                    if current_aspect > target_aspect:
                        new_width = int(height * target_aspect)
                        left = (width - new_width) // 2
                        top = 0
                        right = left + new_width
                        bottom = height
                    else:
                        new_height = int(width / target_aspect)
                        left = 0
                        top = (height - new_height) // 2
                        right = width
                        bottom = top + new_height
                left = max(0, left)
                top = max(0, top)
                right = min(width, right)
                bottom = min(height, bottom)
                cropped = img.crop((left, top, right, bottom))
                cropped = cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)
                name, ext = os.path.splitext(file)
                filename = f'{name}_{ratio.lower()}{ext}'
                cropped.save(filename, quality=95, optimize=True)
                return filename
        except Exception:
            return None
    
    @staticmethod
    def scale(file: str, factor: float = None):
        if not factor or not isinstance(factor, float):
            raise ValueError('Factor must be float (example: 2.0)')
        if factor <= 0:
            raise ValueError('Factor must be greater than 0')
        try:
            with Image.open(file) as img:
                width, height = img.size
                to_width = int(width * factor)
                to_height = int(height * factor)
                scaled = img.resize((to_width, to_height), Image.Resampling.LANCZOS)
                name, ext = os.path.splitext(file)
                filename = f'{name}_scaled_{factor}{ext}'
                scaled.save(filename, quality=95, optimize=True)
                return filename
        except Exception:
            return None