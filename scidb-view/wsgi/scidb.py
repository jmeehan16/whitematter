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


def queryTopTile(brain,width,height,slicedepth):
    header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (brain, 0, 0, slicedepth, 0, width - 1, height - 1,slicedepth,0))
    return renderPngTop(width-1, height-1, rows)


def queryFrontTile(brain, height, width, slicedepth):#switched width and height
    header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (brain, slicedepth, 0, 0, 0, slicedepth, width - 1, height - 1, 0))#maybe swap width-1 and height-1
    return renderPng2(width-1, height-1, rows)

def querySideTile(brain, height, width, slicedepth):#switched width and height
    header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (brain, 0, slicedepth, 0, 0, width-1, slicedepth, height - 1, 0))#maybe swap width-1 and height-1
    return renderPng2(width-1, height-1, rows)


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
            pix[i, height - j] = (val,val,val)
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

    return base64.b64encode(png)

def renderPngTop(width, height, rows):
    """Render an image specified by a list of pixel values"""

    image = Image.new("RGB", (height, width))
    pix = image.load()
    i = 0
    j = 0 #SHOULD SWITCH ALL HEIGHTS AND WIDTHS TO MAKE THIS MORE INTUITIVE
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
            pix[j, i] = (val,val,val) 
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

    return base64.b64encode(png)

def renderPng3(width, height, rows):
    """Render an image specified by a list of pixel values"""

    image = Image.new("RGB", (height, width))
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

    return base64.b64encode(png)

def removeArrays(pattern):
    import re
    
    for name in queryList():
        if re.match(pattern, name):
            querySciDB("remove(%s)" % name)
