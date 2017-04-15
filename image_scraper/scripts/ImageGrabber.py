#!/usr/bin/env python3
import os, sys
import urllib3 as ul
import cv2

import numpy as np
import requests as rq
#from io.StringIO import StringIO
# grab images of given category, using a list of links

#  I do feel like I need a base class
DEF_HEADER = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'}


class ImageGrabber(object):
  def __init__(self, name, header = DEF_HEADER, session=rq.Session()):
    self._name = name.replace(' ','_') # let's not ahve spaces in folder names
    self._header = header
    self._session = session
    self._dir = '../data/'+ self._name
    self._idx = 0
    os.makedirs(self._dir, exist_ok=True)

# HERE
  def download_image(self, url, fmt):
    try:
      resp = self._session.get(url, headers=self._header, stream=True);
      resp.raw.decode_content = True
      #TODO: resize !!
      if fmt=='gif':
        #fmt='png'
        print('skipping .GIFs for now (%s)' %url)
        
      else:
        if not fmt:
          fmt='jpg'
        
        # read the image
        img=np.asarray(bytearray(resp.content), dtype="uint8")
        img=cv2.imdecode(img, cv2.IMREAD_COLOR)
        # path/to/image.fmt :
        img_name=self._name+str(self._idx)+'.'+fmt
        fullname=os.path.join(self._dir, img_name) #could have done it in one line
        #do something for gifs

      
        #imdecode
        cv2.imwrite(fullname, img)

        self._idx+=1

        print('%s saved' %url, ' index: %i' %self._idx)
      return 1

    except Exception as e:
      print('could not load %s  \n' %url, e)
      return 0

  def grab_all(self, list):
    for link, ext in list:
      self.download_image(link, ext)
    print('done')
