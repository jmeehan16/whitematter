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
    study_name = qs.get("study_name")[0]

    studies = mysql.queryStudies(study_name)

    content = {"studies":studies}
    start_response('200 OK', [('Content-Type', 'image/json')])
    return [json.dumps(content)]

if __name__ == "__main__":
    sys.stdout.write("started\n")

    sys.stdout.write("querying studies\n")
    patients = mysql.queryStudies("fit_dti_dti_fa")
    for row in patients:
        print row
    sys.stdout.write("finished\n")
