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
import base64
import csv

sys.path.append('/var/www/wm/wsgi')
import render
import MySQLdb #gotta install this    apt-get install python-mysqldb


def queryMySQL(cmd):
    """Execute the given SciDB command using iquery, returning the tabular result"""

    #open the connection to mysql:
    conn = MySQLdb.connect (host = "localhost", user = "root", db = "whitematter") 
    with conn:
        cur = conn.cursor()
        cur.execute(cmd)

        #header = cur.fetchone()
        #print header
    
        rows = cur.fetchall()

    return rows 


def queryList():
    """Get a list of available arrays"""
    #f = open("/var/log/scidbpy_log.txt","w+")
    #f.write("starting queryList")

    rows = queryMySQL("show tables;")

    return rows

def queryDimensions(name):
    """Determine the dimensions of the specified array"""
    rows = queryMySQL("select MAX(slice) from %s group by plane order by plane;" % name)

    if len(rows) < 2:
        return 0, 0
    else:
        return [int(row[0]) + 1 for row in rows] #f,s,t

def queryNumVolumes(name):
    dimensions = queryMySQL("select MAX(vol) from %s;" % name)
    return [int(row[0]) + 1 for row in dimensions]

def queryDimensionNames(name):
    """Determine the dimension names of the specified array"""

    return "f,s,t"


"""***NOTE, the variable names width and height may not mean exactly what you think (not consistent with how picture is displayed) throughout these following functions,
 	this is because the orientations were not 'consistent' in scidb so in order to keep the three views oriented correctly 
	relative to each other (eyes/neck pointed same way) the semantics of width and height are broken"""

def queryTopTile(study,vol,slicedepth):
    f = open("/var/log/scidbpy_log.txt","w+")
    f.write("starting queryTopTile")
    rows = queryMySQL("select png from %s where vol = %d and plane = 't' and slice = $d;" % (study,vol,slicedepth)

    #l = [x[0] for x in rows]
    f.write("l = " + str(rows))
    return rows
    
    #volume = queryEntireVolume()
    #f = open("/var/log/scidbpy_log.txt", 'w+')
    #f.write("volume of 90, 100  " + str(volume[90,100, 90])) 
    #return renderPngTop2(slicedepth, volume)
    #return renderPngDummy()
"""
def queryFrontTile(study,vol,slicedepth):
    rows = queryMySQL("select png from %s where vol = %d and plane = 'f' and slice = $d;" % (study,vol,slicedepth)
    l = [x[0] for x in rows]
    return l[0]]

def querySideTile(study,vol,slicedepth):
    rows = queryMySQL("select png from %s where vol = %d and plane = 's' and slice = $d;" % (study,vol,slicedepth)
    l = [x[0] for x in rows]
    return l[0]
   

######this is the function which iterates through the volume generating pngs to load to mysql
######gotta call this somewhere
def loadVolumeMySql(name, volume, width, height, depth):

    #open the connection to mysql:
    conn = MySQLdb.connect (host = "localhost", user = "root", db = "whitematter") 
    cursor = conn.cursor()
    
    #first do xy plane, the top view
    for z in range(depth):
        header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (name, 0, 0, z, volume, width-1, height-1, z, volume))#debug help, the width, height and depth may be mismatched/out of place
        img = render.renderPngTop(width-1, height-1, rows)
        cursor.execute("INSERT INTO image VALUES (%s, %s, %s, %s)", (volume, 't', z, img))
        conn.commit()
    #second do xz plane, the side view
    for y in range(height):
        header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (name, 0, y, 0, volume, width-1, y, depth-1, volume))
        img = render.renderPngFrontSide(width-1, depth-1, rows)
        cursor.execute("INSERT INTO image VALUES (%s, %s, %s, %s)", (volume, 's', y, img))
        conn.commit()
    #last do the yz plane, the front view
    for x in range(width):
        header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (name, x, 0, 0, volume, x, height-1, depth-1, volume))
        img = render.renderPngFrontSide(height-1, depth-1, rows)
        cursor.execute("INSERT INTO image VALUES (%s, %s, %s, %s)", (volume, 'f', x, img)) 
        conn.commit()
    cursor.close()
    conn.close()
    
"""


