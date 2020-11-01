import os
import re
import shutil
import urllib.request
import zipfile
from logging import debug
from logging import warning
from os.path import join

from kindlecomicconverter.comic2ebook import main as kcc_c2e

from chapter import Chapter


def volume_pattern(title, volume_number):
    return '{} - Volume {}'.format(title, volume_number)


def chapter_pattern(chapter_number, chapter_title):
    return 'Chapter {}: {}'.format(chapter_number, chapter_title)


def read_files_as_chapters(files):
    chapters = []

    for file in files:
        with zipfile.ZipFile(file, "r") as zip_file:
            for name in zip_file.namelist():

                if re.search(r'info\.json$', name) is not None:
                    zip_file_data = zip_file.read(name).decode("utf-8")

                    chapters.append(Chapter(zip_file_data, file))

    return chapters


def read_chapters_as_volumes(chapters):
    volumes = {}

    for chapter in chapters:
        if chapter.volume not in volumes:
            volumes[chapter.volume] = []

        volumes_chapters = volumes[chapter.volume]
        volumes_chapters.append(chapter)

    return volumes


def build_comic_info_xml(comic, volume):
    return '''<?xml version="1.0" encoding="utf-8"?>
<ComicInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<Series>{}</Series>
<Volume>{}</Volume>
<Summary>{}</Summary>
<Writer>{}</Writer>
</ComicInfo>'''.format(comic.title, volume, comic.description, list(comic.authors)[0])


def extract_volume_pages(settings, comic, volumes):
    for volume, chapters in volumes.items():
        volume_directory = settings.volume_temp_directory(comic, volume)
        os.mkdir(volume_directory)

        debug('Extracting pages for "{}"...'.format(volume_pattern(volume, comic.title)))

        for chapter in chapters:
            chapter_directory = join(volume_directory, chapter_pattern(chapter.chapter, chapter.title))
            os.mkdir(chapter_directory)

            with zipfile.ZipFile(chapter.local_path, "r") as zip_file:
                for name in zip_file.namelist():
                    with open(join(chapter_directory, name), 'wb') as copy_file:
                        copy_file.write(zip_file.read(name))

            debug('Extracting {}'.format(chapter_pattern(chapter.chapter, chapter.title)))

        # build ComicInfo.xml file
        with open(join(volume_directory, 'ComicInfo.xml'), 'w') as comic_info_xml:
            comic_info_xml.write(build_comic_info_xml(comic, volume))


def assemble_volumes(settings, comic, volumes):
    assembled = {}

    for volume in volumes.keys():
        volume_temp_data = settings.volume_temp_directory(comic, volume)
        os.path.isdir(settings.output) or os.makedirs(settings.output)

        args = [
            '--profile={}'.format(settings.device_profile),
            settings.comic_style_param,
            settings.low_quality_param,
            '--output={}'.format(settings.output),
            '--title={}'.format(comic.title),
            '--format={}'.format(settings.comic_format),
            settings.upscale_param,
            settings.stretch_param,
            settings.grayscale_param,
            volume_temp_data,
        ]
        args = [arg for arg in args if arg != '']  # cleanup kcc args
        debug("kcc args: {}".format(' '.join(args)))
        success = kcc_c2e(args) == 0  # assemble success

        if success:
            assembled[volume] = (
                join(settings.output,
                     '{}.{}'.format(volume_pattern(comic.title, volume), settings.comic_format.lower())))

    return assembled


def chapter_publishers_and_languages(chapters):
    return chapter_publishers(chapters), chapter_languages(chapters)


def chapter_publishers(chapters):
    return set([chapter.publisher for chapter in chapters])


def chapter_languages(chapters):
    return set([chapter.language for chapter in chapters])


def calibre_metadata(settings, comic, chapters, assembled_ebooks):
    if os.system('ebook-meta --version') == 0:
        publishers, languages = chapter_publishers_and_languages(chapters)

        for volume, ebook_file in assembled_ebooks.items():
            cloud_cover_url = comic.covers[int(volume) - 1]
            response = urllib.request.urlopen(cloud_cover_url)

            local_cover_path = join(settings.temp_directory(comic), volume_pattern(comic.title, volume), 'cover')
            with open(local_cover_path, 'wb') as local_cover:
                local_cover.write(response.read())

            args = [
                '--title="{}"'.format(volume_pattern(comic.title, volume)),
                '--authors="{}"'.format('&'.join(author for author in comic.authors)),
                '--cover="{}"'.format(local_cover_path),
                '--comments="{}"'.format(comic.description),
                '--publisher="{}"'.format(', '.join([pub for pub in publishers])),
                '--series="{}"'.format(comic.title),
                '--index="{}"'.format(volume),
                '--identifier uri:"{}"'.format(comic.sauce),
                '--book-producer="{}"'.format(', '.join([pub for pub in publishers])),
                '--language="{}"'.format(', '.join([lang for lang in languages])),
                '--date=""',
                '"{}"'.format(ebook_file)
            ]
            args = [arg for arg in args if arg != '' and arg != '""']
            debug('ebook-meta args: {}'.format(' '.join(args)))
            os.system('ebook-meta {}'.format(' '.join([arg for arg in args])))
    else:
        warning('Calibre is not installed. Skipping metadata edit...')


def clean_temporary_data(temp_directory, assembled_ebooks=None, force_clean=False):
    if assembled_ebooks is None:
        assembled_ebooks = {}

    safe_to_remove_temp_dir = force_clean or len(
        [ebook for ebook in assembled_ebooks.values() if ebook in temp_directory]) == 0

    if safe_to_remove_temp_dir:
        shutil.rmtree(temp_directory)

    else:
        warning(
            'Some books are in the same folder used as auxiliary folder! So the cache cleaning is your responsibility')
