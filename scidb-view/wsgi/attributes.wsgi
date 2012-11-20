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

    qs = urlparse.parse_qs(environ['QUERY_STRING'])        
    if qs.get("name"):
        name = qs.get("name")[0]

    attributes = scidb.queryAttributes(name)

    content = {"attributes": attributes}
    start_response('200 OK', [('Content-Type', 'image/json')])
    return [json.dumps(content)]

if __name__ == "__main__":
    sys.stdout.write("started\n")

    sys.stdout.write("querying description\n")
    attributes = scidb.queryAttributes("image")

    sys.stdout.write("printing description\n")
    print attributes 

    sys.stdout.write("finished\n")
