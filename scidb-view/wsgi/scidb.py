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
    f = open("/var/log/scidbpy_log.txt","w+")
    f.write(str(timeDelta))
    #f.write("lines: " + str(lines[1:11]) + "\n")
    rows = lines[1:-1]
    #rows = [line.split(",") for line in lines[1:-1]]
    #f.write("rows: " + str(rows[0:10]) + "\n")

    return header, rows 

def queryList():
    """Get a list of available arrays"""
    #f = open("/var/log/scidbpy_log.txt","w+")
    #f.write("starting queryList")

    header, rows = querySciDB("list('arrays')")
    names = [row[1].translate(None, "\"") for row in rows]

    return names

def queryDimensions(name):
    """Determine the dimensions of the specified array"""
    header, rows = querySciDB("dimensions(%s)" % name)

    if len(rows) < 2:
        return 0, 0
    else:
        return [int(row[3]) + 1 for row in rows]

def queryDimensionNames(name):
    """Determine the dimension names of the specified array"""

    header, rows = querySciDB("dimensions(%s)" % name)
    return [row[1].translate(None, "\"") for row in rows]

def queryAttributeNames(name):
    """Determine the attribute names of the specified array"""

    header, rows = querySciDB("attributes(%s)" % name)
    return [row[1].translate(None, "\"") for row in rows]

def queryImage(name):
    """Render an image of the entirety of the specified array, returning a
    string encoding a PNG image"""

    width, height = queryDimensions(name)
    header, rows = querySciDB("scan(%s)" % name)

    return renderPng(width, height, rows)

#def queryTopTile(name, width, height, x, y, z):
#    """Render an image of a tile of the specified array, returning a string
#    encoding a PNG image.  This will always return an image of the specified
#    dimensions, but the intensities may be zero for pixels that map outside the
#    array"""
#
#    wholeDims = queryDimensions(name) 
#    wholeWidth = wholeDims[0]
#    wholeHeight = wholeDims[1]
#    wholeDepth = wholeDims[2]
#    #wholeVolume = wholeDims[3]
#
#    x0 = width * x
#    y0 = height * y
#    x1 = min(wholeWidth, x0 + width)
#    y1 = min(wholeHeight, y0 + height)
#    z = min(wholeDepth, z)
#
#    rows = []
#    if x1 > x0 and y1 > y0:
#        # subarray uses inclusive ranges 
#        header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (name, x0, y0, z, 0, x1 - 1, y1 - 1,z,0))
#    return renderPng2(wholeWidth-1, wholeHeight-1, rows)


"""***NOTE, the variable names width and height may not mean exactly what you think (not consistent with how picture is displayed) throughout these following functions,
 	this is because the orientations were not 'consistent' in scidb so in order to keep the three views oriented correctly 
	relative to each other (eyes/neck pointed same way) the semantics of width and height are broken"""
def queryTopTile(brain,width1,height1,slicedepth):
    #header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (brain, 0, 0, slicedepth, 0, width - 1, height - 1,slicedepth,0))
    #return renderPngTop(width-1, height-1, rows)
    
    volume = queryEntireVolume()
    #f = open("/var/log/scidbpy_log.txt", 'w+')
    #f.write("volume of 90, 100  " + str(volume[90,100, 90])) 
    #return renderPngTop2(slicedepth, volume)
    return renderPngDummy()

def queryFrontTile(brain, height, width, slicedepth):
    header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (brain, slicedepth, 0, 0, 0, slicedepth, width - 1, height - 1, 0))#maybe swap width-1 and height-1
    return renderPngFrontSide(width-1, height-1, rows)
    #return renderPngDummy()

def querySideTile(brain, height, width, slicedepth):
    header, rows = querySciDB2("subarray(%s,%d,%d,%d,%d,%d,%d,%d,%d)" % (brain, 0, slicedepth, 0, 0, width-1, slicedepth, height - 1, 0))#maybe swap width-1 and height-1
    return renderPngFrontSide(width-1, height-1, rows)
    #return renderPngDummy()
     

def queryEntireVolume():
    # open("001.csv")
    # first line = width
    # sec line = height
    # third line = depth
    # fourth line start with loop
	# volume = {"x":"y":"z":"v"}
	# volume = dict()
    #
    #lines = [line.rstrip('\n') for line in open('000.csv')] # this should be a list of the lines without new line character

    global volume
    global width
    global heigth
    global depth

    #if len(volume.keys())==0:
    if 1 == 1:
        f = open('/opt/whitematter/data/csv/000.csv', 'r')
        s = open("/var/log/scidbpy_log.txt", 'a')
        
        x = 0
        y = 0
        z = 0
        counter = 0
        
        for line in f:
            if counter ==0:
                width = int(line)
                counter = 1
            elif counter ==1:
                height = int(line)
                counter = 2
            elif counter ==2:
                depth = int(line)
                counter = 3
            else:
                volume[x,y,z] = int(line)
                z = (z+1) % depth
                if z == 0:
                    y = (y+1) % height
                if y==0 and z==0:
                    x = (x+1) % width
                counter+=1      
                s.write("counter is  " + str(counter) + '\n') 
            
    return volume
    
	
	 



	
def renderPngFrontSide(width, height, rows):
    """Render the imaage for either the side or front view"""

    image = Image.new("RGB", (width, height))
    pix = image.load()
    i = 0
    j = 0
    #g = open("/var/log/scidbpy_log.txt","w+")
    #g.write("width: " + str(width))
    #g.write("height: " + str(height))
    #f = lambda v: int(v)
    for row in rows:
        try:
            val = int(row)
            #<bfichter> to make it white, a little contrived but...
            #g.write(str(i) + "," + str(j) + "\n")
            #g.write(str(val) + "\n")
            pix[i, (height - 1) - j] = (val,val,val) #this mirrors vertically to make tri-view consistent with itself
            j = (j+1)%height
            if j == 0:
                i = (i+1)%width
        except Exception:
            #g.write("exception\n")
            pass

    sout = StringIO.StringIO()
    image.save(sout, "PNG") 
    png = sout.getvalue()
    sout.close()

    return base64.b64encode(png)

def renderPngTop2(slicedepth, volume):
    global width
    global depth
    image = Image.new("RGB", (depth, width))
    pix = image.load()
    x = 0
    z = 0 
    for rows in range(width * depth):
        val = int(volume[x, slicedepth, z])
        pix[x, z] = (val, val, val)
        x = (x+1)%width
        if x == 0:
            z = (z+1)%depth
    
    sout = StringIO.StringIO()
    image.save(sout, "PNG") 
    png = sout.getvalue()
    sout.close()

    return base64.b64encode(png)
    

def renderPngTop(width, height, rows):
    """Render a top view slice, the height and width are not semantically correct here, see above for explanation"""

    image = Image.new("RGB", (height, width))
    pix = image.load()
    i = 0
    j = 0 
    #g = open("/var/log/scidbpy_log.txt","w+")
    #g.write("width: " + str(width))
    #g.write("height: " + str(height))
    #f = lambda v: int(v)
    for row in rows:
        try:
            val = int(row)
            #<bfichter> to make it white, a little contrived but...
            #g.write(str(i) + "," + str(j) + "\n")
            #g.write(str(val) + "\n")
            pix[j, i] = (val,val,val) 
            j = (j+1)%height 
            if j == 0: 
                i = (i+1)%width
        except Exception:
            #g.write("exception\n")
            pass

    sout = StringIO.StringIO()
    image.save(sout, "PNG") 
    png = sout.getvalue()
    sout.close()

    return base64.b64encode(png)

#renderPng is not called locally
def renderPng(width, height, rows):
    """Render an image specified by a list of pixel values"""

    image = Image.new("RGB", (width, height))
    pix = image.load()
    #f = lambda v: int(round(float(v)))
    f = lambda v: int(v)
    for row in rows:
        try:
            i, j, r, g, b = map(f, row)
            #<bfichter> to make it white, a little contrived but...
            #if b>0:
            #    r = b
            #    g = b#</bfichter>
            pix[i, j] = (b, b, b)
        except Exception:
            pass

    sout = StringIO.StringIO()
    image.save(sout, "PNG") 
    png = sout.getvalue()
    sout.close()

    return png

def removeArrays(pattern):
    import re
    
    for name in queryList():
        if re.match(pattern, name):
            querySciDB("remove(%s)" % name)

def renderPngDummy():
    return str("iVBORw0KGgoAAAANSUhEUgAAANkAAAC1CAIAAABd6s0AAAB8C0lEQVR4nO2915NdV5LdvY+73t+yQMHQNil1aEYxmtDL6L9XKKSQNA+jjgnNNAkChULZ67055nv4Ta7YVWg6EADJ/nQeGMXCrXPP2Tt3mpUrMwP3/4+r0+lEUVQqlZrNZpIk9Xq9Uqns9/vZbHZ3d3d7e/trP+D/u1z8az/Ah7263W65XE6SJAiCIAjiOG40GpVKpVwul0qlOI6Xy2WlUjk9Pc3zPMuyoiiGw+E7f12n0wnDMAiCMAydc1EUOeeKooiiKM/zPM+LosiybDQavbc3/Cu6gl/7AT7g1el04jiuVCr1ej1JklKp5JxDFpvNZrVaRSlut9vdbrfdbvf7faVSWSwWFxcXP3Dbg4ODOI6LokjTFDkLwzCKojiO+blcLvObJEnCMCyKIgxDBNE55wtllmXb7Xa73aZpmmVZEAR8IMuyyWTyURbpN3T99cgiVhjlF8cx2x+GYZIktVotjuNqtVqtVtvtdqVSCYJgu93O5/PRaIQMZVk2m83iOF6tVqPR6Pu04/HxcavVKpVKyA3q1jnHTfh2fiiVSqVSCRnNsixN0yRJEEd0J7KI5O12OwS0KAoOBiK72WxWq9V+v8+ybDwef8z1/PjXX4ON7vV6cRw758IwRC0lSYJ9dM4FQRBF0Xa75QO73S5JEufcarWaz+dhGO73+/1+75xDhvjY931Ro9GQLFYqFckWmhLRj+O4XC5Xq9UkSZAwtCPCFwRBmqb7/T5Jkv1+z5/wAe623+952jRNt9vtarVCc7darc1mw02KovjrU5y/b1nsdrvSRlhhRAFBLJVKaZo659hsfQylmKYpn8zzHMUTBAHCEUVRt9t9e78R61KpVKvVkD/nXK1WK4oCXctJqFarOKNIWJqm/BM/FEWBPyAPtVQqFUXBMXDOFUWxXq8lu0ikhHK73S6Xy81mw5P/NQnl71gWu90u5jhJkkqlgglGHEulEjrSObfb7ZbLJaoRi1mpVLIsQxDRiM45hCNN081mg3HP8/zBN0pY2+12p9Nxzm02Gx6gVqvleZ4kSavVKpfLBOmoZ0QKIZb8IU/S0wjrarXa7XYcJCna/X6/2Wz4r3NOhns2m00mk9Vq1ev1iqL4K7Dgv2NZlC4kEKlUKrVarVqtorQqlYpzDhU4HA7X63WSJIoq8OEQRBTVbreTBtrv92gpBM5XPAhxs9nkS51z6/U6juN6vS73oFQqVSqV+XyOg1ir1XAroyjabDY4kUVRNBqNcrmcpmmz2eTYzOfz/X5fKpV2u10QBIggAoryXq1WWZZVq9Vut3t6ekrsNRqNEOg0TX/XEfrvUhYxzdjKer3O/8Zx3Ov1KpVKq9UidEiSZLVaBUHQarUQPrZ5v9/X6/XNZoPrNhwOZ7OZbxaxmEiMc67X6/FzHMfYUz7TbrdrtdpqtYqiCDTHOacIWm5rrVbLsmy5XDqLdYIgqFar/BP+IiL76NGjUqmEt4ClzvOcc7Lb7abT6WQy2Ww24/GYX/Z6vXq9fnBwMB6Pp9PpcrnEB/2dSuTvUhYJDur1ervdbrfb9XqdjW+1WlEUNZtNJA8QsVQqNRqNxWIh9TYej/v9fqPRiON4t9sNh0NMJ/+VZ4mVR/tiN8MwrNVqeJ+ot1qtdnBwkGVZpVKReQ2CoNFopGmapmm9Xq9Wq3meR1FULpf3+z0KuFqt4j7udruiKMrlMi8lVCjPc14KV2Gz2SyXy9VqtdlsZrPZfD6fTCbj8bgoCryCZrO5WCzm8/lisQiC4JegpL/W9TuTRXzEcrncaDS63S6CWKvVUF1sbRzH7XYb52y73eIdNpvNfr+PBXzx4sVqtTo8PMTJwyCWy+XNZoNkIIKEJqVSqVqtKk5PkoTwiDAZe52m6Xq9Jp6YzWaI2t3dXZIkvV6v2+32er1Op8OToFbxBIqiwD1FEe73+/V6HQTBYrEolUr1ep23cM5VKpWDgwOecDabLRYL/MWbm5vlcrlYLFgWvBQebLfb/b6cyN+TLHY6nSRJwAgRRDaYSGW73eKokU3ZbrfoFWDkLMvQMY1G49NPP53NZpVKBUF8/PhxuVyeTCbEB4vFgu2vVqsEv/hqyHqWZavVCh8OeSJ84Yftdvvy5Usw881mw7enaVoulw8ODoqiyPMcK1+tVrmb/FSkmbdwzuEjcpNms4mhz/OcY9DpdFCxk8lkvV7f3t7e3t6+efNmsVgoqzSfz3mw30ug/buRxX6/Twav1Wq1Wq1Op3NwcHB4eIg5QzFwrVYrnDNcRiJf51wcx2ma3t3doYRWqxVRRaVS6ff7RL5YQGIXZBeZw7kEqXHOjUajer0ukKhWq+33+ziOZ7PZcrnE1DabzeFw2O12q9XqeDxGWYZh2Ov1sO+4BDgD6Etugp4molqv1xwzwmosPqeiUqlwt/V63Ww2O51Ot9t9/fr1YDCIoqhareJfLhaLXq/3u/AgfweySEKlWq02Go1ms9lut3u93vHxcb/f73Q66BUiEufcYrHYbrfVapU8CsFypVIhmEAX8nlQlUqlkqYpLlqaplEUtVotUEmEA7HgPtvtFuWEfuKpSBsSkXAkCDVOTk7CMHz9+jVW/uLiotVq9ft9xBSsR/HQdrsNw7BarZ6dnaVpil9IHF2tVkkR8ftGoyFXlaAH6L5cLvd6vcPDw8vLy9evX9/d3YFzjUaj8Xj8uxDH37osYpfr9TqC2Gq1jo6Ozs7Onj59yiYtl0ukajKZYECdc6AtAH6IaZIks9mMAJktlP0Fvlmv14vFAlMex3EQBMgc0QwXyDMmW0lFQux2u002BZgQQ4wyu7297fV6zjnUm6B1UG60L7mfPM9HoxHat9VqiWBBugW/cDqdQjJaLBZEb7xsqVRaLpeY716v9/Lly9evX0dRhEQOBgMOyW/ZXv+mZbHT6eCPE6N0Op3Dw8NPP/308ePHQRDMZrPxeDybzQgbh8OhEs3kcxEgLBoYDUoOMQJnVhYYrTmZTIBXoigijtEHnHMoSHDp5XJ5c3ODVkOVbjab9Xo9n895eHYdFyKKol6vR0oGN5EYCLzTOdftdp1zm80mTdPZbJbnOfgonmW1WhXBgjiJ11wsFkRIGA0iNi7E9Pz8/Pb2Fo07mUyGw2Ecx4PB4Nfa0B++fqOyCMUmSRLUYb1eb7VaZ2dnZ2dnh4eHRVFcXV0Nh0Mw3u12iznG/eIO+GGoQGQR6YR8gInc7XbO0r7k/VCWAITIH2Qcxb8AMcg0kM3h4WGn01mtVuv1WiA5OUZcBX5DhIvWJJrhzs45EiogPuVyOcuyxWJxc3MD5FmpVBqNhnMO5KjT6eDF8ki+O4v1qNVqoOic4dvb22+//ZY3qtVqw+GQXM5vMMT+Lcpit9slrQd202q1ut3u2dnZkydPCJzBdcvl8tHR0Xg8Ho1GMqn4TxhHbB/3RJeIX4NdI8wkgEX0W60WbiLqE8lzxpaIoggb7Zzjv6vVarFYIFVYUmnffr+P4d7tdpvN5vz8HCWH/JFrwUxzf4Kn9Xo9m81wFsvlcrvdJjKTHQenRA2D4/B2o9Hou+++A70CQup0Ok+fPu12u7Va7eLi4vz8HOMQx/F0Ov0NepC/LVkEPkzsIqnQ7/efPHny/PlzQhC2/+joKEmS6+vr6+vr2Wy2Wq2AlEej0Xq9JqBxJjHIJZ4iObpGo1GtVk9OTlqtFvgLAA2OIJesPEYZK4lSwWoTNCArfHsQBJAqnHONRuPk5ASg8e7u7ubmpiiK4+NjfMrdbgfktFqteEjCo8ViQSQUx/F8Pr++viauIlJJkgSSG8qvXq9zPKrV6nK5DMNws9nc3d3NZrNGowG02Ww2nz17BoPz4uJCVJL5fP5bg8R/Q7J4dHREhMhVq9U6nc7p6emnn3769OnTer2Oi3Z3dwe+/ebNm5cvX97e3hLVDofD6XQqqSI6BnrEUGLElY9uNBrL5RKEpVqtlstlMBRCWiwgeovMIW4fahJpc84h2dK+gETr9TpN0+Vyud/ve70eoGYYhvV6/fHjx+v1GluPtzeZTMhAkijCo8DT4ESJkY7LUalUer3e2dkZSSae4ejoqNfrLRYL8IHZbDabzV69ejUYDE5OTtrt9tnZGdmB169fX15ekrsH0t9ut7+RgOY3IYsHBwckwZBCYovDw8OzszMEEafw7u7u4uICU/v69evz8/ObmxugbBISuvD5cOEJdaMoWi6Xw+HQJzIuFgtYDngCwOZoR/w/qDTKkQDo4CkSSRBMKN+I94Y0bLfb6XTa7/dxQ9HxSOrFxcXt7e1wOFwsFsgxATvRDPoS4cNPmM/ny+USnBy0cjKZXF9fP3r06PHjx+QACY9gAJEe5GMXFxfL5RIA8osvvuj1erVa7bvvvnPORVE0HA5/I4LofguyCM6spacA4PHjx/1+/9GjR1Si3N7ertfru7s7knij0eji4oKYl5sgcCKrEp8St5ITwwsEf8Fk48kRjZLMlYIUExsvbb1eQztAChFB7o/tQ2uCuYDsoJhBkfjber1O7u76+vrm5gbSBp4lzi4hFDiicPXULvwEME4A+dFodHt7m6bpF198gRsKVBTH8cHBQafTefz4MWZkPB4vl8v5fN7tdjudzldffVWr1TApZBAw7r+6UP6asqjCKDQiAWOv1zs6Ojo8PIT3QOJ1PB6jqCqVynq9vrq6gpEl5G8+n7NDUPkJCAhIUZkIx3a7FUDjnGObFTFQCkM0KtbZcrnELhOgKHbh2MRxjFnHi1VmWY4m34uU5HlOrE2AzPOjxZFFAmSeUHUIPCphB14HoDd45J/+9KfBYPDJJ58kSZJlWa/Xe/ToEYFRnucHBwdg3dPpdD6fX11ddbvdw8ND1OSf//znV69ecRLG43Gn0/l1xfHXkcVOp4MfJi4MOT1iz36/j76Zz+cYO/BCsl6Xl5foMLLPOF6TyWQ0GqVpijoR1WC5XMq2OuewsNJG/Bcji8QghWEYQrTBOjvn8CCFUauuhUwMjiYIkXMOb08WHIiRgwEUT/ChLyW/4pzDS+Yg4atwDOQb8Azr9do5h8hyAm9ubsgA9Xq9zWbz6NEjLEMcx5zq1Wp1c3NzfX2Nl1Kv13u93pdfflkul7/55hsQImKmXxHr+RVkEZYhK65M/8nJycHBAZmVer1OcDqfz7Fl6M7tdvvmzZv5fF4qlfCQSLRMJhPcKTZPiCAqR1rQOScev3NOtH4B2sKA2GaMOHKA8sAWo6J4AKhAgtZ1Z7wF8j3g4bvdDiZsp9NptVp4k+T68D717twfSMsZIZLH4wkB1UElKTyYTCZkLweDwdXV1enp6dnZ2cHBAWw67oxoDgaD6XQ6Go3IJT558gQolEUejUa/onb8qLIIgo2b75wrlUrdbrfb7WKUqaKvVCr4cBjlNE1Rh7vd7vb2drVaqYQA9gB+PXAg34IUSpfwS/QifyVCa2GX80pFcfLQZNTE8INwIk4CcUYcx/iIIJqEOJhmVbSIpI004DMo3ifN02w2Dw4ORKmU64IciwqOxEtDE34tFguojcRwk8kELtmTJ09AZCHRHRwcwL8cj8fX19c8QKVSOTs7S5Lk1atXwOxvV1Z8tOvjyWK/38ff57iTy3/69Cl6otfrJUkixii2TGE1GnG5XIriiu7Bhd9ut8iWtBFC4JxDjQVeWRMi6P/sK0toWvwrnpmSe5Iz3gLVzreIL6jgCVlB4aGbIYMhu3yS1BzB/vHxMZEQYURo9YRka8rlssB8GI14LNx2NptNp9PBYICyREaXy+X19fXLly+fPXv2/PnzZ8+e4fyUy+VOp9Pv91+9enVzczMej1ut1vPnz4ui+Pbbb1utFg7urwKDfyRZBMZjM6IoYl2Ojo6Oj4+JFZIkWSwWKELMFmxqqANv3rwZj8eYRaLLPM/n8znlAWIh5EbPVgzhnJPA6Tf6pXQAOx1YqTw2l9gc6UR6sJ7ObD3/JPnA70RkFYPX63XiGwm3LLhiEbLtIPCKlwuj8GAE/NcBrqLCAes/GAzG4/FisRiNRldXV0CbJM2Hw+HFxcXr16+/+uqr09PTWq222+2Uf7q8vFytVojjfr//9ttvcyMXf3wY/GPI4uHhoQSRzMTjx48hfZE/xbiwTwC/sFBhEoA+sO6kOmAGjMfj+XwusfP1n7w31aw4T/7eFko9qiQS201sRLyiX4q/gzvITfhf1CHKEt0GfE2sHRgrkc1GFvledLkKJwjIdrvdaDTyUz6yobVazTnX6XSOj48PDg7AAVCQL168+D//5/9cXV2BelKf9c033/yv//W//vjHP/6n//Sfer1eEATVahV4HNtSr9cfPXq02Wyurq6oswGl/5i+44eVRWWW5focHh6SJAVhhlCY2QVCiwhSqfnixYvLy0sFK7h0FCJNp1NOv+JNUBLn3APp4WH08wNN6dto5+VUCHL1S9/XxHbDsQA9IZrmKxA1sYR81zNJEqJgoh9MLba+KIrFYuGcK5fL+Kap1SX6x0M+62Qy4WNwgQ8ODjgJf/zjH7/88sv/9t/+25/+9CcgLR7+9evX33333YsXL/7zf/7PX3/9db1eh/oUhiGLSQUZ6BgoWFEUHzOU+YCyCG8UEwMa9+TJExxEVY6iAne73Xq9JlipVqv1ep3le/PmDYKIpXPOoaXm8zm1cIKEFI7gnynvJ4l0VoP3QBydOY4P/gnNCjz+4PMYX9CcIAiod8GIO+f0391uR9RF8pA+KvyTnlZ0L9TnZrMZjUYcQmx0aJU3WZbBCNED393dDYfDb7755s9//vNXX3317NmzZrPJt3/22WelUung4OCbb7757rvvbm9vd7sdKOxsNru6ujo/P/+P//E/9vt9cvrg50htvV5frVbtdluNfj6chDy4PpQs9vt9nBLC3na7fXJy8uzZM6JF5xxOOr4US4xRJoEB3HV5eems7kRmcbPZkD1z5jyhnPAsMbLoMBEjeCT0isJn53XDcffl1ZnwsbV8hWQIFaiUXb1eRxZ1EwJqxIhTAa1BroiUd6VSEZtLKRZgdnQqeqswEhCIOtzhoiiurq6q1ep33313fX39+eefHx8fJ0kymUwGg8Fyudztdv1+n0UjWYrE/+u//utgMDg/P//bv/3bTz755Pj4GEwHfhAnf7vdtlqt8Xgsy/ARrg8ii91uV/0bqE3p9XonJyf4iBgaEEHWl6oUioxub2/J51K30Wg0IuuMA42Uikwyzs6DDAXKCJDzHUHnHAIt/SfX0P0l3NF3QxW565eKWvARC48i6Rt9Yg4kzDkHBwxEUFE/dX3YB+fJMRbcOQdjCJhwPB5zEpBpukdACnn58iWmhpMTGHc4SZKTk5M0TQeDQZqm3W6XR/rHf/zH169ff/nll1999RV+Z7lcxlNUCK/KjY9zvX9ZJKcCiE2Fx8HBwaNHj/r9PpEpbBpEMAgC6PjOyKT0/ppMJkAe8gVRn+v1Gj9Jxgvoka9G/iQ6/NKXM8UK0p2Bx7t5APc4i6+LomBfiY59Y4045l7ZAB/mpTgtuJXNZpP712o1QpnCWGfYd3QtxsE5h4KkmhFiGDChoET9Ie7dYrE4OTmhPFIRG6qd/D5Wfj6fn5yc1Gq1xWIxHo//63/9r//0T/90enp6enp6eHj46NGj0WhErcJqtUJtfzSX8T3Lot/RAUYn6vDx48cgGqPR6O7uzpmHLiTZOReGITw/0RR0xOGezOdzMr/OORAftAjSwAPg5ylKldA46waGOKKblZV5oEG5fPONYBXWqInfC2oRmigsurA8IZqJopMwDBEjAUCo2MPDQ5A/6hNQsahbub/cGbhRPkkQBMRJWkMWOTcGu/7b6XQQ/fF4fHt7+9VXXz158gQAaDAY3N3dvXz58pNPPvn888+BPNlBKr8+msv4PmVRhQFoROwyB67RaBCg3Nzc7Ha7drvNVu12u/l8js80HA7Pz88JX8g0BFaPTF0L6KPz1BUKqbDGcwhobM0XhYCE1v6B/6JK0c2Cnf0kjTNBDCwdTCTxwJvED9F5QNWF1r2OCimUN3gCJQSkOglEgAadc6Rwms0m6GYQBGCcsrbyKFqtFs40rzafz+nCg3acTqf4taSnCRydc3met9ttjNXt7e3FxcXx8fHTp08hSVBY/e2332ZZ9sknnxweHuIzaNHeo5D8wPU+v4YsKrUpML7IMkPc32w2Nzc3o9GIsIbSEHFbrq+vv/vuOxDm2Bq8UspE4T26B1+KCFcSiTUnGkUWnXP7/V4ANcqJxBrqhM0DYIea4MfRgVdXICFIrWOdcw7RJIeUe1V8CsCVIYQoLjwhiqInT55gAa+urq6vr6fT6W63u7u7y7Ls+Pi40+lMp1NpYuxGbn3PiqJgfajVkhcIQH17e4tDCUWNhJb6ouAe4L5Dkjg8PMRHbzQaZBNevXqVJMmzZ8/6/f56vYYgstvtDg8PsWYf9HqfsqgXEwYLfIOvfXV19fLlSxyp9XqNSYIiNZ1OLy4uqGuOrLXwer2GeAfLEHeKL8JsITQ49e12m+SNs46gmTV7xSDureumH93LWZQZkqOpshVnfqHzHEqwUh/yRLk6cxJia74ItRbqA1FtEATUkWEuLi8v1+s1VF+Q7UqlAjsJxeb7Ici3TwEBrXTO4XGSyME0kctx5jXyPJQcfPvtt5Txs0HlcrnVap2fn5+fn7969QrvlhxEp9PBAfgI9THvTRZZ2Var1Wg0Tk9PHz9+TNUP3t7V1dXFxQVGZ7FYnJ6eFkVBIyJAtSzLWBSs83q9nk6nZAXJkPrSQOTBklGZReWH84IS5xxAOgoysjbuOFjsqOAYPuPuk3ecccx0cZPI2ojF1sGxuI9fon0F7xMIO+dgvJK0pFMeddPj8ZgvgnV7enraaDRgCuPGFFaCSGGhgAUUHq6nsyCpVCpR6QL/UqkEtGye58CK/+N//I/Ly0tIZfgS8H1AMErWaIUao9xKfz5oPev7kUXyKL1er1qtHhwcPH78+ODggChstVqdn5/DfiX3D2Z2e3tLzRRAPyJYsoZMUKBRqEINJW34Q0ghtQH8k7hPvqeI6NBXKTfKKpoV/SG2rARRQszbBfcTM8T+cLoofuD3gjb5UgUxSC32NEmS6XQK35HzA82CZyO2RcSl/OgiLu9CqKezhDjnJLdGprIPUtWy0VKQ+DPT6XQ4HEKPAr5Ay4Kv8Wq80fHxMY+EyH4gjuN7kEVwBA4ixaOQYfERyTvRgwtHp9FoDIdD4mWkzZnQqEIUzphoWr4fRogH6xuSlSLc0BrREiP7JpXsjrjZ3JY4HVPrTMrjOKasab1eC3wJPW6is6Z7iTemANgFpagIhooqHAm4ifzGObff7+m155wD6ybzsV6vUUuBpYxRpXmew5wIbGAHaxJZKz0ej+8SeoBjzZvyXcDdNLSlERnB+O3tLb0l2u02hJU4jlerFd/SbrcxBRirMAw/BHPil8qiGF/VahUci15yWJybm5tXr15Np1PnXL/fPz097XQ68JBRioWR6Vk+ip7AESU6cuDkkjOLAH0TWvN3LT1uIk6bwmpFD878P6lb8cD1TzgMoXXblh4qDNP2lR8XnhnC4R8PnDYaWgjWAZkql8sUsHJs8jznzKCNSqUSzjdftFqtYuua7D9Ju90+PDyEgUssj6vDU6VWKMORII7ebDbffvvtzc0N542gJI7jR48ewZ/qdrv9fj/PcwSUdHmz2XR2CNGL710cf5EsdjodQrN6vY4gnp6eiu4wnU4vLy9ns9lut2s2m0+fPj09PR2NRtfX1zTBgTQqyJrfqPrdRw0Ta3XX6/Vo9ekM2RGDQcGKcw4HCFnhw4p/2SRpDuk5ReVpmqI2cLPkLEoI+C4czdjrTuGsMECcczQK/QW22+3V1VWe5zgqAn0QTcRoZ50geRKAfZ1VOa+SMG7y6NEjDhWMG/l28nE5YGVran97e/vdd9/N5/NqtUrtea1Wo6kpQTobip6+uLiA8KazhDc1GAw4+e8RBv9Fsgjljs7VANqcYwTxm2++ubu7gyLw+PHjx48f53k+nU6hQRD0oe1KpRLpLHKDaucVGPuGRsjEKOqoKcQ48FLM3E12SrY1tzoBaRcsdWb9cUJrFl8Ydi3/jzvoKxB6dXLPvVKsPM/59mq1Knp2Yc3sIMI580dDq3cGKPB542h3Ks6SJFkulygngaaKk0BqCiuT4JBA3sm8JhYK3Waz2b/8y78Mh8MkSc7OzmBIFEWB7yTKPcJH4MUJwQsPw5CzlGXZaDTiD9+X+/jusohTiGqk6xKDT8hHnZ+fv3jxAnS31Wo9efIkiqKrq6u7uzsyUWEYAscUVkAk5r34f7hfQGJE5aDZsqRKMGAcscKCoEOrxJNuC6x1BGY9tBrn2MYNydXLvUSOpNBZCocqbITJeT2fKIFViE32CLaLQvvIGwLinCOxntt8AzS0LD7hCAGKcw7KN4IlYMF55dVAuSVvSEee54kVTMo6l0qls7Ozv/mbv3n69ClKAf1N+jHLMjQCX6eqHeQyDEOSauKrvy+45x1lkQ5gtNFAFpvNJgmo+XxORwfeJAxDQt3b29urqyvqM3LjjVJXgGlGEJEMJABXutfrwXwOjWrA6S9s/pkzdRhZh/fA61gn+oIeXkoCK6yI293P++nz+rkwmg8VhhwA/AEeGOFD1jlIiAUHDG3Ns0VRhNcIyCpSoxItOlS8XWGdlSPrOJ9btlPZQuccjmlhiKkfR6u9Sa/Xe/78+RdffEEfGHj18J0zq6QJrI8Zmh4/PveoJ8DgRVHAIn0v2vEdZREHjgCCuh56Xy+Xy8FgcH19DaeLSLDRaFxfX7MQBCUQOaMognHD73EQFcfEcdxoNEjbCOWSXXbetCliydgqQRUpI4VBEMgQFzZYKrQG8ahD9xZVp/AqY5yXjFGIo355mC18KdVMka5cr9cQsPfWmns6nQZ2+RbAf+vYanrQrDwA+T0OwGazUemqfFnfO5RNQLghpNGj4smTJ19//fUXX3xB9J0kCRtUrVb3Nr8jsHEe0DdJSdPKTGxl3ErnHHdWePdLrneRRfpgoADAcXATQciY9kgoenZ2FkURiSl8xMVigfi2Wi3kFRBHyomDHgQBPmKr1eKL2C00mTMKN/LnlyYhiMDjCj6cYeCKfMUsRGp9J1KvKekMvBy0/hXtuFgsEAJ6cuIkCDbP85yqbUrrSTyi7YRVoUqdN1EwtI4/LKkCNWdzkwACqXdRHOZjPaHNWwDPr1QqdF789NNPv/76688++4yMQxiGtHBBgrk5t8JrEqQVG6sXkyJ3AnCNpf7llvpnyyJRIV4RlZRITFEUy+WSnlpob/wPzX8kWiyVSp1Op9FoiDYstpWz0JizqGDFt7nOOBDSHFJXXNhc9IHim8JL3OlPtKbafn7IrVZGusp5WengPhUXmkJq7VBQ4eyisygHfEBRP9XfMnbO5hfJNCvS13fx4lEUgdpCekWAcF0ePFhRFPV6/csvv0TLjkajV69eVSqVzz///OnTpxCdwH0oJqQrOOAGVZpM5xTkWRgRROQgpRUATf0M7TtfP1sWAWZJlZL0FGgCoQZpAFu+u7vDKPvmDBY7VsAXwcz6bQK8UWoeGHc1t6Z1OqDsllgkxJ7cUx4hEIkgRsF+cgZimyOp4i90JC5gfr9Q0Hnm23n4DhRUfIxGoyFYKrJifhEu5clFRmkT8BR7FQW+h6p6Li0sgXMYhjg2FOTzV3ItENNKpTIajV6/fr1arYAPb29vsyx7/Pgx7R45LbjpWCdEczAYkA9kWZxVh+GH8F4sJqkHfJJ+v/9LQMefJ4u0fOAicNEMC2SR/hhBEPAzbju+vLMuEeQzOEbsDTpScW6n0zk6OoJAVXhNHXh5vCgleVmm1C5+I73i607BOvn9fiaw6gmh9FeBkQ98zeS8IiznxbByH/M8xxxrC9k21C33J7/sLLAIrb8jB0wOWWhIO1dudF1nBDMcdLrcArg4C73zPJ/NZtfX1/V6/fLycj6fNxqN4+Pj2WzmnHv06FGr1cL/VhpTDGWwJJx7mnbIgnOYdYScjWmHr6Q9/RiyCAmP/CmOApQkngNKtnOO5hhy3ThJUFFYMlW3kPjiXGZWWdJoNKhVFeCCFIZWxESVYO7xF/fW8ia2rnm+L6+ffYcPF4edE/ECDmluc6b0SM5DxYP7uWmuwGiOePFSonJhnZfGZF9DD4QPjPChY+Or4cAYa7khiFjGVqtFkDufz/0MNZ3r0RG0NNlut0+fPkVBqHFjEAT4lEDrb968GY1GrVZrtVpdX1/T2M1ZbyAMzt4avBCt693FBfmFBQk/QxZDo+WhFNGLsQ2H2u/3s9msVCr1+32ho7SLLSxhhdj5/o2kgd8Qd4t5KvxZgqiGdLkVpyq7hcCB20n4dGmrnHORV0iFHoLA7DxO9d6q5eXnSY/6eyBOFxAMpAcdxQfuphSeIOjcMEJMc+RV8BRWdiPsJrQWFFEUwYcql8s4AJk1Ko9tBA493ABlFosFNrfVapHLyfOcLuhEn6kVNhBHEhspXtRxzY2KgUdbeAPCxKX4SLKIccS7orQZCeC5cdghitIXUEk8VD0QV2S1ICAFDOdJreMgi0jOQFsivx6DosQDNgtF6IzU6Ns4ZxZQop957H+wNOIPuQo8MyvOPiGpqfXLC6ylHX4CyU80IjuRGeHXWWwbeBAg/mu9XneeqhMFxr1VxC1Rdl5JQ1EU5XK53+8zVU7kcOdcu90urEEF5ZSp9WEjN7bf76lrQY4T6zXAntJDZmvtUpF+uUC5dYYR2CR1Tg4i/J4Z8O9ZFtWWqWrj5pxzpFXQT6AGrVaLvr94isgf/rW2kKWMoojmmSh2ZJEsjrZEXiYbpvyEs4wwu4iCYTl8H1FCJs6ONtV3epwReZxzPC2fxwKgG1A/zmvQwyPhUURRdHNzQ0duZ2QtVka5HMXIaFPyMSJS8E+yws4z0/q6vdW58pyU6G82m1arxRiHxJrmsx0wxtGIYLq6CY5+aJl0cGxwhsxGGWOIcks76RinRkz2Jc9HJz64LAZG09e4Oaias9kMkMI512w25/M5OWjwGnwR/nZrk+4Co+SoF5GzRv4UtGcef1vs68hjKBbGD4g8VqmMhbNyer8+kB/8YEjRj9w1dGpu+WWuwOaXSybkAMTWWwxVzUamHjMyte5k6CqUlqRNmSSxSaRHnWlNZ+0rhEwFXlUkr7+1EUZSpVdXV7AeKXglnNKKYdzQC7Vabblc0ovHWWTGi+fe5Tw9zTsK02VhffTxna+fYaPl1gA1UWRJ3fhsNsOiTSYTbJkOChQB1CGxGJsK+i24J7BMfGFlyP7e8N/cplAhZLh9UgYIIqIjwk5oyWVJYe4lZgIb+qL4lNRWnudklYSBy+lUJBR6hQQoUYQPoWGtUKt7a0nKn/PWgN58i57B30vF0RzswPg7SnbTtwlECeknwqBmcmPXzvre4n4I1uUh0YgYa/XoQUfghhL1R17ljbvPnXPfE899WFmMjQ6oArMwDMFoJpNJrVabz+fT6ZTfoDUhs4CHFR6DAXXCQsiqJl7JmSQyMiaBL0aSdSVwUWnYF2Jk9lJKSyfYeVYvMIaOchu+xeds4DvyXX62kHtyq5J1yBWXjEPS6XTq9Tooibq0k0yTk6A7ADLLJQXA0lkKrPyUxSfjwA2ZCYL0EKngxOP/COcqigIPkpgS2gCjh+Dj0QQBS1WyHvpSirLIgrR0LIu3CCXvdv1UWfQRE8WqnDlmw+Z5DtCNnwTWw2ljHEZhBfmJTbJFqhRkxPeJhqg6PzRJjbn9ID+h7IWP0RCXBF5+LDLivr+szivqI3YJrB5U6ysQXt/I/5KTEFdS4iutw2+Q1FKpdH19rVFWpJScc4Te/ud5Bv/tkHtQMO4PUkj6Lo5jGCcEWGmaUi2EgdKShsYj5slxMdmO/X5PMSsmhTyKzLrAB8Vtcn/zt2h1H0kWIyv31IEmfgRKxeFttVrQc4gWcRBTqx7HhqLeHnBnuD/ZBQmc1IacPK1pcB8i2dn8FQmlPiA/JvbqfLWOvgSLS+ELATf0nVpRzvI8pz1pYblsGXRMJ2cVF4Vf0temVqtBsUvTdDQaMfZHcFVgGfnAmq1hK8MwBKOmJ3RqLSoZR5dZub54yrJFWkOkELFbLBYinVAik1s/tL21EM+9GnMZB2kl+dbB/VzlB5dFBe0oALAVIR21Wm0wGMCJH4/HYvGwJfgo/KG2NvPa0rm3rEBuOWVOoYyjnDbEi3VBMpRhkyAGXoa3MLRPDqjei4d5YHlzq73SfpRsfClDihA1UNU8zyGtBMY5BfkHTJY7Re40yzKYJcCQlUoFnxs1SVShvB+PrbAXQhDaK01TiOIIN3xbXD1FhLmXt5QDiu1mX2q1WrlcVpSpfjLODJEiLTkzSg5pJWW7PoYsMjgXAxdb2RHbRqUzflWj0SC+w5Tsdjvm6OJCqZ5Ssui8I4WmRH0qvxR7NLC3zY0zYp9iTHHvfDviLDz0k4GSMwmKAsOdDeBAwadpSuoytsEfAFJJktDyCzwSvojzUotFUUyn0zzPO51OYG1GApvIJ3iBQ4u3p3YDjUajKAp8ADl5qANyB3gRvAViSkWbHD4tl29YAm84CK9J/ZqzpmdaOm6u7BRLHRig4bsQzqsf+oUVqz9JFrG5CqIREZ5mvV4fHR0VhkiPRiPWNAxDmpjTlkXBROxxDvyAoLgP/uWW9yveuvx8IB595tXJ/9tbefgCp7Yw5mzq1XMprOGQcLRw4BRC+j4fJ1DCRPId4eNnzltqDSAxwdRDxca35dTJ0SRwCcMQrjgyzVdT6UsDu9QocDReC8NQFokiAZJ41GnIn+EqPKZFamMSoygiLJPaY1JxYBeLE3u8Zue5anJgJN/pL26785NkMTI6nUpJ5GPxS5w/muMA7mC8ONB768Qla5t55Sx6+dCQLd5ZmbTcypklBzqXqTU+dB6RxFmIF3p0fJ3v2No7IcG+ChG/S7GzXr9kV2q8Q/6JQK0w0jWuYeZ1q8I4YA0Dg98pAA/DELFDwZDz2Gw2NGojqq3Vak+ePMnznL45jFVT45RSqUTrrDdv3lxfX2OF8rdS54WXi9c/sarO0AOKlgiMQmtqTxiwt14J7F3sEZD5YW/tYj64LLI0iqAVCG+32/l8jqxoCxk955yjmbYkLE3T1WrVaDRyq9zzsQZZ3tDjNARej7nC8Bf/RDrjS0cepUCPHXpdxRQ2OQ+z1Z7pW+jdg44kqRPahdCHHtCYWeKHgIbwE5uLtmafUD/sVmi1ofiadCkh8FJlCfW7URSJAhcEARKZZdnl5SW1pByMR48ePX/+nKapNM1SDFHY7PPA43e6+13/Co9cIrUiNiDeJ607iqKga3Bxv5FfZBQeHfUPK4usNRiNmiXw3ZgJ9inPc3HGlNbEZvGvsfVK1Ikk7JBk6H38U6ucR2apZz5JyKkoWDGy/EIBT3JJ91aE5TxSmaAKgkef66UPB8ZRCIJAVYgyZIElZKlfga9fWGSNtmCh5MtKzhJrelYUBaX42+325uZGOj6O4+l0WqlUHj16RA9BikThGkNJvLi4uLm5wY6/LRDFD+IsvKP+kDY6kICSJAEwpiKHzz8QO73j3isgfufrx2VRBhraIr9kJ4hepcwyyxxQRYVAIJcg5M6Yp2DgWOTCyNipkUGQs8KgrPw+3Kqghx+EpBSWs9blLEzJjMcVGh4kF1M2OjcOYuQNmRJ0led52aaaITFEtamVKidW1EeURro5sJpavRqxKioTeCE3egT8Em6oBDHHPkmS5XJ5dna22WyoEFLNHomW6XSaemxL2QcZAd9e+7/XuwNMVqvV09PTdrvNQ0LFGg6Hw+EQFQ6FgI0WUOUnuj6gLKqlItZZJZVSXWVruo81AanC4sCTYxukpXIj/Qde5gN7R9ioMoDCCH8YLOcNyAitvaJ/6HVmiDez+xWAwf3RLIWXv4m8FI5S0vv9PrLpMop5I6tb5ZWpt4LVEhinC69R2cjCgHSMspyK0Jp8SrmKuBrHMfdkg/lGvKAoikDHWGpMEP5oZiw4P5B3b41UQljlT/vOLppFpH3yFIT5/DnmSDR1BdEfSS8GVizn75kWPcuyUqmEXeNput2uNgCIB/l4IH/OYgi5L8Sw6/Uad1Orllt5b2CMChlH53W3eYDB7m3OAPJU2HhAqQHnFRCh6tSQXZpYNAvuI13F2WD/Kja1T8FclmU4W2oEmlhlIICLtKPse2bNSHlsLmA/XBSSW0VR+OQS7ow/J0a6LxC+RtTK+yozMAAcxca4se12SzoHHaES2ziO6aPCNzor03EeEvnBZZEjHnqQJqpOjR+E1AP9qMZZq5DdZw0WXj5Nbh+yohp4gVjOiOzOcB8fdMyNZ+rMU0QQ2XL9797Y+ZGXyEGy9zamihxaaP0keLzMyzqIv0goFtlkTLQgssW2bbdbmk6FXmoAFQuDobDUolpeIZT7/R6+TGolaXuvSelms4GBAc6ClUBLqcLh7e17+2dJrW/fgJkk2Qg6YKf4ZhQqqe3H3kYtyQP5sLIY3ifuir5AUwGlv3gBUHviADgBucfB8Y0gEpB7IHZgzB0Y88KTC68KTj8XXppYwXJkdVWilmBMC+ttgnhFXp4QASKNCaUtNBKh3AD5mkEQoDi5g0LgNE0humOLeQbkhn0ScekBRIKH6pxTplRgkCxpZg19nClybjUajVTvInDbdwF1yYP0lWJxvz1QnuebzYaSMWY94Q5GRpKlkp9mzCCgxHlKpH0MWZR15sn0GhIFTPNut0uSBEKeth/DURSFiqn1V4qaUZAyuzTD5DMlry2YXBPn5bWkXJ2xJXR/uYOBxzoLvZopBb+5VRXhIQknK6w3jbNoyZlTKIwwsroq9IosvnOOdBRYrJxI/olQJrMRbpk3EymyjlCF10lWWCzfhVM0Go2iKKJv73A49I+0L4LOE019i1aAn/kizg8TBbvdbqfTSY2uRv0xtafT6XQymQRek0vf0fqF1w/JIqk/bbYzrwh94Mzng6rJdqZpqlElgRWMKguCQUf576wzXeHxJPbWRlv6X5FvZHWQkZGpIoMVI2N3Iz1ao8Taf7FegYE7coIR2dj4zKJdBcZelkEPDaUPPa6Xz4gTNRPK3H6/V2UFfwtHkBvimYDLMPdPXoTglcKo1L5s8VQYDTkJhReFFF7UIoHzhdK/oT7AnpLSXK/Xt7e3RVEcHh465yCYoWJGoxHjTpwNgAo9jlX0y4i0PyKLGB3FLmT/sLAU9eDk0uvcWcejLMsAOyKrX5Qc4NxEUVQul/GunIW00rKEOyR4Ci8S9H+Qg8jq+x50ZrX6/uoUXigdeWwJP9BW+MU9fRAxMqq9AmoJh4ymNjW1OYEiETujgxRFgZMjs0AKGABBLFfn2VD/rfWlsbWtl1+ro/XAQMsp1M8SXH9JCwulye4QradpSnN5EXIXiwWHbb/fi9shy5YkycHBwS9JSf+QLLJwocdclDEV2iI7qNOPd4jizKwjQugRXeWxyQw5LwtCjIbuVB207/TIL4m8SRNyyyRzheVeg7f61BQWPKb3K6BzS3MFxmYN3gpCJUYsC56W30QlszSu/6i6f+4RZwSAKzrMvfEw/GHgATFRFAHxapSiciGcXt3ftwAP9lT/pN8UXvHXZrMZj8c7m80RhuHR0VFu9Q+F0TVEToUUouk1URT9EnH8Xlns9Xo6baGBdtpmKY/Uei20Wi3R9fwtTK3ZRWQkQgIddSELDBAGRESqFouFYp3AK7AvLHzJvXbcaCP8hMgyVDLuar7hDNBWLO8sZhInxf8K58UQ7n6RqCQVa4tfhay02229lE6yr/gl0+iezCtt1tkOLM2ohyS7SG/tZrOJaUqNMAGC4aw/tJ7fV6jBX4qpC/N2YH5sNpvb21sSjLSpns1m5GBoJkGvf9Qn0VscxwwyIrJGRq+urt6nLMZWPoIgIkyRodCsl5LiVPGgFJvNZujN0ZXcKIs4Ho+J2rgzkxABFLiDzAGKGU6U73rLqoY2FFcakVger1TqHCFIPQYUSqhkXTf9wt7CK6oP71POFHhJlSZWbVN4jhqkwCAIlI0g25kaTZrVS6xCRV5KbszL2BrHBxZjVSoVGgsCQWsMW+EVyHKeVapSeARk7Zq+XfoiDEO6FiJ/VM8EQUBrpNvbWxrX0tJkMpkwpK0oChoq04KLiIoYiEicKrz3IIudTsfHvRLrwMku6j3RYc65ZrNZqVQYySRp8D2eoijK5XKr1aLVxHA4ZDlg22MU2HvgSWJqHEGx+hTr6DlDbwS9ZI46az/Y2nqzZ7XHzjnyk3SN8YNlXfIfQktUBF4uMbeCJkkPFFqAD59bGVh7T1n/ktftE10rfeZDOTxGs9k8PDykgQzmEoELrUFAYcWmJGMExfsnsLjPincGPtCjS/U6aG5+hj1JPwmyf+pamFirtNB6JOFBohrr9TqNvt+8efNLZTH0itxCrxLFP2Sp11SOPcAOLhYL+DjymQLrWg4IxwvLaVNuWlzU1ApWOH97m0qnLWSH0Hl7ryQ0NjpgYL0fHgCZhUXEPMZkMqFns15c71jcjzd9yYi8LCgGmp+VvUzTlMyyNl5RYGaUOZ4ttAIJd79DqR4gtBTXarWCX4iTk1m+Hk4GpdCsHtWMkWUlWGF/KETgFbuxaFmWMdAAHYm3oMKX1WpFLxAgJN9HEoaFIHL8sN1laxU7nU5vbm7eXRblqDkLBeQDBUEg8BYPjyeOooh+U5zdByhDaJg5EqZULKKG3fHzGYp1gJdxmZUJSGygmlZEdqqwYFxhRGChlfNSOM5Lusj4OouZuImAUkmhJDX0RuPuvboQPArYSRBEwHdCK9HPrdZHoJh/Qoq34jN+QNqgREQ2vAMbwiuotDK1iwykemsD1uyNqqcFFDjP5xMrkHDWsC/z+vFJAAIjwFNfsd1ue71er9djBZBLnh+VSTbuRyXyoSxCiNdCh2FIplyuOrvoDItJrVcGHkNhXKng/oDS3Op6lGPVtrEcgWX8hJzJ7gQe2qdaWHrWI5qBFa2SMnbemB1JoZaSJ2QLW61Wu91GdpE8elaVSqXVasXEdERNZlrvlXkcttTYjWxGo9FgvAM2DolRy1PFJXJ2OYTOI6fl9+txgyDIrHgvsvbJCDFyCTNI/8s7chgiG6oKA5eRJRyJcrkMEwI1gS5Ut0iCBB5A+EMYhrTmCm3C+s66rK9WKxpm66/QjmpGWiqVXr9+/TNkcTKZMKNLno1YJ5Gld3V0EqsuDSy+dvdDNt9lRskRwcQ2zFZ22dmcHIUXSszIeSo8SBm7Qx/vwEhcoZdiibyMdmCFz5lN1o2iyHdD/ROiihP+ierPwJA5+YsSx9hqvii/54EhE4B0ENWxVthKIBgpcgCawqJsZ56cxE4ohOYVS+bkuhRWB6zXV57af0KZ8t1uR1BcrVbpuBxbNS0xkLCIzOYhED+BL8pSs8jo3cRKkAn56/W63CfEMQzDV69e/VRZlGbilYSGIHCsJufbj2Air5xUBl1SxUHnr1qtFptEBUJqnGrpqtCqC4L7kJAerzAYcm+DKhTMKoYIvKSffsis4DLwxqYipuylPsaLEF0WRQFlUM5i6A34VVyCHkqtrIkt1BkGiMmsBj62arrC8H9nbpzUeWA5An5QaOw80FFiR3qMLgAcaV9NaEn9ngLyXEUfxs8r7rdrKgzhlw8jrE3ZtcKDKfb7Pc5rqVRiJNR6vZ7NZmCiYMZ//vOff5Isdrtd3uff/tk61DgDOyDi4zLnVjUnu+B7ZhIC5FIcO/aSsJo1YtUKCzD18jKI8jt1FiXx4B2RFbTnRoDVkwRGRVHEkBjf23k0otCadcs1RFs0Gg3aI+GDhtZeNjdgXMEZDvTGuhdXKpWtzW/LrNdKxSYNclD3+z3DRFhMFIG0de5VfBeGK0VWfuDMTYosv4oCkyIQ+kts67w52grIxD3FlZf6iL1mMoHHfmcNCUoki75rkdoAYeBPPqMcR6/XQ3n/6U9/+nFZ1EEUchEZNdB3XUPDVsRS5s/lWumTOjpb684NN1PHjkOWWl0z7jNp1sCu3LhhxV/K7vNz4g3sDYyKKxOcGXVcdwiNEiZT7jxwW7rBz/ihQvSvkUdl0FtsrZFcYSAon3RWa4cqImWysz6ogpyk6X0rzO95i7KNSggsg5AYeUpSnnrNETKbjJTbRDBoOHLE5U0GVmAk21IYVz+zhC1BN9RupdcDD9hPjH3MvvCmwMbwY8BY/u7v/u5//+///eOyyE31NYVXvhmGIex557EldMSRg8wIxr5McPPIKHcyhXIGwMl8sFDui3uLhxeY+RaLTraS/dM38i0IJWFWZCOJ8vt1SaEHFEiS2Jh6vQ4ILBdWetp/MNyszPovCtMhFC0s2uUF0zSlx7XKDJxhFAirf+B3VneLeVFtlOKDxGufAmjKzQOP2KHY0TmHxXQGmAgaJAQMvSAy8HxuKVomVAJ9FEZTj72eR4HXdSOy6ZmoIQQdL/xHZFGmTesbWa2XEJzQKp1J5+OFoPBDm9Ko6AcVyJ+QQdnYHHsJIt8lsgyOhaKWwOJ3X76d8VvJ34hNqH8VXOcM30YVhVbhK9sqkdI6PtDoyt/opOmfdDxyI2SwUKFVwMTGeyXn5FNfeSrdwXnat7DEIxFuZjWHgiNQP6whL1Wr1ehO3W63m80mYTtUeb2p1AoPKVsHG1XGTQdGMUNoseDWGu8SgztLBORWlSEXk6+OLEMRG3+lbM3c/sN/+A//9E//9EOy+EAdOsPScptCut1uY6NnOxvxRcQkGZUSdV4ZIZQkGc3U6HGR9VMD36EuWEaw8MB2d7/TA3sJ8EbURhQp+QutaweQCsaCs4ug0zZEPonvhOgrCuNoFt44hdBL/2i5giAAKFbEII8WzCUMQzK5qaWnIy+ZJJuuhZUXK2OtPyFl6utyIkKGWIHUsCls2f5+xzC9iPMmKuRv8SZRwyhpLHWapqS1sC3yO3MrzhR5hwwCehrbFRlyzCyz3W73hz/84V/+5V9+RBbd/b4fDyTA3Sd3RPfbz1WrVaAHf7dAO+kUzWsQcKE1qeMUFXdnQ2+km8HPhWvqn4SSsGSIo0Q2MPccliiWTnLgrFm8uz/oRb6yRFly7GuOwKOJ5MbbQCB4fZaiZL1MiRLQi5xATLbvxeoU6Qf5A5LO3Ctek/XkA1AZEhuxTdkUqx3ZJastTwxZxKb5DxAYAUpgrS6IqqpPfWCaYyuuIHPDpAXgPMSa2d8okR/Xi87SLaoN8A2Z/jfyeHvaOX8jC2PI4mIKcOLdqO2ABEVlLgZXbnXhJTzcW5dOBdEobSBhBOZe9YLgBqkZ+TF0HZf8OY86rl0nIUuNsB5DKJKz/E1gyRKOjTNXjC0pvDSJfx780Ed+tsSdHzKP+O08GlHgER38D+PkLBYLEeNjr2cpsTzsjdjjYfnvJcdJjxcYYTS3FLyiZt5ub+2mUuOtZnZpOxSWIVG4VT8kiw8sEa/Kw8nk8wLKIrDZiTXs2lldd2B9bBGsJEkYzz4ej6UR8Thns1kQBI1GY2eV/HtrtKXDADS1tkn1kkU9pMJJ/leb7RNktGc4mtDvQiuCCbxIS6IcWZMGvZecv9RrfSHfBjuF2DFxF2WJwpBNwFuQG+obUO2Fzo/zGuz6ZlGnMfDcTd0nNCwJkMg3BeDngTfFMrDQRFGwD/EQBihaKtl0dkVypF7QOLHXEW+5XO69JghsIqstbuH3yqIi0MAjh8bWYUyKPbREX2EYVWjV8lCGmONHTMMSlK0NYZqmNJEuLLQkACQNsNvt1EuEdSSPVK1WKRvNvdq/KIpwxUTTCgwHQK3meb5arSBA5B5O6Wtc3c155ikwnII9YC9ZWZkCAeCiJmXeMOvQepSRD8SRGgwG1KztvIlDcg11YHTMfOusJ/TlzzfovvIj/Md9DK0HC+FFURSUWUntZV7aIvcYcTIgso2E8Gwuuxl5ndIV0UsdsGt6wiiKOKKS1x+SRV9BZh4HTkY5thIWToZcnyAIiMUia4ogbxe1jHoACkaAlFmXgUNXgUfwMVxJH812Zr+iKKrX63T24AFQq4n1S2Z78CCDICAPK3shI/XAMmrhAi8LSly1t6FGmRHr5WztbcxObhj4A7nhvOUembewDI1UgL79wTP4MlpYEsE/SDpjqC58HhLrnHzOue+Y6tmcV9Igh8EZEBEaPM7yjsdj+ksxojk2VopzTtVCEuXUKhs3NqMkSRKF4c4q0L9XFv1HzL0MARZTn5EXTGCh+8LxxM3CQukgEqyEXpN0VDdhx3K5DI0ftbeeDZH1BcCz3HpzR8AaWHE1+wq9K7d8McEEC5F7rXwSr6Gl5EBmwVecel+FnNqe3AYm5PcLtxOb+5znOQ9PG23UoZwQ6Ta5yM5rvyRxzC0R5dsEbYRABuwDBAVUL56uX7T6wIj7hzCy7teyYOA+9AIpigKPfLlcggbICvEAmUePLzynNvTax8l0SK38kCzKHCj+CC2nh3eF7sUFwZ8jmI1tRIW8n8hmF/LCo9GITDyeFsKqNVK1Sm6DRvT+8l91iPkBHD/LMuJWkYn08vJoBYYtl8sgCKD9qpw+88havibTtvmuOh6LvDHQoux+4Y6z0kQQ06IoZrOZuhH5WQ1f//mylXslJvxr6KWyQo/wQcjMwVBEst/vB4MB8VzhRdySEkl2ZA2D/k0aDEnN8xxToCPN1zE2j1dOjY0VeH62e2sYo3iruXHqQhvf9CP44mAwePLkSeAlvAtLKOfW2QNwVa6A9BDlpIEXgOspWVmdNkKHzFJw8gSceSeSdd8D8xUVdhP/I/TKcQrr48YqcAeOkKAv2vYDAPnmL/QygfoBTAfqlwIO4aMy+tKL0nmEKcpkRB4ReO+V6+vVnIXe+mq9MospVSoHrlQqYRliaxRNxgUnZ+/1uJFDL1usb0TgUo+VF3i16s7rSC0lGhohw3lWXicwDEP100egM8tFycskYf0jetF5TkNhGdjc+oE4cyOc8ftTj26der0lYyNgSlidR2WFfqvYSGqYJU6sTirwUOXAy5Kj2CDGOeMm7qzhELciB4Pm4IGDIABUkt6NDD31LbWEsrAJKIzDEDlS5FnnhbdSPH7WRArVOafirDAMcUtyw0ekkqVu/V/yV2iUzNgYPiJNnLfb7WRnOJwI6NZaT8kJ8b1SncPcyABy5kjZgVMCYE0mE9ziZrOpttnF/cl2KBFF7kVRAIoRREeWgGXwwo/Lom6No73dbilHdxay8PLOtHHmDXuSuZFg5QY3yupRORFYVOXM9AhokGLwNaLkrFwudzod1kLpqdyyHc5aNoZex3k9fNnGqklKdGzkYDxwHOkoR7JED6bTyE0kyqk3yiCwSlxnnavkevKmsXFhCm8Ee2ARiRDHwnpUUNQWBAFgJ4Zo63U5S5JEiWYhf7JpCo9CSzLxr6J+khnCZZcIOucIMfM8n8/ni8WiWq0eHR0dHBz4AaVCco4ERT/ime/3ex1+gLnpdPo//+f//Kl6Mbe+GUof825igGo1sVmcXdw+XZlX5UkcnWUZKRDJR26tOdBzgfEDtPe+FNK5hlohMjTaV2VQhE2Ghuw4c8UUwfhmNLxfu+7M0w2CgLSBT+32j4cv68H9afOJdXRRxM1/kSpeTRQNVSHqhCTWriP3wtLQhjYU1mkjtwJLzazNbEom8NODjI6+RR4nd2i1WlT0KVNCC2ckyXfP0AKU+TGBNLfswNba2avWFpMNpIV1hoExHo/fFsS/LIuyvGwSqlGHWMZCC80kebyxyONoSU3q9HPWY6ML0NZ7Z714aBkdRdHWLvlGLBxpEmiFgXUEwIsg1nOWMGRF2MXUo6vgG+EhgH0W1i62KAqavklki6JAI26tw1hwH/8rvMhd9+FdNB9ga617nXMUiOyt4geDmL7VTFaKLbRaAn7D9E/UJCtP0ll1AiSpAVMfpEx8cQw8cIDAmRNOGE4FI9H3zvrMkKFlHsxms3n58iWE2dyLdKVNeJjQOChEq846SM1ms//+3//721L3l2VxPB5zx8AYbL5VIuanr0Bk5fdirWF2Cy+k13+RD1qo516Cm8eFXYKJwWsGwZJBwRHW3fI8ZyMxARxKuVwoy8xra55bA3osEaffN0wsE8xWCYESBv6m+lsrnzg32BIzxItExnwD4YMoxEIFQSDOgRAivkWRTWz079yGVIpCGwQBAkTgnFtzebHuQ8uT+bY+97BP5yWoGJJFnIHxYWW077wRp6soCqpjIbtg4tvt9tHREVPFZQpEssbK0fv+n//5n/+iIP5lWXSWiIysE0hmqVKWm+dgHdE6sKGS+70lMm/UioxXHMdAU5lXao4a51SxXggTqiv1BnymNnk09Kab59aDITKeGA54ZF11YCTIcUStrtfr0WiECtxbbRR76TzHUR6wgonCi28wpluvD05u/eNiY2StVqvJZEIOhq4SuWW6C2s/Ehl9jrAdR1CxNksnr92Z1pSzERoTjwXxH1W+rPLmqU0QkulnAbHLWFJ5mfxtp9Pp9/vQYCm9wJozISCO44ODA2oUZRz4AKeIxmjT6fTi4uL7BPF7ZRF9E1vVnxw4VgetyQcKrzFS4jUQq1arehN5G9q53ObkBDbbW+RQWiI5Q/xzrw5LaxcaKBhb92yekG3IrGNYaCPTMPSZ1WWHxo/UGD1J0gMXkNXwnS2dLmdsq9ToIL7ukXWbz+cUJVH8IdHJ85yBQntr/4x7gzzFxrtDqbM4rVYLcRTAtLV2xahV1q1kgz9kQHPrOyqTJVPjLBOt34D7OuNkVKvVk5OT58+fn52dkTXgJpgRhIFKK4lNURSEBJw32lv+QMnVj8jiaDSq2IAn+X+ZEUxw9abTqUIBZ/1DJJ2siK9CuCFnJbV5ITgZdGwJvGLNwMuFBFZ4EBhbOLZKq9B4KIpbS1Yuk99HdKleC4wzwfPsbZ4A0QkCEVjK391vDOc8NsaDQyuXMTTCIn9FgRhgb2is7MKyYWREeS8eRlmu0Eswcozb7Xa32z06OqpWqxyh8Xg8m81wltRfT8GylF/ulVj4+LmsZ24AAk8lzDWKol6vd3R09OWXX56dnbVarTzPr66upONxrpSkUUjEbQFl3y4k+Nmy6AxFczbIJPfKcKIoajQa0MRDG4kdBEGtVpOh5GSHHokBmEA3l2IjeRpaEkw7wQbLDwssO7y3YSTEm7nXlDG1Dk9+6Mpyi64i7eicozefDztH1ro9uH/pUOl4+DGHuufASCBsDAyu457wLPV4SZLgQiGsWmdnxhTbwvv6Zw/JLoqCfjfgizTzlSgo9M686rAH/kbhMX3kfbFNhF9HR0effvrp8fHx0dGRYr48zyE7iyMSWo0LYS7cUzrvvHjx4qcL4g/J4t3dHWlN503j0WGt2LhQHojQiQ5A2lExCZx1ytLvZT44W1oj3xDHxrqTTSE2F2ap2waGTWR2hYbPaSfSNEVt67YPnkofCz2Olp4qvM8zFaSsCCPPc7z+irVU5CTwdmIuRt5FdkSGGG6Vf/K1CJvNhrFWg8Hg8PCw3++DraBrh8Mhf8gZk0kRgKA99a2NdLkzx4PABYN7dHT01VdfPX36lM5EWh8kFS4VSocZe7CVOW+cjZ/VSedHZNE5t7XOvrnXeYiXweDO53Px4dQNQ5CEjKnzjJ2gO+dxQEIDhyWjgUHHucFXiJEvzUEQ7K3Jmvww32nTPZ1FFZFVKiHfzsBLpYCF4TuPqeQrldzjy+ipnDerhnLg3Kah1+t1RXiRFTLH1mO8ZB3nI6s99TkECuEz68oM12s2m52cnJD6g/RJ38SNN5VSb+0//4Nz5evL2Boe9fv9k5OTP/zhD8+ePeMg4REGVqd7cHCAaSIc5IebmxtQAp7h9vb25wrij8jizmYzIfiMpc1sUAWFwwgTISFIoaRH/p9zDsKVzJAUIaczsr51vlCmXnm8PLYHUov0yG1FHBPrOF9YebkeBiEWVrL32oFqq6Rr3X2Wf2TEC/1T7LUFBMXlZXc2qSD0yhV87EZBA543EQlhgcJnxDr0spGBN4gTx6awHs+JV5ZaeOC2rwicl4PVgde74L+enp4+f/786dOnJycneBeguZn1mORNqzaQmfcVc4cIkibK71kWR6OR+t34QJ1sU+HlTrA4pEO0YZIwyRYwrPZV4cK/PY1HCQ68GprculPkHrjKn0j+eE7CN+6TeiVOvvgGxs4SeiIvXsoSg0DU72NyzrIyosjnNl5ODw8aIAaNMwsQeEwtfuBPyHPw2LBuQZL1SJKkMAyxj4LriRF1RH3Jcx4y5Z9z/skXRCSs0+k8f/782bNn9FPE8Q0tz6kUq4/a8GyYZpbunQXxR2TRefXFYurLBLMT+/2eo4M/S2WdMyMbGSWJPjh5ngPwsjrOIyNKOckRDL2qBv+fFCz7oWJgjCb5qf6jsluxDfhMjeQsJeQ7poVF7s4jnmTeZI3AIyJJjp3hMrx+YdMb5IMiwbFxDSUxsFwJC0DI5UM709NCKlglPX+tVjs8PKQ/p9wJf/uK+ziADnDghSwcvF6vd3Z2dnh4SIpVfcNUxZLZ0DiiBSoeS1YBwgIOh8N3FkT3o7IooEHvnxlDRIio0FrS/5xdykMDi2ykgZxzsVWl+Noo9Ir8Cy9bFXismcxj9PieZW5TMv1gOTWaQmIUWkWaChcwTMI7+NLc6xvmewiy1KL5ZNYVrrC+SrGNTsJuKn6SIxt6Tdicc7j8hICsGykD1laSJ7xQZwPo+9GjR/1+/7vvvhsMBqFHyHgglIGH44ReTZxOeLVa7fV6BwcHJB2gyoeWj4ZVNJvNmJWeWqV5YTNE5B78EkH8cVlkZdEZfjAoEN8ZBw5qAi+53W6ZlCTrgOLEoUysBYfkiUsr6MNgUpPOkg0SEV+lpTaIheqFnTe9NrB8j+iGgXHJkKcHhFNnmf7IaicCr8grthkL6PidTeLlGIAH5XlObCecSGdMF1lptaLkdO2syZP4ROjLyLqI+Iws8h8nJyd5nl9eXpIpZnd8d/nBVdxv48Eb0ef44ODg0aNHEHCcTaWAJ7Zare7u7mjgS7qF3qHO6wT2QCW/w/UjskiVp7ghkPM4BypGDC1xRPu5wKaQStNgNAktCyvLAJ5FODJLbbv7wKSgjcJjMDjTrJF1yVA8mFrPZvQ0q8m3xzaUynkt9vZWHhAaEskz8I1bG/UqdyI2RjePrRyJUo5Evnj3uqEfLgiRmM1mdDpEyaFfdRRlbXT4FW4jQMRAaIdut9vr9er1OjiL4GsuHaQHXhAXwRM9mA8PD/EUM2uCRQYZd3Y0GmGj+d/lcgkiEXm1V79IEn/KzF6ZaVTIbrfDbWdXRB3FREpRBfe7KymGEPgXWAU70lCycfSJNYJ2Xk2QlFzhTQaWo+kMqgjDUChxYv3s1K9Sto+bo9icSb/vQnFl1v9YCjvwSl58NRkZB4LGGDD/FGZyAlGZPAyaRoKoAyklirIsl8vyiaMoOjg4iI27igDxgXq93ul0oKiFXurF30QJov6rBSyVSpAh5vM5Q69UNzKZTCggJu/sI01Sh3KdfRH/ULJYeN1O5clilJMk2dh0RQQF0QwsCRFYsAw2lCQJPVZ0TFNj6jsDX0JLQxeGVvqRtQLqkpW3OivX5xudc1mWwWHjwWCOiFjqvxrbL1f4wYuj+WQHfEvtTPoFXCOIWxsyKlxGblxhlaCiw1EnJSHmWDqvVBkflNNFGpCbEyJAnKGJNyw1YOfAkoGFkfPlIPrxkHAlPjybzS4vL5G2druN3qHSSpQRRXthGPK9LBTH722e9s+9flwWnRFU9Uo6f5F1qpWPL1B3uVyquKlUKsGADA0ike+cefXhCmb50sCq7B74W5lN0itZDxBpROxjaMSTwKodcIkUByh83ltf0MJjRUjmJBbSgly5XfpMYXxmirxYBz0Md4AfTl6KcIHcCXZjPp9PJhP8isxLWuI1UjLmjJ1JLYGmClAHjaTOZjNf7Pzr7VcLvP77w+EwyzIYuNAg0Otpmo7H4+FwmNtEiMCqpPWagXVrOTk5ub6+/oCymFtvq9wKOv/tL61+MbMZkdoeMDMUoTNnJbH2oZnXDqGwUFpW0pk76JxT6A0DJTIqGp4r7Shzo+Y7oxShMnkkFLk8CrnbqA24qBDGhsOhn5zU4+khE5sJKnHx3XZaD4AekBZ35iL7OkZr1Wg0CFfBSrCJe+tPDqGz2+1CcR2Px6CJtBNHOieTCXH3wcFBr9fr9/vtdnswGHCTzBuGwOX/LGMtm6NKTrQj/sBisRgMBjc3N/P53HmmQEKMdohsIBcfe+frx2VxMpkcHBzITPv+GZ0tCwPkYus/zpljzzJrfRkbAcx3nzMvixp4NJzIuvWnVs4ceo3wQq8TIVqt8NBBvgWT7bubvuPPrXgXrA8fliwqVIosacn90zRVqk1uAPcHeS6sflL1aKvVajQaqeFTaMzTXq8X2njrnc0Z1hM2m81ut8twIf4JFJrCv6urK+Bu9aYHrG61WiKSyUnwxVGnNLQEbGy8E9QNxxJvYT6fT6dTDonz+u8Hls/MbB4M7kQQBP1+/51Rxp9ko3PL1e6triy3YgO0euQ1fkQWITgyaHJrQ29Cm3yBaG6ty7JQxsKrRkDxEIKQkwgNB+bzZHoEEhVezzgfdmZjQq9HgNgMCrMiq08LPDKO7+qFHjC5tVaokk7EAvoMT6VjQBnhdDpFXUm3wTmQx4LdKCz1nKYpVU74lCwFP3e7XefceDwejUY823q9vri44CGbzSZjQ4W4ccnhDrxsFlGLYuHIWtxmWUbdI2k9NjT0+ubL4ycY5SDJu303QfypsugMl8KlgI+eWMeIrU2jBcMjyiNMWS6XcLPzPKeNHWexZA1+cOxw+XOPxFBY7+7Yqo1YX6V0+SWrEFuFOQ+AyUNGAT4k5TubqvJvL2+cHaESeyPbStmH3rBIuYmBN8tI/QVz6yERWVntdruF9y9ohjophiTgbCFnKFRnbDpnnU6RSB5Pn997k5p4ZeGUFB74JsUXx8Dam1esTXW9Xi/Z/Da+JbKhNVTP8DxK0Mtl1xGS9wxqttls3lk1/iRZLDzi1t6G2/jFVno9v5U+XiON97DUSifE1iOKFQdtljWUWpL5k9+m3Ct6VxhnbBSeyIg8YnqDOQs30Q+BcRAFp+mpnLUXIyknvYgRyLyBr2wMQYY4i0o2qnFjZEOmSjYok4OUeSV2zqwNuWxsNH0rc5sBo9BQf6jzH1ghIk2s9/eLuJ3ho+wUFVuhFeFHNrxDGRQNN2CzivtsSGdtBcL7VJXYGwL5AWWRhSgMdcu96SbqCZamKRQm3godgM4IjCrMxeZhTTIroxRYmhtwE1jLnq012VH8LrWKLGZesyW2PPYG+Gg1S97IY6kZ51zZxmkhcLmxyyIPEN3bGNedzSJNrRU+caXPCAagQeXHxovjMVBjOnKKbSOvOTaBf7PZjOOYCeKlUunm5ubm5mY4HGJz0jSlZwErszfuMy2dwjDEMVB2yjlXKpUajcbBwQHdlCPLKPIklKHlXkFCalSpzK7CSpBRB1LnWufoFwCNP9VGa+c47rhHeZ7DYqRvhlptQyiqVCr9fn88Hu9tFKhiF3Ug4bbA+uD4heG9CmgCy/jJj1RBjBKPe5uNww2V4guMWJB7hQc+8BlaiwUQPv4wMIQPkcpsFEpmE2IUsQVWDc3WYqkRQdrNc8PYqiBwvyA48r7ufjAnt4zvpdKPQ5vn+fX19fn5Ob9sNpvA3RxXfVeSJBrNqfhX4QVpQ+5QtSF+8v8Wi8VoNNpbPbiUovNqWZBsVagFRquTJ/pugvhTZZFhWHvrIsVa87gcDlBcIsTUaoEJBgHeEptPm1inB3aIrs7wTzudTvn+kBydWvZ45w3oi+83CkMKZW2dcfISr+954GVQfLtPVmZnvcJk4nMDs3xjqqUXeoUadpYup2caCE65XEYsIuvcktr4gjzP8dVkGQur/8+MmIe0Md6LqmeFRJzDIAjm83lRFNTT+L4HtpgwK7OSGoCko6Ojk5MTyOFa6tCINmEYjsdj+T/yDuXNZ1YURpQjKx9ZMvCdzfRP1Yu5V4GFeNF2jMWi3oJHl44hZhSjomJjlXiBknXvc+agsOWRDfiMrcijsGIuKded13bCWRFqZH2eOCQ7myfgvPy9ooTCg2m4D2aLIAC6vEB4KYnCo2AVBkMi8ZERs2nQMZlMgiCAwwYOSjTgrJcQGheCoO8Nyy93zgHZpGlKdBxFEekDnhxfAs9S+pjzhpTXajUIDbjjEMyePXv22WefPX78+OjoqNPp7Pf76XRKR6idFYbXajUUamhlr4WXBdWBFKATGvlIi/NhZXE8HtMYiUWkIFyAJ2K03W7v7u44UoJI8Box31rl0OgUEh22RyrNDzUkT+pbkltEHBpJp7DJHcofyiFTPl1OtzxL6VRnnOfCmljiFBYel0ISIzn28XAqflCohE2JN+CNb+l0OrVaDbYBekVBdxAEAPtKBfEw8HSQDyKPyAY0cexJtxQ2HTawbrAY4sVi8eLFi6urK5CK4+Pjw8PDk5OTo6MjOlsUhkKAgyL9HABAnwfpidRroq5j41/vLIg/Qxadc6k16txZ1xVy6oSQShKCBhPWMVS61WpRJJt7o2gViPGeePSU2XL02afQ+tlF1h3Ud+Z0KBUwSQWCNxXWhln+rpRH5F18HaXByETuFRcH91u3O69uHxOh2jxeE/2XWB92TSPj7fjD2Ci6O2NHayJLYEWxmUeAVwl5YPXgaZqCoYA7KlPMy9br9dPT08Koskzk6/V63W4XtnlsJdh7Kx4CieONdlYuggmS6dc66Bj7QKPznJ8PK4uIIP088YpIYJAPZZxsYh3kYcmnaUplRrPZJPuSGcGu8Ih9vOd8Pqd7WG408swmRsVeNykAVQAjUsBsKgcgNhJr7BVNB8YSz6y4SUucGWEbl5d6SslH7hGqpQycpyNTG1sOO1NyzLfv93t8ryRJ6KKpfmWhMb1TayQMcIu+RxrUUluaMrK+UBJiEjz9fl/NbsIw1E5FUdTpdFarFSNBUa4KOPZWHs6msFPqhsNWhl4inl1TzKdb6V9ZnLu7uw8ui4S6JOPVt0AWJLD2ofwSPaHR0rg1sHgki8KcnXNpmk6nU1AM1QtnxldILQOJ5nPOETax4oIS9l6HMQEWWim5jM652IZ25QZQq6oy9cqlZY7dW/lc/QaLrKHMcq3wDQpr0oKHt7Vplc5rKoz6QY4RCyxmFEWgs4nN3/RDLnS8Mqt7K0gSRpPnOUoakcXDGQwGnU6HXkU6sUqMRVHUbDbp3V8YxOtzUJzhlMrTRJbcx0nbWQfyDyuLrDvbDzBBPRiOf7vdHo/HzqIcXp7jTuVHZFh0aBNoffOHvaOwkLNeWNFWdv9KvNI7InFtsJzRwkDHwGMl+nvJRqqth/MatWfWL8W3y1KKoUcQlNgJyOTzodWaIdNAlYS0SiHiV8hLQT/5joGIFJG1Wi289saFcUOhQk6n040NUkaURd6D/TocDtM0bbVay+VyMBhQ4SUcqlQqoUqDIGi321TjkycDPnNmSZzNdpCeLiwPktogs48ki0VRaAuVUaAV3Xw+D8MQBoAcYSQPhmbi9bVR9ACOrV1fLBa3t7f7/Z5JMApOpUvYOSlULAtCLyh+u90Kpdt7hRCFRTna8sT6pGdZRuSLivJlTi/u7heOuLd4WToPQrz9cMe/Mks6E6tlXgmiziqYohrz6XhIIJT2oPErd5Bkv3nzBlCJNd9ut9fX10yqI2ZC42KLBTzhVrVaLZr95V6KJTNesAgAiY15zIzGpQTmu10/TxbH43GSJDTsoSEkFE42AHCBQwMhwDlHan80GlGBgC2gIhhRYNFDq9kDvAAKUaAtbSHkWW6KD2sVHiySe+MhQq/Na2ANcH1YG28PgeZNJRwPZC70yPqFV8ok31TPrOeUnpYU6o3429Rrwh4Y3VXAe2aDKWUoZRlwo3EtZDpzay613W7b7fbZ2Vmv11uv169fvx6NRs+fPwdoI+hhfdTfMAgCxre02+35fE63SC0CrgJ8nNCq2tHoqZVoDQaDjySLzjl8I/w/hX6lUonDxIOq9yM6D+dsPB4jEGwMgthut8ERtKNoXMwHh7iwNH9idHyWHsVJm7zC6zvvvH4xMrjOSl782Dmz2YvkSNSngSv0uC2SG8FSzlOTziAhGLJFUdDcOze0fGujyp3Xgrqw+DQwxm7klYpL36Q2a7zw3GUoNqlN6C2KgkENqTEkAhu3hrfDvrx58+b4+Jg0tx6S1F9s47rA4LrdLk6CfFwEXcUbubWEFEkFUs87C+I7yiLJg8ViUalUxuNxuVwGuCqKAnIywQfOIuqBoQcIcWS8slKp1G63eSs5y0VRkGBAyKRXHiBbgYezoIylC31BERguQx8a14F19PWoEgy+NXReMc0DTalniKx6nzaERCHyE3SWQq8K23l2371VfZt7nHMfN5UhDizrTeCMDZGyZDWIZl69ehVYs5fb29t//Md/TNP03/27f9fr9QJrDecM8eW0a5QYUHxo1P3EIztK++Jxwcl6t9Ylun62LE4mk8PDQ85BvV6fTqc8NAFKalTTVqtFhJvn+Ww2K1n7TdwUZ100Cdx2VjmfWw+n5XLJ3QSwxVbLEniMf2cDiGRtCy9VU3iMxtxGAMks5obXRNZGUakjX+D8W/meYnG/fQXwIesQGu1XDpyiqMKLgmXppAsFEciscyxZxr3NvHA2EhU2MW4Sd9Bh439Tq3MoioIZIljq8/Pzf//v//2XX37JmVdPIhweAGNAKL1FYSBi7hHwCutqPp1OX79+/XNl6cH1s2XRWcslTYilwRkLymbc3NwURUG6Ey0YhiEcWOjyRM0sk1KFqVXXsw2Un5HRl/GVf+arrjzPUQ+SucAroBY25Dyyt5SWH8P+Rb9bQu9M/zlrEuS89hiNRoNiPFVJI/dbG4KpmFrKT9Gbs7y2AlLn2WjsJhEVbTmwy/g5nU4HAxJaNlUPVrYGtUVRYH+RY6pLB4PBcDj827/92zAMgXXZi9SacnFb0rnOa0cj1c76r1ar8Xjsz1h+5+tdZHE8HvNuOIgAh8om45bB3CYtRudnnL9SqUQhT2GhMf5l2QY2+Zb67u6uXC4fHR3JUxROq1XGdmgPfMWj+C67PwEkuE/DUV6x8Iak+iIo91Euo+7G89N3QRO+kyTpdrtxHAO/C82WdQ689lEcjMQaQud5jjNHgriwnCS5dXnezjkwQqgkEhFlq3MLgbVreOd5nt/c3OAFYsQ2m81nn33W6XRiK3cEhCLTE1lJceT1vdYqgRbN5/Orq6t3kz//ehdZdOYjy1KzLmIiEUff3NwAfiKUpJjY1Ol0Gnk1zsL6nVkoXhiIB6ZT4pWCy+cLbZaCwm05iIVlqCWdkmDFfVx7b+CP7i9RE3oceGkYfRgxYttiY/465+hd4ZwDLt1bQzOdGWlHPLnMSNo4PFmWkd/Lja282+3U8guTSmVj7tVDxcaEVTAeeHhWHMcAHVmWvXnzZrfb3dzcZFlGH4jnz5/D4eDV2Mder4fjBPQo08/Rojfu+xJE986yOBwOj46OgL6n0yk7kSQJTl5qJbRggWTqSJJyFpVfijxiJskJgc/Oue12OxwOUS29Xi82SqwfgjiLYSV22gNfvHJjMZIOkYfK/76t6iKPZB54nZX920or65ilXgd5drRUKu1tzrfvesrvlNyAHqAUIyv4x2NDRsng0QhdZHUpsweB1N66+8n4EJ1EUdRut6ET7Ha729tbeje+fPmSNibUXENCpcSWDtaUPweWggfxUVnWe7neURbd/YAa3BHOnHrPyedgv4G1ETg8HtKJrCOwVlEUOCiKiNM0HQwGqJZutwsAoUCSVK+sp9Y9szZOsXVEybzpZcJKIq+hHpbUebk+lQDj7+r3XIUh26ockBCk1hAWVUfLdX7JKc28rmVyJyKr9USIFfFAgux0Or1ej6wgB94ZiUSuc+hNvEKTgemwApzkIAja7TawxnA4pMvZq1evbm9vKcTpdrunp6fHx8fk/dkU1gdBnE6nIOGck1/S5O7B9e6yOBwO+/2+s6RQYPl7huhGUcSUWmcCUa/XKSLu9XrOufPzc5I0tHhMvNJSeY18EeK4XC5BTFjKyFoD+CLoPH5Xap2GCxuXhBZUTOCs7Q5GUG0PCguQCRQwtaTUuPxA3r98jzOxcXxAJM1mE8nAl0BQNjZrUbKCTDvnWCiSApzSer0OVSLLMiAzaXGFt9xZ/bRpXednR5wFSUmS9Hq9Wq1G8pAkGVmG29vbq6urTz/99MmTJ81mE1vM4tDVBL7jbrcbjUbvLDx/8Xp3WXRmqTebDe0QEmtYQ83lfr8n0AbEJ3wBX+31epvN5urqCpecQE/lVFtvnKK+a71eX11djcdjlASTwAKvU4V+lkkVbTE1tpuECfecJBgu3XQ61b86i83Z+703cNRXkKJf4M+FXodmH3XCz2u324UliHkYNXJVnMGTQ33FL4Q4E0UR9ie3dvmJN74+t5q48Xg8GAyYjUyqGt9dU4N4Qd63KIpqtcow4TAMIZgNh8O7u7vVagUsgCBSdbBarQaDAfTy/X7/HtWhrl8ki856iBVGB4ytirndbh8cHARBMJlMgCSm0yml5uDAzWYzyzLsrywm7B4CND+8RRXh4eGhIpTUGQnxkd1Mrd5A6INcQGe9tXHOsPjyRAMvBSd1FdrYAedZcMQl9np7psbmkvZS5hclVNgABCwj+IP0tzxUKTnOJ9pOYN7O2k0JmAyNiqF40fdbEm+acXF/tnBuGSzsMk0WefHFYnFzc+OMhb5arW5ubhDE964Odf1SWRyPx2S9IivSi41+TIeDIAgGgwF2cDab9fv9xFq8kTGjw5/Y6jiUgbXC2XkNSPlGPrzZbKbTqSgnfGNkQ+alDtmAyHphKXkjqgS/VALG3e9bwjf68hd4kLWQS/0yteIY1CS+h7xDQFa86vV6fXBwsLNZi1SrvX79GrQlCAKCBrrnkPrbW/MGnGZnlGRnhxDjyxxTAmEwcL5CYVlq5WP0EGMU183NzWg0evPmDYcEh5UE6Wazubu7m0wm2+32wwmi++Wy6KxF8+np6dZaWysp3Gg0Tk9Pq9XqxcUFdmQ2m9EjBikRys2+RkbSFGMcwmzhoXq50fVIz0yn09hq7crWkjS0cVTKz5KcEKNRkopYK33MUzkvMvXj+sCbZ114I6Wchd4K0hFEngoPGDY191e1q3MODNI5h+HGILTbbSYV7G2sGnbZmZvoZ2uc1YPiXAINxsaNLwzbCrzC6iAISNnBW9tsNsPhkOKHZrP57Nmzfr9fGFA/Ho8nkwnQzy+Xlh+43oMscrGmuMMvXryQZYzjuN/vB0HA5EfsLParYkNiUit3Yt1Db86FH1DnXmqk8DgvoAyhkcokMdIEhPAEPQp7nbE3FBJKCh9Im/M6QfpoTmDsir21G3UezL5er6mKl29aq9XEG4cgGIYhFCEi3yzLiCqOj4+Pj4+5M8fS3c9J+riVM5o3vHSxYlko3OvQGj2ysLAYyVlQF0EhRKfTefr06fHxMb6j3CFwn/clKt93vTdZHI/HbAMA2HfffRdZvTChTKPRCIKAHCC5fBQeCAWOIPEaKMbO5vEiB6Jhu/uDSSR8oU2kd87hVOnZMIXz+RyVDJbpnMMAERVmXmNmBcX+9juPquM8HYkYqW9EYJ23SakD4yMi0OegBYGM8ADcvFarMWoUnUcbscCySgqM9FTOS6tkWXZ3dzcYDFRjD5qByU68Bg9I/5s3b/AsnY0CrlQqjx49evLkSa/Xy7JsNBoJsOOovC85+YHrvcmiM2PNgq5Wq/Pz8yzLjo+P8QLL5fLJyUlRFJPJJMsyghjKQWhiibMF0EPdArqEJl1icQs0Rv6gjeEspjb4TkQHwYqYTmAL1FVibbJ8tpgSMIXHmXX32TTBfYZEnuewVoVopjb+g3ZCmGYYN9Pp9Pz8XCVauNew4tXqU9m5wnoTBB45jQeIbE4jZ2Y0Gg0GA0AfxLfdbtM4OfYKlvM8n0wm5+fnEJZZn16v9/Tp06dPn56dnRVFcXt7C4KtMrTdbvchoua3r/cpi1y3t7dFUbRarfF4jL7B2lJPfXh4WK/XGRt2enqKTd/v99gR/kRdr0lSw7cDPBcaV9i029iKrVDDSAm6am/l0s5jrSKU2Ed/Rx/QHXzsRtrXeSQaqRluAonTz/3gO26tHySFofS/IyALgkAdQX2IisR0ZnNrpKRDSzojHwTjPCqKNk3T2AYSwtIIPSZymqbj8fjNmzc8ALHOo0eP/uEf/uHrr79ut9uj0ejVq1c44vjQxO9/kTLyIa73L4vOubu7O7Fc0Y6np6fMC6EmMAzDyWSyWCzw4WazGWA4zAksGhRO5XLSNEWAwjDEwXdWB+S8IS6iv+d2ufvsldDqnlKvK7hUjm8EJXDB/alHvmfJ3jsv7hbinVlTAzhyk8mEIsCNTRugzzakCuLWwGsNFRmzPzduBPI3nU6ZjL7x5lwT+YFiHh4eHh0dkYAVfLvZbEajETyGwrp3fvLJJ//lv/yXv//7vw/D8PLy8ttvv0UZc5J3Vpz6cZSi+0Cy6Jy7vr4+PDys1Wq46ovF4smTJ4eHh+TEANuGwyFBZZIkdETATy+KQv0b8jyXCQaaqVQqk8mE2+5t/KXv5wXWMUe/9KVKkbL/X3e/ES0Xn3c2jhiyeur1doqsPZezeXW+HnJWm5caiTC1xuAiwnS73W63SxOE3Kq0OH7Oxt3tbb4OvYrpA7GzJue8b6lUqtfr9G06OTn5/PPPT09PJfc4Bqm1Rg+CoNfrffnll//wD//wN3/zN/v9/v/+3/+LRqxUKmSZScNAzvhAEvL29aFk0Tl3d3enYSHX19dEJ6SVcQQ5rxy+oii63e6nn36KJ3d7e4vtFoE+siIYKCq1Wg1IQlsSeWUDe69HlvMKVh4EKM5zBOWD6vl9paimfrmxffmMIidnYiHDLYQ5tS7wQrMjr8GrSswir1waR03u4H6/pwpCv5HPAAxJ+VutVut2u3/84x//7u/+rlarXV1dDQaDN2/eXF5evnnzZj6fg2kcHR19/fXXf//3f//5559vt9t//dd/ffHixXK5bLfbeC9oX3LoHyF81vUBZdE5NxgMyFk753BTlsvl48ePe71es9mkhI+OvEVRzGazXq/3xRdfALikaYoOQDEQYIZeGwnn3M3NTWrzHdx9RaIEoB8F84MvhQ9iFBlf/jf0ZkY4D0J3VomnVJNzbrfblW3kia+AnaXsQe+dc/IsISgQ1Mc2ZhV8Sn/LDWn3U6/XgfoKrwE93Uhardbx8fGzZ8+otPrTn/704sULAhGw7tPT006nc3p6+oc//OHLL7/s9/ur1erly5evX7/e7XY0bCZ/SIAPSeoDCsdb14eVRefccDjsdrsgZ0rinZycnJ6egrD0+/1arUbBxPn5+Zdffvnpp5/G1vqSvBNBLg5lZKVr3W6Xnuz5fd5o5tXAu/vSFlgbyMIud58qq8fWXyHomVdFKjcAe0pRQe41vc2tdl1ZQWf1r9TpEpMVRQFigpwBviTWPk9pJOGCeMyNRgNqBRqx0+kcHR2BxdBY7MWLF//8z//84sWL2WwGwwMmGE3Cj46Ojo+P4zi+vLy8vr7+7rvv1us1ybCbmxuoFYT5HwfH8a8PLovOufF4jDhCVRJBi9b7zWaz0WggqXd3d3EcP3369PT0VEEcXiOVH/hGiB2+P2WEznLizmvpEtxv+fAgQCnu91V/8LHCsmrITWrcbGQRQVG2GpqqL76+0OdWqhJ6U2rEycBWFEVRsjaN3AGhVA1oal2KcFFwu2EZMx1oPp+/evXqzZs333zzDTkF5iSAnB8cHFAETQrn5ubm+vr68vISKnQYhldXV6PRiDbg5CE/Wsii62PIonMOt+Pw8JBePLe3t8jQ0dERJDlaA65Wq9evX+d5ziePjo7YYLaBHS2sw10YhlR4AcaiP0RlECzydmjsvMBF5thXn4WxWfEiwjCk9DZ7qzirMIYEn1fMCxazs4kekXUOyq1VEB2jiZp5O33GmW+gtCcyBIOLoXyBlQji28zncyg20+k0yzIM99HRETE1eW19+3A4PD8/x73pdrtFUVxfX2PNyVAvl8uP6Sbq+kiyyKVoJrfhFPLQWeunT59eXl6+fPmSti/0bouiCDlQh3T0H9E3HOPUxqDmXv2ye2u8vH7/tkQG95FtwHa8AmeUggcZyMyKFgIvwR1aXwCyHc45nEjS4om1py+Meg0TQs1hcKPJM+2twRWqy1lgvre+kqC2cLNpMVUulxmeenR01O/3GcALfxR08/Ly8ptvvplMJs1ms9/vMwOBSGU0GvHDryKI7iPLonNuMBj0ej0V8ALKoNiOj48bjcZnn312cXFxe3uLMWIXIRfib7EfymvBiaeDWe6VrYRexdr3hSmBl8nQD6H1w8QIOhNo1K1eRPId2UQWaU2JKWhoYGB1kiS1Wm1nteEkLUWZVgBLbSup88wbxIRo8u3C51HYwEZHR0enp6ePHz8GsCQVqfhjsVhcXFy8fv16s9kcHBy0221EE0rEaDSil+4HZeL88PWxZdE5x9tqstL19TU6cr/fHx4eHhwcPH/+vFqtTiYTKmNgWJVKpW63y/QbguvCxkNTHq92coJIUmu5FNynOzwIlv0fCHiVPce8bq0dY+b1o5IglqwxOKXfhDgocmWBU6vpIb3EjNggCFCZuMVpmpJ2g/FJT0fAmpINP+ScEALiU+K3HBwcPH78+NmzZ+122znHA+RWlsU9SVgnSfLpp5/SiOvq6ooiaybAYXY+vjzo+hVkkWswGNBqAtpw4REgTk9PT05OwMnZUYq2sF9kFweDQWZz85hkFgQBrZqxhnI0lQ55WwsWHgbONrP9EMxyK6dXyy/9eWodcKIooriOmZuYV/QimUx5IAA6vV6PmWpsvAhjkfUjxXCv1+v5fA7vU7BRaANanDW1gn19cnLyySefPHv2jG7+JGBY5CzLrq6urq+vSbo2m83T01NwtPPz87u7O3hDg8EANPHjxyv+9avJorOm3M45ZIi9Qec9efIEzjb5QDVPR7s8evQIKmhRFCR8+/0+AQQjAjKrolLGL7zfHMeZEVesA/wOy9AZVBlaez4ChdRamfnkIHBsFJVIGKRV+FLwGtXdZlnW7XZxztRAUAcjsmL+3AbPOAtfYmumIxSz0WicnZ19/vnnJycnGgdWWAZBAQ3oxNnZWafTCYLg8vLy4uKCwiuM8m9BEN2vK4twwhGF9Xp9c3ODDw6X7smTJ2wzUe3jx4/3+/319TUR6MHBQZ7nMFOU4WXkk8/Ix4o9yFXIyUMXksUhaUHDTABn9lsunWhBfsSD6OBc0g40tbEAMB4Q7sR6SOAEE8wOh8Pr6+vxeIzDl3n90wqvWCfzZg+SxSbsOD4+Pjk5abVaQRDAx+apVIdPX0Y4e6enp3RwffPmDYnE8Xi8WCxkmn+teMW/fk1ZdEYzo8tCYZMiYYgsl8tHjx5hLlnWbrf7+PFjKO9RFEG2oDcz2UIxEeXs8y2hx0UN7SqXy6SDyegk1tAN4aaRfxAEeH4qm0foBRAiN2AoaM31en19fc00oXa73e/36T05mUzevHnjnKPu8+joaDQaHR8fDwYDhu8hQ85CpdTrM8Hj0Yv64OCAzu+c0ul0qiOHlsXP4WFAH6FfUA0jhsRkMqGZCW7Sr7H5D69fWRa5OJTUqqLDxuMxKDdN91F45+fnpFvIWJAYDIIAdqPiCRGtlSMprIg9tBEYDIiEwIYhBnNmVwLjWARelT55CN0K/y+wBAwj0/b7/bfffktzbCVyOBj0A+eM0RkCNAfkRWKETUhtWBVSyAMjUqqUIL7BmXHO4RdioKl9I8VCt5nLy8ubmxscRJ+t/RuRQq7fhCxyjUajTqejiJVfUnjGYJyjo6PJZHJ1dYVFg3sM02K1WmFqndXq7206VeG1c1CgIOCQ9O7WZvLg3hEaA6kENnMAlK6wqXekZDDBKi6GHZwkyePHj6n+wW8rigLKYBRFTKvkqShSgXiRWTP3zCoYA2v+xLcT91SrVSg55E6JgrG5UDxRnOp4NhgMLi4uCJnn8/l8PgfQ/jhlAz/r+kUDOT7QdXh4CE+MKnc8pIODA7i3y+WS9r2r1QqqDrzRJEnYZnRGZG0Y3P3SvsyqwwQkCeKJbIhVYORZqtN33oUA8Wz9fv/g4IA4miRNkiSDwaAoiqOjI0z54eEhqhpLSiM5ysapciSbR3Yns9EVQN+EcZH1ysE1lIOLA0oIwh82m00aDwVBQIH9fD6/u7ujRzDeIZEKxdS/7i6/ff2G9KKuu7s7svXKFogyiAdZrVaHwyHUUQLSKIr6/T7qU4PDnXN4gTAMBEQjGQSe5CqIo6ncQwIecMN0CVJBpVEbgLqlzSS+GqErktftdvv9fmY9qDIrGWNwWlEU1DwURUE8C0ki9wpu+JkxJY1Gg2QxrFA+3+l0yDg75yDajMfj29tbCu+ZCTcej2ezGcygj7qdP/n6Lcqic244HOI+OucAsVV7QA/cfr8/mUyoQMBI0TIF6lSapjAmAxsHifQUVoQaRRFDwaWu6OtAjFIqlUREdV4KJ7CupEgPKR9GVOz3+8vLS1DxNE1vb28pZBGXIrO2PldXVzRQFZY+nU7xCvbWjdN5BGGluYWwojudczR2E8eHJbq7u4P6QDBHfpkizI9QV/pLrt+oLDrnRqMRfXwpuRITjBU/OTl59OgR2YVerwcbmS5TgWWTaSIAyCeGATMj4K31ej0ZQdV05nmOylSK0nnTMAE46XFDRgTvM01TmG/NZpPSE2J8av9AHBEp0uj7/f7Nmzflcvn58+fOOZxg2szhY8Q2GFqOBM6Dc44zENuAEkR2Op0Oh8Pb29vb21ugckrLGU4IcPOrI4g/fP12ZdGZOAI18xtgDoal0XcLShXpV3UmJm4g5oCRAIWH/B55MwU9CDH2SzIUWFMo7Dh3g+1C1NJutxnsCncG6y/qNXnn/X6P6U+S5OjoiOjnyZMni8UCpkwYhr1eD5VMSHF3d6dZa3B8iGzAtkgL+Y1TsOx3d3cXFxeQvvCnITtKHf6m4uXvu37TsugseQ1R1HkVytB2oNKI3CXFgw4gjlkul2TqkNSLi4vlctntduljSfdbCjpVz6WsoPrsAKw4w6Lr9TruKWFHbk2a4zimrzP9SaIoIu1OrAMjhHZCp6endDq9ubkBVz85OUETI/EESZ1Op9/vS1NGNhILi79YLMis8PwcUcU9+C2/We/w7eu3LotcTCsSCRczjf1aLBYEmDhPQDndbvf58+dUsl1eXhY21wMFiWTQtWM0GkH78ylhSqjgTaoViXRto9EAFYJZzXhKUOXRaITtJnWOqc3zfDgcqpCFzHscxzDiEHQcA1JBuCJEP/V6nQ5sIpvRIB2dxw9kByhqJnyGP/Fb9g7fvn6LmM4PX/1+P7I6LKZ+imsIFEdQjE9G1ZL6z8ZxzMRQyrtwp1Q27+9cr9fDbpIYJB+I8PV6vWfPntHvhhwmRYn8DLcIhYo1h+tAOkRUDJwNDC7NW0gkQq0trIFgbhWuyBnhCEk8KDYgDOTxCVPwL3/jruFfvH5/suicw2wFQUD8i6FEf+BUqQ9EFEWgzYBq0Prr9ToRZWFzK36KR0WTZjKHT548AV2KrTl+bDOqUGZBEOAb0LcTB2NrQ0PEXHTOYXlhePBh/2N0+hLWKBEEFXfO+bqQE/V7lEKu36UsOue63W5ovbMAw6nkUldFGUfwapQNCAitfObzOe4XFn9vbeC4+fdZN+Ckk5OTw8NDEo/OiI8y6Ogz5xzZlML6JhLZEC+HYbher6m1LZfL1DoF1nxRX8fnAVmFCYA9Ye71w+/IL/y+6/fhL759jcdjzCi7RdDq873RUqI9O6+uAB2Z2WCixKYrpGkK3wLTXBTF9+kYqA+Al36sw7cjjjiUqV1g7KlNT8FM03sytGkMBOMCcQKPcFkYKR2OmbgUvy+P8Iev36te5EIc2a3Imi7ENjGe3xN24JO1Wi0K9vDAoFSFNjcFU/jDNq7f7zNABHvtrDepM5ZhYj1h0ZGhDTB7kI3kCq17qvNK/fknFcLy361dMOL+CrTg29fvVS9yQacIrB4PjSL6TGSdJJRHRhthGSEagi+i2+gg9cPfOBwOVVqF9kLb8a+hN1ONEEpENTmIqtLiTx7E7KHXSkUPjxSSwvn9uoM/ev2+ZdEZA5IYtvBmUKrVCXyc1EpFKY0LbDihigGcN1nth6/b21tgdrTv9wlHp9NRmWnoTf0I70+mKays29nAh8Kbpw4d6T0s0+/h+t3LIpcvEKAwJRsaD+XHWR86siDOhvjJXQuCn+Gu/BT5+IkKjI7lP/2r/4qvvxJZ9C+YL9hHlZiIQkZyAu4Z+CL1A5jvj++H/T9B1PX/AVDQ4q5diUx7AAAAAElFTkSuQmCC")
