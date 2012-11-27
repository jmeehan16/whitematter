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
    f = open("/var/log/scidbpy_log.txt","w+")
    f.write(str(timeDelta))
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

def queryTopTile(name, width, height, x, y, z):
    """Render an image of a tile of the specified array, returning a string
    encoding a PNG image.  This will always return an image of the specified
    dimensions, but the intensities may be zero for pixels that map outside the
    array"""

    wholeDims = queryDimensions(name) 
    wholeWidth = wholeDims[0]
    wholeHeight = wholeDims[1]
    wholeDepth = wholeDims[2]
    #wholeVolume = wholeDims[3]

    x0 = width * x
    y0 = height * y
    x1 = min(wholeWidth, x0 + width)
    y1 = min(wholeHeight, y0 + height)
    z = min(wholeDepth, z)

    rows = []
    if x1 > x0 and y1 > y0:
        # subarray uses inclusive ranges 
        header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (name, x0, y0, z, 0, x1 - 1, y1 - 1,z,0))
    return renderPng2(wholeWidth-1, wholeHeight-1, rows)

def queryFrontTile(name, depth, height, x, y, z):
    """A rework of the above method switching x and z (this might be wrong order)
    this interprets the z dimension as width and the y dimension as height"""
    wholeDims = queryDimensions(name)
    wholeWidth = wholeDims[0]
    wholeHeight = wholeDims[1]
    wholeDepth = wholeDims[2]
    #wholeVolume = wholeDims[3] #this is gonna need to be uncommented so different volumes can be queried

    z0 = depth * z
    y0 = height * y
    z1 = min(wholeDepth, z0 + depth)
    y1 = min(wholeHeight, y0 + height)
    x = min(wholeWidth, x)

    rows = []
    if z1 > z0 and y1 > y0:#this is being bypassed for some reason!!!!, unless x and z are swapped in tile.wsgi
        # subarray uses inclusive ranges 
        header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (name, x, y0, z0, 0, x, y1 - 1, z1 - 1, 0))#the zeroes here should be changed to a volume variable
    #header, rows = querySciDB("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (name, , , 0, 0, 50, 100, 100, 0))
        
    return renderPng2(depth, height, rows) #this order could be wrong


def querySideTile(name, width, depth, x, y, z):
    """see comment for front, this time z and y switched"""
    wholeDims = queryDimensions(name)
    wholeWidth = wholeDims[0]
    wholeHeight = wholeDims[1]
    wholeDepth = wholeDims[2]
    #wholeVolume = wholeDims[3]

    x0 = width * x
    z0 = depth * z
    x1 = min(wholeWidth, x0 + width)
    z1 = min(wholeDepth, z0 + depth)
    y = min(wholeHeight, y)

    rows = []
    if x1 > x0 and z1 > z0:
        # subarray uses inclusive ranges 
        header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (name, x0, y, z0, 0, x1 - 1, y, z1 - 1, 0))
    return renderPng2(width, depth, rows) #order could be wrong here too

def renderPng(width, height, rows):
    """Render an image specified by a list of pixel values"""

    image = Image.new("RGB", (width, height))
    pix = image.load()
    #f = lambda v: int(round(float(v)))
    f = lambda v: int(v)
    for row in rows:
        try:
            i, j, r, g, b = map(f, row)
            #<bfichter> to make it white, a little contrived but...
            #if b>0:
            #    r = b
            #    g = b#</bfichter>
            pix[i, j] = (b, b, b)
        except Exception:
            pass

    sout = StringIO.StringIO()
    image.save(sout, "PNG") 
    png = sout.getvalue()
    sout.close()

    return png

def renderPng2(width, height, rows):
    """Render an image specified by a list of pixel values"""

    image = Image.new("RGB", (width, height))
    pix = image.load()
    i = 0
    j = 0
    #g = open("/var/log/scidbpy_log.txt","w+")
    #g.write("width: " + str(width))
    #g.write("height: " + str(height))
    #f = lambda v: int(v)
    for row in rows:
        try:
            val = int(row)
            #<bfichter> to make it white, a little contrived but...
            #g.write(str(i) + "," + str(j) + "\n")
            #g.write(str(val) + "\n")
            pix[i, j] = (val,val,val)
            j = (j+1)%height
            if j == 0:
                i = (i+1)%width
        except Exception:
            #g.write("exception\n")
            pass

    sout = StringIO.StringIO()
    image.save(sout, "PNG") 
    png = sout.getvalue()
    sout.close()

    return png

def removeArrays(pattern):
    import re
    
    for name in queryList():
        if re.match(pattern, name):
            querySciDB("remove(%s)" % name)
