#!/usr/bin/python

import os
import json
import sys
import time
import subprocess      
import Image
import StringIO
import urlparse
from cgi import parse_qs, escape
sys.path.append('/var/www/wm/wsgi')
import csvwrapper

from beaker.middleware import SessionMiddleware
import shelve


 
#def application(environ, start_response):
#    name = "image"
#    width = 128 
#    height= 128 
#    x = 0
#    y = 0
#    level = 0
#
#    qs = urlparse.parse_qs(environ['QUERY_STRING'])        
#    if qs.get("name"):
#        name = qs.get("name")[0]
#    if qs.get("width"):
#        width = int(qs.get("width")[0])
#    if qs.get("height"):
#        height = int(qs.get("height")[0])
#    if qs.get("x"):
#        x = int(qs.get("x")[0])
#    if qs.get("y"):
#        y = int(qs.get("y")[0])
#    if qs.get("z"):
#	    z = int(qs.get("z")[0])
#    if qs.get("level"):
#        name = "%s_level_%s" % (name, qs.get("level"))
#    log = environ['wsgi.errors']
#    print >> log,  "name: " + name + str(level)
#    
#    #need to return three images here instead of one, look at js
#    #content = scidb.queryFrontTile(name, width, height, z, y,x)#swapped z and x here
#    content = scidb.queryTopTile(name, width, height, x, y, z)
#    start_response('200 OK', [('Content-Type', 'image/png')])
#    return [content]

def application(environ,start_response):
    request_body = environ['wsgi.input'].read(request_body_size)
    d = parse_qs(request_body)
    study = d.get('study')[0]
    volume = int(d.get('volume')[0])

    content = csvwrapper.prefetchEntireVolume(study, volume)


    status = '200 OK'
    response_headers = [('Content-Type', 'image/png'),('Content-Length', str(len(content)))]
    start_response(status, response_headers)
    return [content]

"""session_opts = {
    'session.type': 'file',
    'session.cookie_expires': True,
    'data_dir': '/tmp/scidb',
    #'cache.data_dir': '/tmp/scidb/cache',
    #'cache.lock_dir':'/tmp/scidb/lock'
}

application = SessionMiddleware(application, session_opts)"""



if __name__ == "__main__":
    print "STARTED"
    start_time = time.time()
    csvwrapper.prefetchEntireVolume("fake", 2)
    print time.time() - start_time, "seconds"
    print "FINISHED"
