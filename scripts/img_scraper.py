#!/usr/bin/env python3
#import argparse
import sys
from LinkScraper import *
from ImageGrabber import *
# TODO: use ArgParse
# http://stackoverflow.com/questions/39390418/python-how-can-i-enable-use-of-kwargs-when-calling-from-command-line-perhaps

def main():
    # no idee why I went with these variable names

    keywrds = input('search query: ')
    n = input('#: ')

    scutty = LinkScraper()
    gibby = ImageGrabber(keywrds)

    #pls argparse

    i_list=scutty.scrape(keywrds ,int(n) ,2)
    #gibby.download_image(i_list[0][0], 'jpg')
    gibby.grab_all(i_list)


if __name__ == "__main__":
    print()
    sys.exit(main())
