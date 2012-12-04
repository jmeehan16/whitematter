#!/usr/bin/python

import os
import json
import sys
import subprocess      
import StringIO
import urlparse
sys.path.append('/var/www/wm/wsgi')
import scidb

def application(environ, start_response):
    qs = urlparse.parse_qs(environ['QUERY_STRING'])        
    name = "image"
    if qs.get("name"):
        name = qs.get("name")[0]

    dims = scidb.queryDimensions(name)
    numvolumes = dims[3]-1
    content = {"numvolumes": numvolumes}
    start_response('200 OK', [('Content-Type', 'image/json')])
    return [json.dumps(content)]
    
if __name__ == "__main__":
    sys.stdout.write("started\n")

    sys.stdout.write("querying list\n")
    dims = scidb.queryDimensions("dti_vectors2")
    numvolumes = dims[3]-1
    sys.stdout.write("printing list\n")
    print numvolumes

    sys.stdout.write("finished\n")
