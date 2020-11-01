import json
from logging import error
from os import path
from os.path import join

from comic import Comic


class MangaDexOrgParser:

    @staticmethod
    def parse(comic_info_path):
        comic_info_file = join(comic_info_path, 'info.json')
        comic_info_json = {}

        if path.isfile(comic_info_file):
            with open(comic_info_file, 'r') as comic_info_json:
                comic_info_json = json.load(comic_info_json)
        else:
            error('{} not found'.format(comic_info_file))
            error('Make sure to run manga-py with the parameter "--save-manga-info"')

        return MangaDexOrgParser.__read_json_info__(comic_info_json)

    @staticmethod
    def __read_json_info__(comic_json):
        return Comic(
            title=comic_json['title'],
            description=comic_json['description'],
            alt_titles=set(comic_json['alt_names']),
            authors={comic_json['author'], comic_json['artist']},
            covers=comic_json['covers'],
            sauce=comic_json['sauce']
        )
