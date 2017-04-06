#!/usr/bin/env python3

import sys #for arg parsing
import os #handling paths
import time

#web stuff
import urllib3 as ul #not really (really) used.
import requests as rq
from bs4 import BeautifulSoup
#
import simplejson as json #JSON conversions

DEF_HEADER = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'}

#TODO : Duplicate check

class LinkScraper(object):
  def __init__(self, header=DEF_HEADER):
  
    #USE KWARGS
    #static stuff
    self._session = rq.Session()
    self._tag = 'div'
    self._class = 'rg_meta'
    self._header = header
    self._preurl = 'https://www.google.com/search?q='
    self._posturl = '&source=lnms&tbm=isch&start=%d'

    #iteration stuff
    self._idx=0 # TODO: read the sidx from # of files in the folder
    self._response = [] #should I?
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
    resp=self._session.get(self._preurl + kywrd + posturl, headers=self._header)
    return BeautifulSoup(resp.text, 'lxml')
     
##TRY this
  def googleSearch(self, query):
    url = 'https://images.google.com'
    query = {'q': query}
    
    resp = self._session.get(url, headers=self._header, params=query)
    
    # FOR DEBUG
    #    with open('output/output.txt', 'wb') as fd:
    #      for chunk in resp.iter_content(chunk_size=128):
    #        fd.write(chunk)
    return BeautifulSoup(resp.text, 'lxml')
    
# vectorize instead of for loops
  def get_image_links(self,soup):
    a_list=[]
    img_links=[]# contains the link for Large original images, type of  image
   
    for a in soup.find_all(self._tag,{"class":self._class}):
      #a_list.append(a)     
      link , Type =json.loads(a.text)["ou"]  ,json.loads(a.text)["ity"]
      img_links.append((link,Type)) #print(Type)

    self.increment_idx(len(img_links))
    return img_links
  
  # HERE
  
  # this won't update the links
  def scrape_once(self,query):
      return (self.get_image_links(self.search(query)))
 
  # query = search query for images
  # size = amount of images
  # delay = wait between each ite., don't make Uncle Google angry.   
  def scrape(self,query,size,delay):
    
    while self._idx<size:
        self.update_links(self.scrape_once(query))
        print('link_count: ', self._idx)
        time.sleep(delay)
        
    return self._links
   

