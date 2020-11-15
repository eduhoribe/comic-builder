import sys
import zipfile
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter as Formatter
from logging import fatal
from os import path, listdir
from os.path import isfile, join

import ruamel.std.zipfile as zip_utils


def build_argument_parser():
    parser = ArgumentParser(
        prog='metadata-injector',
        description=(
            'metadata-injector is a comic_builder auxiliary tool, made to insert metadata in comic chapters'
        ),
        formatter_class=Formatter
    )
    parser.add_argument(
        'chapter_dir',
        metavar='CHAPTER_DIR',
        help='Chapter directory with zip files that will receive the metadata in the same path with the same name',
    )
    return parser


def main():
    # Read arguments
    argument_parser = build_argument_parser()
    args = argument_parser.parse_args()

    chapter_dir = args.chapter_dir
    chapter_metadata_filename = 'eduhoribe.json'

    if not path.isdir(chapter_dir):
        fatal('Directory "{}" does not exists'.format(chapter_dir))
        sys.exit(1)

    zip_files = [join(chapter_dir, file) for file in listdir(chapter_dir) if file.endswith('.zip')]
    metadata_chapters = {
        file: file.rstrip('.zip') + '.json'
        for file in zip_files if isfile(file.rstrip('.zip') + '.json')
    }

    for chapter, metadata in metadata_chapters.items():
        with zipfile.ZipFile(chapter, 'r') as zip_file:
            contains_metadata = len([file for file in zip_file.namelist() if file == chapter_metadata_filename]) > 0

        if contains_metadata:
            zip_utils.delete_from_zip_file(chapter, file_names=chapter_metadata_filename)

        with zipfile.ZipFile(chapter, 'a') as zip_file:
            zip_file.write(metadata, chapter_metadata_filename)


if __name__ == '__main__':
    main()
