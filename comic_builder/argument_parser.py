import os
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter as Formatter


def build_argument_parser():
    parser = ArgumentParser(
        prog='comic_builder',
        description=(
            'comic_builder is a manga-py auxiliary tool, made for organize and join comic chapters{}'
            'Links:{}'
            '  comic_builder{}'
            '    * source-code.: https://github.com/eduhoribe/comic-builder{}'
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

    required_group = parser.add_argument_group('Required options')
    required_group.add_argument('comic_path', metavar='COMIC_PATH', help='Comic path to be assembled')

    archive_group = parser.add_argument_group('Archive options')
    archive_group.add_argument('--output-format',
                               help='Output format. (Default: %(default)s)',
                               choices=['MOBI', 'EPUB'],
                               default='MOBI'
                               )
    archive_group.add_argument('--output', help='Output folder. (Default: COMIC_PATH/assembled)')
    archive_group.add_argument('--aux-parent-folder',
                               help='Auxiliary parent folder, who will store the images temporally. '
                                    '(Default: System temporary folder)')
    archive_subgroup = archive_group.add_mutually_exclusive_group()
    archive_subgroup.add_argument('--overwrite-existing', help='Writes over existing files', action='store_true')
    archive_subgroup.add_argument('--skip-existing', help='Skip existing files', action='store_true')

    metadata_group = parser.add_argument_group('Metadata options')
    metadata_group.add_argument('--metadata',
                                help='Path to comic metadata file. (Default: COMIC_PATH/info.json) '
                                     'The file must follow the sample in '
                                     'https://github.com/eduhoribe/comic-builder/blob/goshujin-sama/samples/comic-metadata-sample.json')
    metadata_group.add_argument('--title', help='Comic Title')
    metadata_group.add_argument('--authors', help='Comic Authors', nargs='+')

    image_group = parser.add_argument_group('Image processing options')
    image_group.add_argument('--device-profile',
                             help='Device profile. (Default: %(default)s)',
                             choices=['K1', 'K2', 'K34', 'K578', 'KDX', 'KPW', 'KV', 'KO', 'KoMT', 'KoG', 'KoGHD',
                                      'KoA',
                                      'KoAHD', 'KoAH2O', 'KoAO', 'KoF'],
                             default='KO',
                             )
    image_group.add_argument('--comic-style', help='Comic style. (Default: %(default)s)',
                             choices=['DEFAULT', 'MANGA', 'WEBTOON'], default='DEFAULT')
    image_group.add_argument('--no-upscale',
                             help='Do not resize images smaller than device resolution. (NOT RECOMMENDED!)',
                             action="store_true")
    image_group.add_argument('--stretch', help='Stretch images to device resolution. May lose original proportion!',
                             action="store_true")
    image_group.add_argument('--grayscale', help='Apply grayscale filter in all pages', action="store_true")
    image_group.add_argument('--low-quality', help='Omits -hq parameter for kcc', action="store_true")

    misc_group = parser.add_argument_group('Miscellaneous options')
    misc_group.add_argument('--debug', help='Enable debug mode', action="store_true")

    return parser
