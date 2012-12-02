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

volume = dict()
width = 0
height = 0
depth = 0


"""***NOTE, the variable names width and height may not mean exactly what you think (not consistent with how picture is displayed) throughout these following functions,
 	this is because the orientations were not 'consistent' in scidb so in order to keep the three views oriented correctly 
	relative to each other (eyes/neck pointed same way) the semantics of width and height are broken"""
def queryTopTile(brain,width1,height1,slicedepth):
    
    volume = queryEntireVolume()
    #f = open("/var/log/scidbpy_log.txt", 'w+')
    #f.write("volume of 90, 100  " + str(volume[90,100, 90])) 
    #return renderPngTop2(slicedepth, volume)
    return render.renderPngDummy()

def queryFrontTile(brain, height, width, slicedepth):
    header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (brain, slicedepth, 0, 0, 0, slicedepth, width - 1, height - 1, 0))#maybe swap width-1 and height-1
    return render.renderPngFrontSide(width-1, height-1, rows)
    #return renderPngDummy()

def querySideTile(brain, height, width, slicedepth):
    header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (brain, 0, slicedepth, 0, 0, width-1, slicedepth, height - 1, 0))#maybe swap width-1 and height-1
    return render.renderPngFrontSide(width-1, height-1, rows)
    #return renderPngDummy()
     

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

    global volume
    global width
    global heigth
    global depth

    if len(volume.keys())==0:
    #if 1 == 1:
        f = open('/opt/whitematter/data/csv/000.csv', 'r')
#        s = open("/var/log/scidbdebug.txt", 'a')
        
        x = 0
        y = 0
        z = 0
        counter = 0
        
        for line in f:
            if counter ==0:
                width = int(line)
                counter = 1
            elif counter ==1:
                height = int(line)
                counter = 2
            elif counter ==2:
                depth = int(line)
                counter = 3
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
    
	 


