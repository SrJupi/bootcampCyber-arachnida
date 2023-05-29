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
from PIL import Image, ExifTags


ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']


def file_with_allowed_extension(filename):
    """Check if a file has an allowed extension"""

    ext = os.path.splitext(filename)[-1]
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise argparse.ArgumentTypeError(f"File extension on {filename} is not in {ALLOWED_EXTENSIONS}")
    if not os.path.isfile(filename):
        raise argparse.ArgumentTypeError(f"File {filename} not found!")
    
    return filename


def convert_bytes_to_human_readable(size_in_bytes):
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0

    while size_in_bytes >= 1000 and unit_index < len(units) - 1:
        size_in_bytes /= 1000
        unit_index += 1

    return f"{round(size_in_bytes)} {units[unit_index]}"


def print_os_metadata(current_file):
    stat_info = os.stat(current_file)
    print(f'''OS Metadata:
Creation Date:              {datetime.datetime.fromtimestamp(stat_info.st_ctime).strftime("%Y-%m-%d %H:%M:%S")}
Last modification (write):  {datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d %H:%M:%S")}
Last access (read):         {datetime.datetime.fromtimestamp(stat_info.st_ctime).strftime("%Y-%m-%d %H:%M:%S")}
File size:                  {convert_bytes_to_human_readable(stat_info.st_size)}
File permissions:           {stat.filemode(stat_info.st_mode)}''')


def print_exif_metadata(current_file):
    image = Image.open(current_file)
    exif_data = image.getexif()
    print('EXIF Metadata:\n')
    if exif_data:
        for tag_id in exif_data:
            tag_name = ExifTags.TAGS.get(tag_id, tag_id)
            value = exif_data.get(tag_id)
            print(f'{tag_name}: {value}')
    else:
        print('No EXIF metadata')
    image.close()


def print_all_metadata(current_file):
    msg = f'Start of file: {current_file}\n'
    size = len(msg) * 2
    print('V' * size)

    print(f'{msg:^{size}}')
    print_os_metadata(current_file)
    if os.access(current_file, os.R_OK):
        print('~' * size)
        print_exif_metadata(current_file)
    msg = f'End of file: {current_file}'
    print(f'\n{msg:^{size}}')
    print('Ʌ' * size)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search for EXIF data and other metadata.')
    parser.add_argument('files', type=file_with_allowed_extension,
                        metavar='FILE', nargs='+',
                        help=f'{", ".join(ALLOWED_EXTENSIONS)} file(s) to be processed')
    args = parser.parse_args()

    for file in args.files:
        print_all_metadata(file)