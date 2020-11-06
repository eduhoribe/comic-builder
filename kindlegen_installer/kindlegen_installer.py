import hashlib
import os
import sys
import tarfile
import urllib.request
from argparse import ArgumentParser
from logging import warning, fatal
from os import path
from os.path import join
from tempfile import gettempdir as temporary_directory


def kindlegen_linux_install(parser):
    # prepare temporary folder and file
    temp_folder = join(temporary_directory(), 'kindlegen-installer')
    kindlegen_file_path = join(temp_folder, 'kindlegen_linux_2.6_i386_v2_9.tar.gz')
    kindlegen_file_dest = '{}/.local/bin'.format(path.expanduser('~')) if parser.user else '/usr/local/bin'

    # check file integrity
    expected_hash = '5bd4928785ee06d92de1991a34029ffe343c087b4311f52c83df8d821d826b2e42f29e3047c0536140457fd478d300f621648f9eaef3a6568431a791e8147937'

    if path.isfile(kindlegen_file_path):
        with open(kindlegen_file_path, 'rb') as kindlegen_file:
            file_hash = hashlib.sha512(kindlegen_file.read()).hexdigest()

        if file_hash != expected_hash:
            os.remove(kindlegen_file_path)

    path.isdir(temp_folder) or os.makedirs(temp_folder)

    # get file from internet
    if not path.isfile(kindlegen_file_path):
        kindlegen_url = 'https://archive.org/download/kindlegen2.9/kindlegen_linux_2.6_i386_v2_9.tar.gz'
        response = urllib.request.urlopen(kindlegen_url)

        # write file in a temporary file
        with open(kindlegen_file_path, 'wb') as kindlegen_file:
            kindlegen_file.write(response.read())

    # extract kindlegen binary
    with tarfile.open(kindlegen_file_path, 'r') as kindlegen_file:
        try:
            path.isdir(kindlegen_file_dest) or os.makedirs(kindlegen_file_dest)

            kindlegen_file.extract('kindlegen', kindlegen_file_dest)

        except PermissionError:
            warning('User has no permission to create the binary file in "{}"'.format(kindlegen_file_dest))
            warning('Run the command with super user privileges (e.g. sudo) or --user to use the user bin folder')


def kindlegen_mac_install():
    warning('MAC install pending of implementation...')
    sys.exit(1)


def kindlegen_windows_install():
    warning('WIN install pending of implementation...')
    sys.exit(1)


def main():
    # Define and read arguments
    parser = ArgumentParser()
    parser.add_argument('--user', help='Install binary in the user binary folder, instead the system binary folder',
                        action='store_true')
    parser = parser.parse_args()

    if sys.platform.startswith('linux'):
        kindlegen_linux_install(parser)

    elif sys.platform.startswith('mac'):
        kindlegen_mac_install()

    elif sys.platform.startswith('win'):
        kindlegen_windows_install()

    else:
        fatal('Unknown platform "{}"...'.format(sys.platform))
        sys.exit(1)


if __name__ == '__main__':
    main()
