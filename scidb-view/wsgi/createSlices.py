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

volume = dict()
width = 0
height = 0
depth = 0

def querySciDB(cmd):
    """Execute the given SciDB command using iquery, returning the tabular result"""

    proc = subprocess.Popen(["/opt/scidb/12.10/bin/iquery", "-o", "csv+", "-a", "-q", cmd], stdout = subprocess.PIPE)
    out,err = proc.communicate()

    lines = out.split("\n")
    # first line is header, last line is empty
    header = lines[0].split(",")
    rows = [line.split(",") for line in lines[1:-1]]

    return header, rows 

def querySciDB2(cmd):
    """Execute the given SciDB command using iquery, returning the tabular result"""
    start = time.time()
    proc = subprocess.Popen(["/opt/scidb/12.10/bin/iquery", "-o", "csv", "-a", "-q", cmd], stdout = subprocess.PIPE)
    out,err = proc.communicate()
    end = time.time()
    timeDelta = end-start

    lines = out.split("\n")
    # first line is header, last line is empty
    header = lines[0] #.split(",")
    #f = open("/var/log/scidbpy_log.txt","w+")
    #f.write(str(timeDelta))
    #f.write("lines: " + str(lines[1:11]) + "\n")
    rows = lines[1:-1]
    #rows = [line.split(",") for line in lines[1:-1]]
    #f.write("rows: " + str(rows[0:10]) + "\n")

    return header, rows 

def queryDimensions(name):
    """Determine the dimensions of the specified array"""
    header, rows = querySciDB("dimensions(%s)" % name)

    if len(rows) < 2:
        return 0, 0
    else:
        return [int(row[3]) + 1 for row in rows]

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

if __name__ == "__main__":
    sys.stdout.write("started\n")

    sys.stdout.write("querying description\n")
    dimensions = scidb.queryDimensions("image")
    sys.stdout.write("dimensions[0]: " + str(dimensions[0]) + "\n")
    sys.stdout.write("dimensions[1]: " + str(dimensions[1]) + "\n")
    sys.stdout.write("dimensions[2]: " + str(dimensions[2]) + "\n")
    sys.stdout.write("dimensions[3]: " + str(dimensions[3]) + "\n")
    #loadVolumeMySql("image", 

    sys.stdout.write("printing description\n")
    print dimensions 

    sys.stdout.write("finished\n")
    
