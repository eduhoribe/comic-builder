import logging
import os
import sys
from logging import fatal, debug, info, warning
from os import path

from . import utils
from .argument_parser import build_argument_parser
from .metadata_parser import MetadataParser
from .settings import Settings


def main():
    # Read arguments
    argument_parser = build_argument_parser()
    args = argument_parser.parse_args()

    # Define settings and log level
    settings = Settings(args)
    logging.getLogger().setLevel(logging.DEBUG if settings.debug_enabled else logging.INFO)
    debug(args)
    debug(settings)

    if not path.isdir(settings.comic_path):
        fatal('Comic path "{}" does not exist'.format(path.abspath(settings.comic_path)))
        sys.exit(1)

    # Read comic info
    comic = MetadataParser.parse(settings.metadata_path)
    comic.overwrite_user_metadata(args)
    debug(comic)

    # Prepare temporary directory
    temp_directory = settings.temp_directory(comic)
    if path.isdir(temp_directory):
        fatal('Directory {} exists...somehow. Stopping right here to prevent a bigger mess'.format(temp_directory))
        sys.exit(1)

    debug('Using temporary directory "{}"'.format(temp_directory))
    os.makedirs(temp_directory)

    # Find files
    files = settings.read_files()

    # Search for chapters
    chapters = utils.read_files_as_chapters(files)
    if len(chapters) == 0:
        warning('No chapter saved was found!')

        utils.clean_temporary_data(temp_directory, force_clean=True)

        sys.exit(1)

    # Merge chapters in volumes
    volumes = utils.read_chapters_as_volumes(chapters)

    # Extract chapter pages
    utils.extract_volume_pages(settings, comic, volumes)

    # Assemble volumes in ebook format
    assembled_ebooks = utils.assemble_volumes(settings, comic, volumes)
    if len(assembled_ebooks) <= 0:
        warning('No file was assembled!')
        sys.exit(0)

    # Fill metadata
    utils.fill_metadata(settings, comic, chapters, assembled_ebooks)

    # Convert to MOBI
    if settings.comic_format == 'MOBI':
        assembled_ebooks = utils.convert_to_mobi(assembled_ebooks)

    # Show results
    info('Finished!')
    if len(assembled_ebooks) > 0:
        info('Files can be found in: {}'.format(path.abspath(settings.output)))
    else:
        warning('No file was assembled!')

    # Remove temporary data
    utils.clean_temporary_data(temp_directory, assembled_ebooks)


if __name__ == '__main__':
    main()