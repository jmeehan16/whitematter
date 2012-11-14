#!/usr/bin/python

import os
import json
import sys
import time
import subprocess      
import Image
import StringIO
import urlparse

sys.path.append('/var/www/wsgi')
import scidb

def application(environ, start_response):
    names = scidb.queryList()
    content = {"names": names}
    start_response('200 OK', [('Content-Type', 'image/json')])
    return [json.dumps(content)]

if __name__ == "__main__":
    sys.stdout.write("started\n")

    sys.stdout.write("querying list\n")
    names = scidb.queryList()

    sys.stdout.write("printing list\n")
    print names

    sys.stdout.write("finished\n")
