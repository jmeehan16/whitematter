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

sys.path.append('/var/www/wm/wsgi')
import render
from matrix import matrix
width = 0
heigth = 0
depth = 0

start_time = time.time()
f = open('/opt/whitematter/data/csv/000.csv', 'r')
#        s = open("/var/log/scidbdebug.txt", 'a')
        
x = 0
y = 0
z = 0
counter = 0
        
for line in f:
    if counter ==0:
        width = int(line)###MAYBE DO line.rstrip('\n') for all the line usages
        counter = 1
    elif counter ==1:
        height = int(line)
        counter = 2
    elif counter ==2:
        depth = int(line)
        counter = 3
        volume = matrix(width, height, depth)
    else:
        volume[x,y,z] = int(line)
        z = (z+1) % depth
        if z == 0:
            y = (y+1) % height
        if y==0 and z==0:
            x = (x+1) % width
                #counter+=1      
                #s.write("counter is  " + str(counter))
                #s.write("\n") 

print time.time() - start_time, "seconds"
print "DONE!"

