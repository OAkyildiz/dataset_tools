import numpy as np
import cv2
import argparse, re, sys
from os import listdir, makedirs, chdir
from os.path import basename, splitext 


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")

    args = parser.parse_args()
    path=args.path

    segfiles=listdir(path)
    #print(segfiles)
    print('Number of files', len(segfiles))
    chdir(path)

    makedirs('../auto', exist_ok=True)
    
    for seg in segfiles:

        readSeg(seg)  
    
def readSeg(filepath):
    seg=dict()
    f=open(filepath)
    
    
    pathinfo=readSplit(f) #TODO: make it a dictionary
    print(filepath,': .seg file for', pathinfo)
    seg[pathinfo[0]]=pathinfo[1]    
    nm,ext = splitext(basename(seg['image']))
    while(1):
        ln=readSplit(f)
        if ln[0]=='format':    
            f.readline() #skip 'data'
            break
        else:
            seg[ln[0]]=int(ln[1])
            
    mask=np.zeros((seg['height'], seg['width']), np.uint8)

    while(1):
        line=readSplit(f)
        
        if line:
            data=[int(a) for a in line]
            writeRow(data,mask)
        else:
            break
    
    img=cv2.imread(seg['image'])
    if img is not None:
        mergeMask(img, mask, '../masked_seg/'+nm+'.png')
        return True
        
    else:
        cv2.imwrite('../masks_seg/'+nm+'.bmp',mask)
        print('image not found')
        return False
        
        
def mergeMask(img, mask, path):
    print(img.shape)
    b,g,r=cv2.split(img)
    merged=cv2.merge((b,g,r,mask))
    cv2.imwrite(path,merged)
    
def readSplit(file):
    return file.readline().split()


def writeRow(data, arr): #make this a comprehension later
    #check gray, or check multiclass-binary then add the multiclass option
    if data[0]:
        arr[data[1],data[2]:data[3]]=255

if __name__ == "__main__":
    sys.exit(main())
