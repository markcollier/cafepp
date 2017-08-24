#!/usr/bin/env python

##!/apps/python/2.7.6/bin/python
##!/short/p66/mac599/anaconda3/bin/ipython
# Filename : cafepp.py

from __future__ import print_function #this is to allow print(,file=xxx) feature

"""
CAFE Post-Processor for monthly inputs
--------------------------

Compute extended time-series of monthly/seasonal data from breeding ACCESS coupled experiments.

Inputs can start from a month other than January and end in a month other than December. Outputs will be over available months. For monthly outputs this is trivial, however, for seasonal outputs this is non-trivial.

There are 3 kinds of outputs:

1. MONTHLY: input and output are monthly, process one month at a time.
2. SEASONAL: e.g. DJF, MAM, SO input are monthly and read in for a "years" season at a time and processed by wavg. A single time is written out at a time.
3. ANN: 12 continuous months (January to December) are read in at a time. A single time is written out at a time. Partial years are ignored.

Trying to adapt it so that all variables (broadcast or diagnosed) have a leading time dimension, size 1 or more.

look into cartopy: http://ajdawson.github.io/software.html

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
from decadal_diag import MustHaveAllLevs,diag_acc_drake,diag_acc_africa,diag_mozmbq,diag_aabw,diag_nadw,diag_pp,diag_nflux,diag_ep,diag_ssh,diag_moc,diag_moc_atlantic,diag_moc_pacific,diag_moc_indian,diag_shice_cover,diag_nhice_cover,diag_nino34,xtra_nino34,init_data,sum_data,avg_data,filemonth_index,data_wavg,time_avg,diag_nhblocking_index,diag_rws,finish,diag_msftyyz,make_mask3D,diag_mfo,transPort,diag_rws500,create_odirs,create_ofils,diag_iod,diag_iod,xtra_iod,vertical_interpolate,diag_isothetaoNc,calc_iso_surface,calc_isoN,grab_var_meta
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

#https://infohost.nmt.edu/tcc/help/pubs/python/web/print-as-function.html
#
#
#from subprocess import call
#from windspharm.standard import VectorWind
#from windspharm.tools import prep_data, recover_data, order_latdim

#https://ajdawson.github.io/eofs/
#import cartopy.crs as ccrs
#import cartopy.feature as cfeature
#from netCDF4 import Dataset
#import matplotlib.pyplot as plt
#import numpy as np
#from eofs.standard import Eof
#from eofs.examples import example_data_path

def usage(script_name):
    """usage"""
    print('Usage: ',script_name,' -h,help -v input_var -i importance (1-5) --ybeg=process begin year --yend=process end year --ybeg_min=min. year available --yend_max=max. year available --levs=one of pre-defined set --idir=input directory --season="MON" --json_input_instructions=json input command file')

try:
    opts, args=getopt.getopt(sys.argv[1:], "wxdCAhv:i:rFl:",["help","ybeg=","yend=","ybeg_min=","yend_max=","mbeg=","mend=","mbeg_min=","mend_max=","dbeg=","dend=","dbeg_min=","dend_max=","levs=","realisation=","initialisation=","physics=","forcings=","season=","idir=","vertical_interpolation_method=","version=","cmorlogfile=","json_input_instructions=",])
except getopt.GetoptError as err:
    print(err)
    usage(os.path.realpath(__file__))
    sys.exit(2)

printDefinedDiagnostics=False
Forecast=False#the input directory will vary depending on year/month, I am calling these Forecast runs for now. These have one month of data per file - future model configurations may have different inputs. "Non-Forecast" runs are the traditional control runs, which have normally had 12 months per file.
ReGrid=False
NoClobber=False
#NoClobberTfil=False
#ClimRep=True
importance=5
#LevXtrct=False
#Anom=False
#Clim=False
levs_test=None
#delClim=False
MonthlyWeights=False
#CMIP6=False
#StdLev=False #write out on standard levels, at this stage focusing on 3D atmosphere pressure level data.
area_u=False
area_t=False
dfp_defs='dfp_csiro-gfdl.json'
cafepp_experiments='cafepp_experiments.json'
json_input_var_meta='cafepp_vars_mon.json'
json_input_instructions='cafepp.json'
cafepp_machine='raijin.nci.org.au'

#fh_printfile=sys.stdout
#fh_printfile=sys.stderr

cmorlogfile='log'
mbeg=1
mend=12
for o, a in opts:
    #print(o)
    if o in ('-h', '--help'):
        usage(os.path.realpath(__file__)) 
        sys.exit()
    elif o == '-w':
        MonthlyWeights=True
        #weights=np.array([31,28,31,30,31,30,31,31,30,31,30,31])
#    elif o == '-X':
#        NoClobberTfil=True
    elif o == '-x':
        NoClobber=True
#    elif o == '-d':
#        delClim=True
    elif o == '-i':
        importance=int(a) 
#    elif o == '-A':
#        Anom=True
#    elif o == '-C':
#        Clim=True
    elif o == '-l':
         printfile=a
         fh_printfile=open(printfile,"w")
    elif o == '-v':
         dvar=a
         #ivarS=[str(x) for x in a.split(',')]
         #print('ivarS=',ivarS,file=fh_logfile)
    elif o == '--ybeg':
        ybeg=int(a) 
    elif o == '--yend':
        yend=int(a) 

    elif o == '--mbeg':
        mbeg=int(a) 
    elif o == '--mend':
        mend=int(a) 

    elif o == '--dbeg':
        dbeg=int(a) 
    elif o == '--dend':
        dend=int(a) 

    elif o == '--ybeg_min':
        ybeg_min=int(a) 
    elif o == '--yend_max':
        yend_max=int(a) 

    elif o == '--mbeg_min':
        mbeg_min=int(a) 
    elif o == '--mend_max':
        mend_max=int(a) 

    elif o == '--dbeg_min':
        mbeg_min=int(a) 
    elif o == '--dend_max':
        mend_max=int(a) 

    elif o == '--cbeg':
        cbeg=int(a) 
    elif o == '--cend':
        cend=int(a) 
    elif o == '--levs':
      levs=a
    elif o == '--realisation':
        #erange=[str(x) for x in a.split(',')]
        realisation=int(a)
    elif o == '--initialisation':
        initialisation=int(a)
    elif o == '--physics':
        physics=int(a)
    elif o == '--forcings':
        forcings=int(a)
    elif o == '--idir':
        idir=a
    elif o == '--vertical_interpolation_method':
        vertical_interpolation_method=a
#    elif o == '--idirc':
#        idirc=a
#    elif o == '--odir':
#        odir=a
#    elif o == '--tdir':
#        tdir=a
    elif o == '--season':
        season=a
#    elif o == '--cmip6':
#      CMIP6=True
    elif o == '-r':
        ReGrid=True
    elif o == '--version':
        version=a
    elif o == '--cmorlogfile':
        cmorlogfile=a
#    elif o == '--stdlev':
#        StdLev=True
    elif o == '-F':
        Forecast=True
    elif o == '--json_input_instructions':
        json_input_instructions=a #this will be a file with info. to drive cafepp. All other options will be null and void. Will need to test for this.
    else:
        assert False, 'unhandled option'

    try:
        erange
    except NameError:
        erange=('1','2','3','4','5')
    else:
        pass

if 'json_input_instructions' in locals():
  os.system('awk -f uncomment_json.awk JsonTemplates/'+json_input_instructions+' > '+json_input_instructions)
  print('Running cafepp from JSON instructions: '+json_input_instructions)
  json_input_instructions_fh=open(json_input_instructions).read()
  json_input_instructions_data=json.loads(json_input_instructions_fh)
  print('json_input_instructions_data=',json_input_instructions_data)
else:
  print('Running cafepp from command line input:')

if 'json_input_instructions' in locals():
  print("Summary of JSON instructions: ",json.dumps(json_input_instructions_data,indent=4,sort_keys=True))

  #print(type(json_input_instructions_data))

  top_level_keys=json_input_instructions_data.keys()

  print('Top level JSON instructions keys=',top_level_keys)
#  print(json_input_instructions_data)
  for key_now in json_input_instructions_data.iteritems():
    print('processing key_now[0]=',key_now[0])
    key_now0=key_now[0]
    if(key_now0=="options_with_arguments"):
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
        elif(l=='dvar'): dvar=str(list_new[l])
        elif(l=='ybeg'): ybeg=int(list_new[l])
        elif(l=='yend'): yend=int(list_new[l])
#        elif(l=='ybeg_min'): ybeg_min=list_new[l]
#        elif(l=='yend_max'): yend_max=list_new[l]
        elif(l=='mbeg'): mbeg=int(list_new[l])
        elif(l=='mend'): mend=int(list_new[l])
#        elif(l=='mbeg_min'): mbeg_min=list_new[l]
#        elif(l=='mend_max'): mend_max=list_new[l]
#        elif(l=='idir'): idir=str(list_new[l])
        elif(l=='season'): season=str(list_new[l])
        elif(l=='levs'): levs=str(list_new[l])
        elif(l=='cmorlogfile'): cmorlogfile=str(list_new[l])
        elif(l=='printfile'): printfile=str(list_new[l])
        elif(l=='xxxprintfile'): None
        elif(l=='printDefinedDiagnostics'):
          if(list_new[l]=='True'): printDefinedDiagnostics=True
        elif(l==''): grid_label=str(list_new[l])
        elif(l=='cafepp_machine'): cafepp_machine=str(list_new[l])
        else: raise SystemExit('Unknown option_with_argument,',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    elif(key_now0=="options_no_arguments"):
      list_new=(json_input_instructions_data[key_now0])
      for l in list_new: #used to be list_new2
        if(l=='name'): name=str(list_new[l])
        elif(l=='info'): info=str(list_new[l])
        elif(l=='Forecast'): 
          if(list_new[l]=='True'): Forecast=list_new[l]
        elif(l=='Regrid'):
          if(list_new[l]=='True'): Regrid=True
        elif(l=='MonthlyWeights'): 
          if(list_new[l]=='True'): MonthlyWeights=True
        elif(l=='NoClobber'): 
          if(list_new[l]=='True'): NoClobber=list_new[l]
        else: raise SystemExit('Unknown option_no_argument,',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    elif(key_now0=="defaults"):
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
        elif(l=='dfp_defs'): dfp_defs=str(list_new[l])
        elif(l=='json_input_var_meta'): json_input_var_meta=str(list_new[l])

        else: raise SystemExit('Unknown defaults,',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  if 'printfile' in locals():
    fh_printfile=open(printfile,"w")
  else:
    fh_printfile=sys.stdout
  print('fh_printfile=',fh_printfile)

#cafepp_experiments_meta='cafepp_experiments.json'
os.system('awk -f uncomment_json.awk JsonTemplates/'+cafepp_experiments_meta+' > '+cafepp_experiments_meta)
cafepp_experiments_fh=open(cafepp_experiments_meta).read()
print('cafepp_experiments_fh=',cafepp_experiments_fh,file=fh_printfile)
cafepp_experiments_data=json.loads(cafepp_experiments_fh)
print('cafepp_experiments_data=',cafepp_experiments_data)

print("Summary of JSON experiments input: ",json.dumps(cafepp_experiments_data,indent=4,sort_keys=True))

top_level_keys=cafepp_experiments_data.keys()
print('Top level JSON experiments keys=',top_level_keys)

cafepp_experiment_found=False
for key_now in cafepp_experiments_data.iteritems():
  print('processing key_now[0]=',key_now[0])
  key_now0=key_now[0]
  if(key_now0==cafe_experiment):
    cafepp_experiment_found=True
    print("Found required output experiment :",cafe_experiment)
    list_new=(cafepp_experiments_data[key_now0])
    #print('list_new=',list_new)
    for l in list_new:
      print('l=',l)
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
        idir=top_directory_no1
      elif(l=='active_disk_no1'): active_disk_no1=str(list_new[l])
      elif(l=='storage_machine_no2'): storage_machine_no2=str(list_new[l])
      elif(l=='top_directory_no2'):
        top_directory_no2=str(list_new[l])
        idir=top_directory_no2 #temporary until disks sorted out...
      elif(l=='active_disk_no2'): active_disk_no2=str(list_new[l])
      elif(l=='main_science_contact'): main_science_contact=str(list_new[l])
      elif(l=='main_technical_contact'): main_technical_contact=str(list_new[l])
      elif(l=='readable_nexus_ids_no1'): readable_nexus_ids_no1=str(list_new[l])
      elif(l=='readable_nexus_ids_no2'): readable_nexus_ids_no2=str(list_new[l])
      elif(l=='writable_nexus_ids'): writable_nexus_ids=str(list_new[l])
      elif(l=='ybeg_min'): ybeg_min=int(list_new[l])
      elif(l=='yend_max'): yend_max=int(list_new[l])
      elif(l=='mbeg_min'): mbeg_min=int(list_new[l])
      elif(l=='mend_max'): mend_max=int(list_new[l])
      elif(l=='realisation'): realisation=int(list_new[l])
      elif(l=='initialisation'): initialisation=int(list_new[l])
      elif(l=='physics'): physics=int(list_new[l])
      elif(l=='forcing'): forcing=int(list_new[l])
      elif(l=='institution'): institution=str(list_new[l])
      elif(l=='institution_id'): institution_id=str(list_new[l])
      else: raise SystemExit('Unknown variable metadata',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  else:
    pass

if(not cafepp_experiment_found):
  raise SystemExit('Could not find CAFEPP experiment',' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    
#raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

    #c=json_input_instructions_data['options_no_arguments']
    #print('c',c)
    #print('c',c['info'])
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
#    for l in k:
#      print(l['info'])
#    #for l,m in k.iteritems():
#    #  print(l,m)
#
#print(len(json_input_instructions_data))
#print(len(k))

#https://codingnetworker.com/2015/10/python-dictionaries-json-crash-course/
#https://pythonspot.com/en/json-encoding-and-decoding-with-python/
#http://www.compciv.org/guides/python/fundamentals/dictionaries-overview/
#https://www.tutorialspoint.com/python/python_dictionary.htm

#print("xxx" % json_input_instructions_data["options_with_arguments"])
#print("yyy" % json_input_instructions_data["idir"])

#raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

netcdf='NETCDF4_CLASSIC'
netcdf='NETCDF3_64BIT'
netcdf='NETCDF3_CLASSIC'
netcdf='NETCDF4'

print('sys.argv=',sys.argv,file=fh_printfile)

#file_name = __file__
#current_line_no = inspect.stack()[0][2]
#current_function_name = inspect.stack()[0][3]


#if(delClim and not Anom):
#  raise SystemExit('If choose -d then must chose -A.')

#if not MonthlyWeights:
#  weights=np.array([1,1,1,1,1,1,1,1,1,1,1,1])

#if CMIP6:
#  print('Generating CMIP6 like netCDF output.',file=fh_printfile)
#else:
#  print('Generating basic netCDF output.',file=fh_printfile)

#print(levels)

#if not Anom and not Clim then simple broadcast of data.
#odir='.'
#odir='../data'
#odir='/short/v14/mac599/coupled/ao_am2/coupled_da'
#tdir='/short/v14/mac599'
#diag=True
#myatt=True
#diag='aaa'
#setattr(ivarS,diag,True)
#ivarS.myatt
#print(getattr(ivarS,diag),file=fh_printfile)

#area_t=False
#area_u=False

#https://jsonlint.com/

#json_input_var_meta='cafepp_vars_mon.json'
os.system('awk -f uncomment_json.awk JsonTemplates/'+json_input_var_meta+' > '+json_input_var_meta)
json_input_var_fh=open(json_input_var_meta).read()
print('json_input_var_fh=',json_input_var_fh,file=fh_printfile)
json_input_var_data=json.loads(json_input_var_fh)
print('json_input_var_data=',json_input_var_data)

print("Summary of JSON variable input: ",json.dumps(json_input_var_data,indent=4,sort_keys=True))

top_level_keys=json_input_var_data.keys()
print('Top level JSON variable keys=',top_level_keys)

for key_now in json_input_var_data.iteritems():
  print('processing key_now[0]=',key_now[0])
  key_now0=key_now[0]
  if(key_now0=="defaults"):
    list_new=(json_input_var_data[key_now0])
    for l in list_new:
      if(l=='info'): info=str(list_new[l])
      elif(l=='area_t'): area_t=list_new[l]
      elif(l=='area_u'): area_u=list_new[l]
      #elif(l=='grid'): grid=str(list_new[l])
      #elif(l=='grid_label'): grid_label=str(list_new[l])
      #elif(l=='vertical_interpolation_method'): vertical_interpolation_method=str(list_new[l])
      else: raise SystemExit('Unknown defaults,',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  elif(key_now0==dvar):
    print("Found required output variable:",dvar)
    list_new=(json_input_var_data[key_now0])
    for l in list_new:
      #print(l)
      if(l=='info'): info=str(list_new[l])
      elif(l=='area_t'): 
          if(list_new[l]=='True'): area_t=True
      elif(l=='area_u'): 
          if(list_new[l]=='True'): area_u=True
      elif(l=='inputs'): inputs=string.split(str(list_new[l]))
        #newinputs=string.split(inputs)
        #print('inputs=',inputs)
        #print('newinputs=',newinputs)
        #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
      elif(l=='realm'): realm=str(list_new[l])
#      elif(l=='diag_dims'): diag_dims=string.split(str(list_new[l]))
      elif(l=='units'): units=str(list_new[l])
      elif(l=='table'): table=str(list_new[l])
      elif(l=='ovars'): ovars=string.split(str(list_new[l]))
      elif(l=='varStructure'): varStructure=list_new[l]
      elif(l=='positive'): positive=list_new[l]
      elif(l=='output_type'): output_type=list_new[l]
      elif(l=='grid'): grid=str(list_new[l])
      elif(l=='grid_label'): grid_label=str(list_new[l])
      else: raise SystemExit('Unknown variable metadata',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  else:
    print("hello")
print('units=',units)

print('printDefinedDiagnostics=',printDefinedDiagnostics)
if(printDefinedDiagnostics):
  print("Alphabetically ordered List of currently loaded diagnostis (varable/unit):")
  for key_now in sorted(json_input_var_data.iteritems(),reverse=False):
    if(key_now[0]!="defaults"):
      #print(key_now)
      #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
      list_new=(json_input_var_data[key_now[0]])
      #print(list_new)
      for l in list_new:
        if(l=='units'):
          print(key_now[0],list_new[l])
  raise SystemExit('Finished writing current set.')

#print(frequency)

#raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

#frequency='month'
#realm,table,inputs,units,ovars,area_t,area_u,diag_dims,grid_label,grid,vertical_interpolation_method,varStructure=grab_var_meta(dvar,frequency)

#if(dvar=='thetao'):
#  inputs=['temp']
#  units='degC'
#elif(dvar=='so'):
#  inputs=['salt']
#  units='0.001'
#elif(dvar=='umo' or dvar=='vmo'):
#  units='10^9 kg s-1'

if(Forecast):
  cdtime.DefaultCalendar=cdtime.JulianCalendar
else:
  #cdtime.DefaultCalendar=cdtime.GregorianCalendar
  cdtime.DefaultCalendar=cdtime.NoLeapCalendar

cmor.setup(inpath='Tables',netcdf_file_action=cmor.CMOR_REPLACE_4,logfile=cmorlogfile)

#print(dvar,file=fh_printfile)

#print(inputs,file=fh_printfile)
#raise SystemExit('Forced exit.')
#raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
#dfp_defs='dfp_csiro-gfdl.json'
cmor.dataset_json(dfp_defs)
json_data=open(dfp_defs).read()
#pprint.pprint(json_data,width=1)
dfp_data=json.loads(json_data)
institution_id=dfp_data['institution_id']
source_id=dfp_data['source_id']
experiment_id=dfp_data['experiment_id']

#cafe_experiment=os.environ.get('CAFE_EXPERIMENT')

#if not cafe_experiment:
#  raise SystemExit('Must set ENVIRONMENT VARIABLE CAFE_EXPERIMENT.')

#if not 'realisation' in locals():
#  if(cafe_experiment == 'v0'):
#    realisation='1'
#  elif(cafe_experiment == 'v1'):
#    realisation='2'
#  elif(cafe_experiment == 'v2'):
#    realisation='3'
#  elif(cafe_experiment == 'p0'):
#    pass
#    #realisation=ens
#  else:
#    raise SystemExit('cafe_experiment not known.')

#if(cafe_experiment == 'p0'):
#  pass
#else:
#  initialisation='1'
#  realisation='1'

#defaults
if not 'realisation' in locals(): realisation=1
if not 'initialisation' in locals(): initialisation=1
if not 'physics' in locals(): physics=1
if not 'forcings' in locals(): forcings=1

ripf='r'+str(realisation)+'i'+str(initialisation)+'p'+str(physics)+'f'+str(forcings)

#table='Omon'

if(ReGrid):
  grid='ESMPy regridded to (90x144 latxlon)'
  grid_label='gr1'

  #fh=netCDF4.Dataset('/short/v14/lxs599/coupled_model/feb17a/OUTPUT/atmos_month_0001_01.nc')

  #fh=cdms2.open('/short/v14/lxs599/coupled_model/feb17a/OUTPUT/atmos_month_0001_01.nc')
  #data=fh.variables['h500']

  fh=cdms2.open('/short/v14/lxs599/coupled_model/feb17a/OUTPUT/ocean_month_0001_01.nc')
  data=fh.variables['mld']

  ingrid=data.getGrid()
  #print('ingrid=',file=fh_printfile)
  #raise SystemExit('Forced exit.')
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  #print('ingrid=',ingrid,file=fh_printfile)

  #print(data,file=fh_printfile)
  outgrid=cdms2.createUniformGrid(-88.875, 72, 2.5, 0, 144, 2.5)

  print('outgrid=',outgrid,file=fh_printfile)

  #print(outgrid.getAxisList(),file=fh_printfile)

  #lat = outgrid.getLatitude() 
  #print(lat,file=fh_printfile)

  #k=cdms2.regrid(a,regridTool='esmf',regridMethod='linear', coordSys='deg', diag={}, periodicity=1)
  regridfunc = Regridder(ingrid,outgrid)
  #newdata=regridFunc(data)

  #newdata=data.regrid(outgrid)
  newdata=regridfunc(data)
  print('newdata.shape=',newdata.shape,file=fh_printfile)
  #raise SystemExit('Forced exit.')
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

elif(levs=='gn1'):
  grid_label='gn1'
  grid='3D vars level 0,3,5 using C-indexing'
elif(levs=='gn2'):
  grid_label='gn2'
  grid='3D vars level 0,3 using C-indexing'
elif(levs=='gn3'):
  grid_label='gn3'
  grid='3D vars level 0,35,36 using C-indexing'
elif(levs=='gn5'):
  grid_label='gn5'
  grid='3D vars use plev5'
elif(levs=='gn10'):
  grid_label='gn10'
  grid='3D vars use plev10'
elif(levs=='gn17'):
  grid_label='gn17'
  grid='3D vars use plev17'
#else:
#  grid_label='gn'
#  grid='native grid'

if(realm=='atmos' and (varStructure=='time_plev_lat_lon' or varStructure=='time_reducedplev_lat_lon')):
#dvar=='ta5' or dvar=='zg5' or dvar=='ua5' or dvar=='va5' or dvar=='hus5' or dvar=='hur5' or dvar=='pv5' or dvar=='divg5' or dvar=='vort5' or \
#dvar=='ta10' or dvar=='zg10' or dvar=='ua10' or dvar=='va10' or dvar=='hus10' or dvar=='hur10' or dvar=='pv10' or dvar=='divg10' or dvar=='vort10' or \
#dvar=='ta17' or dvar=='zg17' or dvar=='ua17' or dvar=='va17' or dvar=='hus17' or dvar=='hur17' or dvar=='p17' or dvar=='div17' or dvar=='vor17' \
#):
  nlev2=1 #ps needed
  levels2=0 #ps needed

if(dvar=='ta5' or dvar=='zg5' or dvar=='ua5' or dvar=='va5' or dvar=='hus5' or dvar=='hur5' or dvar=='pv5' or dvar=='divg5' or dvar=='vort5'):
  grid_label='gn5'
  grid='3D vars use plev5'

elif(dvar=='ta10' or dvar=='zg10' or dvar=='ua10' or dvar=='va10' or dvar=='hus10' or dvar=='hur10' or dvar=='pv10' or dvar=='divg10' or dvar=='vort10'):
  grid_label='gn10'
  grid='3D vars use plev10'

elif(dvar=='ta17' or dvar=='zg17' or dvar=='ua17' or dvar=='va17' or dvar=='hus17' or dvar=='hur17' or dvar=='pv17' or dvar=='divg17' or dvar=='vort17'):
  grid_label='gn17'
  grid='3D vars use plev17'

today=date.today()
t=today.timetuple()
#print('today=',today,file=fh_printfile)
#for i in t:
#  print('i=',i,file=fh_printfile)
#version='v20170315'

if not 'version' in locals(): version='v'+str('{0:04d}'.format(t[0])) + str('{0:02d}'.format(t[1])) + str('{0:02d}'.format(t[2]))

odir=create_odirs(ovars,institution_id,source_id,experiment_id,ripf,table,grid_label,version)

#print('odir=',odir,file=fh_printfile)
#raise SystemExit('Forced exit.')
#raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

#odir='CMIP6/CMIP/'+institution_id+'/'+source_id+'/'+experiment_id+'/'+ripf+'/'+table+'/'+dvar+'/'+grid_label+'/'+version

#print(mbeg,file=fh_printfile)

#mbeg=2 #temporary
#mend=12 #temporary

#mbeg=1 #temporary
#mend=12 #temporary

#season='SON' #temporary
#season='JJA' #temporary
#season='DJF' #temporary

#season='MON' #temporary
#season='MAM' #temporary
#season='ANN' #temporary

# OUTPUT FILE STUFF USED TO BE HERE MOVED DOWN TO PRIOR TO DATA WRITES...

cmor.set_cur_dataset_attribute('grid_label',grid_label)
cmor.set_cur_dataset_attribute('grid',grid)
cmor.set_cur_dataset_attribute('realization',str(realisation))
cmor.set_cur_dataset_attribute('physics',str(physics))
cmor.set_cur_dataset_attribute('initialization_index',str(initialisation))
cmor.set_cur_dataset_attribute('realization_index',str(realisation))
cmor.set_cur_dataset_attribute('version',version)

if(Forecast):
  calendar='julian'
else:
  calendar='noleap'

cmor.set_cur_dataset_attribute('calendar',calendar)
cmor.set_cur_dataset_attribute('importance',importance)
cmor.set_cur_dataset_attribute('season',season)

if 'vertical_interpolation_method' in locals(): cmor.set_cur_dataset_attribute('vertical_interpolation_method',vertical_interpolation_method)
if(cafe_experiment == 'v0'):
  cmor.set_cur_dataset_attribute('history','input data from experiment raijin:/g/data1/v14/coupled_model/v1/OUTPUT')
elif(cafe_experiment == 'v1'):
  cmor.set_cur_dataset_attribute('history','input data from experiment raijin:/g/data1/v14/coupled_model/v1/OUTPUT')
elif(cafe_experiment == 'v2'):
  cmor.set_cur_dataset_attribute('history','input data from experiment raijin:/short/v14/lxs1099/coupled_model/feb17a/OUTPUT')

if(table=='fx' or table=='Ofx'):
  fileA='TablesTemplates/CMIP6_'+table+'.json'
  fileB='cmor/Tables/CMIP6_'+table+'.json'
  if filecmp.cmp(fileA,fileB):
    pass
  else:
    copyfile(fileA,fileB)
else:
  if(season=='MON'):
    os.system('awk -v number=35.00000 -f process_CMIP6.awk TablesTemplates/CMIP6_'+table+'.json > cmor/Tables/CMIP6_'+table+'.json')
    #awk -v number=35.00000 -f process_CMIP6.awk TablesTemplates/CMIP6_Amon.json
  else:
    os.system('awk -v number=400.00000 -f process_CMIP6.awk TablesTemplates/CMIP6_'+table+'.json > cmor/Tables/CMIP6_'+table+'.json')
    #call(['awk','-v number=400.00000 -f process_CMIP6.awk TablesTemplates/CMIP6_Amon.json'])
    #awk -v number=400.00000 -f process_CMIP6.awk TablesTemplates/CMIP6_Amon.json

fileA='TablesTemplates/CMIP6_coordinate.json'
fileB='cmor/Tables/CMIP6_coordinate.json'
if filecmp.cmp(fileA,fileB):
  pass
else:
  copyfile(fileA,fileB)

fileA='TablesTemplates/CMIP6_CV.json'
fileB='cmor/Tables/CMIP6_CV.json'
if filecmp.cmp(fileA,fileB):
  pass
else:
  copyfile(fileA,fileB)

tables=[]
#tables.append(cmor.load_table('cmor/Tables/CMIP6_Omon.json'))
#tables.append(cmor.load_table('cmor/Tables/CMIP6_Amon.json'))
tables.append(cmor.load_table('cmor/Tables/CMIP6_'+table+'.json'))

#print(inputs)
#print(type(inputs))

#raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

tables.append(cmor.load_table('cmor/Tables/CMIP6_grids.json'))
tables.append(cmor.load_table('cmor/Tables/CMIP6_coordinate.json'))

if os.path.exists('CMIP5/ancillary_files/grid_spec.auscom.20110618.nc'):
  xfh=netCDF4.Dataset('CMIP5/ancillary_files/grid_spec.auscom.20110618.nc')
elif os.path.exists('/home/mon137/cafepp/cafepp/CMIP5/ancillary_files/grid_spec.auscom.20110618.nc'):
  xfh=netCDF4.Dataset('/home/mon137/cafepp/cafepp/CMIP5/ancillary_files/grid_spec.auscom.20110618.nc')
else:
  xfh=netCDF4.Dataset('/g/data/p66/mac599/CMIP5/ancillary_files/grid_spec.auscom.20110618.nc')
if(area_t):
  #afh=netCDF4.Dataset('/short/v19/mtc599/ao_am2/sep16f/OUTPUT/ocean_month_0001_01.nc')
  #area_t=afh.variables['area_t']
   area_t=xfh.variables['area_T'] #check ok
if(area_u):
  #afh=netCDF4.Dataset('/short/v19/mtc599/ao_am2/sep16f/OUTPUT/ocean_month_0001_01.nc')
  #area_u=afh.variables['area_u']
   area_u=xfh.variables['area_C'] #check ok

#if Clim:
#  label='monthclim'
#elif Anom:
#  label='monthanom'
#else:
#  label='month'

#if(Clim and Anom):
#  raise SystemExit('Cant have Clim and Anom.')

#ebeg=erange[0]
#eend=erange[-1]

#raise SystemExit('Forced exit.')
#raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

print(ybeg)
print(yend)

print(ybeg_min)
print(yend_max)

if(ybeg<ybeg_min or ybeg>yend_max or yend<ybeg_min or yend>yend_max):
  raise SystemExit('Problem with ybeg/yend ybeg_min/yend_max',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

#if(cbeg<ybeg_min or cbeg>yend_max or cend<ybeg_min or cend>yend_max):
#  raise SystemExit('Problem with ybeg/yend cbeg/cend.')

#if(cbeg>cend):
#  raise SystemExit('Problem with cbeg/cend.')

#idirc='/short/v14/mac599/coupled/ao_am2/coupled_da'
#ifilc=realm+'_'+label+'_'+dvar+'_'+str('{0:04d}'.format(cbeg))+'-'+str('{0:04d}'.format(cend))+'_e1.nc'

#if(Clim):
#  if (cbeg == cend):
#    #ystr='_'+str(ybeg)
#    ystr='_'+str('{0:04d}'.format(cbeg))
#  else:
#    ystr='_'+str('{0:04d}'.format(cbeg))+'-'+str('{0:04d}'.format(cend))
#else:
#  if (ybeg == yend):
#    #ystr='_'+str(ybeg)
#    ystr='_'+str('{0:04d}'.format(ybeg))
#  else:
#    ystr='_'+str('{0:04d}'.format(ybeg))+'-'+str('{0:04d}'.format(yend))
#
#if (ebeg == eend):
#  estr='_e'+str(ebeg)
#else:
#  estr='_e'+str(ebeg)+'-'+str(eend)

nmy=12

total_months_beg_to_end=(nmy-mbeg)+1 + (yend-ybeg+1-2)*nmy + mend

ybeg_now=ybeg
yend_now=yend

mbeg_now=mbeg
mend_now=mend

print('total_months_beg_to_end=',total_months_beg_to_end,file=fh_printfile)

print('ybeg_now=',ybeg_now,' yend_now=',yend_now,file=fh_printfile)

sstr,times_in_season,tindex_select_maxyears_by_nmy_0or1=filemonth_index(season,ybeg_now,yend_now,mbeg_now,mend_now,fh_printfile) #MON special case where times_in_season=1, so always reading/writing one month at a time...

#iii=np.arange(total_months_beg_to_end).reshape((yend-ybeg+1),12)
#tindex_select_maxyears_by_nmy_0or1=np.zeros(iii.shape)
#tindex_select_maxyears_by_nmy_0or1[index_start]=1
#tindex_select_maxyears_by_nmy_0or1[index_end]=1
#print(iii,file=fh_printfile)
print('tindex_select_maxyears_by_nmy_0or1=',tindex_select_maxyears_by_nmy_0or1,file=fh_printfile)

print('total_months_beg_to_end,total_months_beg_to_end,index_start,end=',total_months_beg_to_end,total_months_beg_to_end,file=fh_printfile)
#,index_start,index_end)
#raise SystemExit('Forced exit.')
#raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

month_in_file_total_months_beg_to_end=np.ones(total_months_beg_to_end,dtype=np.int) #132, this will have to change depending on the layout of the input files...

y=ybeg

if(Forecast):
  idir_extra='/'+str('{0:04d}'.format(y))+str('{0:02d}'.format(mbeg))+str('{0:02d}'.format(1)) #probably can use 
else:
  idir_extra=''

if(Forecast):
  ifil=realm+'_'+frequency+'_'+str('{0:04d}'.format(y))+'_'+str('{0:02d}'.format(mbeg))+'.nc'
else:
  ifil=realm+'_'+frequency+'_'+str('{0:04d}'.format(y))+'_'+str('{0:02d}'.format(1))+'.nc' #always 1

print(y,' ',idir+idir_extra+'/'+ifil,file=fh_printfile)
#raise SystemExit('Forced exit.')
#raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

f=netCDF4.Dataset(idir+idir_extra+'/'+ifil)
time=f.variables['time']

#here var_dims is just dummy as complete requirements depend on the output variable definition.
if(realm=='ocean' and ( varStructure=='time_lat_lon' or varStructure=='time_depth_lat_lon' or varStructure=='time_reduceddepth_lat_lon')):
  ivar=f.variables[inputs[0]]
  var_dims=f.variables[inputs[0]].dimensions
  var_size=f.variables[inputs[0]].shape
elif(realm=='atmos' and ( varStructure=='time_lat_lon' or varStructure=='time_plev_lat_lon' or varStructure=='time_reducedplev_lat_lon')):
  ivar=f.variables[inputs[0]]
  var_dims=f.variables[inputs[0]].dimensions
  var_size=f.variables[inputs[0]].shape
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
elif(dvar=='acc_drake' or dvar=='acc_africa'):
  ivar=f.variables['tx_trans_int_z']
  var_dims=f.variables['tx_trans_int_z'].dimensions
  var_size=f.variables['tx_trans_int_z'].shape
  #MustHaveAllLevs(LevXtrct)
elif(dvar=='mozmbq'):
  ivar=f.variables['ty_trans_int_z']
  var_dims=f.variables['ty_trans_int_z'].dimensions
  var_size=f.variables['ty_trans_int_z'].shape
  #MustHaveAllLevs(LevXtrct)
elif(dvar=='aabw'):
  ivar=f.variables['ty_trans']
  var_dims=f.variables['ty_trans'].dimensions
  var_size=f.variables['ty_trans'].shape
  #MustHaveAllLevs(LevXtrct)
elif(dvar=='nadw'):
  ivar=f.variables['ty_trans']
  var_dims=f.variables['ty_trans'].dimensions
  var_size=f.variables['ty_trans'].shape
  #MustHaveAllLevs(LevXtrct)
elif(dvar=='pp'):
  ivar=f.variables['pprod_gross']
  var_dims=f.variables['pprod_gross'].dimensions
  var_size=f.variables['pprod_gross'].shape
  depth_edges=f.variables['st_edges_ocean']
elif(dvar=='nflux'):
  ivar=f.variables['stf07']
  var_dims=f.variables['stf07'].dimensions
  var_size=f.variables['stf07'].shape
  depth_edges=f.variables['st_edges_ocean']
elif(dvar=='ep'):
  ivar=f.variables['det']
  var_dims=f.variables['det'].dimensions
  var_size=f.variables['det'].shape
  depth_edges=f.variables['st_edges_ocean']
elif(dvar=='nino34' or dvar=='iod'):
  #print('hello',file=fh_printfile)
  ivar=f.variables['temp']
  var_dims=f.variables['temp'].dimensions
  var_size=f.variables['temp'].shape
elif(dvar=='ssh'):
  ivar=f.variables['temp']
  var_dims=f.variables['temp'].dimensions
  var_size=f.variables['temp'].shape
  depth_edges=f.variables['st_edges_ocean']
elif(dvar=='moc' or dvar=='moc_atlantic' or dvar=='moc_pacific' or dvar=='moc_indian'):
  #ivar=f.variables['v']
  #var_dims=f.variables['v'].dimensions
  #var_size=f.variables['v'].shape
  ivar=f.variables['tx_trans']
  var_dims=f.variables['tx_trans'].dimensions
  var_size=f.variables['tx_trans'].shape
  #MustHaveAllLevs(LevXtrct)
  depth_edges=f.variables['st_edges_ocean']
elif(dvar=='shice_cover' or dvar=='nhice_cover'):
  ivar=f.variables['CN']
  var_dims=f.variables['CN'].dimensions
  var_size=f.variables['CN'].shape
elif(dvar=='nhbi'):
  ivar=f.variables['h500']
  var_dims=f.variables['h500'].dimensions
  var_size=f.variables['h500'].shape
elif(dvar=='rws'):
  ivar=f.variables['ucomp']
  var_dims=f.variables['ucomp'].dimensions
  var_size=f.variables['ucomp'].shape
  # (dvar=='tos' or dvar=='thetao' or dvar=='so' or dvar=='uo' or dvar=='vo' or dvar=='volcello' or dvar=='areacello' or dvar=='thkcello' or dvar=='sftof' or dvar=='deptho' or dvar=='isothetao16c' or dvar==dvar=='isothetao20c' or dvar=='isothetao22c' or dvar=='thetao100m' or dvar=='so100m' or dvar=='uo100m' or dvar=='vo100m')):
  #ivar=f.variables['temp']
  #var_dims=f.variables['temp'].dimensions
  #var_size=f.variables['temp'].shape

  #inputs=['temp','salt']
  #print(inputs)
  #print(len(inputs))
  #print(type(inputs))
  #print(inputs[0])
  #print(inputs[1])
  #s=""
  #j=s.join(inputs[:])
  #print(j)

elif(dvar=='zg500'):
  ivar=f.variables['h500']
  var_dims=f.variables['h500'].dimensions
  var_size=f.variables['h500'].shape
elif(dvar=='psl'):
  ivar=f.variables['slp']
  var_dims=f.variables['slp'].dimensions
  var_size=f.variables['slp'].shape
elif(dvar=='ps'):
  ivar=f.variables['ps']
  var_dims=f.variables['ps'].dimensions
  var_size=f.variables['ps'].shape
#elif(dvar=='zg'):
#  ivar=f.variables['hght']
#  var_dims=f.variables['hght'].dimensions
#  var_size=f.variables['hght'].shape
elif(dvar=='temptotal'):
  ivar=f.variables['temp_total']
  var_dims=f.variables['temp_total'].dimensions
  var_size=f.variables['temp_total'].shape
elif(dvar=='salttotal'):
  ivar=f.variables['salt_total']
  var_dims=f.variables['salt_total'].dimensions
  var_size=f.variables['salt_total'].shape
elif(dvar=='ua' or dvar=='ua5' or dvar=='ua10' or dvar=='ua17' or \
  dvar=='va' or dvar=='va5' or dvar=='va10' or dvar=='va17' or \
  dvar=='ta' or dvar=='ta5' or dvar=='ta10' or dvar=='ta17' or \
  dvar=='hur' or dvar=='hur5' or dvar=='hur10' or dvar=='hur17' or \
  dvar=='hus' or dvar=='hus5' or dvar=='hus10' or dvar=='hus17' or \
  dvar=='zg' or dvar=='zg5' or dvar=='zg10' or dvar=='zg17'):
  ivar=f.variables[inputs[0]]
  var_dims=f.variables[inputs[0]].dimensions
  var_size=f.variables[inputs[0]].shape
  var_size2=f.variables[inputs[1]].shape
elif(dvar=='tauu' or dvar=='tauv' or dvar=='pr'):
  ivar=f.variables[inputs[0]]
  var_dims=f.variables[inputs[0]].dimensions
  var_size=f.variables[inputs[0]].shape
elif(dvar=='pv'):
  ivar=f.variables['pv']
  var_dims=f.variables['pv'].dimensions
  var_size=f.variables['pv'].shape
elif(dvar=='divg'):
  ivar=f.variables['divg']
  var_dims=f.variables['divg'].dimensions
  var_size=f.variables['divg'].shape
elif(dvar=='vort'):
  ivar=f.variables['vort']
  var_dims=f.variables['vort'].dimensions
  var_size=f.variables['vort'].shape
elif(dvar=='mlotst'):
  ivar=f.variables['mld']
  var_dims=f.variables['mld'].dimensions
  var_size=f.variables['mld'].shape
elif(dvar=='mlotstsq'):
  ivar=f.variables['mld_sq']
  var_dims=f.variables['mld_sq'].dimensions
  var_size=f.variables['mld_sq'].shape
elif(dvar=='umo'):
  ivar=f.variables['tx_trans']
  var_dims=f.variables['tx_trans'].dimensions
  var_size=f.variables['tx_trans'].shape
elif(dvar=='vmo'):
  ivar=f.variables['ty_trans']
  var_dims=f.variables['ty_trans'].dimensions
  var_size=f.variables['ty_trans'].shape
elif(dvar=='cl'):
  ivar=f.variables['cld_amt']
  var_dims=f.variables['cld_amt'].dimensions
  var_size=f.variables['cld_amt'].shape
elif(dvar=='msftyyz'):
  ivar=f.variables['ty_trans']
  var_dims=f.variables['ty_trans'].dimensions
  var_size=f.variables['ty_trans'].shape
elif(dvar=='mfo'):
  ivar=f.variables['tx_trans']
  var_dims=f.variables['tx_trans'].dimensions
  var_size=f.variables['tx_trans'].shape
elif(dvar=='so' or dvar=='sos'):
  ivar=f.variables['salt']
  var_dims=f.variables['salt'].dimensions
  var_size=np.array(f.variables['salt'].shape)
elif(dvar=='rws500'):
  ivar=f.variables['ucomp']
  var_dims=f.variables['ucomp'].dimensions
  var_size=f.variables['ucomp'].shape
elif(dvar=='nhbi'):
  ivar=f.variables['h500']
  var_dims=f.variables['h500'].dimensions
  var_size=f.variables['h500'].shape
#elif(dvar=='ta10'):
#  ivar=f.variables['temp']
#  var_dims=f.variables['temp'].dimensions
#  var_size=f.variables['temp'].shape
else:
  ivar=f.variables[dvar]
  var_dims=f.variables[dvar].dimensions
  var_size=f.variables[dvar].shape

nvar_dims=len(var_dims)

print('var_size=',var_size,file=fh_printfile)
print(var_dims,file=fh_printfile)
print(nvar_dims,file=fh_printfile)
print('dvar=',dvar,file=fh_printfile)
#raise SystemExit('Forced exit.')
#raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

if(nvar_dims == 4):
    nlev=var_size[1]
    nlat=var_size[2]
    nlon=var_size[3]
elif(nvar_dims == 3):
    nlat=var_size[1]
    nlon=var_size[2]
else:
    nlat=0
    nlon=0

nlev=0
levels=0

print('var_size=',var_size,file=fh_printfile)
print('var_dims=',var_dims,file=fh_printfile)

if(levs=='gn1'):
  levels=[0,3,5]
  nlev=len(levels)
elif(levs=='gn2'):
  levels=[0,3]
  nlev=len(levels)
elif(levs=='gn3'):
  levels=[0,35,36]
  #levels=[1,5,36]
  nlev=len(levels)
#elif(levs=='gn5'):
#  levels=[xxx]
#  #levels=[1,5,36]
#  nlev=len(levels)
else:
  #levels=np.range(0,var_size[1])
  levels=np.array(range(0,var_size[1]-0))
  nlev=len(levels)

if(realm == 'ocean' and ( varStructure=='time_lat_lon' or varStructure=='time')):
  #or dvar=='tos' or dvar=='sos' or dvar=='sftof' or dvar=='nino34' or dvar=='iod'):
  levels=0
  nlev=1
elif(realm=='atmos' and varStructure=='time_lat_lon'):
  #dvar=='zg500' or dvar=='psl' or dvar=='ps' or dvar=='rws500' or dvar=='tauu' or dvar=='tauv' or dvar=='pr'):
  levels=0
  nlev=0

cmor.set_table(tables[1])

ibeg=0

refString='days since 0001-01-01'

#raise SystemExit('Forced exit.')
#raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

if(table=='fx' or table=='Ofx'):
  print('As this is a table fx parameter, all time information will be ignored.',file=fh_printfile)
  input_fhs={}
  input_fhs[0]=netCDF4.Dataset(idir+'/'+realm+'_'+frequency+'_'+str('{0:04d}'.format(ybeg_now))+'_'+'01'+'.nc')
else:
  ybeg_now=ybeg
  yend_now=yend

  tindex=0
  input_files={}
  input_fhs={}
  for y in range(ybeg_now,yend_now+1):
    mend_now=1 #1 files per year of 12 months each.
    if(y==ybeg_now):
      mbeg_now=1 #need to fix
      mend_now=12
      mbeg_now=mbeg
    elif(y==yend_now):
      mbeg_now=1
      mend_now=mend #12 files per year of 1 months each.
    else:
      mbeg_now=1
      mend_now=12 #12 files per year of 1 months each.
    #print(mbeg_now,mend_now,file=fh_printfile)
    #raise SystemExit('Forced exit.')
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

    if(not Forecast):
      mbeg_now=1 #always 1 for 12 months per file.
      mend_now=1 #always 1 for 12 months per file.

    for m in range(mbeg_now,mend_now+1):
      if(Forecast): #has 1 month per file...
        idir_extra='/'+str('{0:04d}'.format(y))+str('{0:02d}'.format(m))+str('{0:02d}'.format(1))
      else:
        idir_extra=''
      iend=ibeg+12
      print(' y=',y,' m=',m,' mend_now=',mend_now,' ibeg=',ibeg,',',' iend=',iend,file=fh_printfile)
      ifila=realm+'_'+frequency+'_'+str('{0:04d}'.format(y))+'_'+str('{0:02d}'.format(m))+'.nc'
      print(y,' ',idir+idir_extra+'/'+ifila,file=fh_printfile)
      input_files[tindex]=idir+idir_extra+'/'+ifila
      if not os.path.exists(idir+idir_extra+'/'+ifila):
        raise SystemExit('Missing '+idir+idir_extra+'/'+ifila+'.')
      input_fhs[tindex]=netCDF4.Dataset(input_files[tindex])
      tindex+=1

  print('input files=',input_files,file=fh_printfile)
  #print(len(input_files),file=fh_printfile)
  print('tindex_select_maxyears_by_nmy_0or1=',tindex_select_maxyears_by_nmy_0or1,file=fh_printfile)
  #print(tindex_select_maxyears_by_nmy_0or1.shape,file=fh_printfile)

  #raise SystemExit('Forced exit.')
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  findex_select_maxyears_by_nmy_b1_withminus1s=np.copy(tindex_select_maxyears_by_nmy_0or1)

  if(Forecast):
    findex_select_maxyears_by_nmy_b1_withminus1s=findex_select_maxyears_by_nmy_b1_withminus1s*0-1 #set to -1, means no file at this position in year,month array.
  else:
    findex_select_maxyears_by_nmy_b1_withminus1s=findex_select_maxyears_by_nmy_b1_withminus1s*0-1

  print('findex_select_maxyears_by_nmy_b1_withminus1s=',findex_select_maxyears_by_nmy_b1_withminus1s,file=fh_printfile)

  yindex_select_maxyears_by_nmy=np.copy(tindex_select_maxyears_by_nmy_0or1)

  if(Forecast): #this is where picks up granularity of files, ie whether 1, 3, 12 months per year.
    fff=0
    for y in range(ybeg_now,yend_now+1):
  
      mend_now=1 #1 files per year of 12 months each.
      if(y==ybeg_now):
        #mbeg_now=1 #need to fix
        mbeg_now=mbeg
        mend_now=12
      elif(y==yend_now):
        mbeg_now=1
        mend_now=mend #12 files per year of 1 months each.
      else:
        mbeg_now=1
        mend_now=12 #12 files per year of 1 months each.
      for m in range(mbeg_now,mend_now+1):
        print('y,fff,y*,m*,mbeg,mend_now=',y,fff,y-ybeg_now,m-mbeg_now,mbeg_now,mend_now,file=fh_printfile)
        if(tindex_select_maxyears_by_nmy_0or1[y-ybeg_now,m-1]!=0):
          findex_select_maxyears_by_nmy_b1_withminus1s[y-ybeg_now,m-1]=tindex_select_maxyears_by_nmy_0or1[y-ybeg_now,m-1]*fff + 1
        else:
          findex_select_maxyears_by_nmy_b1_withminus1s[y-ybeg_now,m-1]=0
        fff+=1
  else:
    y=ybeg_now
    for fff in range(len(input_files)):
      print(fff,file=fh_printfile)
      #if(tindex_select_maxyears_by_nmy_0or1[y-ybeg_now,m-1]!=0):
      #  findex_select_maxyears_by_nmy_b1_withminus1s[fff,:]=tindex_select_maxyears_by_nmy_0or1[fff,:]*fff + 1
      #else:
      #  findex_select_maxyears_by_nmy_b1_withminus1s[y-ybeg_now,m-1]=0
      findex_select_maxyears_by_nmy_b1_withminus1s[fff,:]=(tindex_select_maxyears_by_nmy_0or1[fff,:]*fff + 1)*tindex_select_maxyears_by_nmy_0or1[fff,:]
      y+=1

  print('findex_select_maxyears_by_nmy_b1_withminus1s=',findex_select_maxyears_by_nmy_b1_withminus1s,file=fh_printfile)

  #raise SystemExit('Forced exit.')
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  tindex_select_maxyears_by_nmy_0or1_flat=tindex_select_maxyears_by_nmy_0or1.reshape((yend_now-ybeg_now+1)*12)
  print('tindex_select_maxyears_by_nmy_0or1_flat=',tindex_select_maxyears_by_nmy_0or1_flat,file=fh_printfile)
  #raise SystemExit('Forced exit.')
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  numtims=int(np.sum(tindex_select_maxyears_by_nmy_0or1_flat))

  print('number of times used in each season definition, times_in_season=',times_in_season,file=fh_printfile)
  print('total number of times (months) read in including any partial begin and end year, total_months_beg_to_end=',total_months_beg_to_end,file=fh_printfile)
  print('number of times used from input file, numtims=',numtims,file=fh_printfile)
#  print('total number of seasons written out, numseas=',numseas,file=fh_printfile)

#file_index_maxyears_by_nmy_b1_withminus1s is an array year,month. elements corresonding to the valid input months/years are inserted (0...max-1), a -1 means that no file is present or included. file_index_maxyears_by_nmy_b1_withminus1s_flat is vector version of file_index_maxyears_by_nmy_b1_withminus1s.
#file_index_maxyears_by_nmy_b1_nominus1s_flat is list from 0...max-1 number of files, gets rid of any -1s indicating missing months.
#month_index_ntims is an vector year...month with ONLY valid year,month (values going from 0..11 only corresponding to month.
#year_index_ntims, similar to month_index_ntims, only now years, actual years corresponding to each of the months in month_index_ntims

  file_index_maxyears_by_nmy_b1_withminus1s,month_index_ntims=np.where(tindex_select_maxyears_by_nmy_0or1==1)

  print('file_index_maxyears_by_nmy_b1_withminus1s=',file_index_maxyears_by_nmy_b1_withminus1s,file=fh_printfile)
  print('file_index_maxyears_by_nmy_b1_withminus1s.size=',file_index_maxyears_by_nmy_b1_withminus1s.size,file=fh_printfile)

  year_index_ntims=file_index_maxyears_by_nmy_b1_withminus1s+ybeg_now

  file_index_maxyears_by_nmy_b1_withminus1s=findex_select_maxyears_by_nmy_b1_withminus1s.astype(int) #try, why do I overwrite definition above?

  file_index_maxyears_by_nmy_b1_withminus1s=np.where(file_index_maxyears_by_nmy_b1_withminus1s>0,file_index_maxyears_by_nmy_b1_withminus1s+0,file_index_maxyears_by_nmy_b1_withminus1s) #add 1 to values > 0

  print('file_index_maxyears_by_nmy_b1_withminus1s=',file_index_maxyears_by_nmy_b1_withminus1s,file=fh_printfile)
  print('file_index_maxyears_by_nmy_b1_withminus1s.size=',file_index_maxyears_by_nmy_b1_withminus1s.size,file=fh_printfile)

  #raise SystemExit('Forced exit.')
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  print('month_index_ntims=',month_index_ntims,file=fh_printfile)
  print('month_index_ntims.size=',month_index_ntims.size,file=fh_printfile)
  print('year_index_ntims=',year_index_ntims,file=fh_printfile)
  print('year_index_ntims.size=',year_index_ntims.size,file=fh_printfile)

  file_index_maxyears_by_nmy_b1_withminus1s_flat=file_index_maxyears_by_nmy_b1_withminus1s.flatten()

  print('file_index_maxyears_by_nmy_b1_withminus1s_flat=',file_index_maxyears_by_nmy_b1_withminus1s_flat,file=fh_printfile)

  file_index_maxyears_by_nmy_b1_nominus1s_flat=file_index_maxyears_by_nmy_b1_withminus1s_flat[np.where(file_index_maxyears_by_nmy_b1_withminus1s_flat>0,True,False)]

  print('file_index_maxyears_by_nmy_b1_nominus1s_flat=',file_index_maxyears_by_nmy_b1_nominus1s_flat,file=fh_printfile)

  locate_file_index_Ntimes_b1_nominus1s_flat=file_index_maxyears_by_nmy_b1_nominus1s_flat[np.where(file_index_maxyears_by_nmy_b1_nominus1s_flat>0)]

  print('locate_file_index_Ntimes_b1_nominus1s_flat=',locate_file_index_Ntimes_b1_nominus1s_flat,file=fh_printfile)
  print('locate_file_index_Ntimes_b1_nominus1s_flat.shape=',locate_file_index_Ntimes_b1_nominus1s_flat.shape,file=fh_printfile)

  cnt_file_index_maxyears_by_nmy_b1_nominus1s_flat=len(locate_file_index_Ntimes_b1_nominus1s_flat)
  print('cnt_file_index_maxyears_by_nmy_b1_nominus1s_flat=',cnt_file_index_maxyears_by_nmy_b1_nominus1s_flat,file=fh_printfile)
  #raise SystemExit('Forced exit.')
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  tbeg=[]
  tend=[]
  tavg=[]
  ind_beg=0
  #will need to improve when ending time is December as will need to increment year by 1 too.
  day1=1

  if(season=='MON'):
    ttt=total_months_beg_to_end
  else:
    ttt=cnt_file_index_maxyears_by_nmy_b1_nominus1s_flat/times_in_season #this should be equal to number of valid months/3

  print('ttt=',ttt,' times_in_season=',times_in_season,file=fh_printfile)

  for n in range(0,ttt):
    #ind_end=ind_beg+times_in_season-1

    if(season=='MON'):
      #ind_end=ind_beg+times_in_season
      ind_end=ind_beg #always 1 month at a time for MON
    else:
      ind_end=ind_beg+times_in_season-1

    #print('n,ind_beg,ind_end,year_beg,month_beg,year_end,month_end=',n,ind_beg,ind_end,year_index_ntims[ind_beg],month_index_ntims[ind_beg],year_index_ntims[ind_end],month_index_ntims[ind_end],file=fh_printfile)

    month_index_beg=month_index_ntims[ind_beg]+1
    year_index_beg=year_index_ntims[ind_beg]

    #print('year,month_index_beg=',year_index_beg,month_index_beg,file=fh_printfile)

    tbeg.append(cdtime.comptime(year_index_beg,month_index_beg,day1).torel(refString).value)
    #print(month_index_ntims[ind_beg],file=fh_printfile)

    if(season=='MON'):
      if(n==0):
        #print('n==0',file=fh_printfile)
        month_index_end=month_index_beg+1
        year_index_end=year_index_beg
      else:
        #print('n!=0',file=fh_printfile)
        month_index_end=month_index_beg+1
        year_index_end=year_index_beg
    elif(season=='ANN'):
      if(n==ttt-1): #last one special
        month_index_end=month_index_ntims[ind_end-1]+1+1+1
        year_index_end=year_index_ntims[ind_end-1]
      else:
        month_index_end=month_index_ntims[ind_end]+1+1
        year_index_end=year_index_ntims[ind_end]
    else:
      if(n==ttt-1): #last one special
        month_index_end=month_index_ntims[ind_end-1]+1+1
        year_index_end=year_index_ntims[ind_end-1]
      else:
        month_index_end=month_index_ntims[ind_end]+1
        year_index_end=year_index_ntims[ind_end]

    if(month_index_end>nmy):
       month_index_end=month_index_end-nmy
       year_index_end+=1

    print('n=',n,' ind_beg=',ind_beg,' ind_end=',ind_end,' year_index_beg=',year_index_beg,' month_index_beg=',month_index_beg,' year_index_end=',year_index_end,' month_index_end=',month_index_end,file=fh_printfile)

    tdelta=1.0
    tdelta=0.0

    #tdelta=0
    #tdelta=1

    tend.append(cdtime.comptime(year_index_end,month_index_end,day1).torel(refString).value-tdelta) #assume in days, -1 gets numer of days of wanted month (ie. prior month without having to know number of days in month)
    #print('tbeg,tend=',tbeg,tend,file=fh_printfile)

    #raise SystemExit('Forced exit.')
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    ind_beg=ind_end+1
    if(season=='MON'):
      ind_beg=ind_end+1
    else:
      ind_beg=ind_end+1

  tbeg=np.array(tbeg)
  tend=np.array(tend)
  tavg=(tbeg+tend)/2.0
  tval_bounds=np.column_stack((tbeg,tend))

  #raise SystemExit('Forced exit.')
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  #print('tbeg,tend,tavg=',tbeg,tend,tavg)
  timestamp_avg=netCDF4.num2date(tavg,units=refString,calendar=calendar)
  timestamp_beg=netCDF4.num2date(tbeg,units=refString,calendar=calendar)
  timestamp_end=netCDF4.num2date(tend,units=refString,calendar=calendar)

  print('timestamp_avg,beg,end:',file=fh_printfile)
  for n in range(0,ttt):
    print(timestamp_avg[n],timestamp_beg[n],timestamp_end[n],file=fh_printfile)

  #print('timestamp_avg=',timestamp_avg,timestamp_beg)

  #raise SystemExit('Forced exit.')
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  #tables[0]=cmor.load_table('cmor/Tables/CMIP6_Amon.json')
  cmor.set_table(tables[0])
  #itime=cmor.axis(table_entry= 'time', length=5, units=refString, coord_vals=tavg[:], cell_bounds=tval_bounds[:], interval=None)
  #itime=cmor.axis(table_entry= 'time', length=5, units=refString, coord_vals=tavg[:], cell_bounds=tval_bounds[:])
  #itime=cmor.axis('time', units=refString, coord_vals=tavg[:], cell_bounds=tval_bounds[:])

  #print('tavg=',tavg,file=fh_printfile)
  #print('tval_bounds=',tval_bounds,file=fh_printfile)

  time_axis_id=cmor.axis('time', units=refString, coord_vals=tavg, cell_bounds=tval_bounds)
  #raise SystemExit('Forced exit.')
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

cmor.set_table(tables[1])

if(realm=='ocean' and ( varStructure=='time_lat_lon' or varStructure=='time_depth_lat_lon')):
  # or dvar=='tos' or dvar=='thetao' or dvar=='sos' or dvar=='uo' or dvar=='vo' or dvar=='mlotst' or dvar=='mlotstsq' or dvar=='umo' or dvar=='vmo' or dvar=='volcello' or dvar=='areacello' or dvar=='sftof' or dvar=='thkcello' or dvar=='deptho' or dvar=='msftyyz' or dvar=='mfo' or dvar=='so' or dvar=='isothetao16c' or dvar=='isothetao20c' or dvar=='isothetao22c'):
  cmor.set_table(tables[0])

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

elif(realm=='ocean' and ( varStructure=='time_reduceddepth_lat_lon')):
  #dvar=='thetao100m' or dvar=='so100m' or dvar=='uo100m' or dvar=='vo100m'):
  cmor.set_table(tables[0])

  zt=xfh.variables['zt']
  zb=xfh.variables['zb']
  nzb=len(zb[:])
  z0=np.zeros((nzb))
  z0[0]=0
  z0[1:nzb]=zb[0:nzb-1]
  zbounds=np.column_stack((z0,zb))
  z=zb-z0

  levels=[0,1,2,3,4,5,6,7,8,9]
  nlev=10

  #ztX=zt[[0,10,20]]
  #zboundsX=zbounds[[0,10,20],:]

#st_ocean = 5, 15, 25, 35, 45, 55, 65, 75, 85, 95 (10 elements)
#st_edges_ocean = 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100 (11 elements)

  print('zt=',zt[:])
  print('zb=',zb[:])
  print('zbounds=',zbounds[:])

  zt=np.array([5, 15, 25, 35, 45, 55, 65, 75, 85, 95])
  zb=np.array([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
  nzb=len(zb[:])
  z0=np.zeros((nzb))
  z0[0]=0
  z0[1:nzb]=zb[0:nzb-1]
  zbounds=np.column_stack((z0,zb))
  z=zb-z0

  print('zt=',zt[:])
  print('zb=',zb[:])
  print('zbounds=',zbounds[:])

  #raise SystemExit('Forced exit.')
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

elif(realm=='atmos' or realm=='ocean'):
  #dvar=='zg500' or dvar=='zg' or dvar=='psl' or dvar=='ps' or dvar=='ua' or dvar=='va' or dvar=='pv' or dvar=='divg' or dvar=='vort' or dvar=='cl' or dvar=='rws500' or dvar=='rws' or dvar=='nhbi' or dvar=='nino34' or dvar=='iod' or dvar=='pp' or dvar=='nflux' or dvar=='ep' or dvar=='ta' or dvar=='ta5' or dvar=='ta10' or dvar=='zg10' or dvar=='ua10' or dvar=='va10' or dvar=='hus10' or dvar=='hur10' or dvar=='hus' or dvar=='hur' or dvar=='ta19' or dvar=='tauu' or dvar=='tauv' or dvar=='pr'):

  if(ReGrid):
    lat_vals = outgrid.getLatitude() 
    lon_vals = outgrid.getLongitude()
  else:
    if(realm=='ocean' and varStructure=='time'):
    #dvar=='nino34' or dvar=='iod' or dvar=='pp' or dvar=='nflux' or dvar=='ep'):
      lat_vals=f.variables['yt_ocean']
      lon_vals=f.variables['xt_ocean']
    else:
      lat_vals=f.variables['lat']
      lon_vals=f.variables['lon']

  min_vals=np.append((1.5*lat_vals[0] - 0.5*lat_vals[1]), (lat_vals[0:-1] + lat_vals[1:])/2)
  max_vals=np.append((lat_vals[0:-1] + lat_vals[1:])/2, 1.5*lat_vals[-1] - 0.5*lat_vals[-2])
  lat_vals_bounds=np.column_stack((min_vals, max_vals))

  min_vals=np.append((1.5*lon_vals[0] - 0.5*lon_vals[1]), (lon_vals[0:-1] + lon_vals[1:])/2)
  max_vals=np.append((lon_vals[0:-1] + lon_vals[1:])/2, 1.5*lon_vals[-1] - 0.5*lon_vals[-2])
  lon_vals_bounds=np.column_stack((min_vals, max_vals))

if(realm=='atmos' and varStructure=='time_plev_lat_lon'):
#dvar=='zg' or dvar=='ua' or dvar=='va' or dvar=='pv' or dvar=='divg' or dvar=='vort' or dvar=='cl' or dvar=='rws' or dvar=='ta' or dvar=='hus' or dvar=='hur'):
  if(dvar=='zg'):
    zt=f.variables['phalf'][:]*100.0
  else:
    zt=f.variables['pfull'][:]*100.0
  min_vals=np.append((1.5*zt[0] - 0.5*zt[1]), (zt[0:-1] + zt[1:])/2)
  max_vals=np.append((zt[0:-1] + zt[1:])/2, (1.5*zt[-1] - 0.5*zt[-2]))
  zbounds =np.column_stack((min_vals, max_vals))
  zbounds=np.where(zbounds<0.0,0.0,zbounds)

  print('zt=',zt[:],file=fh_printfile)
  print('zt.shape=',zt.shape,file=fh_printfile)
  print('zbounds=',zbounds[:],file=fh_printfile)
  print('tables=',tables,file=fh_printfile)

  cmor.set_table(tables[2]) #working zg
  cmor.set_table(tables[0])
  #zt=np.array([1000., 5000., 10000., 25000., 50000., 70000., 85000., 100000.0])
  #zt=np.array([100000.,85000., 70000., 50000., 25000., 10000., 5000., 1000.])

  #z_axis_id=cmor.axis('plevs','Pa',coord_vals=zt[:],cell_bounds=zbounds[:])
  #z_axis_id=cmor.axis('plev25','Pa',coord_vals=zt[:],cell_bounds=zbounds[:])
  if(dvar=='zg'):
    z_axis_id=cmor.axis('plev25','Pa',coord_vals=zt[:])
  #elif(dvar=='ta5'):
  #  z_axis_id=cmor.axis('plev5','Pa',coord_vals=zt[:])
  else:
    z_axis_id=cmor.axis('plev24','Pa',coord_vals=zt[:])
  #z_axis_id=cmor.axis('plev8','Pa',coord_vals=zt[:])
  #raise SystemExit('Forced exit.')
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

if(dvar=='ta5' or dvar=='zg5' or dvar=='ua5' or dvar=='va5' or dvar=='hus5' or dvar=='hur5'):
  if(dvar=='zg5'):
    zt=f.variables['phalf'][:]*100.0
  else:
    zt=f.variables['pfull'][:]*100.0
  print('zt=',zt,file=fh_printfile)
  #print('ta5 here.',file=fh_printfile)
  newlevs=np.array([30000., 50000., 70000., 85000., 92500.])
  cmor.set_table(tables[0])
  z_axis_id=cmor.axis('plev5','Pa',coord_vals=newlevs[:])

elif(dvar=='ta10' or dvar=='zg10' or dvar=='ua10' or dvar=='va10' or dvar=='hus10' or dvar=='hur10'):
  if(dvar=='zg10'):
    zt=f.variables['phalf'][:]*100.0
  else:
    zt=f.variables['pfull'][:]*100.0
  print('zt=',zt,file=fh_printfile)
  newlevs=np.array([1000., 5000., 7000., 10000., 15000., 25000., 50000., 70000., 85000., 100000.]) #10 levels
  cmor.set_table(tables[0])
  z_axis_id=cmor.axis('plev10','Pa',coord_vals=newlevs[:])

elif(dvar=='ta19' or dvar=='zg19' or dvar=='ua19' or dvar=='va19' or dvar=='hus19' or dvar=='hur19'):
  if(dvar=='zg19'):
    zt=f.variables['phalf'][:]*100.0
  else:
    zt=f.variables['pfull'][:]*100.0
  print('zt=',zt,file=fh_printfile)
  newlevs=np.array([100., 500., 1000., 2000., 3000., 5000., 7000., 10000., 15000., 20000., 25000., 30000., 40000., 50000., 60000., 70000., 85000., 92500., 100000.])
  #print('newlevs=',newlevs,file=fh_printfile)
  #raise SystemExit('Forced exit.')
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  cmor.set_table(tables[0])
  z_axis_id=cmor.axis('plev19','Pa',coord_vals=newlevs[:])

if(realm=='atmos' and (varStructure=='time' or varStructure=='time_lat_lon' or varStructure=='time_plev_lat_lon' or varStructure=='time_reducedplev_lat_lon')):
#dvar=='zg500' or dvar=='zg' or dvar=='psl' or dvar=='ps' or dvar=='ua' or dvar=='va' or dvar=='pv' or dvar=='vort' or dvar=='divg' or dvar=='cl' or dvar=='rws500' or dvar=='rws' or dvar=='nhbi' or dvar=='nino34' or dvar=='iod' or dvar=='pp' or dvar=='nflux' or dvar=='ep' or dvar=='ta' or dvar=='ta5' or dvar=='ta10' or dvar=='zg10' or dvar=='ua10' or dvar=='va10' or dvar=='hus10' or dvar=='hur10' or dvar=='hus' or dvar=='hur' or dvar=='ta19' or dvar=='tauu' or dvar=='tauv' or dvar=='pr'):
#  lat_axis=f.variables['lat']
#  lon_axis=f.variables['lon']

  print('lat_vals.shape=',lat_vals.shape,file=fh_printfile)
  print('lon_vals.shape=',lon_vals.shape,file=fh_printfile)

  print('lat_vals_bounds.shape=',lat_vals_bounds.shape,file=fh_printfile)
  print('lon_vals_bounds.shape=',lon_vals_bounds.shape,file=fh_printfile)
  lat_vals_bounds=np.where(lat_vals_bounds>90.0,90.0,lat_vals_bounds)
  lat_vals_bounds=np.where(lat_vals_bounds<-90.0,-90.0,lat_vals_bounds)

  print('max=',np.max(lat_vals_bounds),file=fh_printfile)
  print('min=',np.min(lat_vals_bounds),file=fh_printfile)

  nlats=lat_vals.shape[0] #check this
  nlons=lon_vals.shape[0] #check this, should it be 1?

  cmor.set_table(tables[0]) #working zg500
  #cmor.set_table(tables[2])

  lat_axis_id=cmor.axis(table_entry='latitude', units='degrees_north', coord_vals=lat_vals[:], cell_bounds=lat_vals_bounds)

  lon_axis_id=cmor.axis(table_entry='longitude', units='degrees_east', coord_vals=lon_vals[:], cell_bounds=lon_vals_bounds)

#if(dvar=='zg' or dvar=='ua' or dvar=='va' or dvar=='pv' or dvar=='vort' or dvar=='divg' or dvar=='cl' or dvar=='ta' or dvar=='ta5' or dvar=='ta10' or dvar=='zg10' or dvar=='ua10' or dvar=='va10' or dvar=='hus10' or dvar=='hur10' or dvar=='hus' or dvar=='hur' or dvar=='ta19'):
#  pass
#  #axis_ids=np.array([time_axis_id, lat_axis_id, lon_axis_id])
#  #axis_ids=np.array([lat_axis_id, lon_axis_id])
#  #axis_ids=np.array([z_axis_id, lat_axis_id, lon_axis_id])
#  #axis_ids=np.array([time_axis_id, z_axis_id, lat_axis_id, lon_axis_id])
#  #grid_id=cmor.grid(axis_ids=axis_ids, latitude=lat_vals[:], longitude=lon_vals[:])
#  #raise SystemExit('Forced exit.')
   #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

if(dvar=='mfo'):
  lines=['barents_opening','bering_strait','canadian_archipelago','denmark_strait',\
                'drake_passage','english_channel','pacific_equatorial_undercurrent',\
                'faroe_scotland_channel','florida_bahamas_strait','fram_strait','iceland_faroe_channel',\
                'indonesian_throughflow','mozambique_channel','taiwan_luzon_straits','windward_passage']

  nlines=len(lines)
  #cmor.set_table(tables[2])
  cmor.set_table(tables[0])

  oline_axis_id = cmor.axis(table_entry='oline', units='', length=len(lines), coord_vals=lines)
  print(oline_axis_id,file=fh_printfile)

elif(dvar=='msftyyz'):
  cmor.set_table(tables[0])

  basins=np.array(['atlantic_arctic_ocean','indian_pacific_ocean','global_ocean'])
  nbasins=len(basins)
  basin_axis_id = cmor.axis(table_entry='basin', units='', length=len(basins), coord_vals=basins)

  z_axis_id=cmor.axis('depth_coord','m',coord_vals=zt[:],cell_bounds=zbounds[:])

  lat_vals=xfh.variables['grid_y_T']
  lon_vals=xfh.variables['grid_x_C']
  lon_vals_360=np.mod(lon_vals,360)

  print('lon_vals=',lon_vals[:],file=fh_printfile)

  min_vals=np.append((1.5*lat_vals[0] - 0.5*lat_vals[1]), (lat_vals[0:-1] + lat_vals[1:])/2)
  max_vals=np.append((lat_vals[0:-1] + lat_vals[1:])/2, 1.5*lat_vals[-1] - 0.5*lat_vals[-2])
  lat_vals_bounds=np.column_stack((min_vals, max_vals))

  lat_axis_id=cmor.axis(table_entry='latitude', units='degrees_north', coord_vals=lat_vals[:], cell_bounds=lat_vals_bounds)

  nlats=len(lat_vals)
  nlons=len(lon_vals)

  #axis_ids=np.array([basin_axis_id, z_axis_id, lat_axis_id])
  #grid_id=cmor.grid(axis_ids=axis_ids, latitude=lat_vals[:])

  #min_vals=np.append((1.5*lon_vals[0] - 0.5*lon_vals[1]), (lon_vals[0:-1] + lon_vals[1:])/2)
  #max_vals=np.append((lon_vals[0:-1] + lon_vals[1:])/2, 1.5*lon_vals[-1] - 0.5*lon_vals[-2])
  #lon_vals_bounds=np.column_stack((min_vals, max_vals))

  #lon_axis_id=cmor.axis(table_entry='longitude', units='degrees_east', coord_vals=lon_vals[:], cell_bounds=lon_vals_bounds)

  print('time_axis_id=', time_axis_id,file=fh_printfile)
  print('basin_axis_id=', basin_axis_id,file=fh_printfile)
  print('z_axis_id=', z_axis_id,file=fh_printfile)
  print('lat_axis_id=', lat_axis_id,file=fh_printfile)

  #raise SystemExit('Forced exit.')
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

elif(realm=='ocean' and (varStructure=='time_depth_lat_lon' or varStructure=='time_reduceddepth_lat_lon')):
# or dvar=='thetao' or dvar=='so' or dvar=='uo' or dvar=='vo' or dvar=='umo' or dvar=='vmo' or dvar=='volcello' or dvar=='areacello' or dvar=='sftof' or dvar=='thkcello' or dvar=='deptho' or dvar=='thetao100m' or dvar=='so100m' or dvar=='uo100m' or dvar=='vo100m'):

  if(dvar=='umo'):
    lat_vals=xfh.variables['y_T']
    lon_vals=xfh.variables['x_C']
  elif(dvar=='vmo'):
    lat_vals=xfh.variables['y_C']
    lon_vals=xfh.variables['x_T']
  else:
    lat_vals=xfh.variables['y_T']
    lon_vals=xfh.variables['x_T']
  lon_vals_360=np.mod(lon_vals,360)

  cmor.set_table(tables[0])

  #z_axis_id=cmor.axis('depth_coord','m',length=nzb,coord_vals=zt[:],cell_bounds=zbounds[:])
  #z_axis_id=cmor.axis('depth_coord','m',length=3,coord_vals=zt[[0,10,20]],cell_bounds=zbounds[[0,10,20],:])
  #z_axis_id=cmor.axis('depth_coord','m',coord_vals=ztX,cell_bounds=zboundsX)

  z_axis_id=cmor.axis('depth_coord','m',coord_vals=zt[levels],cell_bounds=zbounds[levels,:])
  #z_axis_id=cmor.axis('depth_coord','m',coord_vals=zt[[0,3,5]],cell_bounds=zbounds[[0,3,5],:])

  #z_axis_id=cmor.axis('depth_coord','m',coord_vals=zt[:],cell_bounds=zbounds[:])

  #print('zt=',zt[:],file=fh_printfile)
  #print('zt=',zt[[0,3,5]],file=fh_printfile)
  #z_axis_id=cmor.axis('depth_coord','m',coord_vals=zt[[0,3,5]])
  #raise SystemExit('Forced exit.')
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  cmor.set_table(tables[1])

  j_axis_id=cmor.axis('j_index','1',coord_vals=np.arange(300))
  i_axis_id=cmor.axis('i_index','1',coord_vals=np.arange(360))

  #print('time_axis_id=',time_axis_id,file=fh_printfile)
  print('z_axis_id=',z_axis_id,file=fh_printfile)
  print('j_axis_id=',j_axis_id,file=fh_printfile)
  print('i_axis_id=',i_axis_id,file=fh_printfile)

  lon_vertices=np.mod(get_vertices('geolon_t'),360)
  lat_vertices=get_vertices('geolat_t')

  #axis_ids=np.array([z_axis_id, j_axis_id, i_axis_id])
  axis_ids=np.array([j_axis_id, i_axis_id])

  grid_id=cmor.grid(axis_ids=axis_ids, latitude=lat_vals[:], longitude=lon_vals_360[:], latitude_vertices=lat_vertices[:], longitude_vertices=lon_vertices[:])

elif(realm=='ocean' and varStructure=='time_lat_lon'):
  # or dvar=='tos' or dvar=='sos' or dvar=='mlotst' or dvar=='mlotstsq' or dvar=='umo' or dvar=='vmo' or dvar=='volcello' or dvar=='areacello' or dvar=='sftof' or dvar=='thkcello' or dvar=='deptho' or dvar=='isothetao16c'or dvar=='isothetao20c'or dvar=='isothetao22c'):
  if(dvar=='umo'):
    lat_vals=xfh.variables['y_T']
    lon_vals=xfh.variables['x_C']
  elif(dvar=='vmo'):
    lat_vals=xfh.variables['y_C']
    lon_vals=xfh.variables['x_T']
  else:
    lat_vals=xfh.variables['y_T']
    lon_vals=xfh.variables['x_T']
  lon_vals_360=np.mod(lon_vals,360)

  print('lat_vals.shape=',lat_vals.shape,file=fh_printfile)
  print('lon_vals.shape=',lon_vals.shape,file=fh_printfile)

  #print('lat_axis_bounds.shape=',lat_axis_bounds.shape)

  cmor.set_table(tables[1])

  j_axis_id=cmor.axis('j_index','1',coord_vals=np.arange(300))
  i_axis_id=cmor.axis('i_index','1',coord_vals=np.arange(360))

  print('j_axis_id=',j_axis_id,file=fh_printfile)
  print('i_axis_id=',i_axis_id,file=fh_printfile)

  lon_vertices=np.mod(get_vertices('geolon_t'),360)
  lat_vertices=get_vertices('geolat_t')

  axis_ids=np.array([j_axis_id, i_axis_id])
  grid_id=cmor.grid(axis_ids=axis_ids, latitude=lat_vals[:], longitude=lon_vals_360[:], latitude_vertices=lat_vertices[:], longitude_vertices=lon_vertices[:])
  print('grid_id=',grid_id,file=fh_printfile)
  print('lat_vals.shape=',lat_vals.shape,file=fh_printfile)
  print('lon_vals.shape=',lon_vals.shape,file=fh_printfile)
  print('lat_vertices.shape=',lat_vertices.shape,file=fh_printfile)
  print('lon_vertices.shape=',lon_vertices.shape,file=fh_printfile)

cmor.set_table(tables[0]) #working

data_id=[]
if(realm=='ocean' and varStructure=='time_lat_lon'):
  #or dvar=='tos' or dvar=='sos' or dvar=='mlotst' or dvar=='mlotstsq' or dvar=='isothetao16c' or dvar=='isothetao20c' or dvar=='isothetao22c'):
  axis_ids=[i_axis_id,j_axis_id,time_axis_id]
  axis_ids=[time_axis_id]
  axis_ids=[0]
  axis_ids=[time_axis_id,j_axis_id,i_axis_id]
  axis_ids=np.array([time_axis_id,j_axis_id,i_axis_id])
  axis_ids=np.array([j_axis_id,i_axis_id])
  axis_ids=[0,-100]
  axis_ids=[grid_id]
  axis_ids=[time_axis_id,grid_id] #working
  data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20))
elif(realm=='ocean' and ( varStructure=='time_depth_lat_lon' or varStructure=='time_reduceddepth_lat_lon')):
  # or dvar=='thetao' or dvar=='umo' or dvar=='vmo' or dvar=='so' or dvar=='thetao100m' or dvar=='so100m' or dvar=='uo100m' or dvar=='vo100m' or dvar=='uo' or dvar=='vo'):
  axis_ids=[time_axis_id,grid_id]
  axis_ids=[0,1,2,3]
  axis_ids=[time_axis_id,z_axis_id,grid_id]
  axis_ids=[0,-100]
  axis_ids=[0,2,-100] #works but prob.
  axis_ids=[0,1,-100]
  data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20))
elif(realm=='atmos' and varStructure=='time_lat_lon'):
  #dvar=='zg500' or dvar=='psl' or dvar=='ps' or dvar=='rws500' or dvar=='tauu' or dvar=='tauv' or dvar=='pr'):
  axis_ids=np.array([time_axis_id,lat_axis_id,lon_axis_id])
  axis_ids=np.array([lat_axis_id,lon_axis_id])
  axis_ids=[time_axis_id,lat_axis_id,lon_axis_id] #working zg500
  print('axis_ids=',axis_ids,file=fh_printfile)

  if 'positive' in locals():
    pass
  else:
    positive=None

#  if(dvar=='tauu' or dvar=='tauv'):
#    positive="up"
#  else:
#    positive=None

  data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20,positive=positive))
elif(realm=='atmos' and ( varStructure=='time_plev_lat_lon' or varStructure=='time_reducedplev_lat_lon')):
  #,dvar=='zg' or dvar=='ua' or dvar=='va' or dvar=='pv' or dvar=='vort' or dvar=='divg' or dvar=='cl' or dvar=='rws' or dvar=='ta' or dvar=='ta5' or dvar=='ta10' or dvar=='zg10' or dvar=='ua10' or dvar=='va10' or dvar=='hus10' or dvar=='hur10' or dvar=='hus' or dvar=='hur' or dvar=='ta19'):
  #cmor.set_table(tables[2])
  #cmor.set_table(tables[1])
  #cmor.set_table(tables[0])
  #axis_ids=[time_axis_id,z_axis_id,lat_axis_id,lon_axis_id]
  axis_ids=np.array([time_axis_id,z_axis_id,lat_axis_id,lon_axis_id])
  print('axis_ids=',axis_ids,file=fh_printfile)
  print('dvar=',dvar,' units=',units,file=fh_printfile)
  data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20))

elif( (realm=='ocean' or realm=='atmos') and varStructure=='time'):
  #dvar=='nino34' or dvar=='temptotal' or dvar=='salttotal' or dvar=='iod' or dvar=='pp' or dvar=='nflux' or dvar=='ep'):
  #axis_ids=[time_axis_id,grid_id]
  #axis_ids=[grid_id]
  axis_ids=[]
  axis_ids=[time_axis_id]
  axis_ids=np.array([time_axis_id])
  axis_ids=[0] #working
  #data_id=cmor.variable(dvar, units,  missing_value=-1e20)
  data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20))
elif(dvar=='volcello' or dvar=='thkcello'):
  axis_ids=[0,1,-100]
  axis_ids=[0,-100]
  data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20))
elif(dvar=='areacello' or dvar=='sftof' or dvar=='deptho'):
  axis_ids=[0,1,-100]
  axis_ids=[0,-100]
  axis_ids=[-100]
  data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20))
elif(dvar=='msftyyz'):
  axis_ids=[0,-100]
  axis_ids=np.array([basin_axis_id, z_axis_id, lat_axis_id])
  axis_ids=np.array([time_axis_id, basin_axis_id, z_axis_id, lat_axis_id])
  data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20))
elif(dvar=='mfo'):
  axis_ids=np.array([time_axis_id, oline_axis_id])
  print('axis_ids=',axis_ids,file=fh_printfile)
  data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20))
elif(dvar=='nhbi'):
  axis_ids=np.array([time_axis_id, lon_axis_id])
  print('axis_ids=',axis_ids,file=fh_printfile)
  data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20))
  data_id.append(cmor.variable('GHGS','1.0',axis_ids=axis_ids, missing_value=-1e20))
  data_id.append(cmor.variable('GHGN','1.0',axis_ids=axis_ids, missing_value=-1e20))

ofil,ofil_modified=create_ofils(season,table,ovars,experiment_id,source_id,ripf,grid_label,ybeg,yend,mbeg,mend,0,0) #don't need to worry about dbeg,dend, always monthly data input.

print('odir=',odir,file=fh_printfile)
print('ofil=',ofil,file=fh_printfile)
print('ofil_modified=',ofil_modified,file=fh_printfile)

print('len(ovars)=',len(ovars),file=fh_printfile)
for o in range(0,len(ovars)):
  print('Output CMIP6 file:',odir[o]+'/'+ofil_modified[o],file=fh_printfile)

#print(NoClobber,file=fh_printfile)
#raise SystemExit('Forced exit.')
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

for o in range(0,len(ovars)):
  if(os.path.exists(odir[o]+'/'+ofil_modified[o]) and NoClobber):
    raise SystemExit('No Clobber set and ',odir[o]+'/'+ofil_modified[o],' exist.')

for o in range(0,len(ovars)):
  if(os.path.exists(odir[o]+'/'+ofil[o]) and NoClobber):
    raise SystemExit('No Clobber set and ',odir[o]+'/'+ofil_modified[o],' exist.')


if(table=='fx' or table=='Ofx'):

  if(dvar=='volcello'):
    area=np.tile(np.expand_dims(xfh.variables['area_T'],0), (len(zt),1,1))
    thickness=np.expand_dims(np.expand_dims(z[:],1),2)
    thickness=np.tile( thickness ,(1,nlat,nlon))
    data=np.ma.array(input_fhs[0].variables[inputs[0]][0,:,:,:]/input_fhs[0].variables[inputs[0]][0,:,:,:]) * thickness*area

  elif(dvar=='thkcello'):
    thickness=np.expand_dims(np.expand_dims(z[:],1),2)
    thickness=np.tile( thickness ,(1,nlat,nlon))
    data=np.ma.array(input_fhs[0].variables[inputs[0]][0,:,:,:]/input_fhs[0].variables[inputs[0]][0,:,:,:]) * thickness

  elif(dvar=='areacello'):
    data=np.ma.array(input_fhs[0].variables[inputs[0]][0,0,:,:]/input_fhs[0].variables[inputs[0]][0,0,:,:]) * xfh.variables['area_T']

  elif(dvar=='sftof'):
    data=np.float32(xfh.variables['wet'][:,:]*100.0)

  elif(dvar=='deptho'):
    depths=np.expand_dims(np.expand_dims(z[:],1),2)
    depths=np.tile( depths,(1,nlat,nlon))
    data=np.ma.array(input_fhs[0].variables[inputs[0]][0,:,:,:]/input_fhs[0].variables[inputs[0]][0,:,:,:]) * depths
    data=np.sum(data,axis=0)

  file_name=[]
  for o in range(0,len(ovars)):
    print('o=',o,file=fh_printfile)
    print('file_name=',file_name,file=fh_printfile)
    cmor.write(var_id=data_id[o], data=data[:], ntimes_passed=0)
    file_name.append(cmor.close(var_id=data_id[o], file_name=True))

    finish(file_name[o],odir[o],ofil[o],ofil_modified[o],season,fh_printfile)

icnt=0
ibeg=0
ind_beg=0
for n in range(0,ttt): #this code is copy from one above (need to add in icnt,ind_beg)

  if(season=='MON'):
    ind_end=ind_beg #always 1 month at a time for MON
  else:
    ind_end=ind_beg+times_in_season-1

  month_index_beg=month_index_ntims[ind_beg]+1
  year_index_beg=year_index_ntims[ind_beg]

  if(season=='MON'):
    if(n==0):
      month_index_end=month_index_beg+1
      year_index_end=year_index_beg
    else:
      month_index_end=month_index_beg+1
      year_index_end=year_index_end
  elif(season=='ANN'):
    if(n==ttt-1): #last one special
      month_index_end=month_index_ntims[ind_end-1]+1+1+1
      year_index_end=year_index_ntims[ind_end-1]
    else:
      month_index_end=month_index_ntims[ind_end]+1+1
      year_index_end=year_index_ntims[ind_end]
  else:
    if(n==ttt-1): #last one special
      month_index_end=month_index_ntims[ind_end-1]+1+1
      year_index_end=year_index_ntims[ind_end-1]
    else:
      month_index_end=month_index_ntims[ind_end]+1
      year_index_end=year_index_ntims[ind_end]

  if(month_index_end>12):
     month_index_end=month_index_end-nmy
     year_index_end+=1

  print('n=',n,' year_index_beg=',year_index_beg,' month_index_beg=',month_index_beg,' year_index_end=',year_index_end,' month_index_end=',month_index_end,' ind_beg,end=',ind_beg,ind_end,file=fh_printfile)

  if(len(inputs)==2):
    print('levels=',levels,file=fh_printfile)
    print('nlev=',nlev,file=fh_printfile)
    if(realm=='atmos' and (varStructure=='time_plev_lat_lon' or varStructure=='time_reducedplev_lat_lon')):
    #dvar=='ta5' or dvar=='zg5' or dvar=='ua5' or dvar=='va5' or dvar=='hus5' or dvar=='hur5' or dvar=='ta10' or dvar=='zg10' or dvar=='ua10' or dvar=='va10' or dvar=='hus10' or dvar=='hur10' or dvar=='ta19' or dvar=='zg19' or dvar=='ua19' or dvar=='va19' or dvar=='hus19' or dvar=='hur19'):
      #nlev=0
      pass
    elif(dvar=='rws500'):
      nlev=1
      levels=9

    data1=data_wavg(inputs[0],input_fhs,locate_file_index_Ntimes_b1_nominus1s_flat,ind_beg,ind_end,month_in_file_total_months_beg_to_end,levels,nlev,MonthlyWeights,month_index_ntims,fh_printfile,var_size)

    #nlev=0
    data2=data_wavg(inputs[1],input_fhs,locate_file_index_Ntimes_b1_nominus1s_flat,ind_beg,ind_end,month_in_file_total_months_beg_to_end,levels2,nlev2,MonthlyWeights,month_index_ntims,fh_printfile,var_size2)

    print('data1.shape=',data1.shape,file=fh_printfile)
    print('data2.shape=',data2.shape,file=fh_printfile)

  else:
    print('levels=',levels,file=fh_printfile)
    print('nlev=',nlev,file=fh_printfile)

    data=data_wavg(inputs[0],input_fhs,locate_file_index_Ntimes_b1_nominus1s_flat,ind_beg,ind_end,month_in_file_total_months_beg_to_end,levels,nlev,MonthlyWeights,month_index_ntims,fh_printfile,var_size)

    print('data.shape=',data.shape,file=fh_printfile)
  #raise SystemExit('Forced exit.')
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  if(dvar=='acc_drake'):
    data=diag_acc_drake(data,area_t,lat,lon)
  elif(dvar=='acc_africa'):
    data=diag_acc_africa(data,area_t,lat,lon)
  elif(dvar=='mozmbq'):
    data=diag_mozmbq(data,area_t,lat,lon)
  elif(dvar=='aabw'):
    data=diag_aabw(data,area_t,lat,lon)
  elif(dvar=='nadw'):
    data=diag_nadw(data,area_t,lat,lon)
  elif(dvar=='pp'):
    data=diag_pp(data,depth_edges,area_t,lat_vals,lon_vals)
  elif(dvar=='nflux'):
    data=diag_nflux(data,depth_edges,area_t,lat_vals,lon_vals)
  elif(dvar=='ep'):
    data=diag_ep(data,depth_edges,area_t,lat_vals,lon_vals)
  elif(dvar=='ssh'):
    data=diag_ssh(data1,data2,depth_edges,area_t,lat,lon)
  elif(dvar=='moc'):
    data=diag_moc(data1,data2,depth_edges,area_t,lat,lon)
  elif(dvar=='moc_atlantic'):
    data=diag_moc_atlantic(data1,data2,depth_edges,area_t,lat,lon)
  elif(dvar=='moc_pacific'):
    data=diag_moc_pacific(data1,data2,depth_edges,area_t,lat,lon)
  elif(dvar=='moc_indian'):
    data=diag_moc_indian(data1,data2,depth_edges,area_t,lat,lon)
  elif(dvar=='shice_cover'):
    data=diag_shice_cover(data,area_t,lat,lon)
  elif(dvar=='nhice_cover'):
    data=diag_nhice_cover(data,area_t,lat,lon)
  elif(dvar=='nino34'):
    data=diag_nino34(data,area_t,lat_vals,lon_vals,fh_printfile)
  elif(dvar=='iod'):
    data=diag_iod(data,area_t,lat_vals,lon_vals)
  elif(dvar=='nhbi'):
    data,var0,var1=diag_nhblocking_index(data,lat_vals,lon_vals)
  elif(dvar=='rws'):
    data=diag_rws(data1,data2,lat_vals[:],lon_vals[:])
  elif(realm=='ocean' and (varStructure=='time_depth_lat_lon' or varStructure=='time_lat_lon' or varStructure=='time_reduceddepth_lat_lon')):
  # or dvar=='tos' or dvar=='thetao' or dvar=='so' or dvar=='uo' or dvar=='vo' or dvar=='sos' or dvar=='mlotst' or dvar=='mlotstsq' or dvar=='umo' or dvar=='vmo' or dvar=='thetao100m' or dvar=='so100m' or dvar=='uo100m' or dvar=='vo100m'):
    pass
  elif(dvar=='zg500' or dvar=='psl' or dvar=='ps' or dvar=='tauu' or dvar=='tauv' or dvar=='pr'):
    pass
  elif(dvar=='cl'):
    data=np.where(data<0.,0.,data*100.0)
  elif(dvar=='msftyyz'):
    if(icnt==0):
      atlantic_arctic_mask,indoPac_mask,global_mask=make_mask3D(data1+data2,nbasins,nzb,nlats)
    data=diag_msftyyz(data1+data2,atlantic_arctic_mask,indoPac_mask,global_mask,nbasins,nzb,nlats)
  elif(dvar=='mfo'):
     data=diag_mfo(data1,data2,nlines)
  elif(dvar=='rws500'):

     print('data1.shape=',data1.shape,file=fh_printfile)
     print('data2.shape=',data1.shape,file=fh_printfile)

     #data=diag_rws500(data1[9,:,:],data2[9,:,:],lat_vals[:],lon_vals[:])
     data=diag_rws500(data1,data2,lat_vals[:],lon_vals[:],fh_printfile)
  elif(dvar=='isothetao16c'):
    data=diag_isothetaoNc(data,zt[:],16.0)

  elif(dvar=='isothetao20c'):
    data=diag_isothetaoNc(data,zt[:],20.0)

  elif(dvar=='isothetao22c'):
    data=diag_isothetaoNc(data,zt[:],22.0)

  elif(realm=='atmos' and (varStructure=='time_plev_lat_lon' or varStructure=='time_reducedplev_lat_lon')):
  #dvar=='ta5' or dvar=='ta10' or dvar=='zg10' or dvar=='ua10' or dvar=='va10' or dvar=='hus10' or dvar=='hur10' or dvar=='ta19'):

   data=vertical_interpolate(data1,zt,newlevs,data2,vertical_interpolation_method)

  if(season=='MON'):
    ntimes_passed=np.shape(data)[0]
  else:
    ntimes_passed=1

  if(realm=='ocean' and (varStructure=='time_depth_lat_lon' or varStructure=='time_lat_lon' or varStructure=='time_reduceddepth_lat_lon')):
  #dvar=='thetao' or dvar=='so' or dvar=='vo' or dvar=='uo' or dvar=='isothetao20c' or dvar=='thetao100m' or dvar=='so100m' or dvar=='uo100m' or dvar=='vo100m'):
    print('levels=',levels,file=fh_printfile)
    print('data.shape=',data.shape,file=fh_printfile)
    for o in range(0,len(ovars)):
      cmor.write(var_id=data_id[o], data=data[:,:,:], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])
  elif(realm=='ocean' and (varStructure=='time_depth_lat_lon' or varStructure=='time_lat_lon')):
  # or dvar=='tos' or dvar=='thetao' or dvar=='so' or dvar=='uo' or dvar=='vo' or dvar=='temptotal' or dvar=='salttotal' or dvar=='sos' or dvar=='mlotst' or dvar=='mlotstsq' or dvar=='umo' or dvar=='vmo' or dvar=='msftyyz' or dvar=='mfo' or dvar=='so' or dvar=='isothetao16c' or dvar=='isothetao20c' or dvar=='isothetao22c' or dvar=='thetao100m' or dvar=='so100m' or dvar=='uo100m' or dvar=='vo100m'):
    for o in range(0,len(ovars)):
      cmor.write(var_id=data_id[o], data=data[:], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])

      #raise SystemExit('Forced exit.')
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  elif(realm=='atmos' and (varStructure=='time_plev_lat_lon' or varStructure=='time_lat_lon' or varStructure=='time_reducedplev_lat_lon')):
  #dvar=='zg500' or dvar=='zg' or dvar=='psl' or dvar=='ps' or dvar=='ua' or dvar=='va' or dvar=='pv' or dvar=='vort' or dvar=='divg' or dvar=='cl' or dvar=='rws500' or dvar=='rws' or dvar=='ta' or dvar=='ta5' or dvar=='ta10' or dvar=='zg10' or dvar=='ua10' or dvar=='va10' or dvar=='hus10' or dvar=='hur10' or dvar=='hus' or dvar=='hur' or dvar=='ta19' or dvar=='tauu' or dvar=='tauv' or dvar=='pr'):
    #print('data.shape=',data.shape,file=fh_printfile)
    #raise SystemExit('Forced exit.')
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    for o in range(0,len(ovars)):
      cmor.write(var_id=data_id[o], data=data[:], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])
  elif(dvar=='nhbi'):
    for o in range(0,len(ovars)):
      cmor.write(var_id=data_id[o], data=data[:], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])
  elif(dvar=='nino34' or dvar=='iod' or dvar=='pp' or dvar=='nflux' or dvar=='ep'):
    newdata=np.zeros((1,1),dtype='f')
    newdata[0,0]=data
    data=newdata
    for o in range(0,len(ovars)):
      cmor.write(var_id=data_id[o], data=data[:], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])
  icnt+=1
  ibeg=iend+1
  ind_beg=ind_end+1

print('ovars=',ovars,file=fh_printfile)
print('len(ovars)=',len(ovars),file=fh_printfile)

file_name=[]
for o in range(0,len(ovars)):
  print('o=',o,file=fh_printfile)
  file_name.append(cmor.close(var_id=data_id[o], file_name=True))
  print('file_name=',file_name,file=fh_printfile)

for o in range(0,len(ovars)):
  finish(file_name[o],odir[o],ofil[o],ofil_modified[o],season,fh_printfile)

raise SystemExit('Finished O.K.')

#end
