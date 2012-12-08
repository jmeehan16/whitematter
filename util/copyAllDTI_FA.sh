#!/bin/bash

dir="/data/graphics/mri/brown3t/dan_bipolar_tap.2012.09.12/subjects/"

i=0
while read line
do
    array[ $i ]="$line"        
    (( i++ ))
done < <(ls $dir)

k=1
for j in "${array[@]}"
do
	name="${j%master}"
	#echo $name
	cp "$dir$j/fit_dti/dti_fa.nii.gz" "/home/john/workspace/InterdisciplinaryScientificVisualization/niftifiles/${name}_dti_fa.nii.gz"
done
