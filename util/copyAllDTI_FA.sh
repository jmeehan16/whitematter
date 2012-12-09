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
	cp "$dir$j/fit_dti/dti_fa.nii.gz" "/home/john/workspace/InterdisciplinaryScientificVisualization/niftifiles/${name}-fit_dti_dti_fa.nii.gz"
	cp "$dir$j/init/dwi.nii.gz" "/home/john/workspace/InterdisciplinaryScientificVisualization/niftifiles/${name}-init_dwi.nii.gz"
	cp "$dir$j/fs/brain.nii.gz" "/home/john/workspace/InterdisciplinaryScientificVisualization/niftifiles/${name}-fs_brain.nii.gz"
	cp "$dir$j/reg_fs/fs2diff.nii.gz" "/home/john/workspace/InterdisciplinaryScientificVisualization/niftifiles/${name}-reg_fs_fs2diff.nii.gz"
	cp "$dir$j/reg_fs/aparc+aseg.nii.gz" "/home/john/workspace/InterdisciplinaryScientificVisualization/niftifiles/${name}-reg_fs_aparcaseg.nii.gz"

done
