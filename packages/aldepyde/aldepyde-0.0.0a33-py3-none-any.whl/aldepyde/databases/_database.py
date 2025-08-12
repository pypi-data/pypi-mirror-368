from abc import ABC, abstractmethod
import gzip
import requests
import os
from typing import Tuple, BinaryIO
from io import TextIOWrapper

class _database(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def fetch(self, url):
        pass

    @abstractmethod
    def fetch_code(self, codes):
        pass

    @abstractmethod
    def parse(self, text):
        pass

    @staticmethod
    def open_stream(source:str) -> Tuple[BinaryIO, int] | None:
        if source.startswith('http://') or source.startswith('https://'):
            resp = requests.get(source, stream=True)
            resp.raise_for_status()
            length = resp.headers.get("Content-Length")
            return resp.raw, int(length) if length else None
        else:
            size = os.path.getsize(source)
            return open(source, 'rb'), size



    # Yes, I know the first conditionals do the same thing

    def __call__(self):
        pass