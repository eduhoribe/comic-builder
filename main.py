import urllib.request
import json
import os
import random
import re
import shutil
import tempfile
import zipfile
from os import listdir
from os.path import isfile, join

from kindlecomicconverter.comic2ebook import main as kcc_c2e

from chapter import Chapter
from comic_style import ComicStyle

if __name__ == '__main__':
    random_id = hex(hash(random.random()))

    # TODO: Parameterize
    directory = 'Manga/Youjo Senki'

    manga_info_file = join(directory, 'info.json')

    manga_info = {}
    if os.path.isfile(manga_info_file):
        with open(manga_info_file, 'r') as manga_info:
            manga_info = json.load(manga_info)

    # TODO: Parameterize
    device_profile = 'KO'  # TODO ENUM
    comic_style = ComicStyle.NORMAL
    low_quality = False
    output = None
    comic_title = 'Youjo Senki'
    comic_format = 'MOBI'  # TODO ENUM
    upscale = True
    stretch = True
    grayscale = False
    auxiliary_folder = '/home/eduhoribe'

    temp_directory = '{}/manga-py-assembler/{}_{}'.format(
        auxiliary_folder if auxiliary_folder is not None else tempfile.gettempdir(), random_id, comic_title)

    print(temp_directory)

    os.makedirs(temp_directory)

    chapters = []
    volumes = {}

    publishers = set()
    languages = set()

    # Read files
    files = [file for file in listdir(directory) if isfile(join(directory, file)) and file.endswith('.zip')]
    for f in files:
        with zipfile.ZipFile(join(directory, f), "r") as zip_file:
            for name in zip_file.namelist():

                if re.search(r'info\.json$', name) is not None:
                    zip_file_data = zip_file.read(name).decode("utf-8")

                    chapter = Chapter(zip_file_data, join(directory, f))

                    chapters.append(chapter)

                    publishers.add(chapter.publisher)
                    languages.add(chapter.language)

    # Merge volumes
    for chapter in chapters:
        if chapter.volume not in volumes:
            volumes[chapter.volume] = []

        volumes_chapters = volumes[chapter.volume]
        volumes_chapters.append(chapter)

    for volume, chapters in volumes.items():
        volume_directory = join(temp_directory, '{} - Volume {}'.format(comic_title, volume))
        os.mkdir(volume_directory)

        print(volume)

        for chapter in chapters:
            chapter_directory = join(volume_directory, 'Chapter {}: {}'.format(chapter.chapter, chapter.title))
            os.mkdir(chapter_directory)

            with zipfile.ZipFile(chapter.local_path, "r") as zip_file:
                for name in zip_file.namelist():
                    with open(join(chapter_directory, name), 'wb') as copy_file:
                        copy_file.write(zip_file.read(name))

            print(chapter)

        print()
        break

    assembled_ebooks = {}

    for volume in volumes.keys():
        volume_temp_data = join(temp_directory, '{} - Volume {}'.format(comic_title, volume))
        volume_output = output if output is not None else join(directory, 'assembled')
        if not os.path.isdir(volume_output):
            os.makedirs(volume_output)

        args = [
            '--profile={}'.format(device_profile),
            comic_style.value,
            '' if low_quality else '--hq',
            '--output={}'.format(volume_output),
            '--title="{}"'.format(comic_title),
            '--format={}'.format(comic_format),
            '--upscale' if upscale else '',
            '--stretch' if stretch else '',
            '' if grayscale else '--forcecolor',
            volume_temp_data,
        ]
        args = [arg for arg in args if arg != '']

        success = kcc_c2e(args) == 0  # success exit code

        # if success:
        #     shutil.rmtree(volume_temp_data)
        assembled_ebooks[volume] = (
            join(volume_output, '{} - Volume {}.{}'.format(comic_title, volume, comic_format.lower())))

        break

    # Calibre metadata
    if os.system('ebook-meta --version') == 0:
        for volume, ebook_file in assembled_ebooks.items():
            cloud_cover_url = manga_info['covers'][int(volume) - 1]
            response = urllib.request.urlopen(cloud_cover_url)

            local_cover_path = join(temp_directory, '{} - Volume {}'.format(comic_title, volume), 'cover')
            with open(local_cover_path, 'wb') as local_cover:
                local_cover.write(response.read())

            authors = {manga_info['author'], manga_info['artist']}

            args = [
                '--title="{} - Volume {}"'.format(manga_info['title'], volume),
                '--authors="{}"'.format('&'.join(a for a in authors)),
                '--cover="{}"'.format(local_cover_path),
                '--comments="{}"'.format(manga_info['description']),
                '--publisher="{}"'.format(', '.join([pub for pub in publishers])),
                '--series="{}"'.format(manga_info['title']),
                '--index="{}"'.format(volume),
                '--identifier uri:"{}"'.format(manga_info['sauce']),
                # '--tags="{}"',
                '--book-producer="{}"'.format(', '.join([pub for pub in publishers])),
                '--language="{}"'.format(', '.join([lang for lang in languages])),
                '--date=""',
                '"{}"'.format(ebook_file)
            ]
            args = [arg for arg in args if arg != '' and arg != '""']
            os.system('ebook-meta {}'.format(' '.join([arg for arg in args])))
