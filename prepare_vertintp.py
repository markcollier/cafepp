#!/usr/bin/env python

import os
import re
import socket
import sys
import inspect
import numpy as np
import netCDF4
import inspect
import timeit
import datetime
import getopt

input_files=rundir=input_grid=levels=None
compress=False

help='prepare_vertintp -i input_files -r rundir -c compression -g grid_file -l pressure_levels (Pa).\nNote that input_files & pressure_levels must be comma separated list without space.'

try:
  opts, args = getopt.getopt(sys.argv[1:],'hi:r:cg:l:',['input_files=','rundir=','input_grid=','levels='])
except getopt.GetoptError:
  print(help)
  sys.exit(2)
for opt, arg in opts:
  if(opt=='-h'):
    print(help)
    exit()
  elif(opt in ('-i','--input_files')):
    input_files=arg.split(',')
  elif(opt in ('-r','--rundir')):
    rundir=arg
  elif(opt=='-c'):
    compress=True
  elif(opt in ('-g','--input_grid')):
    rundir=arg
  elif(opt in ('-l','--levels')):
    levels=arg.split(',')
#    print('arg=',arg)
#    levels_test=arg.split(' ')
#    print(len(levels_test))
#print('levels=',levels)
#raise SystemExit('STOP!:'+__file__+' line number: '+str(inspect.stack()[0][2]))

if(type(input_files)==type(None)):
  raise SystemExit('Missing input files '+input_file+':'+__file__+' line number: '+str(inspect.stack()[0][2]))

if(type(rundir)==type(None)):
  raise SystemExit('Missing rundir '+input_file+':'+__file__+' line number: '+str(inspect.stack()[0][2]))

if(type(input_grid)==type(None)):
  input_grid='/OSM/CBR/OA_DCFP/work/squ027/squire_scratch/projects/cafe_hybrid_to_isobaric/shared/cafe_grid_info.nc'

if(type(levels)==type(None)):
  levels = [100, 500, 1000, 2000, 3000, 5000, 7000, 10000, 15000, 20000, 25000, \
 30000, 40000, 50000, 60000, 70000, 85000, 92500, 100000] #cmip6 19 standard pressure levels

#levels = [20000, 30000, 40000, 45000, 50000, 55000, 60000, 70000, 85000, 100000]

prepare_vertintp_extras={'Diag':'False', 'nc_model':'NETCDF4_CLASSIC', 'compression':1, 'history':'True', 'Clobber':'True'} #these are option=argument's to send to function compress_nc

compress_nc_extras={'Diag':'False', 'nc_model':'NETCDF4_CLASSIC', 'compression':1, 'history':'True', 'Clobber':'True'} #these are option=argument's to send to function compress_nc

cwd=os.getcwd()

hostname=socket.gethostname()

if(re.match('raijin',hostname)):
  print('this is rajin')
  os.chdir('/home/599/mac599/decadal')
elif(re.match('oa-3.-cdc',hostname)):
  print('this is vm3.')
  os.chdir('/OSM/CBR/OA_DCFP/work/col414/cafepp')

from decadal_diag import \
	convert_bytes, \
	file_size, \
	compress_nc, \
	prepare_vertintp, \
        get_exitcode_stdout_stderr

os.chdir(rundir)

for cnt,input_file in enumerate(input_files):

  print('Input file: '+input_file)

  if(not os.path.exists(input_file)):
    raise SystemExit('Missing input file '+input_file+':'+__file__+' line number: '+str(inspect.stack()[0][2]))

  prep_file=rundir+'/'+input_file.split('/')[-1].split('.nc')[0]+'.prep.nc'
  prep_file_nc3=rundir+'/'+input_file.split('/')[-1].split('.nc')[0]+'.prepnc3.nc'
  interp_file=rundir+'/'+input_file.split('/')[-1].split('.nc')[0]+'.plev.nc'
  output_file=rundir+'/'+input_file.split('/')[-1].split('.nc')[0]+'.plevz.nc'

  if(compress):
    delete_files=[prep_file, prep_file_nc3, interp_file]
    print('Output file: '+output_file)
  else:
    delete_files=[prep_file, prep_file_nc3]
    print('Output file: '+interp_file)

  status = prepare_vertintp(input_file, input_grid, prep_file, **prepare_vertintp_extras)

  command = 'nccopy -6 '+prep_file+' '+prep_file_nc3

  status, out, err = get_exitcode_stdout_stderr(command)

  if(status!=0):
    raise SystemExit('nccopy return status:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  if(os.path.exists(interp_file)):
    os.remove(interp_file)

          #' -t 1,10,3' + \
  command='/OSM/CBR/OA_DCFP/work/col414/cafepp/plevel_col414.bash ' + \
          ' -a' + \
          ' -i '+prep_file_nc3 + \
          ' -o '+interp_file + \
          ' -p "' + ' '.join(map(str, levels)) + '"' + \
        ' hght'

  status, out, err = get_exitcode_stdout_stderr(command)

  if(status!=0):
    raise SystemExit('plevel_col414.bash return status:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  if(compress):
    status = compress_nc(interp_file, output_file, **compress_nc_extras)

    if(status!=0):
      raise SystemExit('compress_nc non-zero return status:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  for delete_file in delete_files:
    if(os.path.exists(delete_file)):
      os.remove(delete_file)

os.chdir(cwd)

exit(0)
