#!/usr/bin/python

import os
import json
import sys
import time
import subprocess      
import Image
import StringIO
import urlparse

sys.path.append('/var/www/wm/wsgi')
import scidb
 
def application(environ, start_response):
    name = "image"
    width = 128 
    height= 128 
    x = 0
    y = 0
    level = 0

    qs = urlparse.parse_qs(environ['QUERY_STRING'])        
    if qs.get("name"):
        name = qs.get("name")[0]
    if qs.get("width"):
        width = int(qs.get("width")[0])
    if qs.get("height"):
        height = int(qs.get("height")[0])
    if qs.get("x"):
        x = int(qs.get("x")[0])
    if qs.get("y"):
        y = int(qs.get("y")[0])
    if qs.get("level"):
        name = "%s_level_%s" % (name, qs.get("level"))
    log = environ['wsgi.errors']
    print >> log,  "name: " + name + str(level)

    content = scidb.queryTile(name, width, height, x, y)

    start_response('200 OK', [('Content-Type', 'image/png')])
    return [content]

if __name__ == "__main__":
    sys.stdout.write("started\n")

    sys.stdout.write("querying tile\n")
    png = scidb.queryTile("image", 128, 128, 0, 0, 2)

    sys.stdout.write("writing tile\n")
    fout = open("tile.png", "w")
    fout.write(png)
    fout.close()