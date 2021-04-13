#!/bin/bash

StartTime=$(date +%s)

source ttbar.sh 2>&1 | tee ttbar.log
#source WG.sh 2>&1 | tee WG.log
#source WW.sh 2>&1 | tee WW.log
#source WWW.sh 2>&1 | tee WWW.log
#source WWZ.sh 2>&1 | tee WWZ.log
#source WZ.sh 2>&1 | tee WZ.log
#source WZZ.sh 2>&1 | tee WZZ.log
#source ZG.sh 2>&1 | tee ZG.log
#source ZZ.sh 2>&1 | tee ZZ.log
#source ZZZ.sh 2>&1 | tee ZZZ.log

EndTime=$(date +%s)

echo "$(($EndTime - $StartTime))"
