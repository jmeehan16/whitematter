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

sys.path.append('/var/www/wm/wsgi')
import render

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
        return [int(row[3]) + 1 for row in rows] #bfichter comment: i don't know why the + 1 was put here as the data is not 0 based, not going to change it though because of the large amount of compensating -1's now in the code

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

    return render.renderPng(width, height, rows)

def queryTopTile(brain,width,height,slicedepth,volume):
    header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (brain, 0, 0, slicedepth, volume, width - 1, height - 1,slicedepth,volume))
    #header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (brain, 0, 0, slicedepth, volume, height - 1, width - 1,slicedepth,volume))
    return render.renderPngTop(width-1, height-1, rows)
    
    #volume = queryEntireVolume()
    #f = open("/var/log/scidbpy_log.txt", 'w+')
    #f.write("volume of 90, 100  " + str(volume[90,100, 90])) 
    #return renderPngTop2(slicedepth, volume)
    #return renderPngDummy()

def queryFrontTile(brain, width, depth, slicedepth,volume):
    header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (brain, 0, slicedepth, 0, volume, depth-1, slicedepth, width - 1, volume))#maybe swap width-1 and height-1
    return render.renderPngFrontSide(depth-1, width-1, rows)
    #return renderPngDummy()

def querySideTile(brain, depth, height, slicedepth,volume):
    header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (brain, slicedepth, 0, 0, volume, slicedepth, height - 1, depth - 1, volume))#maybe swap width-1 and height-1
    return render.renderPngFrontSide(height-1, depth-1, rows)
    #return renderPngDummy()   
    
def removeArrays(pattern):
    import re
    
    for name in queryList():
        if re.match(pattern, name):
            querySciDB("remove(%s)" % name) 




