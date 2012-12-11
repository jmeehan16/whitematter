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


#def resetFile():
#    f = open("/var/log/benchmark","w+")
#    f.write("Benchmark started\n")
#    f.close()

def startTimer(process):
    f = open("/var/log/benchmark","a")
    f.write("starting " + str(process) + "\n")
    starttime = time.time()
    f.write("start: " + str(starttime) + "\n")
    f.close()
    return starttime

def endTimer(process, starttime):
    f = open("/var/log/benchmark","a")
    endtime = time.time()
    f.write("ending " + str(process) + "\n")
    f.write("end: " + str(endtime) + "\n")
    f.write("duration: " + str((endtime - starttime)*1000) + " ms\n\n")
    f.close()
    return endtime


