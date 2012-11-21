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
    f = open("/var/log/scidbpy_log.txt","w+")
    f.write("starting querySciDb")
    f.write("\ndate " + str(datetime.datetime.now()))

    proc = subprocess.Popen(["/opt/scidb/12.10/bin/iquery", "-o", "csv+", "-a", "-q", cmd], stdout = subprocess.PIPE)
    out,err = proc.communicate()

    lines = out.split("\n")
    # first line is header, last line is empty
    header = lines[0].split(",")
    rows = [line.split(",") for line in lines[1:-1]]

    f.write("\ncmd " + str(cmd))
    f.write("\nout " + str(out))
    f.write("\nerr " + str(err))
    f.write("\nlines " + str(lines))

    return header, rows 

def queryList():
    """Get a list of available arrays"""
    f = open("/var/log/scidbpy_log.txt","w+")
    f.write("starting queryList")

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

def queryHorizontalTile(name, width, height, x, y, z):
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
        header, rows = querySciDB("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (name, x0, y0, z, 0, x1 - 1, y1 - 1,z,0))
        
    return renderPng(width, height, rows)

def renderPng(width, height, rows):
    """Render an image specified by a list of pixel values"""

    image = Image.new("RGB", (width, height))
    pix = image.load()
    f = lambda v: int(round(float(v)))
    for row in rows:
        try:
            i, j, r, g, b = map(f, row)
            pix[i, j] = (r, g, b)
        except Exception:
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
