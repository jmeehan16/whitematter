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

dirimg="$dir${array[0]}"
echo "$dirimg"

echo "detecting image dimensions"
header="$(${img2csv} -h ${dirimg} | tail -n 1)"
numi="$(echo ${header} | cut -d, -f1)"
numj="$(echo ${header} | cut -d, -f2)"
numk="$(echo ${header} | cut -d, -f3)"
numd=$i
size=$((${numi}*${numj}*${numk}))
log="/tmp/scidb_import_full.txt"

maxi=$((${numi}-1));
maxj=$((${numj}-1));
maxk=$((${numk}-1));
maxd=$((${numd}-1));
maxidx=$((${size}-1));

echo "  numi = ${numi}"
echo "  numj = ${numj}"
echo "  numk = ${numk}"
echo "  numd = ${numd}"
echo "  size = ${size}"

echo "removing existing array (if it exists)"
iquery -a -q "remove(${arr})" &> ${log}

echo "creating new full array"
iquery -a -q "create array ${arr} <v:double>[d=0:${maxd},1,0,i=0:${maxi},10,0,j=0:${maxj},10,0,k=0:${maxk},10,0];" &> ${log}
if [ $? -ne 0 ]; then echo "an error occurred.  see log: ${log}"; exit; fi

for j in "${array[@]}"
do
	echo "started"
	img="$j"
	#img="${num}.nii.gz"
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

	#id="${RANDOM}"
	fifo="/tmp/scidb_import_${curd}.fifo"
	log="/tmp/scidb_import_${curd}.txt"
	packarr="${arr}_tmp_${curd}"

	maxi=$((${numi}-1));
	maxj=$((${numj}-1));
	maxk=$((${numk}-1));
	maxd=$((${numd}-1));
	maxidx=$((${size}-1))

	echo "  numi = ${numi}"
	echo "  numj = ${numj}"
	echo "  numk = ${numk}"
	echo "  curd = ${curd}"
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
	iquery -a -q "remove(vol$curd)" &> ${log}
	#!if [ $? -ne 0 ]; then echo "an error occurred.  see log: ${log}"; exit; fi

	echo "creating new array"
	iquery -a -q "create array vol${curd} <v:double>[d=0:${maxd},1,0,i=0:${maxi},10,0,j=0:${maxj},10,0,k=0:${maxk},10,0];" &> ${log}
	if [ $? -ne 0 ]; then echo "an error occurred.  see log: ${log}"; exit; fi

	echo "mapping packed array"
	iquery -a -q "set no fetch; redimension_store(${packarr},vol${curd});" &> ${log}
	if [ $? -ne 0 ]; then echo "an error occurred.  see log: ${log}"; exit; fi

	echo "removing packed array"
	iquery -a -q "remove(${packarr})" &> ${log}
	if [ $? -ne 0 ]; then echo "an error occurred.  see log: ${log}"; exit; fi
	
	echo "inserting data into full array"
	iquery -q "set no fetch; insert into $arr select * from vol$curd where d = $curd;"
	if [ $? -ne 0 ]; then echo "an error occurred.  see log: ${log}"; exit; fi

	echo "removing existing array"
	iquery -a -q "remove(vol$curd)" &> ${log}
	if [ $? -ne 0 ]; then echo "an error occurred.  see log: ${log}"; exit; fi

	echo "finished"
done




