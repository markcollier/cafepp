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

declare -a ivars=("huss")
declare -a ivars=("zg")
declare -a ivars=("hfss")
declare -a ivars=("rlut")
declare -a ivars=("sfcWind")
declare -a ivars=("hfls")
declare -a ivars=("hus")
declare -a ivars=("ua")
declare -a ivars=("va")
declare -a ivars=("wap") #doesn't exist
declare -a ivars=("uas")
declare -a ivars=("vas")
declare -a ivars=("zg700")
declare -a ivars=("hus5")
declare -a ivars=("tslsi")

declare -a ivars=("zg5")
declare -a ivars=("zg500")

declare -a ivars=("ua5")
declare -a ivars=("va5")
declare -a ivars=("tas")
declare -a ivars=("rws500")
declare -a ivars=("psl")
declare -a ivars=("pr")
declare -a ivars=("ps")
declare -a ivars=("ta")
declare -a ivars=("ta5")
declare -a ivars=("ta10")
declare -a ivars=("sos")
declare -a ivars=("thetao")
declare -a ivars=("tos")
declare -a ivars=("thetao100m")
declare -a ivars=("uo100m")
declare -a ivars=("vo")
declare -a ivars=("uo")
declare -a ivars=("so")

season="ANN"
season="JJA"
season="MAM"
season="MON"

breeding=true #process control/ensemble members of breeding forecast
breeding=false #process analysis forecast (data assimilation)

for ivar in "${ivars[@]}";do

if [ $breeding = "true" ];then
  declare -a realisations=(0 1 2 3 4 5 6 7 8 9 10)
else
  declare -a realisations=(0)
fi

experiment="da"
export CAFE_EXPERIMENT=$experiment

julian=false #noleap
julian=true

#realisation=0
for realisation in "${realisations[@]}";do

#let irealisation=$realisation
#if [ $irealisation -eq 2 ];then
# echo "hello"
#fi
#exit

let ybeg_now=2004 #2002
let yend_now=2004 #2016
let yend_now=2015 #2016
let yend_now=2014 #2016
let yend_now=2004 #2016

if [ $breeding = "true" ];then
  let mbeg_now=2
  let mend_now=6
else
  let mbeg_now=3 #1
  let mbeg_now=1
  let mend_now=6
  let mend_now=3 #6
  let mend_now=12 #6
fi

if [ $breeding = "true" ];then

let mval=$realisation+1

idir="/g/data1/v14/dpm599/ao_am2/breeding/da/twostep_carbon/MEMBERS/m."$mval"/OUTPUT"

else #breeding

if [ $ivar = "tauu" ] || [ $ivar = "newtry" ];then
  idir="/g/data1/v14/coupled_da/workdir2/OUTPUT-2step-nobreeding-carbon"
else
  idir="/g/data1/v14/tok599/coupled_da/workdir2/OUTPUT-2step-nobreeding-carbon"
  idir="/g/data1/v14/tok599/coupled_da/workdir2/OUTPUT-2step-nobreeding"
fi

fi #breeding

#echo "ybeg,yend,mbeg,mend,dbeg,dend=$ybeg_now $yend_now $mbeg_now $mend_now"

#-x #noclobber
#--vertical_interpolation_method='linear'

#/g/data1/v14/tok599/coupled_da/workdir2/OUTPUT-2step-nobreeding-carbon/20020101/...

levs=""
#levs="gn5"

#-l stdoutF.txt

./cafepp.py -i 5 --version v20170804 --initialisation=1 --realisation=$realisation --physics=1 --forcings=1 -v $ivar --ybeg=$ybeg_now --yend=$yend_now --ybeg_min=$ybeg_now --yend_max=$yend_now --mbeg=$mbeg_now --mend=$mend_now --mbeg_min=$mbeg_now --mend_max=$mend_now --idir=$idir --season=$season --levs=$levs --cmorlogfile=cmor_log.txt -F -l stdout.txt

#--new_ovars="rws,div,eta,uchi,vchi" --new_units="s-2,s-1,s-1,ms-1,ms-1"

exit

done #realisation
done #ivar

echo "Complete."

set +x

#end
