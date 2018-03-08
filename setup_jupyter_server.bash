#cd ~mac599/decadal/paper_analysis

hostname=hostname

value=`nslookup $hostname | awk '{if ( $1=="Address:" && NR==5 )print$2}'`

echo "Running server, use web address:"
echo "https://$value:9990/"

. /short/v14/mac599/anaconda3/etc/profile.d/conda.sh

conda activate cafepp_27_scipy

jupyter notebook --certfile=mycert.pem --keyfile mykey.key
