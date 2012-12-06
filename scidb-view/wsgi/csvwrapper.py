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
    

def prefetchEntireVolume():
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
    
	 


