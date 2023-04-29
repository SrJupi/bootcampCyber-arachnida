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
import sys


class SpiderWeb:
    pass


class Spider:
    pass


def parse_args(args):
    parser = argparse.ArgumentParser(description='Extract all images from a website',
                                     )
    parser.add_argument('-r', action='store_true',
                        help='recursively downloads the images in a URL received as a parameter')
    parser.add_argument('-l', type=int, nargs='?', const=5,
                        metavar='N',
                        help='indicates the maximum depth level of the recursive download. Default: 5')
    parser.add_argument('-p', type=str, nargs='?',
                        const='./data/', metavar='PATH',
                        help='indicates the path where the downloaded files will be saved. Default: ./data/')
    args = parser.parse_args()
    if hasattr(args, 'l') and not args.r:
        parser.error('-r argument is required when -l is present')
    return(args)


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    if hasattr(args, 'r'):
        print(args.r)
    if hasattr(args, 'l'):
        print(args.l)
    if hasattr(args, 'p'):
        print(args.p)
    print('spider')
