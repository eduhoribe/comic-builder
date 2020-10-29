from enum import Enum


class ComicStyle(Enum):
    NORMAL = ''
    MANGA = '--manga-style'
    WEBTOON = '--webtoon'

    @staticmethod
    def from_parameter(parameter):
        if parameter == ComicStyle.MANGA.value:
            return ComicStyle.MANGA

        elif parameter == ComicStyle.MANGA.value:
            return ComicStyle.WEBTOON

        else:
            return ComicStyle.NORMAL
