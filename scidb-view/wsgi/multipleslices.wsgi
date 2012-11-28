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
    brain = d.get('brain')[0]
    width = int(d.get('width')[0])
    height = int(d.get('height')[0])
	slicedepth = int(d.get('slicedepth')[0])
	
    #slicedepthstart = int(d.get('slicedepthstart')[0])
	#slicedepthend = int(d.get('slicedepthend')[0])
	slicedepthstart = min(0,slicedepth-10)
	slicedepthend = max(slidcedepth+10,181)
    viewtype = d.get('viewtype')[0]
	slices = []
	slicedepth = slicedepthstart;
	while slicedepth <= slicedepthend: 
		if viewtype=="top":
            slices[slicedepth]=scidb.queryTopTile(brain, width, height, slicedepth);
        elif viewtype=="front":
            slices[slicedepth]=scidb.queryFrontTile(brain, 218, 182, slicedepth);
        elif viewtype=="side":
            slice[slicedepth]=slices.append(scidb.querySideTile(brain, 182, 182, slicedepth);
        status = '200 OK'
        response_headers = [('Content-Type', 'image/png'),('Content-Length', str(len(content)))]
        start_response(status, response_headers)
    return [slices]


if __name__ == "__main__":
    sys.stdout.write("started\n")

    sys.stdout.write("querying tile\n")
	#need to add three here for testing
#    png = scidb.queryTopTile("image", 128, 128, 0, 0, 2)

    sys.stdout.write("writing tile\n")
    fout = open("tile.png", "w")
    fout.write(png)
    fout.close()