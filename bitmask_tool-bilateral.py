import cv2
import numpy as np
import sys
import argparse
from os.path import splitext
from os import listdir, makedirs, rename

#cv2.CV_64F, cv2.CV_8UC3
color_mode=cv2.CV_8UC1
#8UC1

def none(img,*args):
    return img

def bilateral(img,d,sSpace,sCol):
    return cv2.bilateralFilter(img,d,sSpace,sCol)
#def adaptivebilateral(img,d,sSpace,Scol):
#    return cv2.adaptiveBilateralFilter(src, d, sSpace, maxSigmaColor=sCol) 

blurs={  
          0 : bilateral,
          #1 : adaptivebilateral
}


   
def sobelX(img):
    return cv2.Sobel(img,color_mode, 1, 0, ksize=5)  # x
   
def sobelY(img):
    return cv2.Sobel(img,color_mode, 0, 1, ksize=5)  # y
    
def laplacian(img):
    return cv2.Laplacian(img,color_mode)

def canny(img):
    return cv2.Canny(img,100,200)
    
        #laplacian = cv2.Laplacian(self.blur,cv2.CV_64F)
        #sobelx = cv2.Sobel(self.blur,cv2.CV_64F,1,0,ksize=5)  # x
        #sobely = cv2.Sobel(self.blur,cv2.CV_64F,0,1,ksize=5)  # y
        #filtered = cv2.Canny(self.blur,100,200)
filters={ 0 : none,
          1 : laplacian,
          2 : sobelX,
          3 : sobelY, 
          4 : canny
}

brushvals=[0,1,2,4,10,20,40]

def binary(img, val, tdir):
    ret,mask=cv2.threshold(img,float(val),255,tdir)
    return mask
    
def adaptive(img, val, tdir):    
    return cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,tdir,11,2)
    
def otsu(img, val, tdir):    
    ret3,mask = cv2.threshold(img,float(val),255,tdir+cv2.THRESH_OTSU)
    return mask


threshing={ 
            0: none,
            1: binary,
            2: adaptive,
            3: otsu
}


class EdgeUI(object):
    name=''
    display=''
    
    #okay, number of  members started to feel wrong for this kind of interface
    
    blurSel=0
    blurVal=1
    sigmaSpace=0
    sigmaColor=0
    thresholdVal=0
    threshSel=1
    THRESH_DIR=cv2.THRESH_BINARY_INV
    filterSel=0
    w,h=0,0
    #currently we can use 2 as each step is triggered if the preeceding one is.
    inp=None
    gray=None
    blurred=None
    filtered=None
    out=None
    canvas=None
    
    # it looks like it is time to create a class for the drawing pad itself
    brush_size=2
    brush_idx=2
    #drawing
    draw = False # true if mouse is pressed
    erase = False # if True, draw rectangle. Press 'm' to toggle to curve
    ix,iy = -1,-1
    
    def __init__(self,w,h, name='Edge Filters',indisplay='Bitmask Drawer'):
        self.name=name
        self.display=indisplay
       
        cv2.namedWindow(self.name)
       #cv2.moveWindow(self.name, 400,20)
        cv2.namedWindow(self.display)
        cv2.moveWindow(self.display, w,h)
        cv2.namedWindow('OG')
        cv2.moveWindow('OG', 800, 400)
        #cv2.createTrackbar('blur mtd  (bi,a.b.)',self.name,0,1,self.setBlurMethod)
        cv2.createTrackbar('blur         ',self.name,0,20,self.setBlur)
        cv2.createTrackbar('sigmaSpace   ',self.name,0,220,self.setSigmaSpace)
        cv2.createTrackbar('sigmaColor   ',self.name,0,36,self.setSigmaCol)
        #cv2.createTrackbar('filter type (0,sx,sy,l,c)',self.name,0,4,self.setFilter)
        #cv2.createTrackbar('threshold mtd (0,b,a,o)',self.name,0,3,self.setThreshMethod)
        cv2.createTrackbar('threshold val',self.name,0,255,self.setThreshold)

        
        cv2.setMouseCallback(self.display, self.mouseHandler)
        cv2.setMouseCallback(self.name, self.filterMouseHandler)
        #cv2.createButton('blur',self.name,self.onChange)

        #
    # Mouse callbacks
    def mouseHandler(self, event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.draw = True # true if mouse is pressed
            self.erase = False
            self.ix,self.iy = x,y
            #print('       brush size: ', self.brush_size)
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.draw == True:
                #self.erase = False
                cv2.circle(self.canvas,(x,y),self.brush_size ,(255,255,255),-1)
        elif event == cv2.EVENT_LBUTTONUP:
            self.draw = False
            cv2.circle(self.canvas,(x,y),self.brush_size ,(255,255,255),-1)
        
        if event == cv2.EVENT_RBUTTONDOWN:
            self.erase = True
            self.draw = False
            self.ix,self.iy = x,y
           # print('       brush size: ', self.brush_size)
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.erase == True:
                #self.draw = False
                cv2.circle(self.canvas,(x,y),self.brush_size ,(0,0,0),-1)
        elif event == cv2.EVENT_RBUTTONUP:
            self.erase = False
            cv2.circle(self.canvas,(x,y),self.brush_size ,(0,0,0),-1) 
          
        if event == cv2.EVENT_MBUTTONDOWN:
            self.draw = False
            self.erase = False
            self.togglebrush()
            
        #change brush size
        if event == cv2.EVENT_MOUSEWHEEL:
            if   flags > 0:
                self.brush_size+=1
            elif flags < 0 and self.brush_size:
                self.brush_size-=1
            #print('brush size: ', self.brush_size)
            #put this on a seperate window
                
        self.showcanvaslayers()
        
    def filterMouseHandler(self, event,x,y,flags,param):
	
            if event == cv2.EVENT_LBUTTONDOWN:
                self.draw = True # true if mouse is pressed
                self.erase = False
                self.ix,self.iy = x,y
                xi,xf,yi,yf = self.roify(x,y)
                #print(x, y)

                #print('       brush size: ', self.brush_size)
            elif event == cv2.EVENT_MOUSEMOVE:
                if self.draw == True:
                    #self.erase = False
                    #copy roi to canvas
                    xi,xf,yi,yf = self.roify(x,y)

                    self.canvas[yi:yf,xi:xf]=cv2.cvtColor(cv2.bitwise_or(self.canvas[yi:yf,xi:xf,0], self.out[yi:yf,xi:xf]),cv2.COLOR_GRAY2RGB)#make this method so it doesn't look nasty

            elif event == cv2.EVENT_LBUTTONUP:
                self.draw = False
                #copy roi to canvas
                xi,xf,yi,yf = self.roify(x,y)

                self.canvas[yi:yf,xi:xf]=cv2.cvtColor(cv2.bitwise_or(self.canvas[yi:yf,xi:xf,0], self.out[yi:yf,xi:xf]),cv2.COLOR_GRAY2RGB)
        
           #hijack ERASER for overwriting, instead of bitwise masking 
            if event == cv2.EVENT_RBUTTONDOWN:
                self.erase = True
                self.draw = False
                self.ix,self.iy = x,y
               # print('       brush size: ', self.brush_size)
            elif event == cv2.EVENT_MOUSEMOVE:
                if self.erase == True:
                    #self.draw = False
                    xi,xf,yi,yf = self.roify(x,y)
                    self.canvas[yi:yf,xi:xf]=cv2.cvtColor(self.out[yi:yf,xi:xf],cv2.COLOR_GRAY2RGB)
            elif event == cv2.EVENT_RBUTTONUP:
                self.erase = False
                xi,xf,yi,yf = self.roify(x,y)
                self.canvas[yi:yf,xi:xf]=cv2.cvtColor(self.out[yi:yf,xi:xf],cv2.COLOR_GRAY2RGB)

            if event == cv2.EVENT_MBUTTONDOWN:
                self.draw = False
                self.erase = False
                self.togglebrush()
                
            self.showcanvaslayers()
            
    def roify(self,x,y):
        sz=self.brush_size
        [xi,xf]=np.clip([x-sz,x+sz],0,self.w-1)
        [yi,yf]=np.clip([y-sz,y+sz],0,self.h-1)
        return xi,xf,yi,yf
   # def 
    #    elif event == cv2.EVENT_MBUTTONCLICK:
        #    cv2.imwrite()
        #def onChange(self):
     #       pass
    
    # any method calls the next one in the chain below.
    # change:
    #[new Img]     [setBlur]  [sel. Filter] [setThreshold]
    #   |                 |      |           |
    #   V                 V      V           V
    # Load -> cvt2Gray-> Blur-> filter -> threshold. 
    def togglebrush(self):
        self.brush_idx= (self.brush_idx+1)%len(brushvals)
        self.brush_size=brushvals[self.brush_idx]
        print('       brush size: ', self.brush_size)
     
    #def setBlurMethod(self, mtd):
        #self.blurSel=mtd
        #self.blur() 
    
    def setBlur(self, val):
        self.blurVal=val*2+1
        self.blur()        
        
    def setSigmaSpace(self, val):
        self.sigmaSpace=val
        self.blur()  
        
    def setSigmaCol(self, val):
        self.sigmaColor=val
        self.blur()  
        
    def setFilter(self, filter):
        self.filterSel=filter
        if(filter == 0):
            self.THRESH_DIR=cv2.THRESH_BINARY_INV
        else:
            self.THRESH_DIR=cv2.THRESH_BINARY
        self.filter()
        
    def setThreshMethod(self, mtd):
        self.threshSel=mtd
        self.threshold()    
        
    def setThreshold(self, val):
        self.thresholdVal=val
        self.threshold()    
        
    def blur(self):
        self.blurred = blurs[self.blurSel](self.gray, self.blurVal,self.sigmaSpace, self.sigmaColor)
        self.filter()
   
    def filter(self):

        self.filtered= filters[self.filterSel](self.blurred)
        self.threshold()
   
    def threshold(self):
        self.out=threshing[self.threshSel](self.filtered, self.thresholdVal, self.THRESH_DIR)
        #if(filter==LAPLACIAN)
        
        
    def updateManual(self, img):
        print('  updated manually')
        cv2.imshow(self.name, img)
        cv2.waitKey(0)
        
    def update(self):
        #print('update')
        cv2.imshow(self.name, self.out)
        cv2.waitKey(30)
        return
    
    def clearcanvas(self):
        self.canvas=np.zeros((self.inp.shape[0], self.inp.shape[1], 3), np.uint8)
        self.showcanvaslayers()
        
    def filter2canvas(self):
        self.canvas=cv2.cvtColor(self.out, cv2.COLOR_GRAY2BGR)  
        self.showcanvaslayers()
        
    def showcanvaslayers(self):

        cv2.imshow(self.display, cv2.add(self.inp, self.canvas))
        
    #can also take in a Mat
    def loadImg(self, img, str=True):
        
        if(str):
            self.inp=cv2.imread(img)
        else:
            self.inp=img
        self.w=self.inp.shape[1]
        self.h=self.inp.shape[0]
        # converting to gray scale
        self.gray = cv2.cvtColor(self.inp, cv2.COLOR_BGR2GRAY)
        self.blur()
        cv2.imshow(self.display, self.inp)
        cv2.imshow('OG', self.inp)
        self.clearcanvas()
        #print(self.canvas.shape)
        #print(self.inp.shape)
        
    def startadvance(self):
        pass
    # def saveFilter(self):
    #    cv2.imwrite()
     #def savePainted(self):
     
    #    cv2.imwrite()
    def run(self):
        while(1):
            cv2.imshow(self.name, self.out)
            key = cv2.waitKey(30)
            if 'b' == chr(key & 255):
                print('    Saving filtered img')
                return self.out
            elif 'm' == chr(key & 255):
                print('    Saving drawn bitmask')
                return cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
            elif 'c' == chr(key & 255):
                print('      Copied filter to canvas')
                self.filter2canvas()      
            elif 'z' == chr(key & 255):
                print('      Cleared canvas')
                self.clearcanvas()     
            
def main():        
    parser = argparse.ArgumentParser(description='Run basic Edge detection algortihms on a given image.')
    parser.add_argument('img_path', metavar='base', type=str, help='Path to the image to process.')
    args = parser.parse_args()
    path=args.img_path

    #blank=np.zeros((240, 320, 3), np.uint8)
    #blank[:] = (0,0,0)

    ui=EdgeUI(400,320)
    #top = tkinter.Tk()

    images=listdir(path)
    mask_save_path = path +'/../masks/'
    merged_save_path = path +'/../masked/'
    processed_path = path +'/../processed/'

    makedirs(mask_save_path, exist_ok=True)
    makedirs(merged_save_path, exist_ok=True)
    makedirs(processed_path, exist_ok=True)

    print('EdgeUI, v0.4')
    print('Image annotation tool for labeling')
    print('by Ozan Akyildiz')
    print('Use scrollbars to:')
    print('  - Set the blur method (None, Average, Gaussian, Median, Bilateral)')
    print('  - Set the blur kernel size (2k+1)')
    print('  - Choose edge filter (None, SobelX, SobelY, Laplacian, Canny)')
    print('  - Choose thresholding method (None, binary, adaptive, OTSU)')
    print('  - Set the threshhold value')
    print('Mouse:')
    print('  LMB - Draw')
    print('  RMB - Erase')     
    print('  MMB - Toggle brush size') 
    print('  MWD - Brush size -')     
    print('  MWU - Brush size +')         
    print('Keyboard:')
    print('Z - Reset drawing canvas')
    print('C - Copy filter result to canvas')
    print('B - Save filter result and proceed to next img')                
    print('M - Save drawn bitmask and ...')        
    # From a SW Design standpoint, this should be a part of the UI class.
    # But, you know... time.
    for img_name in images:
        # loading image
        
        print('----------')
        print('Opened :' + img_name)
        #img0 = cv2.imread(args.img_path, cv2.CV_8UC1)
        img0 = cv2.imread(path+'/'+img_name)

        print(img0.shape, img0.dtype)

        nm,ext = splitext(img_name)
        ui.loadImg(img0, False)
        
        mask = ui.run()
        #print(mask)
        #print('  bitmask:', mask.shape, mask.dtype)
        b,g,r=cv2.split(img0)
        print('Saved :' + nm + '.png', ', and moved the src img')
        to_save=cv2.merge((b,g,r,mask))
        rename(path+'/'+img_name, processed_path+img_name)
        print(to_save.shape, to_save.dtype)
    # remove noise 
        cv2.imwrite( mask_save_path + nm + '.bmp', mask)
        cv2.imwrite( merged_save_path + nm +'.png', to_save)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    print()
    sys.exit(main())
