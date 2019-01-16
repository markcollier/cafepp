#!/usr/bin/env python

import os
import re
import socket
import sys
import inspect

input_files=output_files=None

extras={}
for arg in sys.argv[1:]:
  if(arg.split('=')[0]=='input_files'):
    input_files=arg.split('=')[1].split(',')
  elif(arg.split('=')[0]=='output_files'):
    output_files=arg.split('=')[1].split(',')
  else:
  
    kwords=arg.split('=')
    extras[kwords[0]]=kwords[1]

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

for cnt,input_file in enumerate(input_files):
  #print('cnt,input,output files: ',cnt,input_files[cnt], output_files[cnt])
  status = compress_nc(input_files[cnt], output_files[cnt], **extras)
  #raise SystemExit('STOP!:'+__file__+' line number: '+str(inspect.stack()[0][2]))

os.chdir(cwd)

exit(0)
