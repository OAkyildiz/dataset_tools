import cv2
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()
file = args.file

img=cv2.imread(file, cv2.IMREAD_UNCHANGED)
def checkHits(img):
    shp=img.shape
    if len(shp)==2:
        r,g,b,mask = cv2.split(img)
    elif len(shp)==3:
        mask=img.copy()
    else:
        print('huh?')
        
    size=shp[0]*shp[1]   
     

    marked=cv2.countNonZero(mask)
return

print(marked/size,'%')
