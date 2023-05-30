# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    spider.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: lsulzbac <lsulzbac@student.42barcel>       +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2023/04/20 12:26:40 by lsulzbac          #+#    #+#              #
#    Updated: 2023/05/03 13:23:38 by lsulzbac         ###   ########.fr        #
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
from loading import ft_progress
from queue import Queue

ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']


class SpiderWeb:
    def __init__(self, initial_URL, path_to_save, is_recursive, recursive_depth):
        self.initial_URL = initial_URL
        self.path_to_save = os.path.abspath(path_to_save)+'/'
        self.__check_path()
        self.__check_recursive_depth(is_recursive, recursive_depth)
        self.__get_hostname()
        self.added_to_spiders = set()
        self.spiders = Queue()
        self.visited_list = []
        self.images_to_download = set()
        self.errors = []
        self.spiders.put((self.initial_URL, self.recursive_depth))
        self.added_to_spiders.add(self.initial_URL)


    def __str__(self):
        return '\n'.join([f"{k} = {v}" for k, v in self.__dict__.items()])

    def deploy_spiders(self):
        while not self.spiders.empty():
            current_spider = self.spiders.get()
            if current_spider[0] in self.visited_list:
                continue
            current_spider = self.__create_spider(current_spider[0], current_spider[1])
            try:
                self.visited_list.append(current_spider.URL)
                new_urls, new_images = current_spider.run()             
            except Exception as msg:
                self.errors.append((f'Error on {current_spider.URL}', msg))
            else:
                self.images_to_download.update(new_images)
                if current_spider.depth - 1 < 0:
                    continue
                for new_url in new_urls:
                    if new_url in self.added_to_spiders:
                        continue
                    if not self.__check_is_hostname(new_url):
                        continue
                    self.added_to_spiders.add(new_url)
                    self.spiders.put((new_url, current_spider.depth - 1))


    def download_images(self):
        i = 0
        num_width = len(str(len(self.images_to_download)))
        print(f'Downloading images!')
        for current_url in ft_progress(self.images_to_download):
            name = current_url.split('/')[-1]
            if len(name) > 200:
                name = name[len(name)-200:]
            dst_path = f'{self.path_to_save}{i:0{num_width}} - {name}'
            if os.path.exists(current_url) \
                    and os.path.isfile(current_url) \
                    and os.path.splitext(current_url)[-1] in ALLOWED_EXTENSIONS:
                try:
                    with open(current_url, 'rb') as src_file:
                        with open(dst_path, 'wb') as dst_file:
                            shutil.copyfileobj(src_file, dst_file)
                            i += 1
                except Exception as msg:
                    self.errors.append(f'Error on {current_url}. File not opened - {msg}')
            else:
                try:
                    response = requests.get(current_url)
                except Exception as msg:
                    self.errors.append(f'Error on {current_url}: {msg}')
                else:
                    if response.status_code != 200:
                        self.errors.append(f'{current_url} response was {response.status_code}')
                        continue
                    content_type = response.headers.get('Content-Type')
                    if not content_type and 'image' not in content_type:
                        self.errors.append(f'{current_url} does not have a content type or it is not a image')
                        continue
                    image_type = '.' + content_type[len('image/'):]
                    if image_type.lower() not in ALLOWED_EXTENSIONS:
                        self.errors.append(f"{current_url} is not a {', '.join(ALLOWED_EXTENSIONS)} file")
                        continue
                    index = dst_path.lower().find(image_type)
                    if index != -1:
                        dst_path = dst_path[:index+len(image_type)]
                    elif index == -1:
                        dst_path = dst_path + image_type.lower()
                    try:
                        with open(dst_path, 'wb') as dst_file:
                            dst_file.write(response.content)
                            i += 1
                    except Exception as msg:
                        self.errors.append(f'Error on {current_url}. File not opened - {msg}')

        self.total_downloaded = i

    def __check_recursive_depth(self, is_recursive, recursive_depth):
        if is_recursive and recursive_depth is None:
            self.recursive_depth = 5
        elif is_recursive:
            self.recursive_depth = recursive_depth
        else:
            self.recursive_depth = 0

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
        return spider

    def __check_is_hostname(self, new_url):
        if os.path.isfile(new_url):
            new_hostname = os.path.dirname(os.path.abspath(new_url))
            if self.hostname in new_hostname:
                return True
            else:
                return False
        else:
            try:
                new_hostname = urlsplit(new_url).hostname
            except ValueError:
                return False
            else:
                if self.hostname == new_hostname:
                    return True
                else:
                    return False

    def __get_hostname(self):
        if os.path.isfile(self.initial_URL):
            self.hostname = os.path.dirname(os.path.abspath(self.initial_URL))
        elif urlsplit(self.initial_URL).netloc is None:
            raise ValueError("Original URL does not have a hostname!")
        else:
            try:
                response = requests.get(self.initial_URL)
                if 'Location' in response.headers:
                    self.initial_URL = response.headers['Location']
                    self.__get_hostname()
                else:
                    self.hostname = urlsplit(self.initial_URL).netloc
            except:
                raise ValueError("Original URL does not is valid!")
                



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
        else:
            response = requests.get(self.URL)
            if response.status_code == 200 and 'text/html' in response.headers.get('Content-Type'):
                soup = BeautifulSoup(response.content, 'html.parser')
            elif 'image' in response.headers.get('Content-Type'):
                return [], [self.URL]
            else:
                return [], []
        images = soup.find_all('img', {'src': True})
        images = [self.__get_full_path(image['src']) for image in images if image['src'] != '']
        links = soup.find_all('a', {'href': True})
        links = [self.__get_full_path(link['href']) for link in links if link['href'] != '']
        return links, images

    
    def __get_full_path(self, url):
        if not os.path.isfile(url):
            split = urlparse(url)
            if not bool(split.netloc) and bool(urlparse(self.URL).hostname):
                url = urlparse(self.URL).scheme + '://' + urlparse(self.URL).hostname + url
        return url


def parse_args(args_from_sys):
    parser = argparse.ArgumentParser(description='Extract all images from a website')
    parser.add_argument('-r', action='store_true',
                        help='recursively downloads the images in a URL received as a parameter')
    parser.add_argument('-l', type=int, nargs='?', const=5,
                        metavar='N',
                        help='indicates the maximum depth level of the recursive download. Default: 5')
    parser.add_argument('-p', type=str, nargs='?',
                        default='./data/', metavar='PATH',
                        help='indicates the path where the downloaded files will be saved. Default: ./data/')
    parser.add_argument('URL', type=str, metavar='URL',
                        help='URL to be scrapped')
    parsed_args = parser.parse_args()
    if parsed_args.l and not parsed_args.r:
        parser.error('-r argument is required when -l are present')
    if parsed_args.l is not None and parsed_args.l <= 0:
        parser.error('-l must be bigger than 0')
    if not os.path.exists(parsed_args.URL) \
            or not os.path.isfile(parsed_args.URL) \
            or not os.path.splitext(parsed_args.URL)[-1] == '.html':
        parsed_url = urlparse(parsed_args.URL)
        if not parsed_url.scheme:
            parsed_args.URL = "https://" + parsed_args.URL
            
    return parsed_args


if __name__ == '__main__':
    start_time = time.time()
    args = parse_args(sys.argv[1:])
    my_web = SpiderWeb(args.URL, args.p, args.r, args.l)
    my_web.deploy_spiders()
    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"\nScrap time: {elapsed_time:.2f} seconds")
    ans = ''
    downloaded = False
    while (ans != '4'):
        ans = input(f'''The website(s) were scrapped. What do you want to do?
    1 - Download {len(my_web.images_to_download)} images
    2 - See {len(my_web.visited_list)} URLs visited
    3 - See {len(my_web.errors)} errors
    4 - Exit
    >>> ''')
        if ans == '1':
            if not downloaded:
                my_web.download_images()
                print()
                downloaded = True
            print(f"Images Saved on '{my_web.path_to_save}'\nDownloaded {my_web.total_downloaded} images of {len(my_web.images_to_download)} images found")
        if ans == '2':
            for site in my_web.visited_list:
                print(site)
        if ans == '3':
            if len(my_web.errors) == 0:
                print('No error happened!')
            else:
                for item in my_web.errors:
                    print(item)
        print()

            

