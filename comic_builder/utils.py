import os
import shutil
import urllib.request
import zipfile
from html import unescape as html_unescape
from logging import debug, warning, error, info
from os.path import join
from subprocess import STDOUT, PIPE
from xml.sax.saxutils import escape as xml_escape

import ruamel.std.zipfile as zip_utils
from kindlecomicconverter.comic2ebook import main as kcc_c2e
from psutil import Popen

from .chapter import Chapter
from .comic import Comic


def escape_file_path(path: str):
    return path.replace(os.sep, '|')


def chapter_temp_directory_name(chapter):
    return chapter_pattern(chapter.chapter, escape_file_path(chapter.title))


def volume_pattern(title, volume: str):
    if volume.isnumeric():
        return '{} - Volume {}'.format(title, volume)

    if volume.strip() != '':
        return '{} - {}'.format(title, volume)

    return '{}'.format(title)


def chapter_pattern(chapter_number, chapter_title: str):
    if chapter_title is None or chapter_title.strip() == '':
        return 'Chapter {}'.format(chapter_number)

    return 'Chapter {}: {}'.format(chapter_number, chapter_title)


def read_files_as_chapters(files):
    chapters = []

    chapter_metadata_filename = 'eduhoribe.json'

    for file in files:
        with zipfile.ZipFile(file, "r") as zip_file:
            if chapter_metadata_filename in zip_file.namelist():
                info_file = [file for file in zip_file.namelist() if file == chapter_metadata_filename][0]
                zip_file_data = zip_file.read(info_file).decode("utf-8")

                chapters.append(Chapter.from_file(zip_file_data, file))

            else:
                chapter_info = zip_file.filename.rsplit(os.sep, 1)[1].replace('.zip', '').rsplit('-', 1)
                chapter_number = ''.join([letter for letter in chapter_info[0] if letter.isnumeric()]).strip('0')
                chapter_language = chapter_info[1]
                chapters.append(
                    Chapter(volume='Single Volume',
                            chapter=chapter_number,
                            title='',
                            language=chapter_language,
                            publisher='',
                            local_path=file
                            )
                )

    return chapters


def read_chapters_as_volumes(chapters):
    volumes = {}

    for chapter in chapters:
        if chapter.volume not in volumes:
            volumes[chapter.volume] = []

        volumes_chapters = volumes[chapter.volume]
        volumes_chapters.append(chapter)

    return volumes


def escape_text(text):
    return xml_escape(html_unescape(text))


def build_comic_info_author_xml(authors: list):
    authors_str = escape_text(', '.join(authors))

    return '<Writer>{}</Writer>'.format(authors_str) if authors != '' else ''


def build_comic_info_xml(comic: Comic, volume):
    series_val = escape_text(volume_pattern(comic.title, volume))
    summary_val = escape_text(comic.description)

    series_tag = '<Series>{}</Series>'.format(series_val) if series_val != '' else ''
    summary_tag = '<Summary>{}</Summary>'.format(summary_val) if summary_val != '' else ''

    return '''<?xml version="1.0" encoding="utf-8"?>
<ComicInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
{}
{}
{}
</ComicInfo>'''.format(series_tag, summary_tag, build_comic_info_author_xml(comic.authors))


def extract_volume_pages(settings, comic, volumes):
    for volume, chapters in volumes.items():
        volume_directory = settings.volume_temp_directory(comic, volume)
        os.mkdir(volume_directory)

        debug('Extracting pages for "{}"...'.format(volume_pattern(comic.title, volume)))

        for chapter in chapters:
            chapter_directory = join(volume_directory, chapter_temp_directory_name(chapter))
            os.mkdir(chapter_directory)

            with zipfile.ZipFile(chapter.local_path, "r") as zip_file:
                for name in zip_file.namelist():
                    with open(join(chapter_directory, name), 'wb') as copy_file:
                        copy_file.write(zip_file.read(name))

            debug('Extracting {}'.format(chapter_pattern(chapter.chapter, chapter.title)))

        # build ComicInfo.xml file
        with open(join(volume_directory, 'ComicInfo.xml'), 'w') as comic_info_xml:
            comic_info_xml.write(build_comic_info_xml(comic, volume))


def get_available_file(file):
    if not os.path.exists(file):
        return file

    file_name = file.rsplit('.', 1)
    file_pattern = os.path.join(file_name[0] + ' ({}).' + file_name[1])
    postfix = 0

    while os.path.exists(file_pattern.format(postfix)):
        postfix += 1

    return file_pattern.format(postfix)


def assemble_volumes(settings, comic, volumes):
    assembled = {}

    for volume in volumes.keys():
        final_output_file = join(settings.output,
                                 '{}.{}'.format(volume_pattern(comic.title, volume), settings.comic_format.lower()))

        if os.path.exists(final_output_file):
            info('File "{}" already exists'.format(final_output_file))

            if settings.skip_existing:
                info('Skipping...')
                continue

            if settings.overwrite_existing:
                debug('Overwriting...')
                os.remove(final_output_file)

        volume_temp_data = settings.volume_temp_directory(comic, volume)
        os.path.isdir(settings.output) or os.makedirs(settings.output)

        output_file = join(settings.output,
                           '{}.{}'.format(volume_pattern(comic.title, volume),
                                          settings.device_comic_format_kcc.lower()))

        output_file = get_available_file(output_file)

        args = [
            settings.device_profile_kcc_param,
            settings.comic_style_param,
            settings.low_quality_param,
            settings.output_param,
            '--title={}'.format(volume_pattern(comic.title, volume)),
            settings.device_comic_format_kcc_param,
            settings.upscale_param,
            settings.stretch_param,
            settings.grayscale_param,
            '--output={}'.format(output_file),
            volume_temp_data,
        ]
        args = [arg for arg in args if arg != '']  # cleanup kcc args
        debug("kcc args: {}".format(' '.join(args)))

        success = kcc_c2e(args) == 0  # assemble success

        if success:
            assembled[volume] = output_file

    return assembled


def chapter_publishers_and_languages(chapters):
    return chapter_publishers(chapters), chapter_languages(chapters)


def chapter_publishers(chapters):
    return set([chapter.publisher for chapter in chapters])


def chapter_languages(chapters):
    return set([chapter.language for chapter in chapters])


def fill_metadata(settings, comic, chapters, assembled_ebooks):
    publishers, languages = chapter_publishers_and_languages(chapters)

    for volume, ebook_file in assembled_ebooks.items():
        if volume not in comic.volume_covers:
            warning('Volume "{}" not found in the list of covers...'.format(volume))
            continue

        cloud_cover_url = comic.volume_covers[volume]
        response = urllib.request.urlopen(cloud_cover_url)

        local_cover_path = join(settings.temp_directory(comic), volume_pattern(comic.title, volume), 'cover')

        with open(local_cover_path, 'wb') as local_cover:
            local_cover_bytes = response.read()
            local_cover.write(local_cover_bytes)

        zip_cover_path = join('OEBPS', 'Images', 'cover.jpg')
        zip_utils.delete_from_zip_file(ebook_file, file_names=zip_cover_path)

        with zipfile.ZipFile(ebook_file, 'a') as ebook:
            ebook.write(local_cover_path, zip_cover_path)


def convert_to_mobi(assembled_ebooks):
    converted_ebooks = {}

    kindle_gen_exists = Popen('kindlegen', stdout=PIPE, stderr=STDOUT, stdin=PIPE, shell=True)
    kindle_gen_exists.communicate()

    if kindle_gen_exists.returncode == 0:
        for volume, ebook_file in assembled_ebooks.items():
            info('Converting file "{}" to MOBI...'.format(ebook_file))

            kindle_gen_convert = Popen(
                'kindlegen "{}" -c2'.format(ebook_file),
                stdout=PIPE,
                stderr=STDOUT,
                stdin=PIPE,
                shell=True
            )
            kindle_gen_convert.communicate()

            if kindle_gen_convert.returncode != 0:
                error('Error to convert file "{}" to MOBI'.format(ebook_file))
                continue

            os.remove(ebook_file)
            converted_ebooks[volume] = os.path.join(ebook_file, str(ebook_file).replace('.epub', '.mobi'))
    else:
        warning('KindleGen not found!')

    return converted_ebooks


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
