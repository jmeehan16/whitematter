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
import csv

volume = dict()
width = 0
height = 0
depth = 0

def querySciDB(cmd):
    """Execute the given SciDB command using iquery, returning the tabular result"""

    proc = subprocess.Popen(["/opt/scidb/12.10/bin/iquery", "-o", "csv+", "-a", "-q", cmd], stdout = subprocess.PIPE)
    out,err = proc.communicate()

    lines = out.split("\n")
    # first line is header, last line is empty
    header = lines[0].split(",")
    rows = [line.split(",") for line in lines[1:-1]]

    return header, rows 

def querySciDB2(cmd):
    """Execute the given SciDB command using iquery, returning the tabular result"""
    start = time.time()
    proc = subprocess.Popen(["/opt/scidb/12.10/bin/iquery", "-o", "csv", "-a", "-q", cmd], stdout = subprocess.PIPE)
    out,err = proc.communicate()
    end = time.time()
    timeDelta = end-start

    lines = out.split("\n")
    # first line is header, last line is empty
    header = lines[0] #.split(",")
    #f = open("/var/log/scidbpy_log.txt","w+")
    #f.write(str(timeDelta))
    #f.write("lines: " + str(lines[1:11]) + "\n")
    rows = lines[1:-1]
    #rows = [line.split(",") for line in lines[1:-1]]
    #f.write("rows: " + str(rows[0:10]) + "\n")

    return header, rows 

def queryList():
    """Get a list of available arrays"""
    #f = open("/var/log/scidbpy_log.txt","w+")
    #f.write("starting queryList")

    header, rows = querySciDB("list('arrays')")
    names = [row[1].translate(None, "\"") for row in rows]

    return names

def queryDimensions(name):
    """Determine the dimensions of the specified array"""
    header, rows = querySciDB("dimensions(%s)" % name)

    if len(rows) < 2:
        return 0, 0
    else:
        return [int(row[3]) + 1 for row in rows]

def queryDimensionNames(name):
    """Determine the dimension names of the specified array"""

    header, rows = querySciDB("dimensions(%s)" % name)
    return [row[1].translate(None, "\"") for row in rows]

def queryAttributeNames(name):
    """Determine the attribute names of the specified array"""

    header, rows = querySciDB("attributes(%s)" % name)
    return [row[1].translate(None, "\"") for row in rows]

def queryImage(name):
    """Render an image of the entirety of the specified array, returning a
    string encoding a PNG image"""

    width, height = queryDimensions(name)
    header, rows = querySciDB("scan(%s)" % name)

    return renderPng(width, height, rows)

#def queryTopTile(name, width, height, x, y, z):
#    """Render an image of a tile of the specified array, returning a string
#    encoding a PNG image.  This will always return an image of the specified
#    dimensions, but the intensities may be zero for pixels that map outside the
#    array"""
#
#    wholeDims = queryDimensions(name) 
#    wholeWidth = wholeDims[0]
#    wholeHeight = wholeDims[1]
#    wholeDepth = wholeDims[2]
#    #wholeVolume = wholeDims[3]
#
#    x0 = width * x
#    y0 = height * y
#    x1 = min(wholeWidth, x0 + width)
#    y1 = min(wholeHeight, y0 + height)
#    z = min(wholeDepth, z)
#
#    rows = []
#    if x1 > x0 and y1 > y0:
#        # subarray uses inclusive ranges 
#        header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (name, x0, y0, z, 0, x1 - 1, y1 - 1,z,0))
#    return renderPng2(wholeWidth-1, wholeHeight-1, rows)


"""***NOTE, the variable names width and height may not mean exactly what you think (not consistent with how picture is displayed) throughout these following functions,
 	this is because the orientations were not 'consistent' in scidb so in order to keep the three views oriented correctly 
	relative to each other (eyes/neck pointed same way) the semantics of width and height are broken"""
def queryTopTile(brain,width1,height1,slicedepth):
    #header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (brain, 0, 0, slicedepth, 0, width - 1, height - 1,slicedepth,0))
    #return renderPngTop(width-1, height-1, rows)
    
    volume = queryEntireVolume()
    #f = open("/var/log/scidbpy_log.txt", 'w+')
    #f.write("volume of 90, 100  " + str(volume[90,100, 90])) 
    #return renderPngTop2(slicedepth, volume)
    return renderPngDummy()

def queryFrontTile(brain, height, width, slicedepth):
    header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (brain, slicedepth, 0, 0, 0, slicedepth, width - 1, height - 1, 0))#maybe swap width-1 and height-1
    return renderPngFrontSide(width-1, height-1, rows)
    #return renderPngDummy()

def querySideTile(brain, height, width, slicedepth):
    header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (brain, 0, slicedepth, 0, 0, width-1, slicedepth, height - 1, 0))#maybe swap width-1 and height-1
    return renderPngFrontSide(width-1, height-1, rows)
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
    
def removeArrays(pattern):
    import re
    
    for name in queryList():
        if re.match(pattern, name):
            querySciDB("remove(%s)" % name) 




