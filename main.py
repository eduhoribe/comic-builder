import os
import random
import re
import shutil
import tempfile
import zipfile
from os import listdir
from os.path import isfile, join

from chapter import Chapter

if __name__ == '__main__':
    random_id = hex(hash(random.random()))

    # TODO: Parameterize
    comic_name = 'Youjo Senki'
    directory = '/home/eduwardo/Manga/Youjo Senki'
    temp_directory = '{}/manga-py-assembler/{}_{}'.format(tempfile.gettempdir(), random_id, comic_name)

    print(temp_directory)

    os.makedirs(temp_directory)

    chapters = []
    volumes = {}

    # Read files
    files = [file for file in listdir(directory) if isfile(join(directory, file))]
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
            shutil.copy(chapter.local_path, join(volume_directory, 'chapter_{}'.format(chapter.chapter)))
            print(chapter)

        print()
