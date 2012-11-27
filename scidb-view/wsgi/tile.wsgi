#!/usr/bin/python

import os
import json
import sys
import time
import subprocess      
import Image
import StringIO
import urlparse
import cgi
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
    #post_env = environ.copy()
    #post_env['QUERY_STRING'] = ''
    #post = cgi.FieldStorage(
    #    fp=environ['wsgi.input'],
    #    environ=post_env,
    #    keep_blank_values=True
    #)
	
	#brain = int(post['brain'])
	#width = int(post['width'])
	#height = int(post['height'])
	#slicedepth = int(post['slicedepth'])
	
	
	
	#qs = urlparse.parse_qs(environ['QUERY_STRING'])
    #if qs.get("brain"):
    #    brain = qs.get("brain")[0]
    #if qs.get("width"):
    #    width = int(qs.get("width")[0])
    #if qs.get("height"):
    #    height = int(qs.get("height")[0])
    #if qs.get("slicedepth"):
    #    slicedepth = int(qs.get("slicedepth")[0])
    #content = scidb.queryTopTile(brain, width, height, slicedepth);
	#content = post 
    #start_response('200 OK', [('Content-Type', 'image/png')])
	start_response('200 OK', [('Content-Type', 'text/html')])
    return ["something"]


if __name__ == "__main__":
    sys.stdout.write("started\n")

    sys.stdout.write("querying tile\n")
	#need to add three here for testing
    png = scidb.queryTopTile("image", 128, 128, 0, 0, 2)

    sys.stdout.write("writing tile\n")
    fout = open("tile.png", "w")
    fout.write(png)
    fout.close()
