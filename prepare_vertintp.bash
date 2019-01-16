#!/bin/bash

set -x

./prepare_vertintp.py -c --input_files /OSM/CBR/OA_DCFP/work/col414/CAFEPP/short/v19/mac599/ao_am2/oct18a/OUTPUT/atmos_month_1980_01.nc,/OSM/CBR/OA_DCFP/work/col414/CAFEPP/short/v19/mac599/ao_am2/oct18a/OUTPUT/atmos_daily_1980_01_01.nc -r /OSM/CBR/OA_DCFP/work/col414/cafepp --levels 100,500,1000,2000,3000,5000,7000,10000,15000,20000,25000,30000,40000,50000,60000,70000,85000,92500,100000

exit 0
