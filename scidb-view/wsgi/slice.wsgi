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
import scidb
 
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
    try:
       request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
       request_body_size = 0
    request_body = environ['wsgi.input'].read(request_body_size)
    d = parse_qs(request_body)
    study = d.get('study')[0]
    width = int(d.get('width')[0])
    height = int(d.get('height')[0])
    depth = int(d.get('depth')[0])
    slicedepth = int(d.get('slicedepth')[0])
    
    depth -=2
    height -=1
    width -=1
    f = open('/var/log/dti_log.txt','w+')
    f.write('NEW CALL QQQQQQQQQQQQQQQQQQQQQQQQQ')
    f.write('width is:  ' + str(width))
    f.write('height is:  ' + str(height))
    f.write('depth is:  ' + str(depth))
    
    

    volume = int(d.get('volume')[0])
    viewtype = d.get('viewtype')[0]
    if viewtype=="top":
        content = scidb.queryTopTile(study, width, height, slicedepth, volume)
    elif viewtype=="front":
        #content = scidb.queryFrontTile(study, width, depth, slicedepth, volume)
        content = scidb.queryFrontTile(study, depth, width, slicedepth, volume)
    elif viewtype=="side":
        content = scidb.querySideTile(study, depth, height, slicedepth, volume)
    status = '200 OK'
    response_headers = [('Content-Type', 'image/png'),('Content-Length', str(len(content)))]
    start_response(status, response_headers)
    return [content]


if __name__ == "__main__":
    #this is good for nothing, won't run correctly as stand alone app
    sys.stdout.write("started\n")

    sys.stdout.write("querying tile\n")
#    png = scidb.queryTopTile("image", 128, 128, 0)
    sys.stdout.write("writing tile\n")
    fout = open("tile.png", "w")
    fout.write(png)
    fout.close()
