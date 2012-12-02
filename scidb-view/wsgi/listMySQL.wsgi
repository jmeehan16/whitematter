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
import mysqlwrapper

def application(environ, start_response):
    #f = open('/var/log/list_log.txt','w+')
    #f.write('time: ' + str(datetime.datetime.now()))
    #try:
    #   f.write("I am trying dude")
    names = scidb.queryList()
    #except:
    #    f.write("function exception")
    #names = ['image', 'scidbLoadCsv_load_2964', 'scidbLoadCsv_load_3011', 'scidbLoadCsv_load_3076', 'scidbLoadCsv_load_3195', 'scidbLoadCsv_load_3243', 'scidbLoadCsv_load_3386', 'scidbLoadCsv_load_3449', 'scidbLoadCsv_load_3492', 'scidbLoadCsv_load_3846', 'scidbLoadCsv_load_3916', 'scidbLoadCsv_load_3957', 'scidbLoadCsv_load_4003']

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
    #try:
    names = mysqlwrapper.queryList()
    #except:
    #    f.write("carrots")
    #f.write(json.dumps({"names" : names}))

    #path = os.path.dirname(scidb2.__file__)
    #f.write("\npath: " + str(path))

    sys.stdout.write("printing list\n")
    print names

    sys.stdout.write("finished\n")
