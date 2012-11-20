#!/usr/bin/python

import os,json
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

    qs = urlparse.parse_qs(environ['QUERY_STRING'])        
    if qs.get("name"):
        name = qs.get("name")[0]

    content = scidb.queryImage(name)

    start_response('200 OK', [('Content-Type', 'image/png')])
    return [content]

if __name__ == "__main__":
    sys.stdout.write("started\n")

    sys.stdout.write("querying image\n")
    png = scidb.queryImage("image")

    sys.stdout.write("writing image\n")
    fout = open("image.png", "w")
    fout.write(png)
    fout.close()
