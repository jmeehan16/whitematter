#! /bin/bash

if [ $# -ne "1" ]; then
    echo "Usage:"
    echo "  $(basename $0) dirname image{.nii.gz} array_name"
    echo "Description:"
    echo "  This program imports an image into SciDB"
    exit
fi

echo "started"
img2csv="$(dirname $0)/img2csv/bin/img2csv"
dir="$1"
dirimg="${dir}${img}"

if [ ! -e ${dirimg} ]; then
    echo "an error occurred. image not found: ${img}"
    exit
fi

echo "detecting image dimensions"
header="$(${img2csv} -h ${dirimg} | tail -n 1)"
numi="$(echo ${header} | cut -d, -f1)"
numj="$(echo ${header} | cut -d, -f2)"
numk="$(echo ${header} | cut -d, -f3)"
curd="$(echo ${header} | cut -d, -f4)"
size=$((${numi}*${numj}*${numk}))
