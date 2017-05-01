#!/usr/bin/env python3

from os import listdir, makedirs, getcwd
from os.path import join, splitext

from sklearn.feature_extraction.image import extract_patches_2d

import cv2
import numpy as np

def main():
  fldrs=[]
  images=[]
  classes={}
  data_dir = None
  data_fldr = None

# def imgs_from_fldr():

  while not data_dir:
    try:
      data_dir = join(getcwd(), input('path for dataset folders: '))
      fldrs=listdir(data_dir)
      #eliminate non-folder
      #remove non files in a trivial way
      fldrs=[ elm for elm in fldrs if "." not in elm ]

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

  full_path=join(data_dir, data_fldr +'/originals')
#  return full_path

#def main():
  hw=int(input('patch size: '))
  N=int(input('number of pathces: '))
  #images=listdir(imgs_from_fldr())
  images=listdir(full_path)
  size = (hw, hw) #patch_size
  sizetxt = str(size[0])+str(size[1])
  save_path=join(full_path, '../'+input('Please name your patching attempt: '))
  print(save_path)
  makedirs(save_path, exist_ok=True)
  rand = np.random.RandomState(0)


  for img_name in images:
    img=cv2.imread(join(full_path, img_name))
    print(img_name)
    ###### ACTUAL STUFF #######
    #Alternatively:    tf.extract_image_patches
    data = extract_patches_2d(img, size, max_patches=N, random_state=rand)
    ###########################
    name_split=splitext(img_name)
    count=0
    for patch in data:
      target=save_path+'/'+name_split[0]+'_'+ sizetxt +'_'+str(count)+'.jpg'
      print(target)
      cv2.imwrite(target, patch)
      count+=1


    print(len(data))


if __name__ == "__main__":
    exit(main())
