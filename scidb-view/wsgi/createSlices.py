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
import math

sys.path.append('/var/www/wm/wsgi')
import render
import MySQLdb #gotta install this    apt-get install python-mysqldb

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

def querySciDBAQL(cmd):
    """Execute the given SciDB command using iquery, returning the tabular result"""
    start = time.time()
    proc = subprocess.Popen(["/opt/scidb/12.10/bin/iquery", "-o", "csv", "-q", cmd], stdout = subprocess.PIPE)
    out,err = proc.communicate()
    end = time.time()
    timeDelta = end-start

    lines = out.split("\n")
    # first line is header, last line is empty
    header = lines[0] #.split(",")
    #f = open("/var/log/scidbpy_log.txt","w+")
    #f.write(str(timeDelta))
    #f.write("lines: " + str(lines[1:11]) + "\n")
    row = lines[1]
    #rows = [line.split(",") for line in lines[1:-1]]
    #f.write("rows: " + str(rows[0:10]) + "\n")

    return header, row

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
    conn.commit()

    return rows 

def createNewTable(name):
    queryMySQL("DROP TABLE IF EXISTS %s" % (name))
    queryMySQL("CREATE TABLE %s (vol SMALLINT NOT NULL, plane CHAR NOT NULL, slice INT NOT NULL, png MEDIUMTEXT);" % (name))
    queryMySQL("ALTER TABLE %s ADD PRIMARY KEY(vol,plane,slice)" % (name))

    return

def queryDimensions(name):
    """Determine the dimensions of the specified array"""
    header, rows = querySciDB("dimensions(%s)" % name)

    if len(rows) < 2:
        return 0, 0
    else:
        return [int(row[3]) + 1 for row in rows]

def adjustSciDBValues(name, vol):
    minv = math.floor(getMinValue(name,vol)[0])
    maxv = math.ceil(getMaxValue(name,vol)[0])
    difv = maxv - minv
    querySciDB2("UPDATE %s SET v=(v+%d)*255/%d WHERE vol=%d" % (name,minv,difv,vol))
    
def getMinValue(name, vol):
    """Gets the min value from the current vol"""
    header, row = querySciDBAQL("SELECT min(v) from %s WHERE d=%s;" % (name, vol))
    return int(row[1])

def getMaxValue(name, vol):
    """Gets the min value from the current vol"""
    header, row = querySciDBAQL("SELECT max(v) from %s WHERE d=%s;" % (name, vol))
    return int(row[1])

######this is the function which iterates through the volume generating pngs to load to mysql
######gotta call this somewhere
def loadVolumeMySql(name, volume, width, height, depth):
    
    #first do xy plane, the top view
    for z in range(depth):
        header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (name, 0, 0, z, volume, width-1, height-1, z, volume))#debug help, the width, height and depth may be mismatched/out of place
        img = render.renderPngTop(width, height, rows)
        queryMySQL("INSERT INTO %s (vol,plane,slice,png) VALUES (%d, 't', %d, '%s')" % (name, volume, z, img))
    #second do xz plane, the side view
    for y in range(height):
        header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (name, 0, y, 0, volume, width-1, y, depth-1, volume))
        img = render.renderPngFrontSide(width, depth, rows)
        queryMySQL("INSERT INTO %s (vol,plane,slice,png) VALUES (%d, 's', %d, '%s')" % (name, volume, y, img))
    #last do the yz plane, the front view
    for x in range(width):
        header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (name, x, 0, 0, volume, x, height-1, depth-1, volume))
        img = render.renderPngFrontSide(height, depth, rows)
        queryMySQL("INSERT INTO %s (vol,plane,slice,png) VALUES (%d, 'f', %d, '%s')" % (name, volume, x, img))

    return

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stdout.write("Wrong number of arguments. createSlices.py requires table name")
        sys.exit()
    name = sys.argv[1]

    sys.stdout.write("started with " + str(name) + "\n")
    
    sys.stdout.write("creating table\n")
    createNewTable(name)
    
    sys.stdout.write("querying dimensions\n")
    dimensions = queryDimensions(name)
    print dimensions 

    sys.stdout.write("loading case into MySQL\n")
    header, minv = getMinValue(name, 0)
    header2, maxv = getMaxValue(name, 0)
    sys.stdout.write("minv: " + str(minv) + "\n")
    sys.stdout.write("maxv: " + str(maxv) + "\n")
    """
    for i in range(0, dimensions[3] - 1):
	adjustSciDBValues(name,i)
        sys.stdout.write("loading volume " + str(i+1) + " for case " + str(name) + "\n")
        loadVolumeMySql(name, i, dimensions[0]-1, dimensions[1]-1,dimensions[2]-1)
    """
    sys.stdout.write("finished\n")
    
