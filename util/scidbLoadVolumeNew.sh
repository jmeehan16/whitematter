#! /bin/bash

if [ $# -ne "2" ]; then
    echo "Usage:"
    echo "  $(basename $0) image.{png,jpg} array_name"
    echo "Description:"
    echo "  This program imports an image into SciDB"
    exit
fi

echo "started"
img2csv="$(dirname $0)/../img2csv/dist/bin/img2csv"
dir="$1"
img="$2"
dirimg="$dir${img}"
name="$(echo $img |cut -d. -f1)"

if [ ! -e ${dirimg} ]; then
    	echo "an error occurred. image not found: ${img}"
exit
fi

echo "detecting image dimensions"
header="$(${img2csv} -h ${dirimg} | tail -n 1)"
numi="$(echo ${header} | cut -d, -f1)"
numj="$(echo ${header} | cut -d, -f2)"
numk="$(echo ${header} | cut -d, -f3)"
numd="$(echo ${header} | cut -d, -f4)"
size=$((${numi}*${numj}*${numk}*${numd}))

#id="${RANDOM}"
fifo="/tmp/scidb_import_${name}.fifo"
log="/tmp/scidb_import_${name}.txt"
packarr="${arr}_tmp_${name}"

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

echo "removing existing packed array if necessary"
iquery -a -q "remove(${packarr})" &> ${log}
	
echo "creating new packed array"
iquery -a -q "create array ${packarr} <i:int64,j:int64,k:int64,d:int64,v:double>[idx];" &> ${log}
if [ $? -ne 0 ]; then echo "an error occurred.  see log: ${log}"; exit; fi

echo "creating fifo pipe"
mkfifo ${fifo}

echo "piping image to scidb fifo"
${img2csv} ${dirimg} | csv2scidb -s 1 -p NNNNN > ${fifo} &

echo "loading data to packed array from fifo"
iquery -a -q "set no fetch; load(${packarr},'${fifo}');" &> ${log}
if [ $? -ne 0 ]; then rm ${fifo}; echo "an error occurred.  see log: ${log}"; exit; fi

echo "removing scidb fifo pipe"
rm ${fifo}

echo "removing existing array"
iquery -a -q "remove(${name})" &> ${log}
#!if [ $? -ne 0 ]; then echo "an error occurred.  see log: ${log}"; exit; fi

echo "creating new array"
iquery -a -q "create array ${name} <v:double>[i=0:${maxi},${numi},0,j=0:${maxj},${numj},0,k=0:${maxk},${numk},0,d=0:${maxd},1,0];" &> ${log}
if [ $? -ne 0 ]; then echo "an error occurred.  see log: ${log}"; exit; fi

echo "mapping packed array"
iquery -a -q "set no fetch; redimension_store(${packarr},${name});" &> ${log}
if [ $? -ne 0 ]; then echo "an error occurred.  see log: ${log}"; exit; fi

echo "removing packed array"
iquery -a -q "remove(${packarr})" &> ${log}
if [ $? -ne 0 ]; then echo "an error occurred.  see log: ${log}"; exit; fi

echo "adding array to MySQL"
python ../scidb-view/wsgi/createSlices.py ${name}
if [ $? -ne 0 ]; then echo "an error occurred.  see log: ${log}"; exit; fi

echo "finished"
