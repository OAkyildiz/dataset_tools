#!/usr/bin/env python3

from sys import exit
from os import getcwd, listdir
from os.path import abspath, join, dirname

from sklearn.feature_extraction.image import extract_patches_2d

import cv2
import numpy as np

images=[]
classes={}


def imgs_from_fldr():
  while not data_dir:
    try:
      data_dir = abspath(join(getcwd(), input('path for dataset folders: ')))
      fldrs=listdir(data_dir)
    except (FileNotFoundError, NotADirectoryError) as edir:
      print("Invalid path")
      data_dir=None
    if not fldrs:
      print("Empty directory")
      data_dir=None
  print('In ',data_dir)

  while not data_fldr:
    try:
      idx=int(input('Choose from (0-%d): \n'%(len(fldrs)-1) + str(fldrs)+'\n'))
      data_fldr=fldrs[idx]
    except (IndexError, NotADirectoryError, TypeError) as ei:
      print('Invalid entry')
      data_fldr = None

  full_path=join(data_dir, data_fldr)
  images=listdir(full_path)
  
  
def main():

  data_dir = None
  data_fldr = None


  patch_size = (64, 64)
  
  img=cv2.imread('test_img.png')
  data = extract_patches_2d(img, patch_size, max_patches=50,
                                  random_state=np.random.RandomState(0))
                                  
  print(len(data))                             
     

if __name__ == "__main__":
    exit(main())
