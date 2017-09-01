#!/usr/bin/env python

##!/apps/python/2.7.6/bin/python
##!/short/p66/mac599/anaconda3/bin/ipython
# Filename : cafepp_daily.py

from __future__ import print_function #this is to allow print(,file=xxx) feature

"""
CAFE Post-Processor for daily inputs/outputs
Can be modified to process higher frequency inputs/outputs
--------------------------
"""
import getpass
import numpy as np
import numpy.ma as ma
import os
from time import strftime
import netCDF4
from math import radians, cos, sin, asin, sqrt
import seawater
import sys
import getopt
import string
from decadal_diag import MustHaveAllLevs,diag_acc_drake,diag_acc_africa,diag_mozmbq,diag_aabw,diag_nadw,diag_pp,diag_nflux,diag_ep,diag_ssh,diag_moc,diag_moc_atlantic,diag_moc_pacific,diag_moc_indian,diag_shice_cover,diag_nhice_cover,diag_nino34,xtra_nino34,init_data,sum_data,avg_data,filemonth_index,data_wavg,time_avg,diag_nhblocking_index,diag_rws,finish,diag_msftyyz,make_mask3D,diag_mfo,transPort,diag_rws500,create_odirs,create_ofils,diag_iod,diag_iod,xtra_iod,vertical_interpolate,diag_isothetaoNc,calc_iso_surface,calc_isoN,grab_var_meta,diag_psl,diag_hfls
import cmor
import cdtime
from app_funcs import *
import json
import pprint
from datetime import date
import filecmp
from shutil import copyfile
import cdms2
from regrid2 import Regridder
import inspect
import socket

if(len(sys.argv)!=2):
  raise SystemExit('CAFEPP_DAILY only takes one argument, the JSON instruction file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

hostname=socket.gethostname()

print('hostname=',hostname)

#def usage(script_name):
#    """usage"""
#    print('Usage: ',script_name,' -h,help -v input_var -i importance (1-5) --ybeg=process begin year --yend=process end year --ybeg_min=min. year available --yend_max=max. year available --idir=input directory')
#
#try:
#    opts, args=getopt.getopt(sys.argv[1:], "wxdCAhv:i:rl:",["help","ybeg=","yend=","ybeg_min=","yend_max=","mbeg=","mend=","mbeg_min=","mend_max=","dbeg=","dend=","dbeg_min=","dend_max=","realisation=","initialisation=","physics=","forcings=","idir=","vertical_interpolation_method=","version=","cmorlogfile=","new_ovars=","new_units="])
#except getopt.GetoptError as err:
#    print(err,file=fh_printfile)
#    usage(os.path.realpath(__file__))
#    sys.exit(2)
#
#fh_printfile=sys.stdout
##fh_printfile=sys.stderr
#

nmy=12

printDefinedDiagnostics=False

ReGrid=False
NoClobber=False
importance=5

cafepp_defs='cafepp_csiro-gfdl.json'
cafepp_experiments='cafepp_experiments.json'
json_input_var_meta='cafepp_vars_day.json'
#json_input_instructions='cafepp.json'
json_input_instructions=sys.argv[1]
cafepp_machine='raijin.nci.org.au'

cmorlogfile='log'

#for o, a in opts:
#    #print(o,file=fh_printfile)
#    if o in ('-h', '--help'):
#        usage(os.path.realpath(__file__))
#        sys.exit()
#    elif o == '-x':
#        NoClobber=True
#    elif o == '-i':
#        importance=int(a)
#    elif o == '-l':
#         printfile=a
#         fh_printfile=open(printfile,"w")
#    elif o == '-v':
#         dvar=a
#    elif o == '--ybeg':
#        ybeg=int(a)
#    elif o == '--yend':
#        yend=int(a)
#    elif o == '--mbeg':
#        mbeg=int(a)
#    elif o == '--mend':
#        mend=int(a)
#    elif o == '--dbeg':
#        dbeg=int(a)
#    elif o == '--dend':
#        dend=int(a)
#    elif o == '--ybeg_min':
#        ybeg_min=int(a)
#    elif o == '--yend_max':
#        yend_max=int(a)
#    elif o == '--mbeg_min':
#        mbeg_min=int(a)
#    elif o == '--mend_max':
#        mend_max=int(a)
#    elif o == '--dbeg_min':
#        dbeg_min=int(a)
#    elif o == '--dend_max':
#        dend_max=int(a)
#    elif o == '--cbeg':
#        cbeg=int(a)
#    elif o == '--cend':
#        cend=int(a)
#    elif o == '--realisation':
#        #erange=[str(x) for x in a.split(',')]
#        realisation=int(a)
#    elif o == '--initialisation':
#        initialisation=int(a)
#    elif o == '--physics':
#        physics=int(a)
#    elif o == '--forcings':
#        forcings=int(a)
#    elif o == '--idir':
#        idir=a
#    elif o == '--vertical_interpolation_method':
#        vertical_interpolation_method=a
#    elif o == '-r':
#        ReGrid=True
#    elif o == '--version':
#        version=a
#    elif o == '--cmorlogfile':
#        cmorlogfile=a
#    elif o == '--new_ovars':
#        new_ovars=[str(x) for x in a.split(',')]
#    elif o == '--new_units':
#        new_units=[str(x) for x in a.split(',')]
#    else:
#        assert False, 'unhandled option'

if 'json_input_instructions' in locals():
  os.system('awk -f uncomment_json.awk JsonTemplates/'+json_input_instructions+' > '+json_input_instructions)
  print('Running cafepp from JSON instructions: '+json_input_instructions)
  json_input_instructions_fh=open(json_input_instructions).read()
  json_input_instructions_data=json.loads(json_input_instructions_fh)
  print('json_input_instructions_data=',json_input_instructions_data)
else:
  print('Running cafepp from command line input:')

if 'json_input_instructions' in locals():
  print('Summary of JSON instructions: ',json.dumps(json_input_instructions_data,indent=4,sort_keys=True))

  #print(type(json_input_instructions_data))

  top_level_keys=json_input_instructions_data.keys()

  print('Top level JSON instructions keys=',top_level_keys)
#  print(json_input_instructions_data)
  for key_now in json_input_instructions_data.iteritems():
    #print('processing key_now[0]=',key_now[0])
    key_now0=key_now[0]
    if(key_now0=='options_with_arguments'):
      list_new=(json_input_instructions_data[key_now0])
      #print('list_new=',list_new)
      #list_new2=list(list_new)
      #print('list_new2=',list_new2)
      for l in list_new: #used to be list_new2
        #print('l=',l,list_new[l])
        #eval(l)=1.0
        #eval(l)=list_new[l]
        if(l=='cafe_experiment'): cafe_experiment=str(list_new[l])
        elif(l=='info'): info=str(list_new[l])
        elif(l=='name'): name=str(list_new[l])
        elif(l=='importance'): importance=str(list_new[l])
        elif(l=='version'): version=str(list_new[l])
#        elif(l=='initialisation'): initialisation=str(list_new[l])
#        elif(l=='realisation'): realisation=str(list_new[l])
#        elif(l=='physics'): physics=str(list_new[l])
#        elif(l=='forcings'): forcings=str(list_new[l])
        elif(l=='dvar'):
          #dvar=string.join(str(list_new[l]),sep='')
          #dvar=string.join(list_new[l])
          dvar=str.split(str(list_new[l]))
          #print(dvar)
          #print(len(dvar))
          #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
        elif(l=='ybeg'): ybeg=int(list_new[l])
        elif(l=='yend'): yend=int(list_new[l])
#        elif(l=='ybeg_min'): ybeg_min=list_new[l]
#        elif(l=='yend_max'): yend_max=list_new[l]
        elif(l=='mbeg'): mbeg=int(list_new[l])
        elif(l=='mend'): mend=int(list_new[l])
#        elif(l=='mbeg_min'): mbeg_min=list_new[l]
#        elif(l=='mend_max'): mend_max=list_new[l]
#        elif(l=='idir'): idir=str(list_new[l])
#        elif(l=='season'): season=str(list_new[l])
        elif(l=='levs'): levs=str(list_new[l])
        elif(l=='cmorlogfile'): cmorlogfile=str(list_new[l])
        elif(l=='printfile'): printfile=str(list_new[l])
#        elif(l=='xxxprintfile'): None
        elif(l=='printDefinedDiagnostics'):
          if(list_new[l]=='True'): printDefinedDiagnostics=True
#        elif(l==''): grid_label=str(list_new[l])
        elif(l=='cafepp_machine'): cafepp_machine=str(list_new[l])
        else: raise SystemExit('Unknown option_with_argument,',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    elif(key_now0=='options_no_arguments'):
      list_new=(json_input_instructions_data[key_now0])
      for l in list_new: #used to be list_new2
        if(l=='name'): name=str(list_new[l])
        elif(l=='info'): info=str(list_new[l])
#        elif(l=='Forecast'): 
#          if(list_new[l]=='True'): Forecast=list_new[l]
        elif(l=='Regrid'):
          if(list_new[l]=='True'): Regrid=True
#        elif(l=='MonthlyWeights'): 
#          if(list_new[l]=='True'): MonthlyWeights=True
        elif(l=='NoClobber'): 
          if(list_new[l]=='True'): NoClobber=list_new[l]
        else: raise SystemExit('Unknown option_no_argument,',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    elif(key_now0=='defaults'):
      list_new=(json_input_instructions_data[key_now0])
      for l in list_new: #used to be list_new2
        if(l=='name'): name=str(list_new[l])
        elif(l=='info'): info=str(list_new[l])
        elif(l=='area_t'): 
          if(list_new[l]=='True'): area_t=list_new[l]
        elif(l=='area_u'): 
          if(list_new[l]=='True'): area_u=list_new[l]
        elif(l=='grid'): grid=str(list_new[l])
        elif(l=='grid_label'): grid_label=str(list_new[l])
        elif(l=='vertical_interpolation_method'): vertical_interpolation_method=str(list_new[l])
        elif(l=='frequency'): frequency=str(list_new[l])
        elif(l=='cafepp_experiments_meta'): cafepp_experiments_meta=str(list_new[l])
        elif(l=='cafepp_defs'): cafepp_defs=str(list_new[l])
        elif(l=='json_input_var_meta'): json_input_var_meta=str(list_new[l])
        else: raise SystemExit('Unknown defaults,',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    elif(key_now0=='daily_specific'):
      list_new=(json_input_instructions_data[key_now0])
      for l in list_new:
        if(l=='name'): name=str(list_new[l])
        elif(l=='dbeg'): dbeg=int(list_new[l])
        elif(l=='dend'): dend=int(list_new[l])
        else: raise SystemExit('Unknown daily_specific,',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  if 'printfile' in locals():
    fh_printfile=open(printfile,'w')
  else:
    fh_printfile=sys.stdout
  print('fh_printfile=',fh_printfile)

#print(dend)
#raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

#cafepp_experiments_meta='cafepp_experiments.json'
os.system('awk -f uncomment_json.awk JsonTemplates/'+cafepp_experiments_meta+' > '+cafepp_experiments_meta)
cafepp_experiments_fh=open(cafepp_experiments_meta).read()
print('cafepp_experiments_fh=',cafepp_experiments_fh,file=fh_printfile)
cafepp_experiments_data=json.loads(cafepp_experiments_fh)
print('cafepp_experiments_data=',cafepp_experiments_data,file=fh_printfile)

print('Summary of JSON experiments input: ',json.dumps(cafepp_experiments_data,indent=4,sort_keys=True),file=fh_printfile)

top_level_keys=cafepp_experiments_data.keys()
print('Top level JSON experiments keys=',top_level_keys,file=fh_printfile)

cafepp_experiment_found=False
for key_now in cafepp_experiments_data.iteritems():
  #print('processing key_now[0]=',key_now[0],file=fh_printfile)
  key_now0=key_now[0]
  if(key_now0==cafe_experiment):
    cafepp_experiment_found=True
    print('Found required output experiment :',cafe_experiment,file=fh_printfile)
    list_new=(cafepp_experiments_data[key_now0])
    #print('list_new=',list_new,file=fh_printfile)
    for l in list_new:
      #print('l=',l,file=fh_printfile)
      if(l=='experiment'): experiment=str(list_new[l])
      elif(l=='experiment_id'): experiment_id=str(list_new[l])
      elif(l=='parent_experiment_id'): parent_experiment_id=str(list_new[l])
      elif(l=='history'): history=str(list_new[l])
      elif(l=='confluence_notes'): confluence_notes=str(list_new[l])
      elif(l=='reference'): reference=str(list_new[l])
      elif(l=='integration_machine'): integration_machine=str(list_new[l])
      elif(l=='integration_machine_info'): integration_machine_info=str(list_new[l])

      elif(l=='storage_machine_no1'): storage_machine_no1=str(list_new[l])
      elif(l=='top_directory_no1'):
        top_directory_no1=str(list_new[l])
      elif(l=='active_disk_no1'): active_disk_no1=str(list_new[l])

      elif(l=='storage_machine_no2'): storage_machine_no2=str(list_new[l])
      elif(l=='top_directory_no2'):
        top_directory_no2=str(list_new[l])
      elif(l=='active_disk_no2'): active_disk_no2=str(list_new[l])

#      elif(l=='storage_machine_no1'): storage_machine_no1=str(list_new[l])
#      elif(l=='top_directory_no1'):
#        top_directory_no1=str(list_new[l])
#        #idir=top_directory_no1
#      elif(l=='active_disk_no1'): active_disk_no1=str(list_new[l])
#
#      elif(l=='storage_machine_no2'): storage_machine_no2=str(list_new[l])
#      elif(l=='top_directory_no2'):
#        top_directory_no2=str(list_new[l])
#        #idir=top_directory_no2 #temporary until disks sorted out...
#      elif(l=='active_disk_no2'): active_disk_no2=str(list_new[l])

      elif(l=='storage_machine_no3'): storage_machine_no3=str(list_new[l])
      elif(l=='top_directory_no3'):
        top_directory_no3=str(list_new[l])
      elif(l=='active_disk_no3'): active_disk_no3=str(list_new[l])

      elif(l=='main_science_contact'): main_science_contact=str(list_new[l])
      elif(l=='main_technical_contact'): main_technical_contact=str(list_new[l])
      elif(l=='readable_nexus_ids_no1'): readable_nexus_ids_no1=str(list_new[l])
      elif(l=='readable_nexus_ids_no2'): readable_nexus_ids_no2=str(list_new[l])
      elif(l=='writable_nexus_ids'): writable_nexus_ids=str(list_new[l])
      elif(l=='ybeg_min'): ybeg_min=int(list_new[l])
      elif(l=='yend_max'): yend_max=int(list_new[l])
      elif(l=='mbeg_min'): mbeg_min=int(list_new[l])
      elif(l=='mend_max'): mend_max=int(list_new[l])
      elif(l=='dbeg_min'): dbeg_min=int(list_new[l])
      elif(l=='dend_max'): dend_max=int(list_new[l])
      elif(l=='daily_data_layout'): daily_data_layout=str(list_new[l])
      elif(l=='monthly_data_layout'): pass #ignore.
      elif(l=='realisation'): realisation=int(list_new[l])
      elif(l=='initialisation'): initialisation=int(list_new[l])
      elif(l=='physics'): physics=int(list_new[l])
      elif(l=='forcing'): forcing=int(list_new[l])
      elif(l=='institution'): institution=str(list_new[l])
      elif(l=='institution_id'): institution_id=str(list_new[l])
      elif(l=='Forecast'): 
        if(list_new[l]=='True'): Forecast=list_new[l]
      else: raise SystemExit('Unknown variable metadata',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  else:
    pass

#storage_machine_no2_split=storage_machine_no2.split('.')
#storage_machine_no2_split=storage_machine_no2.split('.')
#print(storage_machine_no2_split)
#print(type(storage_machine_no2))
#print(storage_machine_no2)
#print(string.split(storage_machine_no2),sep='.')
#print(string.join(storage_machine_no2),sep='')
#        #erange=[str(x) for x in a.split(',')]

if 'storage_machine_no1' in locals() and active_disk_no1=='yes':
  storage_machine_no1_split=storage_machine_no1.split('.')
  if re.match(storage_machine_no1,hostname):
    idir=top_directory_no1

if 'storage_machine_no2' in locals() and active_disk_no2=='yes':
  storage_machine_no2_split=storage_machine_no2.split('.')
  if re.match(storage_machine_no2_split[0],hostname):
    idir=top_directory_no2

if 'storage_machine_no3' in locals() and active_disk_no3=='yes':
  storage_machine_no3_split=storage_machine_no3.split('.')
  if re.match(storage_machine_no3,hostname):
    idir=top_directory_no3

#print(hostname)
#print(storage_machine_no1)
#print(storage_machine_no2)
#print(storage_machine_no3)
#print(top_directory_no1)
#print(top_directory_no2)
#print(top_directory_no3)
#print(idir)

#raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

if not 'idir' in locals():
  raise SystemExit('Could not determine input dir in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

if(not cafepp_experiment_found):
  raise SystemExit('Could not find CAFEPP experiment',' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

netcdf='NETCDF4_CLASSIC'
netcdf='NETCDF3_64BIT'
netcdf='NETCDF3_CLASSIC'
netcdf='NETCDF4'

print(sys.argv,file=fh_printfile)

#json_input_var_meta='cafepp_vars_day.json'
os.system('awk -f uncomment_json.awk JsonTemplates/'+json_input_var_meta+' > '+json_input_var_meta)
json_input_var_fh=open(json_input_var_meta).read()
print('json_input_var_fh=',json_input_var_fh,file=fh_printfile)
json_input_var_data=json.loads(json_input_var_fh)
print('json_input_var_data=',json_input_var_data,file=fh_printfile)

print('Summary of JSON variable input: ',json.dumps(json_input_var_data,indent=4,sort_keys=True))

top_level_keys=json_input_var_data.keys()
print('Top level JSON variable keys=',top_level_keys,file=fh_printfile)

for key_now in json_input_var_data.iteritems():
  #print('processing key_now[0]=',key_now[0],file=fh_printfile)
  key_now0=key_now[0]
  if(key_now0=='defaults'):
    list_new=(json_input_var_data[key_now0])
    for l in list_new:
      if(l=='info'): info=str(list_new[l])
      elif(l=='area_t'): area_t=list_new[l]
      elif(l=='area_u'): area_u=list_new[l]
      #elif(l=='grid'): grid=str(list_new[l])
      #elif(l=='grid_label'): grid_label=str(list_new[l])
      #elif(l=='vertical_interpolation_method'): vertical_interpolation_method=str(list_new[l])
      else: raise SystemExit('Unknown defaults,',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  elif(key_now0==dvar[0]):
    print('Found required output variable:',dvar[0],file=fh_printfile)
    list_new=(json_input_var_data[key_now0])
    for l in list_new:
      #print(l,file=fh_printfile)
      if(l=='info'): info=str(list_new[l])
      elif(l=='area_t'): 
          if(list_new[l]=='True'): area_t=True
      elif(l=='area_u'): 
          if(list_new[l]=='True'): area_u=True
      elif(l=='inputs'): inputs=string.split(str(list_new[l]))
      elif(l=='inputs_alternative'): inputs_alternative=string.split(str(list_new[l]))
        #newinputs=string.split(inputs)
        #print('inputs=',inputs)
        #print('newinputs=',newinputs)
        #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
      elif(l=='realm'): realm=str(list_new[l])
#      elif(l=='diag_dims'): diag_dims=string.split(str(list_new[l]))
      elif(l=='units'): units=str(list_new[l])
#      elif(l=='table'): table_tmp=str(list_new[l])
      elif(l=='table'): table_tmp=string.split(str(list_new[l]),sep=',')
      elif(l=='table_frequency'): table_frequency=string.split(str(list_new[l]),sep=',')
      elif(l=='ovars'): ovars=string.split(str(list_new[l]))
      elif(l=='varStructure'): varStructure=str(list_new[l])
      elif(l=='positive'): positive=str(list_new[l])
      elif(l=='output_type'): output_type=str(list_new[l])
      elif(l=='plev_type'): plev_type=str(list_new[l])
      elif(l=='lat_lon_type'): lat_lon_type=string.split(str(list_new[l]))
      elif(l=='diagnostic_args_string'): diagnostic_args_string=str(list_new[l])
      elif(l=='grid'): grid=str(list_new[l]) #this will override defaults.
      elif(l=='grid_label'): grid_label=str(list_new[l]) #this will override defaults.
      elif(l=='comment'): comment=str(list_new[l])
      else: raise SystemExit('Unknown variable metadata',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  else:
    pass
    #print('hello',file=fh_printfile)
#print('units=',units,file=fh_printfile)
#j='mlotst'
#print('j=',j)
#print('before ovars=',ovars)
#print('dvar=',dvar.strip())
#print('dvar=',dvar)
#print('type(dvar)=',type(dvar))
#print(len(ovars))
#print(len(dvar))

if not 'comment' in locals():
  comment=None

if not 'positive' in locals():
  positive=None

if(ovars[0]=='dvar'):
#  print('true')
  #ovars=str(dvar)
  ovars=dvar
else:
   pass
#  print('false')
#print('after ovars=',ovars)
#print(len(ovars))
#print(len(dvar))
#print(type(dvar))

#raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

print('printDefinedDiagnostics=',printDefinedDiagnostics,file=fh_printfile)
if(printDefinedDiagnostics):
  print('Alphabetically ordered List of currently loaded diagnostis (varable/unit):',file=fh_printfile)
  for key_now in sorted(json_input_var_data.iteritems(),reverse=False):
    if(key_now[0]!='defaults'):
      #print(key_now)
      list_new=(json_input_var_data[key_now[0]])
      #print(list_new)
      find_table_frequency=re.search(frequency,list_new['table_frequency'])
      for l in list_new:
        if(l=='units' and find_table_frequency):
          print(key_now[0],list_new[l],list_new['table'])
  raise SystemExit('Finished writing current set.')

if 'table_tmp' in locals():
  table=table_tmp[table_frequency.index(frequency)]
else:
  raise SystemExit('Must choose valid table:'+__file__+' line number: '+str(inspect.stack()[0][2]))

#area_u=False
#area_t=False

#frequency='daily'
#realm,table,inputs,units,ovars,area_t,area_u,diag_dims,grid_label,grid,vertical_interpolation_method,varStructure=grab_var_meta(dvar,frequency)

#raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

if 'new_ovars' in locals():
  ovars=new_ovars

if 'new_units' in locals():
  units=new_units

#print(ovars,file=fh_printfile)
#print(units,file=fh_printfile)
#raise SystemExit('Finished O.K.')
#cdtime.DefaultCalendar=cdtime.NoLeapCalendar
#cdtime.DefaultCalendar=cdtime.GregorianCalendar

if(daily_data_layout=='noleap_1fileperyear'):
  cdtime.DefaultCalendar=cdtime.NoLeapCalendar
  calendar='noleap'
elif(daily_data_layout=='leap_1fileperday' or daily_data_layout=='leap_1fileperyear'):
  cdtime.DefaultCalendar=cdtime.JulianCalendar
  calendar='julian'
else:
  print('Unknown daily_data_layout=',daily_data_layout)
  raise SystemExit('Unknown daily_data_layout=',daily_data_layout,':'+__file__+' line number: '+str(inspect.stack()[0][2]))

cmor.setup(inpath='Tables',netcdf_file_action=cmor.CMOR_REPLACE_4,logfile=cmorlogfile)

cafepp_defs='cafepp_csiro-gfdl.json'
cmor.dataset_json(cafepp_defs)
json_data=open(cafepp_defs).read()
#pprint.pprint(json_data,width=1)
cafepp_data=json.loads(json_data)
institution_id=cafepp_data['institution_id']
source_id=cafepp_data['source_id']
experiment_id=cafepp_data['experiment_id']

cafe_experiment=os.environ.get('CAFE_EXPERIMENT')

if not 'realisation' in locals(): realisation=1
if not 'initialisation' in locals(): initialisation=1
if not 'physics' in locals(): physics=1
if not 'forcings' in locals(): forcings=1

ripf='r'+str(realisation)+'i'+str(initialisation)+'p'+str(physics)+'f'+str(forcings)

#grid_label='gn'
#grid='native grid'
season='None'

#if(dvar=='ta5' or dvar=='ua5' or dvar=='va5' or dvar=='zg5' or dvar=='hus5' or dvar=='rws5'):
#  grid_label='gn5'
#  grid='3D vars use plev5, 300, 500, 700 and 850hPa'

if not 'version' in locals(): version='v'+str('{0:04d}'.format(t[0])) + str('{0:02d}'.format(t[1])) + str('{0:02d}'.format(t[2]))

odir=create_odirs(ovars,institution_id,source_id,experiment_id,ripf,table,grid_label,version)

ofil,ofil_modified=create_ofils(season,table,ovars,experiment_id,source_id,ripf,grid_label,ybeg,yend,mbeg,mend,dbeg,dend)

#raise SystemExit('Finished O.K.')

for o in range(0,len(ovars)):
  print('Output CMIP6 file:',odir[o]+'/'+ofil_modified[o],file=fh_printfile)

for o in range(0,len(ovars)):
  if(os.path.exists(odir[o]+'/'+ofil_modified[o]) and NoClobber):
    raise SystemExit('No Clobber set and ',odir[o]+'/'+ofil_modified[o],' exists')

for o in range(0,len(ovars)):
  if(os.path.exists(odir[o]+'/'+ofil[o]) and NoClobber):
    raise SystemExit('No Clobber set and ',odir[o]+'/'+ofil_modified[o],' exists')

#calendar='julian'
cmor.set_cur_dataset_attribute('grid_label',grid_label)
cmor.set_cur_dataset_attribute('grid',grid)
cmor.set_cur_dataset_attribute('realization',realisation)
cmor.set_cur_dataset_attribute('initialization_index',initialisation)
cmor.set_cur_dataset_attribute('realization_index',realisation)
cmor.set_cur_dataset_attribute('version',version)
cmor.set_cur_dataset_attribute('calendar',calendar)

cmor.set_cur_dataset_attribute('importance',importance)
cmor.set_cur_dataset_attribute('season',season)

if 'vertical_interpolation_method' in locals(): cmor.set_cur_dataset_attribute('vertical_interpolation_method',vertical_interpolation_method)
if(cafe_experiment == 'v0'):
  cmor.set_cur_dataset_attribute('history','input data from experiment raijin:/g/data1/v14/coupled_model/v1/OUTPUT')
elif(cafe_experiment == 'v1'):
  cmor.set_cur_dataset_attribute('history','input data from experiment raijin:/g/data1/v14/coupled_model/v1/OUTPUT')
elif(cafe_experiment == 'da'):
  cmor.set_cur_dataset_attribute('history','input data from experiment raijin:/g/data1/v14/tok599/coupled_da/workdir2/OUTPUT-2step-nobreeding-carbon')

if(table=='Oday' or table=='day'):
  fileA='TablesTemplates/CMIP6_'+table+'.json'
  fileB='cmor/Tables/CMIP6_'+table+'.json'
  if filecmp.cmp(fileA,fileB):
    pass
  else:
    copyfile(fileA,fileB)

cmor_tables=['coordinate','CV','Ofx','fx']
#raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
for cmor_table in cmor_tables:
  #print(cmor_table,file=fh_printfile)
  fileA='TablesTemplates/CMIP6_'+cmor_table+'.json'
  fileB='cmor/Tables/CMIP6_'+cmor_table+'.json'
  if filecmp.cmp(fileA,fileB):
    pass
  else:
    copyfile(fileA,fileB)

#print('cmor/Tables/CMIP6_'+table+'.json',file=fh_printfile)

tables=[]
tables.append(cmor.load_table('cmor/Tables/CMIP6_'+table+'.json'))
tables.append(cmor.load_table('cmor/Tables/CMIP6_grids.json'))
tables.append(cmor.load_table('cmor/Tables/CMIP6_coordinate.json'))

if os.path.exists('CMIP5/ancillary_files/grid_spec.auscom.20110618.nc'):
  xfh=netCDF4.Dataset('CMIP5/ancillary_files/grid_spec.auscom.20110618.nc')
else:
  xfh=netCDF4.Dataset('/g/data/p66/mac599/CMIP5/ancillary_files/grid_spec.auscom.20110618.nc')
if(area_t):
   area_t=xfh.variables['area_T'] #check ok
if(area_u):
   area_u=xfh.variables['area_C'] #check ok

if(ybeg<ybeg_min or ybeg>yend_max or yend<ybeg_min or yend>yend_max):
  raise SystemExit('Problem with ybeg/yend ybeg_min/yend_max.')

cmor.set_table(tables[1]) #grids

refString='days since 0001-01-01'

ydiff=yend-ybeg+1

#tindex=0
input_files={}
input_fhs={}

year_vec=[]
month_vec=[]
day_vec=[]
tavg_str=[]

print('daily_data_layout=',daily_data_layout,file=fh_printfile)

days_in_month=[31,28,31,30,31,30,31,31,30,31,30,31]

if(daily_data_layout=='noleap_1fileperyear' or daily_data_layout=='leap_1fileperyear'):
  ndy=365 #basic 365 days will be added to by 1 in case of leap years.

  if(daily_data_layout=='noleap_1fileperyear'):
    fh_number=np.ones((yend-ybeg+1)*ndy,dtype=np.int)*-1 #file handle number, set to negative number (fh's have to be >=0)
    fr_number=np.ones((yend-ybeg+1)*ndy,dtype=np.int)*-1 #record number in each file, set to negative number (fr's have to be >=0)
    #fc_number=np.ones((yend-ybeg+1)*ndy,dtype=np.int)*-1 #counter (0..max. elements) , set to negative number (fr's have to be >=0)
    fc_number=range(0,(yend-ybeg+1)*ndy)
  else: #leap year case.
    cnt_leap_years=0
    for ynow in range(ybeg,yend+1):
      print('ynow=',ynow,file=fh_printfile)
      #if(ynow%4==0):
      if(ynow%4==0 and ynow%100!=0 or ynow%400==0):
        cnt_leap_years+=1
        print('yes',file=fh_printfile)
    print('number of years that are leap years=',cnt_leap_years,file=fh_printfile)
    fh_number=np.ones((yend-ybeg+1)*ndy+cnt_leap_years,dtype=np.int)*-1 #file handle number, set to negative number (fh's have to be >=0)
    fr_number=np.ones((yend-ybeg+1)*ndy+cnt_leap_years,dtype=np.int)*-1 #record number in each file, set to negative number (fr's have to be >=0)
    fc_number=np.array(range(0,(yend-ybeg+1)*ndy+cnt_leap_years))
    #print(fc_number.size)
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  #print(fh_number.size,file=fh_printfile)

  cnt_total=0
  day_range_beg=0#used to assign file handle number to a particular time.
  for ynow in range(ybeg,yend+1):
    #day_extra=0

    if(ynow%4==0 and ynow%100!=0 or ynow%400==0 and daily_data_layout=='leap_1fileperyear'):
     days_in_month[1]=29
     day_extra=1 #add one extra day if leap year.
    else:
     days_in_month[1]=28
     day_extra=0

    cnt_record=0
    #print('ynow=',ynow,file=fh_printfile)

    day_range_end=day_range_beg+ndy-1+day_extra
    #print('ynow=',ynow,' day_range_beg=',day_range_beg,' day_range_end=',day_range_end,' day_extra=',day_extra,file=fh_printfile)
    #print(type(day_range_beg))
    #print(type(day_range_end))
    #print('fh_number=',fh_number.size,file=fh_printfile)
    #print('fr_number=',fr_number.size,file=fh_printfile)
    #print('fc_number=',fc_number.size,file=fh_printfile)
    #print(ynow-ybeg,file=fh_printfile)
    fh_number[day_range_beg:day_range_end+1]=ynow-ybeg+0
    #print(fh_number,file=fh_printfile)
    #print(fh_number.size,file=fh_printfile)
    #print(fh_number[day_range_beg:day_range_end+1])
    #print(len(fh_number[day_range_beg:day_range_end+1]))
    day_range_beg=day_range_end+1
    #fh_number[(ynow-ybeg)*ndy:(ynow-ybeg)*ndy+ndy+day_extra]=ynow-ybeg+0
    #print('check=',fh_number[364])
    #print(type(fh_number))
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

    ifila=realm+'_'+frequency+'_'+str('{0:04d}'.format(ynow))+'_01_01.nc'
    input_files[ynow-ybeg]=idir+'/'+ifila
    if not os.path.exists(idir+'/'+ifila):
      #print(input_files,file=fh_printfile)
      #raise SystemExit('Missing '+idir+'/'+ifila+'.')
      raise SystemExit('Missing '+idir+'/'+ifila,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
      #pass
    else:
      print('input file: ',idir+'/'+ifila,file=fh_printfile)
      input_fhs[ynow-ybeg]=netCDF4.Dataset(input_files[ynow-ybeg])
      #cnt_total+=1

    mbeg_now=1
    if(ynow==ybeg):
      mbeg_now=mbeg

    mend_now=nmy
    if(ynow==yend):
     mend_now=mend
  
    for mnow in range(mbeg_now,mend_now+1):

      dbeg_now=1
      if(ynow==ybeg and mnow==mbeg):
        dbeg_now=dbeg

      dend_now=days_in_month[mnow-1]
      if(ynow==yend and mnow==mend):
        dend_now=dend

      for dnow in range(dbeg_now,dend_now+1):
        #print('ynow=',ynow,' mnow=',mnow,' dnow=',dnow,' cnt_record=',cnt_record,' cnt_total=',cnt_total)
        fr_number[cnt_total]=cnt_record
        cnt_total+=1;cnt_record+=1
        day_vec.append(dnow)
        month_vec.append(mnow)
        year_vec.append(ynow)
        tavg_str.append(cdtime.comptime(ynow,mnow,dnow).torel(refString).value)

elif(daily_data_layout=='leap_1fileperday'):
  fh_number=[]
  fr_number=[]
  fc_number=[]

  cnt_total=0
  #day_range_beg=0
  for ynow in range(ybeg,yend+1):
    #print('y='+str(ynow),file=fh_printfile)

    #print(days_in_month,file=fh_printfile)
    if(ynow%4==0):
     days_in_month[1]=29

    #print('ydiff=',ydiff,file=fh_printfile)

    day_range_end=day_range_beg+ndy-1
    mbeg_now=1
    if(ynow==ybeg):
      mbeg_now=mbeg

    mend_now=nmy
    if(ynow==yend):
     mend_now=mend
  
    #if(ydiff==1):
    #  mend_now=mend
    ##elif(ydiff==2):
    ##  mend_now=mend
    #else:
    #  mend_now=nmy
  #
  #  if(ynow==ybeg):
  #    mbeg_now=mbeg
  #  else:
  #    mbeg_now=1
  #    mend_now=mend
    #print('mbeg_now,mend_now=',mbeg_now,mend_now,file=fh_printfile)
    #raise SystemExit('Finished O.K.')
    for mnow in range(mbeg_now,mend_now+1):
      #print('mnow=',mnow,file=fh_printfile)
      idir_extra='/'+str('{0:04d}'.format(ynow))+str('{0:02d}'.format(mnow))+str('{0:02d}'.format(1))

      dbeg_now=1
      if(ynow==ybeg and mnow==mbeg):
        dbeg_now=dbeg

      dend_now=days_in_month[mnow-1]
      if(ynow==yend and mnow==mend):
        dend_now=dend

      for dnow in range(dbeg_now,dend_now+1):
        #print('ynow=',ynow,' mnow=',mnow,' dnow=',dnow,file=fh_printfile)
        month_vec.append(mnow)
        fh_number.append(cnt_total)

        fr_number.append(0)
        fc_number.append(cnt_total+1)
        day_vec.append(dnow)
        month_vec.append(mnow)
        year_vec.append(ynow)
        tavg_str.append(cdtime.comptime(ynow,mnow,dnow).torel(refString).value)
        ifila=realm+'_'+frequency+'_'+str('{0:04d}'.format(ynow))+'_'+str('{0:02d}'.format(mnow))+'_'+str('{0:02d}'.format(dnow))+'.nc'
        input_files[cnt_total]=idir+idir_extra+'/'+ifila
        if not os.path.exists(idir+idir_extra+'/'+ifila):
          #print(input_files,file=fh_printfile)
          #raise SystemExit('Missing '+idir+'/'+ifila+'.')
          raise SystemExit('Missing '+idir+idir_extra+'/'+ifila,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
          #pass
        else:
          print('input file: ',idir+idir_extra+'/'+ifila)
        input_fhs[cnt_total]=netCDF4.Dataset(input_files[cnt_total])
        #tindex+=1
        cnt_total+=1

#print(fh_number)
#print(fh_number.size)
#for ppp in range(len(fc_number)):
#  print(ppp,fh_number[ppp],fr_number[ppp],fc_number[ppp],file=fh_printfile)
#raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

#    ind_beg=0
#print(input_files[0],file=fh_printfile)
print('input files=',input_files,file=fh_printfile)
#raise SystemExit('Finished O.K.')

#day1=1
#print('year,month,day=',tbeg,year_vec,month_vec,day_vec,file=fh_printfile)

tavg=np.array(tavg_str)
#print(tavg)

#raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

tbeg=tavg-0.5
tend=tavg+0.5

tbeg=tavg-0.0
tend=tavg+1.0

tavg=tavg+0.5

timestamp_avg=netCDF4.num2date(tavg,units=refString,calendar=calendar)
timestamp_beg=netCDF4.num2date(tbeg,units=refString,calendar=calendar)
timestamp_end=netCDF4.num2date(tend,units=refString,calendar=calendar)

ttt=len(tavg)
#print('timestamp_avg,beg,end:',file=fh_printfile)
#for n in range(0,ttt):
#  print(timestamp_avg[n],timestamp_beg[n],timestamp_end[n],file=fh_printfile)

tval_bounds=np.column_stack((tbeg,tend))

#print('refString=',refString,file=fh_printfile)
#print('tavg=',tavg,file=fh_printfile)
#print('tval_bounds=',tval_bounds,file=fh_printfile)

cmor.set_table(tables[0]) #cmor table

time_axis_id=cmor.axis('time', units=refString, coord_vals=tavg, cell_bounds=tval_bounds)

#raise SystemExit('Finished O.K. abc')

#print(tbeg,tend,tavg,file=fh_printfile)

cmor.set_table(tables[1]) #grids

#if(dvar=='tos' or dvar=='psl' or dvar=='pr' or dvar=='tas' or dvar=='huss'):
#  levels=0
#  nlev=1

if(realm=='ocean'):
#dvar=='tos'):
  cmor.set_table(tables[0]) #cmor table

  zt=xfh.variables['zt']
  zb=xfh.variables['zb']
  nzb=len(zb[:])
  z0=np.zeros((nzb))
  z0[0]=0
  z0[1:nzb]=zb[0:nzb-1]
  zbounds=np.column_stack((z0,zb))
  z=zb-z0

  ztX=zt[[0,10,20]]
  zboundsX=zbounds[[0,10,20],:]

if(realm=='ocean'):

  if(varStructure=='time'):
    lat_vals=xfh.variables[lat_lon_type[0]][:,0]
    lon_vals=xfh.variables[lat_lon_type[1]][0,]
  else:
    lat_vals=xfh.variables[lat_lon_type[0]]
    lon_vals=xfh.variables[lat_lon_type[1]]
  lon_vals_360=np.mod(lon_vals,360)
#dvar=='nino34'):
  #lat_vals=np.squeeze(xfh.variables[lat_lon_type[0]][:,0])
  #lon_vals=xfh.variables[lat_lon_type[1]][0,]
  #raise SystemExit('Finished O.K.')
  #print('lat_vals=',lat_vals)
  #print('lon_vals=',lon_vals)
  #print('lon_vals_360=',lon_vals_360)
#elif(dvar=='tos'):
#  if(dvar=='umo'):
#    lat_vals=xfh.variables['y_T']
#    lon_vals=xfh.variables['x_C']
#  elif(dvar=='vmo'):
#    lat_vals=xfh.variables['y_C']
#    lon_vals=xfh.variables['x_T']
#  else:
#    lat_vals=xfh.variables['y_T']
#    lon_vals=xfh.variables['x_T']

  #print(lat_vals.shape)
  #print(lon_vals_360.shape)

  print(lat_vals.size)
  print(lon_vals_360.size)

  if(varStructure=='time'):
    nlats=lat_vals.size
    nlons=lon_vals_360.size
  else:
    nlats=lat_vals[:,0].size
    nlons=lon_vals_360[0,].size

  #nlats=lat_vals.size
  #nlons=lon_vals_360.size

  #nlats=300
  #nlons=360

  #print('nlats,nlons=',nlats,nlons,file=fh_printfile)

  cmor.set_table(tables[1]) #grids

  j_axis_id=cmor.axis('j_index','1',coord_vals=np.arange(nlats))
  i_axis_id=cmor.axis('i_index','1',coord_vals=np.arange(nlons))

  #j_axis_id=cmor.axis('j_index','1',coord_vals=np.arange(108000))
  #i_axis_id=cmor.axis('i_index','1',coord_vals=np.arange(108000))

  #print('j_axis_id=',j_axis_id,file=fh_printfile)
  #print('i_axis_id=',i_axis_id,file=fh_printfile)

  lon_vertices=np.mod(get_vertices('geolon_t'),360)
  lat_vertices=get_vertices('geolat_t')

  axis_ids=np.array([j_axis_id, i_axis_id])

  if(varStructure!='time'):
    grid_id=cmor.grid(axis_ids=axis_ids, latitude=lat_vals[:], longitude=lon_vals_360[:], latitude_vertices=lat_vertices[:], longitude_vertices=lon_vertices[:])
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

elif(realm=='atmos' and (varStructure=='time_lat_lon' or varStructure=='time_plev_lat_lon' or varStructure=='time_reducedplev_lat_lon')):
#dvar=='psl' or dvar=='pr' or dvar=='tas' or dvar=='huss' or dvar=='zg' or dvar=='hfss' or dvar=='rlut' or dvar=='sfcWind' or dvar=='tslsi' or dvar=='hfls' or dvar=='uas' or dvar=='vas' or dvar=='ua' or dvar=='va' or dvar=='ta' or dvar =='hus' or dvar=='zg500' or dvar=='zg700' or dvar=='ta10' or dvar=='zg10' or dvar=='ua10' or dvar=='va10' or dvar=='ta5' or dvar=='ua5' or dvar=='va5' or dvar=='zg5' or dvar=='hus5' or dvar=='rws5'):

#  if(ReGrid):
#    lat_vals = outgrid.getLatitude()
#    lon_vals = outgrid.getLongitude()
#  else:
#    if(dvar=='nino34'):
#      #lat_vals=input_fhs[0].variables['yt_ocean']
#      #lon_vals=input_fhs[0].variables['xt_ocean']
#      levels=0
#      nlev=1
#    else:
  lat_vals=input_fhs[0].variables['lat']
  lon_vals=input_fhs[0].variables['lon']

  min_vals=np.append((1.5*lat_vals[0] - 0.5*lat_vals[1]), (lat_vals[0:-1] + lat_vals[1:])/2)
  max_vals=np.append((lat_vals[0:-1] + lat_vals[1:])/2, 1.5*lat_vals[-1] - 0.5*lat_vals[-2])
  lat_vals_bounds=np.column_stack((min_vals, max_vals))

  min_vals=np.append((1.5*lon_vals[0] - 0.5*lon_vals[1]), (lon_vals[0:-1] + lon_vals[1:])/2)
  max_vals=np.append((lon_vals[0:-1] + lon_vals[1:])/2, 1.5*lon_vals[-1] - 0.5*lon_vals[-2])
  lon_vals_bounds=np.column_stack((min_vals, max_vals))

#if(realm=='atmos' and (varStructure=='time_lat_lon' or varStructure=='time_plev_lat_lon')):
if(realm=='atmos' and (varStructure=='time_plev_lat_lon')):
#dvar=='zg' or dvar=='ua' or dvar=='va' or dvar=='ta' or dvar =='hus' or dvar=='zg700'):
  zt=input_fhs[0].variables[plev_type][:]*100.0
  #if(dvar=='zg'):
  #  zt=input_fhs[0].variables['phalf'][:]*100.0
  #else:
  #  zt=input_fhs[0].variables['pfull'][:]*100.0

  min_vals=np.append((1.5*zt[0] - 0.5*zt[1]), (zt[0:-1] + zt[1:])/2)
  max_vals=np.append((zt[0:-1] + zt[1:])/2, (1.5*zt[-1] - 0.5*zt[-2]))
  zbounds =np.column_stack((min_vals, max_vals))
  zbounds=np.where(zbounds<0.0,0.0,zbounds)

  cmor.set_table(tables[2]) #working zg
  cmor.set_table(tables[0]) #cmor

  if(plev_type=='phalf'):
  #if(dvar=='zg'):
    z_axis_id=cmor.axis('plev25','Pa',coord_vals=zt[:])
  else:
    z_axis_id=cmor.axis('plev24','Pa',coord_vals=zt[:])

if(realm=='atmos' and varStructure=='time_reducedplev_lat_lon'):
#dvar=='ta5' or dvar=='zg5' or dvar=='ua5' or dvar=='va5' or dvar=='hus5' or dvar=='hur5' or dvar=='rws5'):
  zt=input_fhs[0].variables[plev_type][:]*100.0
  #if(dvar=='zg5'):
  #  zt=input_fhs[0].variables['phalf'][:]*100.0
  #else:
  #  zt=input_fhs[0].variables['pfull'][:]*100.0
  #print('zt=',zt,file=fh_printfile)

  newlevs=np.array([30000., 50000., 70000., 85000., 92500.])

  cmor.set_table(tables[0]) #cmor
  z_axis_id=cmor.axis('plev5','Pa',coord_vals=newlevs[:])

if(realm=='atmos' and (varStructure=='time_lat_lon' or varStructure=='time_plev_lat_lon' or varStructure=='time_reducedplev_lat_lon')):
#dvar=='psl' or dvar=='pr' or dvar=='tas' or dvar=='huss' or dvar=='zg' or dvar=='hfss' or dvar=='rlut' or dvar=='sfcWind' or dvar=='tslsi' or dvar=='hfls' or dvar=='uas' or dvar=='vas' or dvar=='ua' or dvar=='va' or dvar=='ta' or dvar =='hus'  or dvar=='ta5' or dvar=='ua5' or dvar=='va5' or dvar=='zg5' or dvar=='hus5'or dvar=='zg500' or dvar=='zg700' or dvar=='rws5'):
  #print('lat_vals.shape=',lat_vals.shape,file=fh_printfile)
  #print('lon_vals.shape=',lon_vals.shape,file=fh_printfile)

  #print('lat_vals_bounds.shape=',lat_vals_bounds.shape,file=fh_printfile)
  #print('lon_vals_bounds.shape=',lon_vals_bounds.shape,file=fh_printfile)
  lat_vals_bounds=np.where(lat_vals_bounds>90.0,90.0,lat_vals_bounds)
  lat_vals_bounds=np.where(lat_vals_bounds<-90.0,-90.0,lat_vals_bounds)

  #print('max=',np.max(lat_vals_bounds),file=fh_printfile)
  #print('min=',np.min(lat_vals_bounds),file=fh_printfile)

  nlats=lat_vals.shape[0] #check this
  nlons=lon_vals.shape[0] #check this, should it be 1?

  cmor.set_table(tables[0]) #cmor #working zg500
  #cmor.set_table(tables[2])

  lat_axis_id=cmor.axis(table_entry='latitude', units='degrees_north', coord_vals=lat_vals[:], cell_bounds=lat_vals_bounds)

  lon_axis_id=cmor.axis(table_entry='longitude', units='degrees_east', coord_vals=lon_vals[:], cell_bounds=lon_vals_bounds)

cmor.set_table(tables[0]) #cmor #working

if not 'positive' in locals() and positive!='None':
  positive=None

data_id=[]
if(realm=='ocean' and varStructure=='time_lat_lon'):
  axis_ids=[time_axis_id,grid_id] #working
  data_id.append(cmor.variable(dvar[0], units, axis_ids=axis_ids, missing_value=-1e20))
elif(varStructure=='time'):
#dvar=='nino34'):
  axis_ids=[0] #working
  #data_id=cmor.variable(dvar, units,  missing_value=-1e20)
  data_id.append(cmor.variable(dvar[0], units, axis_ids=axis_ids, missing_value=-1e20))
#elif(dvar=='tos'):
#  axis_ids=[time_axis_id,grid_id] #working
#  data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20))
elif(realm=='atmos' and varStructure=='time_lat_lon'):
#dvar=='psl' or dvar=='pr' or dvar=='tas' or dvar=='huss' or dvar=='hfss' or dvar=='rlut' or dvar=='sfcWind' or dvar=='tslsi' or dvar=='hfls' or dvar=='uas' or dvar=='vas' or dvar=='zg500' or dvar=='zg700'):
  #print('xxx')
  #print(positive)
  axis_ids=[time_axis_id,lat_axis_id,lon_axis_id] #working zg500
  data_id.append(cmor.variable(dvar[0], units, axis_ids=axis_ids, missing_value=-1e20,positive=positive,comment=comment))
  #print('axis_ids=',axis_ids,file=fh_printfile)
  #if(dvar=='hfss' or dvar=='tauu' or dvar=='tauv' or dvar=='rlut' or dvar=='hfls'):
  #  positive='up'
  #else:
  #  positive=None
#  if(dvar=='hfls'):
#    data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20,positive=positive,comment='Converted from evap using 28.9, assuming latent heat of vaporization of 2.5 MJ/kg'))
#  if(dvar=='zg700'):
#    data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20,positive=positive,comment='Note that level extracted is 691.673132hPa, approximately 700hPa'))
#  else:
#    data_id.append(cmor.variable(dvar[0], units, axis_ids=axis_ids, missing_value=-1e20,positive=positive))
#elif(dvar=='zg' or dvar=='ua' or dvar=='va' or dvar =='hus' or dvar=='ta' or dvar=='ta5' or dvar=='ua5' or dvar=='va5' or dvar=='zg5' or dvar=='hus5' or dvar=='rws5'):
#  axis_ids=np.array([time_axis_id,z_axis_id,lat_axis_id,lon_axis_id])
#  for o in range(0,len(ovars)):
#    data_id.append(cmor.variable(ovars[o], units[o], axis_ids=axis_ids, missing_value=-1e20))

#data=np.zeros((300,360),dtype='f')
ntimes_passed=1
for icnt in range(0,len(tavg)):

  print('icnt=',icnt,' input_fhs[]=',input_fhs[fh_number[icnt]],' tbeg[]=',tbeg[icnt],' tend[]=',tend[icnt],file=fh_printfile)

  if(output_type=='diagnostic'):
    try:
      data=input_fhs[fh_number[icnt]].variables[inputs[0]][fr_number[icnt],]
    except KeyError:
      data=input_fhs[fh_number[icnt]].variables[inputs_alternative[0]][fr_number[icnt],]

    diagnostic_args=(eval(diagnostic_args_string))
    function_name='diag_'+dvar[0]
    data=eval(function_name)(data,*diagnostic_args)

#    raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  elif(varStructure=='time'):
  #dvar=='nino34'):
    data=input_fhs[fh_number[icnt]].variables[inputs[0]][0,0,]
    data=np.expand_dims(data,axis=0)
    #print('data=',data)
    #print('data.shape=',data.shape)
    data=diag_nino34(data,area_t,lat_vals[:],lon_vals[:],fh_printfile)
    #print('data=',data)
    #print('data.shape=',data.shape)

  elif(realm=='ocean' and varStructure=='time_lat_lon'):
  #dvar=='tos'):
    #data=input_fhs[fh_number[icnt]].variables[inputs[0]][0,0,]
    #data=input_fhs[fh_number[icnt]].variables[inputs[0]][0,]
    #print(fr_number[icnt],file=fh_printfile)
    data=input_fhs[fh_number[icnt]].variables[inputs[0]][fr_number[icnt],]
    #print(data.shape)
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  elif(realm=='atmos' and (varStructure=='time_lat_lon' or varStructure=='time_plev_lat_lon')):
  #dvar=='psl' or dvar=='pr' or dvar=='tas' or dvar=='huss' or dvar=='zg' or dvar=='hfss' or dvar=='rlut' or dvar=='sfcWind' or dvar=='tslsi' or dvar=='uas' or dvar=='vas' or dvar=='ua' or dvar=='va' or dvar =='hus' or dvar=='ta') or dvar=='zg500':
    data=input_fhs[fh_number[icnt]].variables[inputs[0]][0,]
#  elif(dvar=='hfls'):
#    data=input_fhs[fh_number[icnt]].variables[inputs[0]][0,]
#    data=data/28.9 #assuming latent heat of vaporization of 2.5 MJ/kg
#    cmor.set_cur_dataset_attribute('comment','abc')
    #see document ~sjj554/CMIP5/scripts/Variable_examples/RUN_post_processor_atmos_monthly_2D_E1.bash.variable_hfls.table_CMIP5_Amon
#  elif(dvar=='zg700'):
#    data=input_fhs[fh_number[icnt]].variables[inputs[0]][0,12]
#  elif(dvar=='ta5' or dvar=='zg5' or dvar=='ua5' or dvar=='va5' or dvar=='hus5'):
#    data1=input_fhs[fh_number[icnt]].variables[inputs[0]][0,]
#    data2=input_fhs[fh_number[icnt]].variables[inputs[1]][0,]
#    #print(data.shape,file=fh_printfile)
#    #raise SystemExit('forced break')
#    data=vertical_interpolate(data1,zt,newlevs,data2,vertical_interpolation_method)
#    del data1,data2
#
#  elif(dvar=='rws5'):
#    data1=input_fhs[fh_number[icnt]].variables[inputs[0]][0,]#ucomp
#    data2=input_fhs[fh_number[icnt]].variables[inputs[1]][0,]#vcomp
#    data3=input_fhs[fh_number[icnt]].variables[inputs[2]][0,]#ps
#
#    data1=np.expand_dims(data1,axis=0)
#    data2=np.expand_dims(data2,axis=0)
#    data3=np.expand_dims(data3,axis=0)
#
##    print('data1.shape=',data1.shape)
#
#    data1a=vertical_interpolate(data1,zt,newlevs,data3,vertical_interpolation_method)
#    #raise SystemExit('Forced exit.')
#    data2a=vertical_interpolate(data2,zt,newlevs,data3,vertical_interpolation_method)
#    del data1,data2,data3
#    #rws_string=('rws','div','eta','uchi','vchi')
#    #jjj='rws,div,eta,uchi,vchi'
#
#    #rws,div,eta,uchi,vchi=diag_rws(data1a,data2a,lat_vals[:],lon_vals[:],rws_string)
#    #print(jjj,file=fh_printfile)
#    #eval(jjj)=diag_rws(data1a,data2a,lat_vals[:],lon_vals[:],rws_string)
#    #rws_tuple=diag_rws(data1a,data2a,lat_vals[:],lon_vals[:],rws_string)
#    rws_tuple=diag_rws(data1a,data2a,lat_vals[:],lon_vals[:],new_ovars)
#    #print(rws_tuple.shape,file=fh_printfile)
#    #print(len(rws_tuple),file=fh_printfile)
#    #print(len(rws_tuple[0]),file=fh_printfile)
#    del data1a,data2a
#    #raise SystemExit('Forced exit.')

  if( (realm=='atmos' and (varStructure=='time_lat_lon' or varStructure=='time_plev_lat_lon' or varStructure=='time_plevreduced_lat_lon')) or (realm=='ocean' and (varStructure=='time_lat_lon' or varStructure=='time_depth_lat_lon' or varStructure=='time_depthreduced_lat_lon')) ):
  #dvar=='psl' or dvar=='pr' or dvar=='tas' or dvar=='huss' or dvar=='tos' or dvar=='zg' or dvar=='hfss' or dvar=='rlut' or dvar=='sfcWind' or dvar=='tslsi' or dvar=='hfls' or dvar=='uas' or dvar=='vas' or dvar=='ua' or dvar=='va' or dvar=='ta' or dvar =='hus' or dvar=='zg500' or dvar=='zg700' or dvar=='ta5' or dvar=='ua5' or dvar=='va5' or dvar=='zg5' or dvar=='hus5'):
    for o in range(0,len(ovars)):
      #print(data.shape)
      #print(tbeg[icnt],tend[icnt])
      cmor.write(var_id=data_id[o], data=data[:], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])

  if(varStructure=='time'):
  #dvar=='nino34'):
    newdata=np.zeros((1,1),dtype='f')
    newdata[0,0]=data
    data=newdata
    for o in range(0,len(ovars)):
      cmor.write(var_id=data_id[o], data=data[:], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])

#  elif(dvar=='rws5'):
#    #print(rws_string,file=fh_printfile)
#    #print(data_id,file=fh_printfile)
#    for o in range(0,len(ovars)):
#      #data_now=eval(rws_string[o])
#      #data_now=rws_tuple[0,:,:,:]
#      #data_now=rws_tuple[0]
##      print(len(rws_tuple),file=fh_printfile)
#      #cmor.write(var_id=data_id[o], data=rws_tuple[0], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])
#      if(len(rws_tuple)==0):
##        print('abc',file=fh_printfile)
#        cmor.write(var_id=data_id[o], data=rws_tuple, ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])
#      else:
#        cmor.write(var_id=data_id[o], data=rws_tuple[0], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])
#    #raise SystemExit('Forced exit here.')

#print('ovars=',ovars,file=fh_printfile)
#print('len(ovars)=',len(ovars),file=fh_printfile)

file_name=[]
for o in range(0,len(ovars)):
  print(o,file=fh_printfile)
  file_name.append(cmor.close(var_id=data_id[o], file_name=True))

for o in range(0,len(ovars)):
  finish(file_name[o],odir[o],ofil[o],ofil_modified[o],season,fh_printfile)

raise SystemExit('Finished O.K.')

#end
