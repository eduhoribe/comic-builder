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
    directory = '/home/eduhoribe/Manga/Youjo Senki'

    temp_directory = '{}/manga-py-assembler/{}_{}'.format(
        auxiliary_folder if auxiliary_folder is not None else tempfile.gettempdir(), random_id, comic_title)

    print(temp_directory)

    os.makedirs(temp_directory)

    chapters = []
    volumes = {}

    # Read files
    files = [file for file in listdir(directory) if isfile(join(directory, file)) and file.endswith('.zip')]
    for f in files:
        with zipfile.ZipFile(join(directory, f), "r") as zip_file:
            for name in zip_file.namelist():

                if re.search(r'info\.json$', name) is not None:
                    zip_file_data = zip_file.read(name).decode("utf-8")

                    chapter = Chapter(zip_file_data, join(directory, f))

                    chapters.append(chapter)

    # Merge volumes
    for chapter in chapters:
        if chapter.volume not in volumes:
            volumes[chapter.volume] = []

        volumes_chapters = volumes[chapter.volume]
        volumes_chapters.append(chapter)

    for volume, chapters in volumes.items():
        volume_directory = join(temp_directory, 'volume_{}'.format(volume))
        os.mkdir(volume_directory)

        print(volume)

        for chapter in chapters:
            chapter_directory = join(volume_directory, 'chapter_{}'.format(chapter.chapter))
            os.mkdir(chapter_directory)

            with zipfile.ZipFile(chapter.local_path, "r") as zip_file:
                for name in zip_file.namelist():
                    with open(join(chapter_directory, name), 'wb') as copy_file:
                        copy_file.write(zip_file.read(name))

            print(chapter)

        print()
        break

    assembled_ebooks = []

    for volume in volumes.keys():
        volume_temp_data = join(temp_directory, 'volume_{}'.format(volume))
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

        if success:
            shutil.rmtree(volume_temp_data)
            assembled_ebooks.append(join(volume_output, 'volume_{}.{}'.format(volume, comic_format.lower())))

            break

    # Calibre metadata
    if os.system('ebook-meta --version') == 0:
        for ebook_file in assembled_ebooks:
            args = [
                '--title="{}"'.format(comic_title),
                '--authors="{}"'.format('YARE YARE DAZE'),
                # '--cover="{}"',
                # '--comments="{}"',
                # '--publisher="{}"',
                # '--category="{}"',
                # '--series="{}"',
                # '--index="{}"',
                # '--identifier="{}"',
                # '--tags="{}"',
                # '--language="{}"',
                # '--date="{}"',
                '"{}"'.format(ebook_file)
            ]
            args = [arg for arg in args if arg != '' and arg != '""']
            os.system('ebook-meta {}'.format(' '.join([arg for arg in args])))
