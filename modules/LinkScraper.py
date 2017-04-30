#!/usr/bin/env python3
from os import makedirs
import time


#web stuff
import requests as rq
from bs4 import BeautifulSoup
import simplejson as json #JSON conversions

DEF_HEADER = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'}
#TODO: provide this from a file
BLACKLIST = ['shutterstock','dreamstime','123rf','fotolia','alamy','depositphotos', 'turbosquid']

#TODO : Duplicate check

# request images of given query, grab links
class LinkScraper(object):
  def __init__(self, header=DEF_HEADER, session=rq.Session()):

    #USE KWARGS
    #static stuff
    self._header = header
    self._session = session
    self._tag = 'div'
    self._class = 'rg_meta'
    self._preurl = 'https://www.google.com/search?q='
    self._posturl = '&source=lnms&tbm=isch&start=%d'
    self._discarded = 0
    #iteration stuff
    self._idx=0 # TODO: read the sidx from # of files in the folder
    self._links = []


  #update index
  def update_idx(self,idx):
    self._idx=idx

  #might be useful
  def increment_idx(self, inc):
    self._idx+=inc

  def update_links(self, new_ls):
    self._links+=new_ls

  def search(self,kywrd):
    posturl = self._posturl %self._idx

    #INSTEAD do resp=,  increment index,  return
    # (or do it after processing links: len(ActualImages))
    src_url=self._preurl + kywrd + posturl
    resp=self._session.get(src_url, headers=self._header, params={'start': self._idx})
    print(src_url)
    return BeautifulSoup(resp.text, 'lxml')

  # different search request
  def googleSearch(self, query):
    url = 'https://images.google.com'
    kvs = {'q': query,
              'start': self._idx}

    resp = self._session.get(url, headers=self._header, params=kvs)
    return BeautifulSoup(resp.text, 'lxml')

  # vectorize instead of for loops
  def get_image_links(self,soup):
    a_list=[]
    img_links=[]# contains the link for Large original images, type of  image

    for a in soup.find_all(self._tag,{"class":self._class}):
      #a_list.append(a)
      link , fmt =json.loads(a.text)["ou"]  ,json.loads(a.text)["ity"]
      if not any(site in link for site in BLACKLIST):
        img_links.append((link,fmt)) # flag to check existance?
      else:
        self._discarded+=1

    self.increment_idx(len(img_links))
    return img_links

  # HERE

  # this won't update the links
  def scrape_once(self ,query,txt , log):

      links = self.get_image_links(self.search(query))
      if log:
        for url,fmt in links:
          txt.write("%s, %s\n" %(url,fmt))


      return links
  # query = search query for images
  # size = amount of images
  # delay = wait between each ite., don't make Uncle Google angry.
  def scrape(self,query,size,delay,log = True):
    makedirs('lists', exist_ok=True)
    txt=open('lists/'+query.replace(' ','_') +'.txt', 'w')
    while self._idx<size:
        self.update_links(self.scrape_once(query,txt, log))
        print('link_count: ', self._idx, ' discarded: ', self._discarded)
        time.sleep(delay)
    txt.close()
    return self._links
