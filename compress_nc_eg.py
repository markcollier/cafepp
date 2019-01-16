#!/usr/bin/env python

import os
import re
import socket
import sys
import inspect

input_files=['/OSM/CBR/OA_DCFP/data/CAFEPP/g/data1/v14/coupled_model/v1/OUTPUT/land_month_0500_01.nc', '/OSM/CBR/OA_DCFP/data/CAFEPP/g/data1/v14/coupled_model/v1/OUTPUT/atmos_month_0500_01.nc']

output_files=['./test1.nc','./test2.nc']

extras={'Diag':'False', 'nc_model':'NETCDF4_CLASSIC', 'compression':1, 'history':'True', 'Clobber':'True'} #these are option=argument's to send to function compress_nc

if(type(input_files)==type(None) or type(output_files)==type(None)):
  raise SystemExit('set input_files and output_files:'+__file__+' line number: '+str(inspect.stack()[0][2]))

if(len(input_files)!=len(output_files)):
  raise SystemExit('length of input_files and output_files different:'+__file__+' line number: '+str(inspect.stack()[0][2]))

cwd=os.getcwd()

hostname=socket.gethostname()

if(re.match('raijin',hostname)):
  print('this is rajin')
  os.chdir('/OSM/CBR/OA_DCFP/work/col414/cafepp')
elif(re.match('oa-3.-cdc',hostname)):
  print('this is vm3.')
  os.chdir('/OSM/CBR/OA_DCFP/work/col414/cafepp')

from decadal_diag import \
	convert_bytes, \
	file_size, \
	compress_nc

import numpy as np
import netCDF4
import inspect
import timeit
import datetime

#print(type(extras))
#print(extras)
#raise SystemExit('STOP!:'+__file__+' line number: '+str(inspect.stack()[0][2]))

for cnt,input_file in enumerate(input_files):
  #print('cnt,input,output files: ',cnt,input_files[cnt], output_files[cnt])
  status = compress_nc(input_files[cnt], output_files[cnt], **extras)
  #raise SystemExit('STOP!:'+__file__+' line number: '+str(inspect.stack()[0][2]))

os.chdir(cwd)

exit(0)
