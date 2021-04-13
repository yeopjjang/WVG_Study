#!bin/bash

for dir in $(ls -ld $PWD/testfile | grep "^d" | awk '{print $9}') ;do

	for subdir in $(ls -ld $dir/* | grep "^d" | awk '{print $9}') ;do
		ls -d $subdir/*.lhe > `basename $dir`_`basename $subdir`.list
		source testmore.sh `basename $dir`_`basename $subdir`.list
		echo "done"
		break
	done
	break
done

