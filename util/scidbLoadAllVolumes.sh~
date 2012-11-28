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
done < <(ls $dir)

dirimg= "$dir${array[1]}.nii.gz"

echo "detecting image dimensions"
header="$(${img2csv} -h ${dirimg} | tail -n 1)"
numi="$(echo ${header} | cut -d, -f1)"
numj="$(echo ${header} | cut -d, -f2)"
numk="$(echo ${header} | cut -d, -f3)"
numd="$(echo ${header} | cut -d, -f4)"
size=$((${numi}*${numj}*${numk}*${numd}))

maxi=$((${numi}-1));
maxj=$((${numj}-1));
maxk=$((${numk}-1));
maxd=$((${numd}-1));
maxidx=$((${size}-1))

echo "  numi = ${numi}"
echo "  numj = ${numj}"
echo "  numk = ${numk}"
echo "  numd = ${numd}"
echo "  size = ${size}"

echo "creating new full array (if it does not exist)"
iquery -a -q "create array ${arr} <v:double>[i(int64)=${numi},${numi},0,j(int64)=${numj},${numj},0,k(int64)=${numk},${numk},0,d(int64)=*,100,0];" &> ${log}
#!if [ $? -ne 0 ]; then echo "an error occurred.  see log: ${log}"; exit; fi

for j in "${array[@]}"
do
	num = "echo $j| cut -d'.' -f 1"
	source "scidbLoadVolumeFromDir.sh $dir $j $arr"
done




