#!/bin/bash

#'salt' #ocean
#'eta_t' #ocean
#'olr' #atmos
#'vcomp' #atmos
#'ucomp' #atmos
#'precip' #atmos
#'tx_trans_int_z' #ocean
#'acc_africa' #ocean diagnostic
#'mozmbq' #ocean diagnostic
#'aabw' #ocean diagnostic
#'nadw' #ocean diagnostic
#'o2' #ocean_bgc
#'pp' #ocean_bgc diagnostic
#'nino34' #ocean diagnostic
#'ssh' #ocean diagnostic
#'moc' #ocean diagnostic
#'moc_pacific' #ocean diagnostic
#'moc_indian' #ocean diagnostic
#'moc_atlantic' #ocean diagnostic
#'shice_cover' #ice diagnostic
#'nhice_cover' #ice diagnostic
#'temp' #ocean
#'acc_drake' #ocean diagnostic

#declare -a ivars=("temp" "acc_drake")

#declare -a ivars=("acc_drake")

declare -a ivars=("ps")
declare -a ivars=("psl")
declare -a ivars=("salttotal")
declare -a ivars=("temptotal")
declare -a ivars=("sos")
declare -a ivars=("divg")
declare -a ivars=("vort")
declare -a ivars=("pv")
declare -a ivars=("mlotstsq")
declare -a ivars=("mlotst")
declare -a ivars=("vmo")
declare -a ivars=("umo")
declare -a ivars=("areacello")
declare -a ivars=("cl")
declare -a ivars=("thkcello")
declare -a ivars=("volcello")
declare -a ivars=("sftof")
declare -a ivars=("deptho")
declare -a ivars=("salt")
declare -a ivars=("msftyyz")
declare -a ivars=("mfo")
declare -a ivars=("so")
declare -a ivars=("rws500")
declare -a ivars=("rws")
declare -a ivars=("nhblocking")
declare -a ivars=("nhbi")
declare -a ivars=("nino34")
declare -a ivars=("iod")
declare -a ivars=("sam")
declare -a ivars=("zg500")
declare -a ivars=("tos")
declare -a ivars=("pp")
declare -a ivars=("nflux")
declare -a ivars=("ep")
declare -a ivars=("hur") #no raw input yet.
declare -a ivars=("hur10") #no raw input yet

declare -a ivars=("zg10")
declare -a ivars=("ua")
declare -a ivars=("ua10")
declare -a ivars=("va10")
declare -a ivars=("va")
declare -a ivars=("hus10")
declare -a ivars=("hus")
declare -a ivars=("ta")
declare -a ivars=("ta10")
declare -a ivars=("ta19")
declare -a ivars=("thetao")
declare -a ivars=("isothetao20c")
declare -a ivars=("zg")
declare -a ivars=("tauv")
declare -a ivars=("tauu")

#cbeg=451
#cend=500
#cbeg=1
#cend=500


for ivar in "${ivars[@]}"
do

levs=""
if [ $ivar = "thetaoX" ];then
levs="gn1"
levs="gn3"
elif [ $ivar = "salt" ];then
levs="gn2"
elif [ $ivar = "ta10" ] || [ $ivar = "ua10" ] || [ $ivar = "va10" ] || [ $ivar = "hur10" ] || [ $ivar = "hus10" ] || [ $ivar = "zg10" ];then
levs="gn10"
elif [ $ivar = "ta19" ] || [ $ivar = "ua19" ] || [ $ivar = "va19" ] || [ $ivar = "hur19" ] || [ $ivar = "hus19" ] || [ $ivar = "zg19" ];then
levs="gn19"
fi

#if [ $ivar = "temp" ];then
#levs="0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29"
#levs="0"
#elif [ $ivar = "salt" ];then
#levs="0,1,2"
#elif [ $ivar = "ucomp" ];then
#levs="6,9,15"
#elif [ $ivar = "hght" ];then
#levs="8,10,17"
#else
#levs=""
#fi

#declare -a arr=$(echo $levs | tr "," "\n")

#num=0
#for i in ${arr[@]}; do
##echo $i
#let num=$num+1
#done

#echo $num

set -x

experiment='v0'
experiment='v1'
experiment='v2'

if [ $experiment == 'v0' ];then
idir='/g/data1/v14/coupled_model/v0/OUTPUT'
ybeg_min=295
yend_max=625
export CCFS_EXPERIMENT=v0
elif [ $experiment == 'v1' ];then
idir='/g/data1/v14/coupled_model/v1/OUTPUT'
ybeg_min=1
yend_max=502
yend=100
ybeg=1
yend=5
yend=500
yend=2
export CCFS_EXPERIMENT=v1
elif [ $experiment == 'v2' ];then
idir='/short/v14/lxs599/coupled_model/feb17a/OUTPUT'
idir='/short/r67/mac599/coupled_model/feb17a/OUTPUT'
ybeg_min=1
yend_max=286
yend_max=500
yend=157
yend=150
yend=5
yend=$yend_max
yend=200
yend=1
yend=50
yend=10
yend=285
yend=100
ybeg=1
yend=2
ybeg=400
yend=401
yend=400
export CCFS_EXPERIMENT=v2
else
echo 'problem.'
exit
fi
#odir='/short/v14/mac599/coupled_model/'+experiment
idirc=$idir
idirc=$odir
tdir='/short/v14/mac599'

season='DecJan'
season='JJA'
season='DJF'
season='MON'
season='ANN'

#levs='A'
#levs='B'
#levs='C'

./cafepp.py -w -i5 -v $ivar --ybeg=$ybeg --yend=$yend --ybeg_min=$ybeg_min --yend_max=$yend_max --idir=$idir --season=$season --levs=$levs

#--vertical_interpolation_method='linear'

#if [ $num -gt 0 ];then
#if [ $levs != "" ];then
#-C
#-A
#./diag_spinup_monthly.py -w -i5 --ens=1 -v $ivar --ybeg=$ybeg --yend=$yend --ybeg_min=$ybeg_min --yend_max=$yend_max --idir=$idir --season=$season --levs=$levs
#else
#./diag_spinup_monthly.py -w -i5 --ens=1 -v $ivar --ybeg=$ybeg --yend=$yend --ybeg_min=$ybeg_min --yend_max=$yend_max --idir=$idir --season=$season
#fi

set +x

done

#end
