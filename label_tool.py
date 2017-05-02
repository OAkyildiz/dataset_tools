#!/usr/bin/env python

from sys import exit
from os import getcwd, listdir, chdir, makedirs, rename
from os.path import abspath, join, dirname
import cv2

images=[]
classes={}

def main():
  # no idee why I went with these variable names
  data_dir = None
  data_fldr = None
  set_fldr = None
  while not data_dir:
    try:
      data_dir=input('path for dataset folders: ')
      chdir(data_dir)
      #remove non files in a trivial way
      fldrs=[ elm for elm in listdir('.') if "." not in elm ]

    except (FileNotFoundError, NotADirectoryError) as edir:
      print("Invalid path")
      data_dir=None
    if not fldrs:
      print("Empty directory")
      chdir('..')
      data_dir=None

  print('In ',data_dir)
  while not data_fldr:
    try:
      idx=int(input('Choose from (0-%d): \n'%(len(fldrs)-1) + str(fldrs)+'\n'))
      data_fldr=fldrs[idx]
      chdir(data_fldr)

      # full_path=join(data_dir, data_fldr)
      sets=[ elm for elm in listdir('.') if "." not in elm ]

    except (IndexError, NotADirectoryError, TypeError) as ei:
      print('Invalid entry')
      data_fldr = None


  print('In ',data_fldr)
  while not set_fldr:
    try:
      idx=int(input('Choose from (0-%d): \n'%(len(sets)-1) + str(sets)+'\n'))
      set_fldr=sets[idx]
      chdir(set_fldr)
    except (IndexError, NotADirectoryError, TypeError) as ei:
      print('Invalid entry')
      set_fldr = None
## add one more layer

  images=[ img for img in listdir('.') if "."  in img ]
  print('image count: %d' %len(images) )
  # ask number of classes
  N=int(input('Number of classes: '))

  # name each class, select key for labels
  dflt='a' # hold the default key value
  for cn in range(N):
    # increment default char if key exists
    if dflt in classes:  dflt=chr(ord(dflt)+1)
    c=input('Name class_%d: ' %cn)
    inp=input('Assign key[%s]: ' %dflt)
    k=inp if inp  else dflt #and len(inpt)==1?
    classes[k]=c
    makedirs(c, exist_ok=True) # Each to its own.
    dflt=chr(ord(dflt)+1)

  #start labeling
  discards=[]
  makedirs('discards', exist_ok=True)

  labels=open('../'+set_fldr+ '_labels.txt', 'w')
  #iterate through images
  print("Start labeling the images with the keys you defined.")
  print('Hit ESC to discard the image')
  print("Hit any other key to skip the image for now.")

  cv2.namedWindow('image', cv2.WINDOW_NORMAL)
  c=0;
  for fname in images:
    c+=1
    print(fname, 'n: ',c)

    img=cv2.imread(fname) # laod image, could do it in one line
    cv2.imshow('image', img)
    hit=cv2.waitKey(0) & 0xff
    print(chr(hit))
    if chr(hit) in classes:
      c=classes[chr(hit)]
      labels.write(fname +', ' + c + '\n')
      rename(fname, c+ '/'+fname)
    elif hit == 27:
      print('Discarding %s.' %fname)
      images.remove(fname)
      discards.append(fname)
      rename(fname, 'discards/'+fname)

    else:
      print('skipping image %s for now.' %fname)
      images.remove(fname)
      images.append(fname)

  # wrap up
  labels.write('Discards: ' + str(discards))
  labels.close()

  cv2.destroyWindow('image')
  # log the discarded images/

if __name__ == "__main__":
    exit(main())
