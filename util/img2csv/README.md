img2csv
=======

This project is a Java program for converting image data to
comma-separated-value (CSV) format.  This was written to import data into
SciDB.  Supported input file formats include JPG, PNG, GIF, and BMP images and
NIfTI volumes.  The output will be two lines specifying the image dimensions
followed by the table specifying image intensities.

To build the code, run "ant" in the project directory.  This will create a
directory "dist" that contains the compiled program.  A python script
"dist/bin/img2csv" wraps the Java interface and recognizes the "-Xms" and
"-Xmx" memory JVM arguments. 

This depends on Java 1.6+ and Python 2.6+ and Apache Ant.  Java ImageIO is used
for reading planar images and niftijio is used for reading volumes.

This is released under the MIT license.  Any comments can be directed to
cabeen@gmail.com
