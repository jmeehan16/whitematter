#!/usr/bin/python

import os
import json
import sys
import time
import subprocess      
import Image
import StringIO
import urlparse
import datetime
import base64

sys.path.append('/var/www/wm/wsgi')
import render
from matrix import matrix



"""***NOTE, the variable names width and height may not mean exactly what you think (not consistent with how picture is displayed) throughout these following functions,
 	this is because the orientations were not 'consistent' in scidb so in order to keep the three views oriented correctly 
	relative to each other (eyes/neck pointed same way) the semantics of width and height are broken"""
def queryTopTile(volume, slicedepth):
    
    return render.renderPngDummy()

def queryFrontTile(volume, slicedepth):
    #return render.renderPngFrontSide(width-1, height-1, rows)
    return render.renderPngDummy()

def querySideTile(volume, slicedepth):
    #return render.renderPngFrontSide(width-1, height-1, rows)
    return render.renderPngDummy()
     

def queryEntireVolume():
    # open("001.csv")
    # first line = width
    # sec line = height
    # third line = depth
    # fourth line start with loop
	# volume = {"x":"y":"z":"v"}
	# volume = dict()
    #
    #lines = [line.rstrip('\n') for line in open('000.csv')] # this should be a list of the lines without new line character

    
    width = 0
    heigth = 0
    depth = 0

    f = open('/opt/whitematter/data/csv/000.csv', 'r')
#        s = open("/var/log/scidbdebug.txt", 'a')
        
    x = 0
    y = 0
    z = 0
    counter = 0
        
    for line in f:
        if counter ==0:
            width = int(line)###MAYBE DO line.rstrip('\n') for all the line usages
            counter = 1
        elif counter ==1:
            height = int(line)
            counter = 2
        elif counter ==2:
            depth = int(line)
            counter = 3
            volume = matrix(width, height, depth)
        else:
            volume[x,y,z] = int(line)
            z = (z+1) % depth
            if z == 0:
                y = (y+1) % height
            if y==0 and z==0:
                x = (x+1) % width
                #counter+=1      
                #s.write("counter is  " + str(counter))
                #s.write("\n") 
            
    return volume
    

def prefetchEntireVolume(study, volume):

    
    width = 0
    heigth = 0
    depth = 0

    path = '/opt/whitematter/data/csv/' + study + '/' + volume + '.csv' #this makes some assumptions about how the file system is set up, mandate this or change it 

    f = open('/opt/whitematter/data/csv/000.csv', 'r')
    #f = open(path, 'r') #switch to this when ready
        
    x = 0
    y = 0
    z = 0
    counter = 0
        
    for line in f:
        if counter ==0:
            width = int(line)###MAYBE DO line.rstrip('\n') for all the line usages
            counter = 1
        elif counter ==1:
            height = int(line)
            counter = 2
        elif counter ==2:
            depth = int(line)
            counter = 3
            pixels = matrix(width, height, depth)
        else:
            pixels[x,y,z] = int(line)
            z = (z+1) % depth
            if z == 0:
                y = (y+1) % height
            if y==0 and z==0:
                x = (x+1) % width
                #counter+=1      
                #s.write("counter is  " + str(counter))
                #s.write("\n") 
        
    topslices = {}
    sideslices = {}
    frontslices = {}
    allslices = {}

    #should probably factor this code into a method but just trying to get it working
    for zi in range(depth):
        image = Image.new("RGB", (height, width))#maybe this should be reversed (and if so also pix[])
        pix = image.load() 
        for xi in range(width):
            for yi in range(height):
                pix[yi, xi] = pixels[xi, yi, zi] 
        #done with this slice make a png
        sout = StringIO.StringIO()
        image.save(sout, "PNG") 
        pn = sout.getvalue()
        sout.close()
        png = base64.b64encode(pn)
        #add slice and slice depth        
        topslices[zi] = {'c':png, 's':zi} #i think this is right but could easily be side or front

    for xo in range(width):
        image = Image.new("RGB", (height, depth))
        pix = image.load() 
        for zo in range(depth):
            for yo in range(height):
                pix[yo, zo] = pixels[xo, yo, zo]
        sout = StringIO.StringIO()
        image.save(sout, "PNG") 
        pn = sout.getvalue()
        sout.close()
        png = base64.b64encode(pn)
        #add slice and slice depth        
        sideslices[xo] = {'c':png, 's':xo}

    for yj in range(height):
        image = Image.new("RGB", (width, depth))
        pix = image.load() 
        for zj in range(depth):
            for xj in range(width):
                pix[xj, zj] = pixels[xj, yj, zj]
        sout = StringIO.StringIO()
        image.save(sout, "PNG") 
        pn = sout.getvalue()
        sout.close()
        png = base64.b64encode(pn)
        #add slice and slice depth
        frontslices[yj] = {'c':png, 's':yj}        

    allslices['top'] = topslices
    allslices['front'] = frontslices
    allslices['side'] = sideslices
    return allslices

   
	 


