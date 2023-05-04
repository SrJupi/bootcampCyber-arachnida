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
import pyexiv2
import pypdf
import docx

ALLOWED_IMG_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
ALLOWED_EXTENSIONS = ['.pdf', '.docx'] + ALLOWED_IMG_EXTENSIONS


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


def print_os_metadata(current_file):
    stat_info = os.stat(current_file)
    print(f'''OS Metadata:
Creation Date:              {datetime.datetime.fromtimestamp(stat_info.st_ctime).strftime("%Y-%m-%d %H:%M:%S")}
Last modification (write):  {datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d %H:%M:%S")}
Last access (read):         {datetime.datetime.fromtimestamp(stat_info.st_ctime).strftime("%Y-%m-%d %H:%M:%S")}
File size:                  {convert_bytes_to_human_readable(stat_info.st_size)}
File permissions:           {get_mode_info(stat_info.st_mode)}''')


def print_exif_metadata(current_file):
    image = pyexiv2.Image(current_file)
    exif_data = image.read_exif()
    print('EXIF Metadata:')
    if exif_data:
        for k, v in exif_data.items():
            print(f"{k}: {v}")
    else:
        print('No EXIF metadata')
    image.close()


def print_xmp_metadata(current_file):
    image = pyexiv2.Image(current_file)
    xmp_data = image.read_xmp()
    print('XMP Metadata:')
    if xmp_data:
        for k, v in xmp_data.items():
            print(f"{k}: {v}")
    else:
        print('No XMP metadata')
    image.close()


def print_iptc_metadata(current_file):
    image = pyexiv2.Image(current_file)
    iptc_data = image.read_iptc()
    print('IPTC Metadata:')
    if iptc_data:
        for k, v in iptc_data.items():
            print(f"{k}: {v}")
    else:
        print('No IPTC metadata')
    image.close()


def print_pdf_metadata(current_file):
    pdf_file = open(current_file, 'rb')
    pdf_reader = pypdf.PdfReader(pdf_file)
    metadata = pdf_reader.metadata
    if metadata:
        for k, v in metadata.items():
            print(f"{k}: {v}")
    else:
        print('No Metadata')
    pdf_file.close()


def print_docx_metadata(current_file):
    doc = docx.Document(current_file)
    metadata = doc.core_properties
    for arg in dir(metadata):
        if arg[0] != '_':
            print(f'{arg}: {getattr(metadata, arg)}')


def print_all_metadata(current_file):
    msg = f'Start of file: {current_file}\n'
    size = len(msg) * 2
    print('V' * size)

    print(f'{msg:^{size}}')
    print_os_metadata(current_file)
    print('~' * size)
    ext = os.path.splitext(current_file)[-1].lower()
    if ext in ALLOWED_IMG_EXTENSIONS:
        print_exif_metadata(current_file)
        print('~' * size)
        print_xmp_metadata(current_file)
        print('~' * size)
        print_iptc_metadata(current_file)
    elif ext == '.pdf':
        print_pdf_metadata(current_file)
    elif ext == '.docx':
        print_docx_metadata(current_file)
    msg = f'End of file: {current_file}'
    print(f'\n{msg:^{size}}')
    print('Ʌ' * size)


def edit_image_metadata(data_file):
    if data_file:
        editing = True
        while editing:
            meta_name = input(f'''You are going to edit a metadata.
Choose metadata to edit: {", ".join([key for key in data_file.keys()])}\n>> ''')
            while meta_name not in data_file.keys() and meta_name != "":
                meta_name = input(f'''Metadata does not exists.
Choose metadata to edit: {", ".join([key for key in data_file.keys()])}\n>> ''')
            if meta_name == "":
                adding = False
            else:
                value = input(f'Choose a new value for {meta_name}: ')
                data_file[meta_name] = value
                ans = input('Do you want to edit another metadata? (Y)es / (n)o\n>> ')
                while ans.lower() != 'y' and ans.lower() != 'n':
                    ans = input('>> ')
                if ans.lower() == 'n':
                    adding = False
    else:
        ans = input('''It seems that you don't have any exif metadata. Do you want to add some metadata? (Y)es / (n)o
>> ''')
        while ans.lower() != 'y' and ans.lower() != 'n':
            ans = input('(Y)es / (n)o >> ')
        if ans.lower() == 'y':
            add_image_metadata(data_file)


def delete_image_metadata(data_file):
    if data_file:
        deleting = True
        while deleting:
            meta_name = input(f'''You are going to delete a metadata.
Choose metadata to delete: {", ".join([key for key in data_file.keys()])}\n>> ''')
            while meta_name not in data_file.keys() and meta_name != "":
                meta_name = input(f'''Metadata does not exists.
Choose metadata to delete: {", ".join([key for key in data_file.keys()])}\n>> ''')
            if meta_name == "":
                deleting = False
            else:
                data_file[meta_name] = None
                ans = input('Do you want to delete another metadata? (Y)es / (n)o\n>> ')
                while ans.lower() != 'y' and ans.lower() != 'n':
                    ans = input('>> ')
                if ans.lower() == 'n':
                    deleting = False
    else:
        input("It seems that you don't have any exif metadata to delete...\nPress enter to return")


def add_image_metadata(data_file):
    adding = True
    while adding:
        meta_name = input('''You are going to add a new metadata.
    Choose your metadata name: ''')
        while meta_name in data_file.keys() and meta_name != "":
            meta_name = input('''Metadata already exists.
    Choose your metadata name: ''')
        if meta_name == "":
            adding = False
        else:
            value = input(f'Choose a value for your new {meta_name}: ')
            data_file[meta_name] = value
            ans = input('Do you want to add another metadata? (Y)es / (n)o\n>> ')
            while ans.lower() != 'y' and ans.lower() != 'n':
                ans = input('>> ')
            if ans.lower() == 'n':
                adding = False


def enter_edit(current_file, data_type):
    image = pyexiv2.Image(current_file)
    data_file = None
    if data_type == "EXIF":
        data_file = image.read_exif()
    elif data_type == "XMP":
        data_file = image.read_xmp()
    elif data_type == "IPTC":
        data_file = image.read_iptc()
    editing = True
    while editing and data_file is not None:
        ans = input(f'''You are editing {data_type.upper()} metadata. What do you want to do?
        
    1 - Edit current metadata
    2 - Delete current metadata
    3 - Add new metadata
    0 - Exit editing
    >> ''')
        while ans != '1' and ans != '2' \
                and ans != '3' and ans != '0':
            ans = input('   >> ')
        if ans == '1':
            edit_image_metadata(data_file)
        elif ans == '2':
            delete_image_metadata(data_file)
        elif ans == '3':
            add_image_metadata(data_file)
        elif ans == '0':
            editing = False
        try:
            if data_type == "EXIF":
                image.modify_exif(data_file)
            elif data_type == "XMP":
                image.modify_xmp(data_file)
            elif data_type == "IPTC":
                image.modify_iptc(data_file)
        except Exception as msg:
            print(f"\nERROR!\n{msg}\n")
            editing = False
    image.close()


def edit_images(current_file):
    editing = True
    while editing:
        ans = input('''Which metadata do you want to edit?
        
    1 - EXIF
    2 - XMP
    3 - IPTC
    4 - Show me the metadata
    0 - Exit edit mode
    >> ''')
        while ans != '1' and ans != '2' \
                and ans != '3' and ans != '4' \
                and ans != '0':
            ans = input('   >> ')
        if ans == '1':
            enter_edit(current_file, 'EXIF')
        elif ans == '2':
            enter_edit(current_file, 'XMP')
        elif ans == '3':
            enter_edit(current_file, 'IPTC')
        elif ans == '4':
            print_all_metadata(current_file)
        elif ans == '0':
            editing = False


def edit_pdf_metadata(current_file):
    was_edited = False
    with open(current_file, 'rb') as pdf_file:
        pdf_reader = pypdf.PdfReader(pdf_file)
        metadata = pdf_reader.metadata
        new_metadata = {}
        for k, v in metadata.items():
            new_metadata[k] = v
        editing = True
        while editing:
            meta_name = input(f'''You are going to edit a new metadata.
Choose metadata to edit: {", ".join([key for key in new_metadata.keys()])}\n>> ''')
            while meta_name not in new_metadata.keys() and meta_name != "":
                meta_name = input(f'''Metadata does not exists.
Choose metadata to edit: {", ".join([key for key in new_metadata.keys()])}\n>> ''')
            if meta_name == "":
                editing = False
            else:
                value = input(f'Choose a value for your new {meta_name}: ')
                new_metadata[meta_name] = value
                was_edited = True
                ans = input('Do you want to edit another metadata? (Y)es / (n)o\n>> ')
                while ans.lower() != 'y' and ans.lower() != 'n':
                    ans = input('>> ')
                if ans.lower() == 'n':
                    editing = False
        if was_edited:
            pdf_merger = pypdf.PdfWriter()
            pdf_merger.append(pdf_file)
            try:
                pdf_merger.add_metadata(new_metadata)
            except Exception as msg:
                print(f"\nERROR!\n{msg}\n")
                editing = False
            else:
                with open(current_file, 'wb') as pdf_output_file:
                    pdf_merger.write(pdf_output_file)


def delete_pdf_metadata(current_file):
    was_edited = False
    with open(current_file, 'rb') as pdf_file:
        pdf_reader = pypdf.PdfReader(pdf_file)
        metadata = pdf_reader.metadata
        new_metadata = {}
        for k, v in metadata.items():
            new_metadata[k] = v
        editing = True
        while editing:
            meta_name = input(f'''You are going to delete a metadata.
Choose metadata to delete: {", ".join([key for key in new_metadata.keys()])}\n>> ''')
            while meta_name not in new_metadata.keys() and meta_name != "":
                meta_name = input(f'''Metadata does not exists.
Choose metadata to delete: {", ".join([key for key in new_metadata.keys()])}\n>> ''')
            if meta_name == "":
                editing = False
            else:
                del (new_metadata[meta_name])
                was_edited = True
                ans = input('Do you want to add another metadata? (Y)es / (n)o\n>> ')
                while ans.lower() != 'y' and ans.lower() != 'n':
                    ans = input('>> ')
                if ans.lower() == 'n':
                    editing = False
        if was_edited:
            pdf_merger = pypdf.PdfWriter()
            pdf_merger.append(pdf_file)
            try:
                pdf_merger.add_metadata(new_metadata)
            except Exception as msg:
                print(f"\nERROR!\n{msg}\n")
                editing = False
            else:
                with open(current_file, 'wb') as pdf_output_file:
                    pdf_merger.write(pdf_output_file)


def add_pdf_metadata(current_file):
    was_added = False
    with open(current_file, 'rb') as pdf_file:
        pdf_reader = pypdf.PdfReader(pdf_file)
        metadata = pdf_reader.metadata
        new_metadata = {}
        for k, v in metadata.items():
            new_metadata[k] = v
        adding = True
        while adding:
            meta_name = input('''You are going to add a new metadata.
    Choose your metadata name: ''')
            while meta_name in metadata and meta_name != "":
                meta_name = input('''Metadata already exists.
    Choose your metadata name: ''')
            if meta_name == "":
                adding = False
            else:
                value = input(f'Choose a value for your new {meta_name}: ')
                new_metadata[meta_name] = value
                was_added = True
                ans = input('Do you want to add another metadata? (Y)es / (n)o\n>> ')
                while ans.lower() != 'y' and ans.lower() != 'n':
                    ans = input('>> ')
                if ans.lower() == 'n':
                    adding = False
        if was_added:
            pdf_merger = pypdf.PdfWriter()
            pdf_merger.append(pdf_file)
            try:
                pdf_merger.add_metadata(new_metadata)
            except Exception as msg:
                print(f"\nERROR!\n{msg}\n")
                adding = False
            else:
                with open(current_file, 'wb') as pdf_output_file:
                    pdf_merger.write(pdf_output_file)


def edit_pdf(current_file):
    editing = True
    while editing:
        ans = input(f'''You are editing PDF metadata. What do you want to do?

    1 - Edit current metadata
    2 - Delete current metadata
    3 - Add new metadata
    0 - Exit editing
    >> ''')
        while ans != '1' and ans != '2' \
                and ans != '3' and ans!= '4' \
                and ans != '0':
            ans = input('   >> ')
        if ans == '1':
            edit_pdf_metadata(current_file)
        elif ans == '2':
            delete_pdf_metadata(current_file)
        elif ans == '3':
            add_pdf_metadata(current_file)
        elif ans == '4':
            print_all_metadata(current_file)
        elif ans == '0':
            editing = False


def edit_docx_metadata(current_file):
    doc = docx.Document(current_file)
    metadata = doc.core_properties
    was_edited = False
    editing = True
    while editing:
        meta_name = input(f'''You are going to edit a new metadata.
Choose metadata to edit: {", ".join([arg for arg in dir(metadata) if arg[0] != '_'])}\n>> ''')
        while meta_name not in dir(metadata) and meta_name != "":
            meta_name = input(f'''Metadata does not exists.
Choose metadata to edit: {", ".join([arg for arg in dir(metadata) if arg[0] != '_'])}\n>> ''')
        if meta_name == "":
            editing = False
        else:
            value = input(f'Choose a value for your new {meta_name}: ')
            setattr(metadata, meta_name, value)
            was_edited = True
            ans = input('Do you want to edit another metadata? (Y)es / (n)o\n>> ')
            while ans.lower() != 'y' and ans.lower() != 'n':
                ans = input('>> ')
            if ans.lower() == 'n':
                editing = False
            if was_edited:
                doc.save(current_file)


def delete_docx_metadata(current_file):
    doc = docx.Document(current_file)
    metadata = doc.core_properties
    was_edited = False
    editing = True
    while editing:
        meta_name = input(f'''You are going to delete a new metadata.
Choose metadata to delete: {", ".join([arg for arg in dir(metadata) if arg[0] != '_'])}\n>> ''')
        while meta_name not in dir(metadata) and meta_name != "":
            meta_name = input(f'''Metadata does not exists.
Choose metadata to delete: {", ".join([arg for arg in dir(metadata) if arg[0] != '_'])}\n>> ''')
        if meta_name == "":
            editing = False
        else:
            setattr(metadata, meta_name, '')
            was_edited = True
            ans = input('Do you want to delete another metadata? (Y)es / (n)o\n>> ')
            while ans.lower() != 'y' and ans.lower() != 'n':
                ans = input('>> ')
            if ans.lower() == 'n':
                editing = False
            if was_edited:
                doc.save(current_file)


def add_docx_metadata(current_file):
    pass


def edit_docx(current_file):
    editing = True
    while editing:
        ans = input(f'''You are editing DOCX metadata. What do you want to do?

    1 - Edit current metadata
    2 - Delete current metadata
    3 - Add new metadata
    4 - Show metadata
    0 - Exit editing
    >> ''')
        while ans != '1' and ans != '2' \
                and ans != '3' and ans != '4' \
                and ans != '0':
            ans = input('   >> ')
        if ans == '1':
            edit_docx_metadata(current_file)
        elif ans == '2':
            delete_docx_metadata(current_file)
        elif ans == '3':
            add_docx_metadata(current_file)
        elif ans == '4':
            print_all_metadata(current_file)
        elif ans == '0':
            editing = False


def edit_file(current_file):
    ext = os.path.splitext(current_file)[-1].lower()
    if ext in ALLOWED_IMG_EXTENSIONS:
        edit_images(current_file)
    elif ext == '.pdf':
        edit_pdf(current_file)
    elif ext == '.docx':
        edit_docx(current_file)


def start_edit_mode(current_file):
    input(f'''You are in edit mode. Press enter to print all the metadata for your file {current_file}.\n''')
    print_all_metadata(current_file)
    ans = input('''Do you want to edit any metadata?(Y)es / (N)o\n>> ''')
    while ans.lower() != 'y' and ans.lower() != 'n':
        ans = input('>> ')
    if ans.lower() == 'y':
        edit_file(current_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search for EXIF data and other metadata.')
    parser.add_argument('files', type=file_with_allowed_extension,
                        metavar='FILE', nargs='+',
                        help=f'{", ".join(ALLOWED_EXTENSIONS)} file(s) to be processed')
    parser.add_argument('-e', '--edit', action='store_true',
                        help='enter scorpion in edit mode')

    args = parser.parse_args()

    for file in args.files:
        if not args.edit:
            print_all_metadata(file)
        else:
            start_edit_mode(file)
