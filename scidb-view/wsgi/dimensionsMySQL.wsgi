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
import mysql

def application(environ, start_response):
    name = "image"

    qs = urlparse.parse_qs(environ['QUERY_STRING'])        
    if qs.get("name"):
        name = qs.get("name")[0]



    height, width, depth = mysql.queryDimensions(name)
    dimensions = mysql.queryNumVolumes(name)
    #width = 0
    #height = 0
    content = {"width": width, "height": height,"depth" : depth,"volume": dimensions}
    start_response('200 OK', [('Content-Type', 'image/json')])
    return [json.dumps(content)]

if __name__ == "__main__":
    sys.stdout.write("started\n")

    sys.stdout.write("querying description\n")
    dimensions = scidb.queryDimensions("image")

    sys.stdout.write("printing description\n")
    print dimensions 

    sys.stdout.write("finished\n")
