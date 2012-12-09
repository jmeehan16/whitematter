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
    

    qs = urlparse.parse_qs(environ['QUERY_STRING'])        
    pat_name = qs.get("pat_name")[0]

    patients = mysql.queryPatients(pat_name)

    content = {"patients":patients}
    start_response('200 OK', [('Content-Type', 'image/json')])
    return [json.dumps(content)]

if __name__ == "__main__":
    sys.stdout.write("started\n")

    sys.stdout.write("querying patients\n")
    patients = mysql.queryPatients("s1001")

    sys.stdout.write("finished\n")
