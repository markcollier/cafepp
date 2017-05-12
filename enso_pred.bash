#!/bin/bash

#declare -a ivars=("tos")
#declare -a ivars=("isothetao16c")
#declare -a ivars=("isothetao20c")
declare -a ivars=("isothetao22c")
#declare -a ivars=("tauu")

for ivar in "${ivars[@]}"
do

levs=""

set -x

season='ANN'
season='MON'

experiment='v1'
export CCFS_EXPERIMENT=$experiment

if [ $ivar = "tauu" ];then
  idir='/short/r67/mac599/coupled_model/v1/OUTPUT'
else
  idir='/g/data1/v14/coupled_model/v1/OUTPUT'
fi

ybeg=310
yend=330

ybeg=301
yend=400
#yend=301 #temporary

./cafepp.py --version v20170501 -w -i5 --initialisation=0 --realisation=0 -v $ivar --ybeg=$ybeg --yend=$yend --ybeg_min=$ybeg --yend_max=$yend --idir=$idir --season=$season --levs=$levs

exit

experiment='p0'
export CCFS_EXPERIMENT=$experiment

ybeg_min=0
yend_max=9999

#ybeg=315
#yend=329

idirc=$idir
idirc=$odir
tdir='/short/v14/mac599'

init_beg_min=315
init_end_max=319

init_beg=316 #temporary
init_beg=315
init_end=319

ens_beg=8 #temporary
ens_beg=1
ens_end=10

init_now=$init_beg
let ybeg=$init_beg

while [ $init_now -le $init_end ];do

if [ $init_now -eq 316 ] && [ $ens_beg -eq 8 ];then
  let yend=ybeg+7
  #exit
elif [ $init_now -eq $init_beg_min ];then
  let yend=ybeg+14
else
  let yend=ybeg+8
fi

  ens_now=$ens_beg
  while [ $ens_now -le $ens_end ];do

  #let init=$ens_now-$ens_beg+1

if [ $ivar = "tauu" ];then
  idir='/short/r67/mac599/coupled_model/mar17a/OUTPUT/yr'$init_now'/OUTPUT.'$ens_now
else
  idir='/short/v14/lxs599/coupled_model/mar17a/OUTPUT/yr'$init_now'/OUTPUT.'$ens_now
fi

  let init_here=$init_now-$init_beg_min+1

  ./cafepp.py --version v20170501 -w -i5 --initialisation=$init_here --realisation=$ens_now -v $ivar --ybeg=$ybeg --yend=$yend --ybeg_min=$ybeg_min --yend_max=$yend_max --idir=$idir --season=$season --levs=$levs

exit

  let ens_now=$ens_now+1
  done #realisation

let ybeg=$ybeg+1
let init_now=$init_now+1
done #initialisation

set +x

done #ivar

#end
