import json
from dataclasses import dataclass


@dataclass
class Chapter:
    volume: str
    chapter: str
    title: str
    language: str
    publisher: str
    local_path: str

    @staticmethod
    def from_file(json_string, local_path):
        json_object = json.loads(json_string)

        return Chapter(
            volume=json_object['volume'],
            chapter=json_object['chapter'],
            title=json_object['title'],
            language=json_object['language'],
            publisher=json_object['publisher'],
            local_path=local_path
        )
