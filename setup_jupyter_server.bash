#!/bin/bash

#cd ~mac599/decadal/paper_analysis

hostname=`hostname`

echo hostname=$hostname

nslookup $hostname

let record=`nslookup $hostname | wc -l`
let record=$record-1

#echo $record
#exit

value=`nslookup $hostname | awk -v record=$record '{if ( $1=="Address:" && NR==record )print$2}'`

echo "Running server, use web address:"
echo "https://$value:9990/"

#exit

. /short/v14/mac599/anaconda3/etc/profile.d/conda.sh

conda activate cafepp_27_scipy

#put & at end if want put in background:
jupyter notebook --certfile=mycert.pem --keyfile=mykey.key
