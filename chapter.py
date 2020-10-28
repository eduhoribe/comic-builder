import json
from dataclasses import dataclass


@dataclass
class Chapter:
    volume: float
    chapter: float
    title: str
    language: str
    publisher: str
    local_path: str

    def __init__(self, json_string, local_path):
        json_object = json.loads(json_string)

        self.volume = json_object['volume']
        self.chapter = json_object['chapter']
        self.title = json_object['title']
        self.language = json_object['lang_name']
        self.publisher = json_object['group_name']
        self.local_path = local_path
