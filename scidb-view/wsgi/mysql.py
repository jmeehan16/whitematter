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

def queryPatients(pat_name):
    """Determine the possible pat_id given a pat_name"""
    pat_ids = queryMySQL("select pat_id, pat_name from patient_tbl where pat_name = '%s';" % pat_name)
    patients = {}
    for row in pat_ids:
        patients[row] = {'pat_id':row[0], 'pat_name':row[1]}
    return patients

def queryStudies(pat_id):
    """Determine the possible study_ids given a study_name"""
    study_ids = queryMySQL("select study_id, study_name from study_tbl as s, patientToStudy_tbl as p  where s.study_id = p.study_id and p.pat_id = %d;" % pat_id)
    studies = {}
    for row in study_ids:
        studies[row] = {'id':row[0], 'name':row[1]}
    return studies

def queryAllStudies():
    """get all tuples in study"""
    study_ids = queryMySQL("select * from study_tbl;")
    studies = {}
    for row in study_ids:
        studies[row] = {'id':row[0], 'name':row[1]}
    return studies

def queryTableName(pat_id, study_id):
    """Determine the table name given the two ids"""
    table_name = queryMySQL("select table_name from patientToStudy_tbl where pat_id = %d and study_id = %d;" % (pat_id, study_id))
    return [row[0] for row in table_name]


"""***NOTE, the variable names width and height may not mean exactly what you think (not consistent with how picture is displayed) throughout these following functions,
 	this is because the orientations were not 'consistent' in scidb so in order to keep the three views oriented correctly 
	relative to each other (eyes/neck pointed same way) the semantics of width and height are broken"""

def queryTopTile(study,vol,slicedepth):
    rows = queryMySQL("select png from %s where vol = %d and plane = 't' and slice = %d;" % (study,vol,slicedepth))
    l = [x[0] for x in rows]
    return l[0]

def queryAllTopTiles(study,vol,slicedepth):
    rows = queryMySQL("select png from %s where vol = %d and plane = 't';" % (study,vol,slicedepth))
    return rows

def queryFrontTile(study,vol,slicedepth):
    rows = queryMySQL("select png from %s where vol = %d and plane = 'f' and slice = %d;" % (study,vol,slicedepth))
    l = [x[0] for x in rows]
    return l[0]

def queryAllFrontTiles(study,vol,slicedepth):
    rows = queryMySQL("select png from %s where vol = %d and plane = 'f';" % (study,vol,slicedepth))
    return rows

def querySideTile(study,vol,slicedepth):
    rows = queryMySQL("select png from %s where vol = %d and plane = 's' and slice = %d;" % (study,vol,slicedepth))
    l = [x[0] for x in rows]
    return l[0]

def queryAllTopTiles(study,vol,slicedepth):
    rows = queryMySQL("select png from %s where vol = %d and plane = 's';" % (study,vol,slicedepth))
    return rows
   





