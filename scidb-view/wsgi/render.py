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
import benchmark

def renderPngFrontSide(width, height, rows):
    """Render the imaage for either the side or front view"""
    startT = benchmark.startTimer("renderPngFrontSide")
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
            pix[i, (height - 1) - j] = (val,val,val) #this mirrors vertically to make tri-view consistent with itself
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
    benchmark.endTimer("renderPngFrontSide", startT)

    return base64.b64encode(png)

def renderPngTop2(slicedepth, volume):
    startT = benchmark.startTimer("renderPngTop2")
    global width
    global depth
    image = Image.new("RGB", (depth, width))
    pix = image.load()
    x = 0
    z = 0 
    for rows in range(width * depth):
        val = int(volume[x, slicedepth, z])
        pix[x, z] = (val, val, val)
        x = (x+1)%width
        if x == 0:
            z = (z+1)%depth
    
    sout = StringIO.StringIO()
    image.save(sout, "PNG") 
    png = sout.getvalue()
    sout.close()
    benchmark.endTimer("renderPngTop2", startT)

    return base64.b64encode(png)
    

def renderPngTop(width, height, rows):
    """Render a top view slice, the height and width are not semantically correct here, see above for explanation"""
    startT = benchmark.startTimer("renderPngTop")
    image = Image.new("RGB", (height, width))
    pix = image.load()
    i = 0
    j = 0 
    #g = open("/var/log/scidbpy_log.txt","w+")
    #g.write("width: " + str(width) +"\n")
    #g.write("height: " + str(height) + "\n")
    #f = lambda v: int(v)
    for row in rows:
        try:
            val = int(row)
            #g.write("val: " + str(val) + "\n")
            #<bfichter> to make it white, a little contrived but...
            #g.write(str(i) + "," + str(j) + "\n")
            #g.write(str(val) + "\n")
            pix[j, i] = (val,val,val) 
            j = (j+1)%height 
            if j == 0: 
                i = (i+1)%width
        except Exception:
            #g.write("exception\n")
            #g.write("row: " + str(row) + "\n")
            pass

    sout = StringIO.StringIO()
    image.save(sout, "PNG") 
    png = sout.getvalue()
    sout.close()
    benchmark.endTimer("renderPngTop", startT)

    return base64.b64encode(png)

#renderPng is not called locally
def renderPng(width, height, rows):
    """Render an image specified by a list of pixel values"""
    startT = benchmark.startTimer("renderPng")
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
    benchmark.endTimer("renderPng", startT)

    return png

