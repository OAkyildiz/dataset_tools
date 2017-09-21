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

    makedirs('../auto/masks_seg', exist_ok=True)
    makedirs('../auto/masked_seg', exist_ok=True)
    
    errs=[]
    for seg in segfiles:

        if not readSeg(seg):
           errs.append(seg)  
    print('Orphan segs:')
    print(errs)
    
def readSeg(filepath):
    segobj=dict()
    f=open(filepath)
    
    
    pathinfo=readSplit(f) #TODO: make it a dictionary
    print(filepath,': .seg file for', pathinfo)
    segobj[pathinfo[0]]=pathinfo[1]    
    nm,ext = splitext(basename(segobj['image']))
    while(1):
        ln=readSplit(f)
        if ln[0]=='format':    
            f.readline() #skip 'data'
            break
        else:
            segobj[ln[0]]=int(ln[1])
            
    mask=np.zeros((segobj['height'], segobj['width']), np.uint8)
 
    while(1):
        line=readSplit(f)
        
        if line:
            data=[int(a) for a in line]
            writeRow(data,mask)
        else:
            break
    cv2.imwrite('../auto/masks_seg/'+nm+'.bmp',mask)
    img=cv2.imread(segobj['image'])
    if img is not None:
        mergeMask(img, mask, '../auto/masked_seg/'+nm+'.png')
        return True
        
    else:
        print('image '+ nm + ' not found')
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
