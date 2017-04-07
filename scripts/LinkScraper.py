
import sys #for arg parsing
import time

#web stuff
import requests as rq
from bs4 import BeautifulSoup
import simplejson as json #JSON conversions

DEF_HEADER = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'}

#TODO : Duplicate check
#TODO: ignore stock image providers
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
    resp=self._session.get(self._preurl + kywrd + posturl, headers=self._header)
    return BeautifulSoup(resp.text, 'lxml')

  # different search request
  def googleSearch(self, query):
    url = 'https://images.google.com'
    query = {'q': query}

    resp = self._session.get(url, headers=self._header, params=query)
    return BeautifulSoup(resp.text, 'lxml')

  # vectorize instead of for loops
  def get_image_links(self,soup):
    a_list=[]
    img_links=[]# contains the link for Large original images, type of  image

    for a in soup.find_all(self._tag,{"class":self._class}):
      #a_list.append(a)
      link , Type =json.loads(a.text)["ou"]  ,json.loads(a.text)["ity"]
      img_links.append((link,Type)) # flag to check existance?

    self.increment_idx(len(img_links))
    return img_links

  # HERE

  # this won't update the links
  def scrape_once(self ,query, log):

      links = self.get_image_links(self.search(query))
      if log:
        with open('../data/'+query.replace(' ','_') +'.txt', 'w') as record:
          #os.path.join maybe
            for url,fmt in links:
              record.write("%s, %s\n" %(url,fmt))
            record.close()

      return links
  # query = search query for images
  # size = amount of images
  # delay = wait between each ite., don't make Uncle Google angry.
  def scrape(self,query,size,delay,log = True):

    while self._idx<size:
        self.update_links(self.scrape_once(query, log))
        print('link_count: ', self._idx)
        time.sleep(delay)

    return self._links
