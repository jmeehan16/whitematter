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
    volume = int(d.get('volume')[0])#change this to something meaningful later
    slicedepth = 0#int(d.get('slicedepth')[0])
	
    #slicedepthstart = int(d.get('slicedepthstart')[0])
	#slicedepthend = int(d.get('slicedepthend')[0])
    slicedepthstart = 0#min(0,slicedepth-10)
    slicedepthend = 181# max(slidcedepth+10,181)
    viewtype = d.get('viewtype')[0]
    topslices = {'slice':'content'}
    sideslices = {'slice':'content'}
    frontslices = {'slice':'content'}
    allslices = {'viewtype':'view'}
    slicedepth = slicedepthstart
    while slicedepth <= slicedepthend: 
        #if viewtype=="top":
        topslices[slicedepth]=mysql.queryTopTile(study, width, height, slicedepth, volume)
        #elif viewtype=="front":
        frontslices[slicedepth]=mysql.queryFrontTile(study, width, depth, slicedepth, volume)
        #elif viewtype=="side":
        sideslices[slicedepth]=mysql.querySideTile(study, depth, height, slicedepth, volume)
        slicedepth+=1
    
    allslices['top'] = topslices
    allslices['front'] = frontslices
    allslices['side'] = sideslices
    start_response('200 OK', [('Content-Type', 'image/json')])
    return [json.dumps(allslices)]
    


if __name__ == "__main__":
    sys.stdout.write("started\n")

    sys.stdout.write("querying tile\n")
	#need to add three here for testing
#    png = scidb.queryTopTile("image", 128, 128, 0, 0, 2)

    sys.stdout.write("writing tile\n")
    fout = open("tile.png", "w")
    fout.write(png)
    fout.close()
