import json
import os
import random
import re
import sys
import tempfile
import urllib.request
import zipfile
from argparse import ArgumentParser
from argparse import RawTextHelpFormatter as Formatter
from os import listdir
from os.path import isfile, join

from kindlecomicconverter.comic2ebook import main as kcc_c2e

from chapter import Chapter


def volume_pattern(title, volume_number):
    return '{} - Volume {}'.format(title, volume_number)


def chapter_pattern(chapter_number, chapter_title):
    return 'Chapter {}: {}'.format(chapter_number, chapter_title)


def fatal(message):
    print('fatal: {}'.format(message))
    sys.exit(1)


def debug(message):
    if debug_enabled:
        print('debug: {}'.format(message))


def build_argument_parser():
    parser = ArgumentParser(
        description=(
            'manga-py-assembler is a manga-py auxiliary tool, made for organize and join comic chapters{}'
            'Links:{}'
            '  manga-py-assembler{}'
            '    * source-code.: https://github.com/eduhoribe/manga-py-assembler{}'
            '  manga-py{}'
            '    * site........: https://manga-py.com/manga-py{}'
            '    * source-code.: https://github.com/manga-py/manga-py{}'
        ).format(os.linesep, os.linesep, os.linesep, os.linesep, os.linesep, os.linesep, os.linesep),
        epilog=(
            'So, that is how manga-py-assemble can be executed to join yours favourite comics.{}'
            'Enjoy! ;)'
        ).format(os.linesep),
        formatter_class=Formatter
    )

    parser.add_argument('--comic-path', metavar='$COMIC_PATH', help='Comic path to be assembled', required=True)
    parser.add_argument('--device-profile',
                        help='Device profile',
                        choices=['K1', 'K2', 'K34', 'K578', 'KDX', 'KPW', 'KV', 'KO', 'KoMT', 'KoG', 'KoGHD', 'KoA',
                                 'KoAHD', 'KoAH2O', 'KoAO', 'KoF'],
                        default='KV',
                        )
    parser.add_argument('--title', help='Comic title. IT WILL REPLACES THE KNOWN TITLE!')
    parser.add_argument('--output-format',
                        help='Output format',
                        choices=['MOBI', 'EPUB', 'CBZ', 'KFX'],
                        default='MOBI')
    parser.add_argument('--comic-style', help='Comic style', choices=['DEFAULT', 'MANGA', 'WEBTOON'], default='DEFAULT')

    parser.add_argument('--no-upscale', help='Do not resize images smaller than device resolution', action="store_true")
    parser.add_argument('--stretch', help='Stretch images to device resolution', action="store_true")
    parser.add_argument('--grayscale', help='Apply grayscale filter in all pages', action="store_true")

    parser.add_argument('--output', help='Output folder')
    parser.add_argument('--aux-parent-folder', help='Auxiliary parent folder, who will store the images temporally')
    parser.add_argument('--debug', help='Enable debug mode', action="store_true")
    parser.add_argument('--low-quality', help='Omits -hq parameter for kcc', action="store_true")
    return parser


def read_comic_info(path):
    comic_info_file = join(path, 'info.json')
    comic_info_json = {}

    if os.path.isfile(comic_info_file):
        with open(comic_info_file, 'r') as comic_info_json:
            comic_info_json = json.load(comic_info_json)

    return comic_info_json


if __name__ == '__main__':
    argument_parser = build_argument_parser()
    args = argument_parser.parse_args()

    random_id = hex(hash(random.random()))

    comic_path = args.comic_path
    comic_info = read_comic_info(comic_path)

    comic_title = args.title if args.title is not None else comic_info['title']
    device_profile = args.device_profile
    comic_style_param = '--manga-style' if args.comic_style == 'MANGA' else '--webtoon' if args.comic_style == 'WEBTOON' else ''
    low_quality = args.low_quality
    output = args.output
    comic_format = args.output_format
    no_upscale = args.no_upscale
    stretch = args.stretch
    grayscale = args.grayscale
    auxiliary_folder = args.aux_parent_folder
    debug_enabled = args.debug

    temp_directory = '{}/manga-py-assembler/{}_{}'.format(
        auxiliary_folder if auxiliary_folder is not None else tempfile.gettempdir(),
        random_id,
        comic_title
    )

    if os.path.isdir(temp_directory):
        fatal('directory {} exists...somehow'.format(temp_directory))

    debug('using temporary directory "{}"'.format(temp_directory))
    os.makedirs(temp_directory)

    chapters = []
    volumes = {}
    assembled_ebooks = {}

    publishers = set()
    languages = set()

    # Find files
    files = [file for file in listdir(comic_path) if isfile(join(comic_path, file)) and file.endswith('.zip')]

    # Search for chapters
    for f in files:
        with zipfile.ZipFile(join(comic_path, f), "r") as zip_file:
            for name in zip_file.namelist():

                if re.search(r'info\.json$', name) is not None:
                    zip_file_data = zip_file.read(name).decode("utf-8")

                    chapter = Chapter(zip_file_data, join(comic_path, f))

                    chapters.append(chapter)

                    publishers.add(chapter.publisher)
                    languages.add(chapter.language)

    # Merge chapters in volumes
    for chapter in chapters:
        if chapter.volume not in volumes:
            volumes[chapter.volume] = []

        volumes_chapters = volumes[chapter.volume]
        volumes_chapters.append(chapter)

    # Extract chapter pages
    for volume, chapters in volumes.items():
        volume_directory = join(temp_directory, volume_pattern(comic_title, volume))
        os.mkdir(volume_directory)

        debug('Extracting pages for "{}"...'.format(volume_pattern(volume, comic_title)))

        for chapter in chapters:
            chapter_directory = join(volume_directory, chapter_pattern(chapter.chapter, chapter.title))
            os.mkdir(chapter_directory)

            with zipfile.ZipFile(chapter.local_path, "r") as zip_file:
                for name in zip_file.namelist():
                    with open(join(chapter_directory, name), 'wb') as copy_file:
                        copy_file.write(zip_file.read(name))

            debug('Extracting {}'.format(chapter_pattern(chapter.chapter, chapter.title)))

    # todo remove temp data
    for volume in volumes.keys():
        volume_temp_data = join(temp_directory, volume_pattern(comic_title, volume))
        volume_output = output if output is not None else join(comic_path, 'assembled')
        os.path.isdir(volume_output) or os.makedirs(volume_output)

        args = [
            '--profile={}'.format(device_profile),
            comic_style_param,
            '' if low_quality else '--hq',
            '--output={}'.format(volume_output),
            '--title="{}"'.format(comic_title),
            '--format={}'.format(comic_format),
            '' if no_upscale else '--upscale',
            '--stretch' if stretch else '',
            '' if grayscale else '--forcecolor',
            volume_temp_data,
        ]
        args = [arg for arg in args if arg != '']

        success = kcc_c2e(args) == 0  # success exit code

        if success:
            assembled_ebooks[volume] = (
                join(volume_output, '{}.{}'.format(volume_pattern(comic_title, volume), comic_format.lower())))

    # Calibre metadata
    if os.system('ebook-meta --version') == 0:
        for volume, ebook_file in assembled_ebooks.items():
            cloud_cover_url = comic_info['covers'][int(volume) - 1]
            response = urllib.request.urlopen(cloud_cover_url)

            local_cover_path = join(temp_directory, volume_pattern(comic_title, volume), 'cover')
            with open(local_cover_path, 'wb') as local_cover:
                local_cover.write(response.read())

            authors = {comic_info['author'], comic_info['artist']}

            args = [
                '--title="{}"'.format(volume_pattern(comic_info['title'], volume)),
                '--authors="{}"'.format('&'.join(a for a in authors)),
                '--cover="{}"'.format(local_cover_path),
                '--comments="{}"'.format(comic_info['description']),
                '--publisher="{}"'.format(', '.join([pub for pub in publishers])),
                '--series="{}"'.format(comic_info['title']),
                '--index="{}"'.format(volume),
                '--identifier uri:"{}"'.format(comic_info['sauce']),
                # '--tags="{}"',
                '--book-producer="{}"'.format(', '.join([pub for pub in publishers])),
                '--language="{}"'.format(', '.join([lang for lang in languages])),
                '--date=""',
                '"{}"'.format(ebook_file)
            ]
            args = [arg for arg in args if arg != '' and arg != '""']
            os.system('ebook-meta {}'.format(' '.join([arg for arg in args])))
