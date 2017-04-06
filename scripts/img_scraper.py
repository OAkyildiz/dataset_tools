#!/usr/bin/env python3
#import argparse
import sys
from ScraperTools import *
   
# TODO: use ArgParse 
# http://stackoverflow.com/questions/39390418/python-how-can-i-enable-use-of-kwargs-when-calling-from-command-line-perhaps

def main():
    scutty = LinkScraper()
    keywrds = input('search query: ')
    n = input('#: ')
    the_list = scutty.scrape(keywrds ,int(n) ,2)
   
   # ofc change path according to query name (sys path join stuff)
    with open('output/list.txt', 'w') as record:
      for url,fmt in the_list:
        record.write("%s, %s\n" %(url,fmt))
      record.close()
    
if __name__ == "__main__":
    print()
    sys.exit(main()) 
