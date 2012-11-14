SciDB-Vis Project
=================

This project explores applications of [SciDB](http://www.scidb.org/) to vis
research.  One application is includes the storage, manipulation, transmission,
and visualization of brain images and models of anatomy derived from those
images. 

Structure
---------

data:       Example images for testing 
util:       Scripts to import data into SciDB (which make a lot of assumptions)
img2csv:    Java program for converting pngs, jpegs, and nifti volumes to text
            csv files.  The output can be piped to stdout to avoid disk access.
scidb-view: Web interface to view a SciDB array in an panorama viewer.  This
            includes server-side WSGI code to handle tile requests.  This 
            uses apache wsgimod and server configuration. 

Brain Image Background
----------------------

An example NIfTI image is included in the 'data' subdirectory.  This is the
standard format for volumetric brain imaging data.  You can think of it as a
stack of 2D images with a header storing metadata like the coordinate system,
voxel (a 3D pixel) size, patient data, etc.  Unlike most images, the
intensities aren't RGB colors, but scalar values.  The intensities can be one
of many signed or unsigned integer and floating point types of varying
bit-depth.  The attached image has a single volume, but multiple volumes are
also supported.  It's common for these images to be gzipped to save space, and
most programs will read the the compressed version (i.e. *.nii.gz).  If you
want to work with an uncompressed volume, "tar -xzvf example.nii.gz" will
decompress it.  We do have data with varying intensity types and multiple
volumes, so eventually supporting those will be useful.

Here's format specification (warning, very boring) and libraries:

http://nifti.nimh.nih.gov/nifti-1/
http://niftilib.sourceforge.net/

There are a lot of programs for viewing these volumes, but here's a lightweight
one to try out, which will also let you inspect some of the metadata:

http://www.mccauslandcenter.sc.edu/mricro/mricron/

