#!/bin/bash


if [ $# -ne "2" ]; then
    echo "Usage:"
    echo "  $(basename $0) dirname array_name"
    echo "Description:"
    echo "  This program imports an image into SciDB"
    exit
fi

echo "started"
img2csv="$(dirname $0)/img2csv/bin/img2csv"
dir="$1"
arr="$2"

i=0
while read line
do
    array[ $i ]="$line"        
    (( i++ ))
    echo ${array[$i]}
done < <(ls -ls)

echo ${array[1]}
