#!bin/bash

for process in /home/dylee/workspace/BKG/MG/*
do
for procname in /home/dylee/workspace/BKG/MG/`basename $process`/*
do

cd $procname

for runnum in /home/dylee/workspace/BKG/MG/`basename $process`/`basename $procname`/Events/*
do
	#source ~/workspace/BKG/Delphes/condorDel.sh $runnum
#	echo `basename $process`
#	echo `basename $procname`
#	echo  ${runnum}

for file in ${runnum}/*.lhe
do
	if [ ! -d /home/dylee/workspace/BKG/Delphes/`basename $process` ]; then mkdir /home/dylee/workspace/BKG/Delphes/`basename $process`; fi

	if [ ! -d /home/dylee/workspace/BKG/Delphes/`basename $process`/`basename $procname` ]; then mkdir /home/dylee/workspace/BKG/Delphes/`basename $process`/`basename $procname`; fi

	cp ${file} /home/dylee/workspace/BKG/Delphes/`basename $process`/`basename $procname`/`basename $process`_`basename $procname`_`basename $runnum`.lhe

done	
done
done
done

cd /home/dylee/workspace/BKG/Delphes
