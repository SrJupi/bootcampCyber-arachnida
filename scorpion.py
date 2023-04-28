# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    scorpion.py                                        :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: lsulzbac <lsulzbac@student.42barcel>       +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2023/04/20 12:26:54 by lsulzbac          #+#    #+#              #
#    Updated: 2023/04/20 12:27:02 by lsulzbac         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import argparse
import os
import datetime
import stat
from PIL import Image
from PIL.ExifTags import TAGS
from functools import reduce

ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']


def file_with_allowed_extension(filename):
    """Check if a file has an allowed extension"""

    ext = os.path.splitext(filename)[-1]
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise argparse.ArgumentTypeError(f"Invalid file extension: {filename}")
    return filename


def convert_bytes_to_human_readable(size_in_bytes):
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0

    while size_in_bytes >= 1000 and unit_index < len(units) - 1:
        size_in_bytes /= 1000
        unit_index += 1

    return f"{round(size_in_bytes)} {units[unit_index]}"


def get_mode_info(mode):
    permissions = ""
    if mode & stat.S_IRUSR:
        permissions += "r"
    else:
        permissions += "-"
    if mode & stat.S_IWUSR:
        permissions += "w"
    else:
        permissions += "-"
    if mode & stat.S_IXUSR:
        permissions += "x"
    else:
        permissions += "-"
    if mode & stat.S_IRGRP:
        permissions += "r"
    else:
        permissions += "-"
    if mode & stat.S_IWGRP:
        permissions += "w"
    else:
        permissions += "-"
    if mode & stat.S_IXGRP:
        permissions += "x"
    else:
        permissions += "-"
    if mode & stat.S_IROTH:
        permissions += "r"
    else:
        permissions += "-"
    if mode & stat.S_IWOTH:
        permissions += "w"
    else:
        permissions += "-"
    if mode & stat.S_IXOTH:
        permissions += "x"
    else:
        permissions += "-"

    return f"{permissions}"


def get_os_metadata(current_file):
    stat_info = os.stat(current_file)
    print(f'''OS Metadata:
Creation Date:              {datetime.datetime.fromtimestamp(stat_info.st_ctime).strftime("%Y-%m-%d %H:%M:%S")}
Last modification (write):  {datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d %H:%M:%S")}
Last access (read):         {datetime.datetime.fromtimestamp(stat_info.st_ctime).strftime("%Y-%m-%d %H:%M:%S")}
File size:                  {convert_bytes_to_human_readable(stat_info.st_size)}
File permissions:           {get_mode_info(stat_info.st_mode)}''')


def get_exif_metadata(current_file):
    image = Image.open(current_file)
    exif = image.getexif()
    print('EXIF Metadata:')
    if exif:
        exif_dict = {}
        for (k, v) in exif.items():
            tag = TAGS.get(k, k)
            exif_dict[tag] = v
        max_size = max([len(str(x)) for x in exif_dict.keys()])
        for (k, v) in exif_dict.items():
            print(f'{k:<{max_size}}: {v}')
    else:
        print ('No EXIF metadata')



def scorpion(current_file):
    get_os_metadata(current_file)
    get_exif_metadata(current_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search for EXIF data and other metadata.')
    parser.add_argument('files', type=file_with_allowed_extension,
                        metavar='FILE', nargs='+',
                        help=f'[{", ".join(ALLOWED_EXTENSIONS)}] file(s) to be processed')

    args = parser.parse_args()

    for file in args.files:
        if not os.path.isfile(file):
            print(f"File not found: {file}")
        else:
            scorpion(file)
