#!/bin/bash

set -x

input_files='/OSM/CBR/OA_DCFP/data/CAFEPP/g/data1/v14/coupled_model/v1/OUTPUT/land_month_0500_01.nc,/OSM/CBR/OA_DCFP/data/CAFEPP/g/data1/v14/coupled_model/v1/OUTPUT/atmos_month_0500_01.nc'

output_files='./test1.nc,./test2.nc'

/OSM/CBR/OA_DCFP/work/col414/cafepp/compress_nc.py input_files=$input_files output_files=$output_files Diag=False nc_model='NETCDF4_CLASSIC' compression=1 history=True Clobber=True

exit 0
