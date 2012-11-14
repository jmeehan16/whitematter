#! /bin/bash

if [ $# -ne "2" ]; then
    echo "Usage:"
    echo "  $(basename $0) image.{png,jpg} array_name"
    echo "Description:"
    echo "  This program imports an image into SciDB"
    exit
fi

echo "started"
img2csv="$(dirname $0)/img2csv/bin/img2csv"
img="$1"
arr="$2"

if [ ! -e ${img} ]; then
    echo "an error occurred. image not found: ${img}"
    exit
fi

id="${RANDOM}"
fifo="/tmp/scidb_import_${id}.fifo"
log="/tmp/scidb_import_${id}.txt"
packarr="${arr}_tmp_${id}"

echo "detecting image dimensions"
header="$(${img2csv} -h ${img} | tail -n 1)"
width="$(echo ${header} | cut -d, -f1)"
height="$(echo ${header} | cut -d, -f2)"
size=$((${width}*${height}))

maxi=$((${width}-1));
maxj=$((${height}-1));
maxidx=$((${size}-1))

echo "  width = ${width}"
echo "  height = ${height}"
echo "  size = ${size}"

echo "removing existing packed array if necessary"
iquery -a -q "remove(${packarr})" &> ${log}

echo "creating new packed array"
iquery -a -q "create array ${packarr} <i:uint64,j:uint64,r:uint8,g:uint8,b:uint8>[idx];" &> ${log}

echo "creating fifo pipe"
mkfifo ${fifo}

echo "piping image to scidb fifo"
${img2csv} ${img} | csv2scidb -s 1 -p NNNNN > ${fifo} &

echo "loading data to packed array from fifo"
iquery -a -q "set no fetch; load(${packarr},'${fifo}');" &> ${log}
if [ $? -ne 0 ]; then rm ${fifo}; echo "an error occurred.  see log: ${log}"; exit; fi

echo "removing scidb fifo pipe"
rm ${fifo}

echo "removing existing array"
iquery -a -q "remove($arr)" &> ${log}

echo "creating new array"
iquery -a -q "create array ${arr} <r:uint8,g:uint8,b:uint8>[i=0:${maxi},${width},0,j=0:${maxj},${height},0];" &> ${log}
if [ $? -ne 0 ]; then echo "an error occurred.  see log: ${log}"; exit; fi

echo "mapping packed array"
iquery -a -q "set no fetch; redimension_store(${packarr},${arr});" &> ${log}
if [ $? -ne 0 ]; then echo "an error occurred.  see log: ${log}"; exit; fi

echo "removing packed array"
iquery -a -q "remove(${packarr})" &> ${log}
if [ $? -ne 0 ]; then echo "an error occurred.  see log: ${log}"; exit; fi

echo "finished"
