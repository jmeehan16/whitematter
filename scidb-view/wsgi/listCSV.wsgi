#!/usr/bin/python

import os
import json
import sys
import time
import subprocess      
import Image
import StringIO
import urlparse
import datetime

sys.path.append('/var/www/wm/wsgi')

def application(environ, start_response):
    #f = open('/var/log/list_log.txt','w+')
    #f.write('time: ' + str(datetime.datetime.now()))
    mypath = "/opt/whitematter/data/csv"

    from os import listdir
    from os.path import isfile, join
    names = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]

    content = {"names": names}
    start_response('200 OK', [('Content-Type', 'image/json')])
    
    #f.write('\n')
    #f.write(json.dumps({"names" : names}))

    #path = os.path.dirname(scidb2.__file__)
    #f.write("\npath: " + str(path))

    return [json.dumps(content)]
    #return [json.dumps({"names" : "john"})]
    
if __name__ == "__main__":
    sys.stdout.write("started\n")
    #f = open('/var/log/list_log.txt','w')

    sys.stdout.write("querying list\n")

    mypath = "/opt/whitematter/data/csv"
    from os import listdir
    from os.path import isfile, join
    names = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]

    sys.stdout.write("printing list\n")
    print names

    sys.stdout.write("finished\n")
