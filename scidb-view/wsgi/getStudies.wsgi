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
    if qs.get("id"):
        pat_id = qs.get("id")[0]

        studies = mysql.queryStudies(pat_id)

        
    else:
        studies = mysql.queryAllStudies()
    
    content = {"studies":studies}
    start_response('200 OK', [('Content-Type', 'image/json')])
    return [json.dumps(content)]
       
if __name__ == "__main__":
    sys.stdout.write("started\n")

    sys.stdout.write("querying studies\n")
    patients = mysql.queryAllStudies()
    """for row in patients:
        print row[0]
        print row[1]"""
    print patients
    sys.stdout.write("finished\n")
