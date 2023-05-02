# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    spider.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: lsulzbac <lsulzbac@student.42barcel>       +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2023/04/20 12:26:40 by lsulzbac          #+#    #+#              #
#    Updated: 2023/04/20 12:26:47 by lsulzbac         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import argparse
import os
import shutil
import sys
from urllib.parse import urlsplit
from urllib.parse import urlparse
import time
import requests
from bs4 import BeautifulSoup

ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']


def ft_progress(listy, bar_size=20, load_str="|\-/"):
    if not isinstance(bar_size, int):
        bar_size = 20
    load_str = str(load_str)
    str_size = len(load_str)
    start_time = time.time()
    size = len(listy)
    width = len(str(size))
    prog_str = '>'.ljust(bar_size)
    next_step = 1 / bar_size
    other_step = 0.2 / bar_size
    load_char = load_str[0]
    j = 1
    for i, item in enumerate(listy):
        progress = (i + 1) / size
        if progress > next_step:
            while next_step < progress:
                prog_str = '=' + prog_str[0:-1]
                next_step += 1 / bar_size
        if progress > other_step:
            load_char = load_str[j % str_size]
            j += 1
            other_step += 0.2 / bar_size
        diff_time = time.time() - start_time
        remain_time = (1 - progress) * (diff_time / progress)
        if remain_time > 60:
            remain_time /= 60
            remain_time = f"{remain_time:6.2f} min"
        else:
            remain_time = f"{remain_time:6.2f} s  "
        if diff_time > 60:
            diff_time /= 60
            diff_time = f"{diff_time:6.2f} min"
        else:
            diff_time = f"{diff_time:6.2f} s  "
        if i == size:
            load_char = 'OK!'
        print(
            f"\r-> ETA: {remain_time} [{prog_str[0:int(bar_size / 2)]} {progress * 100:6.2f}% {prog_str[int(bar_size / 2):]}] {i + 1:{width}d}/{size:{width}d} | elapsed time: {diff_time}  {load_char}",
            end='')

        yield item


class SpiderWeb:
    def __init__(self, initial_URL, path_to_save, is_recursive, recursive_depth, is_hostname):
        self.initial_URL = initial_URL
        self.path_to_save = path_to_save
        self.is_recursive = is_recursive
        self.recursive_depth = recursive_depth
        self.is_hostname = is_hostname
        self.spiders = []
        self.visited_list = []
        self.images_to_download = []
        self.errors = []
        self.__check_recursive_depth()
        self.__check_path()
        self.__check_valid_hostname()
        self.__create_spider(self.initial_URL, self.recursive_depth)

    def __str__(self):
        return '\n'.join([f"{k} = {v}" for k, v in self.__dict__.items()])

    def deploy_spiders(self):
        counter = 0
        while len(self.spiders):
            counter += 1
            current_spider = self.spiders.pop(0)
            if current_spider.URL in self.visited_list:
                continue
            try:
                new_urls, new_images = current_spider.run()
                self.visited_list.append(current_spider.URL)
            except Exception as msg:
                self.errors.append((f'Error on {current_spider.URL}', msg))
            else:
                new_images = [image for image in new_images if '.'+image.split('.')[-1] in ALLOWED_EXTENSIONS]
                self.images_to_download += new_images
                if not current_spider.depth - 1 == 0:
                    for new_url in new_urls:
                        if self.is_hostname and not self.__check_is_hostname(new_url):
                            continue
                        self.__create_spider(new_url, current_spider.depth - 1)

            if counter % 10 == 0:
                print("I'm still alive... For now... " + str(counter) + " we still have " + str(len(self.spiders)))

    def download_images(self):
        i = 0
        name = 'image'
        print(len(self.images_to_download))
        self.images_to_download = dict.fromkeys(self.images_to_download).keys()
        print(len(self.images_to_download))

        for current_url in ft_progress(self.images_to_download):
            dst_path = self.path_to_save + name + str(i)
            if os.path.exists(current_url) \
                    and os.path.isfile(current_url) \
                    and os.path.splitext(current_url)[-1] in ALLOWED_EXTENSIONS:
                with open(current_url, 'rb') as src_file:
                    # Open the destination file in binary mode
                    with open(dst_path, 'wb') as dst_file:
                        # Copy the contents of the source file to the destination file using shutil.copyfileobj
                        shutil.copyfileobj(src_file, dst_file)
                        i += 1
            else:
                try:
                    response = requests.get(current_url)
                except:
                    continue
                else:
                    if response.status_code == 200:
                        content_type = response.headers.get('Content-Type')
                        if content_type and 'image' in content_type:
                            image_type = '.' + content_type[len('image/'):]
                            if image_type in ALLOWED_EXTENSIONS:
                                dst_path += image_type
                                with open(dst_path, 'wb') as dst_file:
                                    dst_file.write(response.content)
                                    i += 1

    def __check_recursive_depth(self):
        if self.is_recursive and self.recursive_depth is None:
            self.recursive_depth = 5
        if not self.is_recursive:
            self.recursive_depth = 1

    def __check_path(self):
        if not os.path.exists(self.path_to_save):
            try:
                os.makedirs(self.path_to_save)
            except OSError:
                raise ValueError(f"Failed to create directory at {self.path_to_save}")
        elif not os.path.isdir(self.path_to_save):
            raise ValueError(f"{self.path_to_save} is not a directory")

    def __create_spider(self, URL, depth):
        spider = Spider(URL, depth)
        self.spiders.append(spider)

    def __check_is_hostname(self, new_url):
        hostname = urlsplit(self.initial_URL).hostname
        try:
            new_hostname = urlsplit(new_url).hostname
        except ValueError:
            return False
        else:
            if hostname == new_hostname:
                return True
            else:
                return False

    def __check_valid_hostname(self):
        if self.is_hostname:
            try:
                urlsplit(self.initial_URL).hostname
            except ValueError:
                print(f"{self.initial_URL} does not have a hostname so it cannot be used with -oh flag")
                ans = input(
                    'Do you want to exit or do you want to deactivate the -oh flag?\n(E)xit or (D)eactivate >> ')
                while ans != 'E' and ans != 'D':
                    ans = input('(E)xit or (D)eactivate >> ')
                if ans == 'E':
                    exit()
                if ans == 'D':
                    self.is_hostname = False


class Spider:
    def __init__(self, URL, depth):
        self.URL = URL
        self.depth = depth

    def run(self):
        """Run this spider!
    Raises:
        requests.exceptions.RequestException: If the request to the website fails
        ValueError: If soup parsing fails
    Returns:
        urls_list: list of all URLs found in the website
        images_list: list of all images URLs found in the website"""
        if os.path.exists(self.URL) \
                and os.path.isfile(self.URL) \
                and os.path.splitext(self.URL)[-1] == '.html':
            with open(self.URL, 'rb') as f:
                html = f.read()
            soup = BeautifulSoup(html, 'html.parser')
            images = soup.find_all('img')
            links = soup.find_all('a')
        else:
            try:
                response = requests.get(self.URL)
            except:
                pass
            else:
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    images = soup.find_all('img')
                    links = soup.find_all('a')

        links = [link['href'] for link in links if link['href'] != '']
        images = [image['src'] for image in images if image['src'] != '']

        return links, images


def parse_args(args_from_sys):
    parser = argparse.ArgumentParser(description='Extract all images from a website',
                                     )
    parser.add_argument('-r', action='store_true',
                        help='recursively downloads the images in a URL received as a parameter')
    parser.add_argument('-l', type=int, nargs='?', const=5,
                        metavar='N',
                        help='indicates the maximum depth level of the recursive download. Default: 5')
    parser.add_argument('-oh', action='store_true',
                        help='indicates to only access the Original Hostname in recursive download.')
    parser.add_argument('-p', type=str, nargs='?',
                        default='./data/', metavar='PATH',
                        help='indicates the path where the downloaded files will be saved. Default: ./data/')
    parser.add_argument('URL', type=str, metavar='URL',
                        help='URL to be scrapped')
    parsed_args = parser.parse_args()
    if (parsed_args.l or parsed_args.oh) and not parsed_args.r:
        parser.error('-r argument is required when -l or -oh are present')
    if not os.path.exists(parsed_args.URL) \
            and not os.path.isfile(parsed_args.URL) \
            and not os.path.splitext(parsed_args.URL)[-1] == '.html':
        try:
            parsed_url = urlparse(parsed_args.URL)
            if not parsed_url.scheme:
                parsed_args.URL = "https://" + parsed_args.URL
        except:
            parser.error('URL passed is not valid')
    return parsed_args


if __name__ == '__main__':
    start_time = time.time()
    args = parse_args(sys.argv[1:])
    my_web = SpiderWeb(args.URL, args.p, args.r, args.l, args.oh)
    my_web.deploy_spiders()
    my_web.download_images()
    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"\nElapsed time: {elapsed_time:.2f} seconds")
    print(f'Visited URLs -> {len(my_web.visited_list)}:')
    print(f'Images URLs -> {len(my_web.images_to_download)}:')
#  print(my_web)
