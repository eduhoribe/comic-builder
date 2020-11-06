import random
from dataclasses import dataclass
from os import listdir
from os.path import isfile, join
from tempfile import gettempdir as temporary_directory

from . import utils


@dataclass
class Settings:
    random_id: str
    comic_path: str
    device_profile: str
    comic_style: str
    low_quality: bool
    output: str
    comic_format: str
    no_upscale: bool
    stretch: bool
    grayscale: bool
    auxiliary_folder: str
    overwrite_existing: bool
    skip_existing: bool
    debug_enabled = bool

    def __init__(self, args):
        self.random_id = hex(hash(random.random()))

        self.comic_path = args.comic_path
        self.metadata_path = self.__prepare_metadata_path__(args.metadata)
        self.device_profile = args.device_profile
        self.comic_style = args.comic_style
        self.low_quality = args.low_quality
        self.output = self.__prepare_output__(args.output)
        self.comic_format = args.output_format
        self.no_upscale = args.no_upscale
        self.stretch = args.stretch
        self.grayscale = args.grayscale
        self.auxiliary_folder = args.aux_parent_folder
        self.overwrite_existing = args.overwrite_existing
        self.skip_existing = args.skip_existing
        self.debug_enabled = args.debug

    @property
    def device_comic_format_kcc(self):
        return 'EPUB'

    @property
    def device_comic_format_kcc_param(self):
        return '--format={}'.format(self.device_comic_format_kcc)

    @property
    def device_profile_kcc_param(self):
        return '--profile={}'.format(self.device_profile)

    @property
    def comic_style_param(self):
        if self.comic_style == 'MANGA':
            return '--manga-style'

        elif self.comic_style == 'WEBTOON':
            return '--webtoon'

        return ''

    @property
    def low_quality_param(self):
        return '' if self.low_quality else '--hq'

    @property
    def output_param(self):
        return '--output={}'.format(self.output)

    @property
    def upscale_param(self):
        return '' if self.no_upscale else '--upscale'

    @property
    def stretch_param(self):
        return '--stretch' if self.stretch else ''

    @property
    def grayscale_param(self):
        return '' if self.grayscale else '--forcecolor'

    def temp_directory(self, comic):
        return '{}/comic_builder/{}_{}'.format(
            self.auxiliary_folder if self.auxiliary_folder is not None else temporary_directory(),
            self.random_id,
            comic.title
        )

    def volume_temp_directory(self, comic, volume):
        return join(self.temp_directory(comic), utils.escape_file_path(utils.volume_pattern(comic.title, volume)))

    def read_files(self):
        return [join(self.comic_path, file) for file in listdir(self.comic_path)
                if isfile(join(self.comic_path, file)) and file.endswith('.zip')]

    def __prepare_output__(self, output):
        return output if output is not None else join(self.comic_path, 'assembled')

    def __prepare_metadata_path__(self, metadata_path):
        return metadata_path if metadata_path is not None else join(self.comic_path, 'info.json')
