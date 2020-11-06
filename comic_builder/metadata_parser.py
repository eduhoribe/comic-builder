import json
import sys
from logging import fatal
from os import path

from .comic import Comic


class MetadataParser:

    @staticmethod
    def parse(metadata_file):
        if path.isfile(metadata_file):
            with open(metadata_file, 'r') as comic_info_json:
                comic_info_json = json.load(comic_info_json)
        else:
            fatal('Metadata file "{}" not found'.format(metadata_file))
            sys.exit(1)

        return MetadataParser.__read_json_info__(comic_info_json)

    @staticmethod
    def __read_json_info__(comic_json):
        return Comic(
            title=comic_json['title'],
            description=comic_json['description'],
            authors=comic_json['authors'],
            sauce=comic_json['sauce'],
            volume_covers=comic_json['volume_covers']
        )
