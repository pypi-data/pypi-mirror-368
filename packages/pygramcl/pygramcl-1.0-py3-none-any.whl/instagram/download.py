from typing import List, Optional
from urllib.parse import urlparse
from datetime import datetime
from .parser import Parser

import os
import requests

class Download:
    
    @staticmethod
    def from_url(url: str, filename: Optional[str] = None, directory: Optional[str] = None):
        try:
            directory = directory if directory is not None else 'download'
            os.makedirs(directory, exist_ok=True)
            if not filename:
                parsed = urlparse(url)
                filename = os.path.basename(parsed.path)
                if not filename or '.' not in filename:
                    filename = f'download_{str(datetime.now().strftime("%Y%m%d%H%M%S"))}'
                if 'instagram' in url:
                    _, exts = os.path.splitext(filename)
                    filename = f'instagram_{str(datetime.now().strftime("%Y%m%d%H%M%S"))}{exts}'
            if '.' not in filename:
                pathname = os.path.basename(urlparse(url).path)
                if '.' in pathname:
                    _, exts = os.path.splitext(pathname)
                    filename = f'{filename}{exts}'
            name, exts = os.path.splitext(filename)
            counting = 0
            original = filename
            filepath = os.path.join(directory, filename)
            while os.path.exists(filepath):
                counting = counting + 1
                filename = f'{name}_{counting}{exts}'
                filepath = os.path.join(directory, filename)
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            filesize = os.path.getsize(filepath) / (1024 * 1024)
            return Parser.file({'file': filepath, 'size': f'{filesize:.2f} MiB'})
        except Exception:
            return None
    
    @staticmethod
    def multiple_url(urls: List[str], filenames: List[str] = None, directory: Optional[str] = None):
        if not isinstance(filenames, list):
            filenames = [filenames]
        download = []
        for idx, url in enumerate(urls):
            try:
                filename = filenames[idx] if filenames and idx < len(filenames) else None
                filedata = Download.from_url(url, filename, directory)
                if filedata:
                    download.append(filedata)
            except Exception:
                continue
        return download