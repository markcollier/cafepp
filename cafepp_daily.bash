#!/bin/bash

set -x

#./cafepp_daily.py -x -i 5 --version v20170609 --initialisation=1 --realisation=1 --physics=1 --forcings=1 -v tos --ybeg=2002 --yend=2003 --ybeg_min=2002 --yend_max=2003 --mbeg=12 --mend=1 --mbeg_min=12 --mend_max=1 --dbeg=1 --dend=15 --dbeg_min=1 --dend_max=15 --idir=/g/data1/v14/tok599/coupled_da/workdir2/OUTPUT-2step-nobreeding-carbon/20021201
#exit

#/g/data1/v14/tok599/coupled_da/workdir2/OUTPUT-2step-nobreeding-carbon/20020101/
#
#dirs:
#20020101 - 20160601
#
#20020101: daily 20020101 - 20020215
#20020201: daily 20020201 - 20020315
#20020301: daily 20020301 - 20020415
#
#...
#
#20160401: daily 20160401 - 20160515
#20160501: daily 20160501 - 20160615
#20160601: daily 20160601 - 20160715

#echo ${days_in_month[2]}
#exit

#let l=33
#printf "%02d\n" $l
#exit

let cnt_max=200 #some large number to cope with all input directories.

#declare -a ivars=("huss")
#declare -a ivars=("zg")
#declare -a ivars=("hfss")
#declare -a ivars=("rlut")
#declare -a ivars=("hfls")
#declare -a ivars=("hus")
#declare -a ivars=("ua")
#declare -a ivars=("va")
#declare -a ivars=("wap") #doesn't exist
#declare -a ivars=("ta")
#declare -a ivars=("vas")
#declare -a ivars=("zg700")
#declare -a ivars=("hus5")
#declare -a ivars=("tslsi")
#declare -a ivars=("zg5")
#declare -a ivars=("ta5")
#declare -a ivars=("ua5")
#declare -a ivars=("va5")
#declare -a ivars=("tos")
#declare -a ivars=("tas")
#declare -a ivars=("zg500")
#declare -a ivars=("psl")
#declare -a ivars=("uas")
#declare -a ivars=("sfcWind")
#declare -a ivars=("tauu") #wind stress in atmos realm for daily.
#declare -a ivars=("tauv") #wind stress in atmos realm for daily.
#declare -a ivars=("nino34")
#declare -a ivars=("pr")
#declare -a ivars=("rws5")

#for ivar in "${ivars[@]}";do

declare -a realisations=(0 1 2 3 4 5 6 7 8 9 10)

#let lastR="${realisations[-1]}"
#echo ${realisations[${#realisation[@]}-1]} #old bash
#echo ${realisations[@]: -1} #works
#exit

experiment="da"
export CAFE_EXPERIMENT=$experiment

julian=false #noleap
julian=true

breeding=true #process control/ensemble members of breeding forecast
breeding=false #process analysis forecast (data assimilation)

#realisation=0
for realisation in "${realisations[@]}";do

#let irealisation=$realisation
#if [ $irealisation -eq 2 ];then
# echo "hello"
#fi
#exit

y_final=2016 #normally 2016
m_final=6 #normally 6

#y_final=2002
#m_final=12

let ybeg_initial=2004 #normally 2002
let yend_initial=2004 #normally 2002

if [ $((ybeg_initial % 4)) -eq 0 ];then
  days_in_month=(31 29 31 30 31 30 31 31 30 31 30 31)
else
  days_in_month=(31 28 31 30 31 30 31 31 30 31 30 31)
fi
#exit

let dbeg_initial=1

if [ $breeding = "true" ];then
  let mbeg_initial=2
  let mend_initial=2
  let dend_initial=${days_in_month[$mbeg_initial-1]}
else
  let mbeg_initial=1
  let mend_initial=2
  let dend_initial=15
fi

#exit

let ybeg_now=$ybeg_initial
let yend_now=$yend_initial

let mbeg_now=$mbeg_initial
let mend_now=$mend_initial

let dbeg_now=$dbeg_initial
let dend_now=$dend_initial

let cnt=0
while [ $cnt -le $cnt_max ];do

end_directory=$ybeg_now$(printf "%02d\n" $mbeg_now)$(printf "%02d\n" $dbeg_now)

#echo $end_directory
#exit

if [ $breeding = "true" ];then

let mval=$realisation+1

  idir="/g/data1/v14/dpm599/ao_am2/breeding/da/twostep_carbon/MEMBERS/m."$mval"/OUTPUT/"$end_directory

else #breeding

if [ $ivar = "xxx" ] || [ $ivar = "newtry" ];then
  idir="/g/data1/v14/coupled_da/workdir2/OUTPUT-2step-nobreeding-carbon/"$end_directory
else
  idir="/g/data1/v14/tok599/coupled_da/workdir2/OUTPUT-2step-nobreeding-carbon/"$end_directory
  idir="/g/data1/v14/tok599/coupled_da/workdir2/OUTPUT-2step-nobreeding/"$end_directory #use this directory as other one has been moved...
fi

fi #breeding

#echo "ybeg,yend,mbeg,mend,dbeg,dend=$ybeg_now $yend_now $mbeg_now $mend_now $dbeg_now $dend_now"

#-x #noclobber
#--vertical_interpolation_method='linear'

#./cafepp_daily.py -i 5 --version v20170804 --initialisation=1 --realisation=$realisation --physics=1 --forcings=1 -v $ivar --ybeg=$ybeg_now --yend=$yend_now --ybeg_min=$ybeg_now --yend_max=$yend_now --mbeg=$mbeg_now --mend=$mend_now --mbeg_min=$mbeg_now --mend_max=$mend_now --dbeg=$dbeg_now --dend=$dend_now --dbeg_min=$dbeg_now --dend_max=$dend_now --idir=$idir --cmorlogfile=cmor_log.txt -l stdout.txt --new_ovars="rws5,div5,eta5,uchi5,vchi5" --new_units="s-2,s-1,s-1,ms-1,ms-1"

./cafepp_daily.py cafepp_daily.json

# --new_ovars="rws5,div5,eta5,uchi5,vchi5" --new_units="s-2,s-1,s-1,ms-1,ms-1" #can be used with rws5

exit

#if [ $cnt -eq 2 ];then
#  exit
#fi

if [ $ybeg_now -eq $y_final ] && [ $mbeg_now -eq $m_final ];then

if [ $realisation -eq ${realisations[@]: -1} ];then
 echo "Complete."
 exit
else
 break #go to next realisation
fi

fi

let mbeg_now=$mbeg_now+1
let mend_now=$mend_now+1

let mbeg_nowm1=$mbeg_now-1
let mend_nowm1=$mend_now-1

if [ $mbeg_now -gt 12 ];then
 let mbeg_now=1
 let ybeg_now=$ybeg_now+1
fi

if [ $mend_now -gt 12 ];then
 let mend_now=1
 let yend_now=$yend_now+1
fi

if [ $((ybeg_now % 4)) -eq 0 ];then
  days_in_month=(31 29 31 30 31 30 31 31 30 31 30 31)
else
  days_in_month=(31 28 31 30 31 30 31 31 30 31 30 31)
fi

if [ $breeding = "true" ];then
  let dbeg_now=1
  let dend_now=${days_in_month[$mbeg_now-1]}
fi

let cnt=$cnt+1
done #cnt
done #realisation
#done #ivar

set +x

#end
