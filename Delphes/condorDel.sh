#!/bin/bash

Delphes="/home/dylee/tools/Delphes3.4.2/"
lhe=$1/unweighted_events.lhe
runnum=`basename $1`

cat <<EOF > config_${runnum}.cmnd
! 1) Settings used in the main program.

Main:numberOfEvents = 10000            ! number of events to generate
Main:timesAllowErrors = 3          ! how many aborts before run stops

! 2) Settings related to output in init(), next() and stat().

Init:showChangedSettings = on      ! list changed settings
Init:showChangedParticleData = off ! list changed particle data
Next:numberCount = 200             ! print message every n events
Next:numberShowInfo = 1            ! print event information n times
Next:numberShowProcess = 1         ! print process record n times
Next:numberShowEvent = 0           ! print event record n times

! 3) Set the input LHE file
Beams:frameType = 4
Beams:LHEF = $lhe
EOF

cat <<EOF > runCondorDelPy_${runnum}.sh
#!/bin/bash

export SCRAM_ARCH=slc6_amd64_gcc530
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
echo "\$VO_CMS_SW_DIR \$SCRAM_ARCH"
source \$VO_CMS_SW_DIR/cmsset_default.sh
cd /home/dylee/tools/CMSSW_9_1_0_pre3/src
eval \`scramv1 runtime -sh\`
cd -

${Delphes}DelphesPythia8 ${Delphes}cards/delphes_card_CMS.tcl config_${runnum}.cmnd DelPy_${runnum}.root
if [ ! -d condorDelPyOut ]; then mkdir condorDelPyOut; fi
mv DelPy_${runnum}.root condorDelPyOut/
EOF

chmod   +x runCondorDelPy_${runnum}.sh

cat <<EOF > job_${runnum}.jdl
executable = runCondorDelPy_${runnum}.sh
universe = vanilla
output   = condorDelPyLog/condorDelPyLog_${runnum}.log
error    = condorDelPyLog/condorDelPyLog_${runnum}.log
log      = /dev/null
should_transfer_files = yes
transfer_input_files = config_${runnum}.cmnd
when_to_transfer_output = ON_EXIT
transfer_output_files = condorDelPyOut
requirements = (machine == "node01" || machine == "node02")
arguments = \$(Cluster)
queue 1
EOF

condor_submit job_${runnum}.jdl
