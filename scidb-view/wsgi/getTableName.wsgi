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
    study_id = qs.get("study_id")[0]
    pat_id = qs.get("pat_id")[0]

    tableName = mysql.queryTableName(int(pat_id), int(study_id))

    #content = {"table_name":tableName}
    start_response('200 OK', [('Content-Type', 'image/json')])
    return [json.dumps(tableName)]

if __name__ == "__main__":
    sys.stdout.write("started\n")

    sys.stdout.write("querying table name\n")
    patients = mysql.queryTableName(1, 1)
    for row in patients:
        print row
    sys.stdout.write("finished\n")
