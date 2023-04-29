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
import sys


class SpiderWeb:
    def __init__(self, initial_URL, path_to_save, is_recursive, recursive_depth, is_hostname):
        self.initial_URL = initial_URL
        self.path_to_save = path_to_save
        self.is_recursive = is_recursive
        self.recursive_depth = recursive_depth
        self.is_hostname = is_hostname
        self.spiders = []
        self.visited_list = []
        self.to_download_list = {}
        self._check_recursive_depth()
        self._check_path()
        self._create_initial_spider()

    def __str__(self):
        return '\n'.join([f"{k} = {v}" for k, v in self.__dict__.items()])

    def deploy_spiders(self):
        while len(self.spiders):
            spider = self.spiders.pop(0)
            if spider in self.visited_list:
                continue
            self.visited_list.append(spider)
            try:
                spider.run()
            except Exception as msg:
                print(f"Spider with URL '{spider.URL} failed\nERROR: {msg}'")



    def _check_recursive_depth(self):
        if self.is_recursive and self.recursive_depth is None:
            ans = input('''You set recursion to True but did not set a depth limit.
This could lead to an infite scrap of the web...
Do you want to continue?
    (Y)es or (n)o: ''')
            while ans != 'Y' and ans != 'n':
                ans = input('(Y)es or (n)o: ')
            if ans == 'Y':
                self.recursive_depth = -1
                print('Ok, boss... Good luck!')
            if ans == 'n':
                new_depth = input('Insert a integer to set the maximum depth\n>> ')
                while not new_depth.isnumeric():
                    new_depth = input('>> ')
                self.recursive_depth = int(new_depth)
                print(f'Maximum depth set to {new_depth}')

    def _check_path(self):
        if not os.path.exists(self.path_to_save):
            try:
                os.makedirs(self.path_to_save)
            except OSError:
                raise ValueError(f"Failed to create directory at {self.path_to_save}")
        elif not os.path.isdir(self.path_to_save):
            raise ValueError(f"{self.path_to_save} is not a directory")

    def _create_initial_spider(self):
        spider = Spider(self.initial_URL, self.is_recursive, self.recursive_depth)
        self.spiders.append(spider)




class Spider:
    def __init__(self, URL, is_recursive, depth):
        self.URL = URL
        self.is_recursive = is_recursive

    def run(self):
        """Run this spider
returns:
    spiders: If recursive returns list with next level of spiders
    images: list of images URLS"""

        pass


def parse_args(args):
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
    return parsed_args


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    # if hasattr(args, 'r'):
    #     print(args.r)
    # if hasattr(args, 'l'):
    #     print(args.l)
    # if hasattr(args, 'p'):
    #     print(args.p)
    # if hasattr(args, 'oh'):
    #     print('oh',args.oh)
    # print('spider')
    my_web = SpiderWeb(args.URL, args.p, args.r, args.l, args.oh)
    my_web.deploy_spiders()
    print(my_web)
