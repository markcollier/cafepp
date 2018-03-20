#!/usr/bin/env python

##!/apps/python/2.7.6/bin/python
##!/short/p66/mac599/anaconda3/bin/ipython
# Filename : cafepp.py

from __future__ import print_function #this is to allow print(,file=xxx) feature

"""
CAFE Post-Processor for monthly inputs
--------------------------

needs more comments

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
#import sys
import getopt
import string
from decadal_diag import MustHaveAllLevs,diag_acc_drake,diag_acc_africa,diag_mozmbq,diag_aabw,diag_nadw,diag_pp,diag_nflux,diag_ep,diag_ssh,diag_moc,diag_moc_atlantic,diag_moc_pacific,diag_moc_indian,diag_shice_cover,diag_nhice_cover,diag_nino34,xtra_nino34,init_data,sum_data,avg_data,filemonth_index,data_wavg,time_avg,diag_nhblocking_index,diag_rws5,finish,diag_msftyyz,make_mask3D,diag_mfo,transPort,diag_rws500,create_odirs,create_ofils,diag_iod,diag_iod,xtra_iod,atmos_vertical_interpolate,diag_isothetaoNc,calc_iso_surface,calc_isoN,grab_var_meta,diag_psl,diag_hfls,diag_heat_content,diag_salt_content,diag_north_heat_trans,diag_north_salt_trans,ocean_vertical_interpolate,diag_thetao0to80m,diag_varNl,uncomment_json,process_json,modify_json,get_daily_indices_for_monthlyave,get_timestamp_number,data_wavg_ProcTime

from decadal_diag import diag_maxdTbydz,diag_depmaxdTbydz,diag_dTbydz,shade_2d_simple,shade_2d_latlon,diag_zmld_boyer,zmld_boyer,sigmatheta,diag_zmld_so,zmld_so,diag_spice,spice,diag_bigthetao,diag_soabs,diag_spiciness,diag_potrho

import cmor
import cdtime
from app_funcs import *
import json
import pprint
#from datetime import date,datetime,timedelta
import datetime
import filecmp
from shutil import copyfile
import cdms2
from regrid2 import Regridder
import inspect  
import socket
import glob
from matplotlib.mlab import griddata
import scipy.sparse as sps
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from cartopy.util import add_cyclic_point
import matplotlib as mpl

mpl.rcParams['mathtext.default'] = 'regular'
import matplotlib.pyplot as plt
#plt.switch_backend("TkAgg")
from gridfill import fill as poisson_fill
from array import array
import types

def main(json_input_instructions):

  print('MAIN')
  #return(0)

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

#if(len(sys.argv)!=2):
#  raise SystemExit('CAFEPP only takes one argument, the JSON instruction file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  hostname=socket.gethostname()
  
  print('hostname=',hostname)
  
  printDefinedDiagnostics=False
  Forecast=False#the input directory will vary depending on year/month, I am calling these Forecast runs for now. These have one month of data per file - future model configurations may have different inputs. "Non-Forecast" runs are the traditional control runs, which have normally had 12 months per file.
  ReGrid=False
  NoClobber=False
  ProcessFileList=False
  ProcessFileTxtTF=False
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
  cafepp_defs='cafepp_csiro-gfdl.json'
  cafepp_experiments='cafepp_experiments.json'
  json_input_var_meta='cafepp_vars_mon.json'
  #json_input_instructions='cafepp.json'
  #json_input_instructions=sys.argv[1]
  cafepp_machine='raijin.nci.org.au'
  
  #fh_printfile=sys.stdout
  #fh_printfile=sys.stderr
  
  cmorlogfile='log'
  mbeg=1
  mend=12
  
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  if 'json_input_instructions' in locals():
    #os.system('awk -f ~mac599/decadal/uncomment_json.awk JsonTemplates/'+json_input_instructions+' > '+json_input_instructions)
    uncomment_json('JsonTemplates/'+json_input_instructions,json_input_instructions,True)
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
      #print('processing key_now[0]=',key_now[0])
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
          elif(l=='force_hostname'): force_hostname=str(list_new[l])
          elif(l=='name'): name=str(list_new[l])
          elif(l=='importance'): importance=str(list_new[l])
          elif(l=='version'): version=str(list_new[l])
  #        elif(l=='initialisation'): initialisation=str(list_new[l])
  #        elif(l=='realisation'): realisation=str(list_new[l])
  #        elif(l=='physics'): physics=str(list_new[l])
  #        elif(l=='forcings'): forcings=str(list_new[l])
  #        elif(l=='dvar'): dvar=str(list_new[l])
          elif(l=='dvar'): dvar=str.split(str(list_new[l]))
  
  #      elif(l=='table'): table_tmp=string.split(str(list_new[l]),sep=",")
  
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
  #        elif(l=='xxxprintfile'): None
          elif(l=='printDefinedDiagnostics'):
            if(list_new[l]=='True'): printDefinedDiagnostics=True
          elif(l=='ProcessFileTxt'):
            ProcessFileTxt=str(list_new[l])
            ProcessFileTxtTF=True
  #        elif(l=='grid'): grid=str(list_new[l])
  #        elif(l=='grid_label'): grid_label=str(list_new[l])
          elif(l=='cafepp_machine'): cafepp_machine=str(list_new[l])
          else: raise SystemExit('Unknown option_with_argument,',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
      elif(key_now0=="options_no_arguments"):
        list_new=(json_input_instructions_data[key_now0])
        for l in list_new: #used to be list_new2
          if(l=='name'): name=str(list_new[l])
          elif(l=='info'): info=str(list_new[l])
  #        elif(l=='Forecast'): 
  #          if(list_new[l]=='True'): Forecast=list_new[l]
          elif(l=='Regrid'):
            if(list_new[l]=='True'): Regrid=True
          elif(l=='MonthlyWeights'): 
            if(list_new[l]=='True'): MonthlyWeights=True
          elif(l=='NoClobber'): 
            if(list_new[l]=='True'): NoClobber=list_new[l]
          elif(l=='ProcessFileList'):
            if(list_new[l]=='True'): ProcessFileList=list_new[l]
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
          #elif(l=='vertical_interpolation_method'): vertical_interpolation_method=str(list_new[l])
          elif(l=='frequency'): frequency=str(list_new[l])
          elif(l=='cafepp_experiments_meta'): cafepp_experiments_meta=str(list_new[l])
          elif(l=='cafepp_defs'): cafepp_defs=str(list_new[l])
          elif(l=='json_input_var_meta'): json_input_var_meta=str(list_new[l])
      elif(key_now0=="monthly_specific"):
        list_new=(json_input_instructions_data[key_now0])
        for l in list_new:
          if(l=='name'): name=str(list_new[l])
          else: raise SystemExit('Unknown monthly_specific,',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
          #else: raise SystemExit('Unknown defaults,',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
    if 'printfile' in locals():
      fh_printfile=open(printfile,"w")
    else:
      fh_printfile=sys.stdout
    print('fh_printfile=',fh_printfile)

  if(ProcessFileList and ProcessFileTxtTF):
    raise SystemExit('Cannot have both ProcessFileList and ProcessFileTxtTF True:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  #cafepp_experiments_meta='cafepp_experiments.json'
  #os.system('awk -f ~mac599/decadal/uncomment_json.awk JsonTemplates/'+cafepp_experiments_meta+' > '+cafepp_experiments_meta)
  uncomment_json('JsonTemplates/'+cafepp_experiments_meta,cafepp_experiments_meta,True)
  cafepp_experiments_fh=open(cafepp_experiments_meta).read()
  print('cafepp_experiments_fh=',cafepp_experiments_fh,file=fh_printfile)
  cafepp_experiments_data=json.loads(cafepp_experiments_fh)
  print('cafepp_experiments_data=',cafepp_experiments_data,file=fh_printfile)
  
  print("Summary of JSON experiments input: ",json.dumps(cafepp_experiments_data,indent=4,sort_keys=True),file=fh_printfile)
  
  top_level_keys=cafepp_experiments_data.keys()
  print('Top level JSON experiments keys=',top_level_keys,file=fh_printfile)
  
  cafepp_experiment_found=False
  for key_now in cafepp_experiments_data.iteritems():
    #print('processing key_now[0]=',key_now[0],file=fh_printfile)
    key_now0=key_now[0]
    if(key_now0==cafe_experiment):
      cafepp_experiment_found=True
      print("Found required output experiment :",cafe_experiment,file=fh_printfile)
      list_new=(cafepp_experiments_data[key_now0])
      #print('list_new=',list_new,file=fh_printfile)
      for l in list_new:
        #print('l=',l,file=fh_printfile)
        if(l=='experiment'): experiment=str(list_new[l])
        elif(l=='Forecast'): 
          if(list_new[l]=='True'): Forecast=list_new[l]
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
          #idir=top_directory_no1
        elif(l=='active_disk_no1'): active_disk_no1=str(list_new[l])
  
        elif(l=='storage_machine_no2'): storage_machine_no2=str(list_new[l])
        elif(l=='top_directory_no2'):
          top_directory_no2=str(list_new[l])
          #idir=top_directory_no2 #temporary until disks sorted out...
        elif(l=='active_disk_no2'): active_disk_no2=str(list_new[l])
  
        elif(l=='storage_machine_no3'): storage_machine_no3=str(list_new[l])
        elif(l=='top_directory_no3'):
          top_directory_no3=str(list_new[l])
          #idir=top_directory_no3 #temporary until disks sorted out...
        elif(l=='active_disk_no3'): active_disk_no3=str(list_new[l])
  #tube-hba
  #raijin*
  #Snapper-as
        elif(l=='main_science_contact'): main_science_contact=str(list_new[l])
        elif(l=='main_technical_contact'): main_technical_contact=str(list_new[l])
        elif(l=='readable_nexus_ids_no1'): readable_nexus_ids_no1=str(list_new[l])
        elif(l=='readable_nexus_ids_no2'): readable_nexus_ids_no2=str(list_new[l])
        elif(l=='writable_nexus_ids'): writable_nexus_ids=str(list_new[l])
        elif(l=='ybeg_min'): ybeg_min=int(list_new[l])
        elif(l=='yend_max'): yend_max=int(list_new[l])
        elif(l=='mbeg_min'): mbeg_min=int(list_new[l])
        elif(l=='mend_max'): mend_max=int(list_new[l])
        elif(l=='dbeg_min'): pass #ignore for cafepp.py only relevant for cafepp_daily.py
        elif(l=='dend_max'): pass #ignore for cafepp.py only relevant for cafepp_daily.py
        elif(l=='daily_data_layout'): pass #ignore.
        elif(l=='monthly_data_layout'): monthly_data_layout=str(list_new[l])
        elif(l=='realisation'): realisation=int(list_new[l])
        elif(l=='initialisation'): initialisation=int(list_new[l])
        elif(l=='physics'): physics=int(list_new[l])
        elif(l=='forcing'): forcing=int(list_new[l])
        elif(l=='institution'): institution=str(list_new[l])
        elif(l=='institution_id'): institution_id=str(list_new[l])
        elif(l=='source'): source=str(list_new[l])
        elif(l=='source_id'): source_id=str(list_new[l])
        else: raise SystemExit('Unknown variable metadata',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    else:
      pass
  
  if 'force_hostname' in locals():
    hostname=force_hostname
  
  #if 'storage_machine_no1' in locals():
  #  if re.match(storage_machine_no1,hostname):
  #    idir=top_directory_no1
  #
  #if 'storage_machine_no2' in locals():
  #  if re.match(storage_machine_no2,hostname):
  #    idir=top_directory_no2
  #
  #if 'storage_machine_no3' in locals():
  #  if re.match(storage_machine_no3,hostname):
  #    idir=top_directory_no3
  
  if 'storage_machine_no1' in locals() and active_disk_no1=='yes':
    storage_machine_no1_split=storage_machine_no1.split('.')
    if re.match(storage_machine_no1_split[0],hostname):
      idir=top_directory_no1
  
  if 'storage_machine_no2' in locals() and active_disk_no2=='yes':
    storage_machine_no2_split=storage_machine_no2.split('.')
    if re.match(storage_machine_no2_split[0],hostname):
      idir=top_directory_no2
  
  if 'storage_machine_no3' in locals() and active_disk_no3=='yes':
    storage_machine_no3_split=storage_machine_no3.split('.')
    if re.match(storage_machine_no3_split[0],hostname):
      idir=top_directory_no3
  
  #print('hostname=',hostname)
  #print('storage_machine_no1=',storage_machine_no1)
  #idir=top_directory_no2 #this is hardwired until I sort out how to manage this on raijin's quque...
  
  if not 'idir' in locals():
    raise SystemExit('Could not determine input directory, idir ',' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  if not os.path.exists(idir):
    raise SystemExit('Input directory specified does not exist, file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
   
  #print(outputs_string)
  #print(dvar)
  #if(not 'outputs_string' in locals() and dvar!='rws'):
  #  raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
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
  
  #print('sys.argv=',sys.argv,file=fh_printfile)
  
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
  
  define_basin_mask=False
  #os.system('awk -f ~mac599/decadal/uncomment_json.awk JsonTemplates/'+json_input_var_meta+' > '+json_input_var_meta)
  uncomment_json('JsonTemplates/'+json_input_var_meta,json_input_var_meta,True)
  json_input_var_fh=open(json_input_var_meta).read()
  print('json_input_var_fh=',json_input_var_fh,file=fh_printfile)
  json_input_var_data=json.loads(json_input_var_fh)
  print('json_input_var_data=',json_input_var_data,file=fh_printfile)
  
  print("Summary of JSON variable input: ",json.dumps(json_input_var_data,indent=4,sort_keys=True),file=fh_printfile)
  
  top_level_keys=json_input_var_data.keys()
  print('Top level JSON variable keys=',top_level_keys,file=fh_printfile)
  
  for key_now in json_input_var_data.iteritems():
    #print('processing key_now[0]=',key_now[0],file=fh_printfile)
    key_now0=key_now[0]
    if(key_now0=="defaults"):
      list_new=(json_input_var_data[key_now0])
      for l in list_new:
        if(l=='info'): info=str(list_new[l])
        elif(l=='area_t'): area_t=list_new[l]
        elif(l=='area_u'): area_u=list_new[l]
        #elif(l=='grid'): grid=str(list_new[l])
        #elif(l=='grid_label'): grid_label=str(list_new[l])
        else: raise SystemExit('Unknown defaults,',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    elif(key_now0==dvar[0]):
      print("Found required output variable:",dvar,file=fh_printfile)
      list_new=(json_input_var_data[key_now0])
      for l in sorted(list_new):
        print(l,file=fh_printfile)
        if(l=='info'): info=str(list_new[l])
        elif(l=='area_t'): 
            if(list_new[l]=='True'): area_t=True
        elif(l=='area_u'): 
            if(list_new[l]=='True'): area_u=True
        elif(l=='inputs'): inputs=string.split(str(list_new[l]),sep=",")
        elif(l=='inputs_shape'): inputs_shape=string.split(str(list_new[l]),sep=",")
          #newinputs=string.split(inputs)
          #print('inputs=',inputs)
          #print('newinputs=',newinputs)
          #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
        elif(l=='inputs_alternative'): inputs_alternative=string.split(str(list_new[l]))
        elif(l=='realm'): realm=str(list_new[l])
  #      elif(l=='diag_dims'): diag_dims=string.split(str(list_new[l]))
        elif(l=='ounits'): ounits=str(list_new[l])
        elif(l=='table'): table_tmp=string.split(str(list_new[l]),sep=",")
        elif(l=='table_frequency'): table_frequency=string.split(str(list_new[l]),sep=",")
        elif(l=='ovars'): ovars=string.split(str(list_new[l]))
        elif(l=='OutputVarStructure'): OutputVarStructure=str(list_new[l])
        elif(l=='positive'): positive=str(list_new[l])
        elif(l=='output_type'): output_type=str(list_new[l])
        elif(l=='plev_type'): plev_type=str(list_new[l])
        elif(l=='plevN'): plevN=str(list_new[l])
        elif(l=='lat_lon_type'): lat_lon_type=string.split(str(list_new[l]),sep=",")
        elif(l=='diagnostic_args_string'): diagnostic_args_string=str(list_new[l])
        elif(l=='diagnostic_function_name'): diagnostic_function_name=str(list_new[l])
        elif(l=='define_basin_mask'): 
            if(list_new[l]=='True'): define_basin_mask=True
            else: define_basin_mask=False
        elif(l=='grid'): grid=str(list_new[l]) #this will override defaults.
        elif(l=='grid_label'): grid_label=str(list_new[l]) #this will override defaults.
        elif(l=='comment'): comment=str(list_new[l])
        elif(l=='aaa_newlevs_type'): aaa_newlevs_type=str(list_new[l])
        elif(l=='newlevs'):
         #print(list_new[l])
         newlevs=[eval(aaa_newlevs_type)(x) for x in list_new[l].split(',')]
         #levels=[float(x) for x in list_new[l].split(',')]
         #levels=[int(x) for x in list_new[l].split(',')]
         #levels=[x for x in list_new[l].split(',')]
         #newnlev=len(levels)
        elif(l=='dummy_shape'):
         dummy_shape=tuple([int(x) for x in list_new[l].split(',')])
        elif(l=='dummy_dimensions'):
         dummy_dimensions=tuple(string.split(str(list_new[l]),sep=','))
        elif(l=='zt0b_new'):
         zt0b_new=[float(x) for x in list_new[l].split(',')]
        elif(l=='vertical_interpolation_method'): vertical_interpolation_method=str(list_new[l])
        elif(l=='interp_fill_options'):
          #should check list to see if valid choices...
          interp_fill_options=string.split(str(list_new[l]),sep=',')
          #print(interp_fill_options)
          #if 'poisson_fill' in interp_fill_options:
          for check in sorted(interp_fill_options):
            #print(check)
            if check not in ['griddata_scipy','poisson_fill','dot_weighting_regrid','apply_ls_mask_regrid']:
              raise SystemExit('Invalid choice with interp_fill options:'+__file__+' line number: '+str(inspect.stack()[0][2]))

        elif(l=='outputs_string'): outputs_string=string.split(str(list_new[l]),sep=",")
        elif(l=='outputs_units_string'): outputs_units_string=string.split(str(list_new[l]),sep=",")
        else: raise SystemExit('Unknown variable metadata',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
    else:
      pass
      #print("hello",file=fh_printfile)
  #print('ounits=',ounits,file=fh_printfile)
  
  #print(output_type)
  #print(levels)
  #print(len(levels))
  #print(type(levels))
  #if not 'levels' in locals():
  #nlev=len(levels)
  #print(experiment_id)
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  if(output_type=='diagnostic' and not 'diagnostic_args_string' in locals()):
    raise SystemExit('When generating a diagnostic, must define a diagnostic_args_string to go with it: '+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  if(output_type=='diagnostic' and not 'diagnostic_function_name' in locals()):
    diagnostic_function_name=dvar[0]
  
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
  
  print('printDefinedDiagnostics=',printDefinedDiagnostics,file=fh_printfile)
  if(printDefinedDiagnostics):
    print("Alphabetically ordered List of currently loaded diagnostis (varable/unit):",file=fh_printfile)
    for key_now in sorted(json_input_var_data.iteritems(),reverse=False):
      if(key_now[0]!="defaults"):
        #print(key_now)
        #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
        list_new=(json_input_var_data[key_now[0]])
        #print(list_new)
        for l in list_new:
          if(l=='ounits'):
            print(key_now[0],list_new[l],file=fh_printfile)
    raise SystemExit('Finished writing current set.')
  
  #print(table_tmp)
  #print(table_frequency)
  if 'table_tmp' in locals():
    table=table_tmp[table_frequency.index(frequency)]
  else:
    raise SystemExit('Must choose valid table:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  #print(table_tmp)
  #print(table_frequency)
  #print(frequency)
  #print(table)
  #frequency='day'
  #j=table_frequency.index(frequency)
  #print(j)
  #print(type(table))
  #newtable=
  
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  #frequency='month'
  #realm,table,inputs,ounits,ovars,area_t,area_u,diag_dims,grid_label,grid,vertical_interpolation_method,OutputVarStructure=grab_var_meta(dvar,frequency)
  
  #if(dvar=='thetao'):
  #  inputs=['temp']
  #  ounits='degC'
  #elif(dvar=='so'):
  #  inputs=['salt']
  #  ounits='0.001'
  #elif(dvar=='umo' or dvar=='vmo'):
  #  ounits='10^9 kg s-1'
  
#!  if(Forecast):
#!    cdtime.DefaultCalendar=cdtime.JulianCalendar
#!  else:
#!    #cdtime.DefaultCalendar=cdtime.GregorianCalendar
#!    cdtime.DefaultCalendar=cdtime.NoLeapCalendar
  
  #cmor.setup(inpath='Tables',netcdf_file_action=cmor.CMOR_REPLACE_4,logfile=cmorlogfile)
  cmor.setup(inpath='cmip6-cmor-tables/Tables',netcdf_file_action=cmor.CMOR_REPLACE_4,logfile=cmorlogfile)
  
  #print(dvar,file=fh_printfile)
  
  #print(inputs,file=fh_printfile)
  #raise SystemExit('Forced exit.')
  #cafepp_defs='cafepp_csiro-gfdl.json'
  
  #os.system('awk -f ~mac599/decadal/uncomment_json.awk JsonTemplates/'+cafepp_defs+' > '+cafepp_defs)
  #print('cafepp_defs=',cafepp_defs)
  uncomment_json('JsonTemplates/'+cafepp_defs,cafepp_defs,True)
  cmor.dataset_json(cafepp_defs)
  json_data=open(cafepp_defs).read()
  #pprint.pprint(json_data,width=1)
  cafepp_data=json.loads(json_data)
  #institution_id=cafepp_data['institution_id']
  #source_id=cafepp_data['source_id']
  #institution_id=cafepp_data['institution_id']
  #source_id=cafepp_data['source_id']
  #experiment_id=cafepp_data['experiment_id']
  
  if not 'institution_id' in locals():
    institution_id=cafepp_data['institution_id']
  
  if not 'source_id' in locals():
    source_id=cafepp_data['source_id']
  
  if not 'experiment_id' in locals():
    experiment_id=cafepp_data['experiment_id']
  
  if not 'experiment' in locals():
    experiment=cafepp_data['experiment']
  
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
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
  
  if(realm=='atmos' and (OutputVarStructure=='time_plev_lat_lon' or OutputVarStructure=='time_reducedplev_lat_lon')):
    nlev2=1 #ps needed
    levels2=0 #ps needed
  
  #if(dvar=='ta5' or dvar=='zg5' or dvar=='ua5' or dvar=='va5' or dvar=='hus5' or dvar=='hur5' or dvar=='pv5' or dvar=='divg5' or dvar=='vort5'):
  #  grid_label='gn5'
  #  grid='3D vars use plev5'
  #
  #elif(dvar=='ta10' or dvar=='zg10' or dvar=='ua10' or dvar=='va10' or dvar=='hus10' or dvar=='hur10' or dvar=='pv10' or dvar=='divg10' or dvar=='vort10'):
  #  grid_label='gn10'
  #  grid='3D vars use plev10'
  #
  #elif(dvar=='ta17' or dvar=='zg17' or dvar=='ua17' or dvar=='va17' or dvar=='hus17' or dvar=='hur17' or dvar=='pv17' or dvar=='divg17' or dvar=='vort17'):
  #  grid_label='gn17'
  #  grid='3D vars use plev17'
  
  today=datetime.date.today()
  t=today.timetuple()
  #print('today=',today,file=fh_printfile)
  #for i in t:
  #  print('i=',i,file=fh_printfile)
  #version='v20170315'
  
  if not 'version' in locals(): version='v'+str('{0:04d}'.format(t[0])) + str('{0:02d}'.format(t[1])) + str('{0:02d}'.format(t[2]))
  
  if 'outputs_string' in locals():
    ovars=outputs_string
  if 'outputs_units_string' in locals():
    ounits=outputs_units_string
  print(ovars)
  
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
  cmor.set_cur_dataset_attribute('physics',str(physics))
  cmor.set_cur_dataset_attribute('physics_index',str(physics))
  cmor.set_cur_dataset_attribute('forcing',forcing)
  cmor.set_cur_dataset_attribute('forcing_index',forcing)
  cmor.set_cur_dataset_attribute('realization',str(realisation))
  cmor.set_cur_dataset_attribute('realization_index',str(realisation))
  cmor.set_cur_dataset_attribute('initialization',str(initialisation))
  cmor.set_cur_dataset_attribute('initialization_index',str(initialisation))
  cmor.set_cur_dataset_attribute('version',version)

#should these be commented out?
  cmor.set_cur_dataset_attribute('experiment',experiment)
  cmor.set_cur_dataset_attribute('experiment_id',experiment_id)
  cmor.set_cur_dataset_attribute('parent_experiment_id',parent_experiment_id)
  cmor.set_cur_dataset_attribute('history',history)
  cmor.set_cur_dataset_attribute('institution',institution)
  cmor.set_cur_dataset_attribute('institution_id',institution_id)
  
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

#  if(table=='fx' or table=='Ofx'):
#    fileA='TablesTemplates/CMIP6_'+table+'.json'
#    fileB='cmor/Tables/CMIP6_'+table+'.json'
#    if filecmp.cmp(fileA,fileB):
#      pass
#    else:
#      copyfile(fileA,fileB)
#  else:

  if(season=='MON'):
    modify_json('TablesTemplates/CMIP6_'+table+'.json','cmip6-cmor-tables/Tables/CMIP6_'+table+'.json','35.00000',True)
  else:
    modify_json('TablesTemplates/CMIP6_'+table+'.json','cmip6-cmor-tables/Tables/CMIP6_'+table+'.json','400.00000',True)

  #modify_json('TablesTemplates/CMIP6_'+table+'.json','cmip6-cmor-tables/Tables/CMIP6_'+table+'.json','35.00000',True)
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  cmor_tables=['coordinate','CV','Ofx','fx']
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  for cmor_table in cmor_tables:
    #print(cmor_table,file=fh_printfile)
    fileA='TablesTemplates/CMIP6_'+cmor_table+'.json'
    fileB='cmip6-cmor-tables/Tables/CMIP6_'+cmor_table+'.json'
    if filecmp.cmp(fileA,fileB):
      pass
    else:
      copyfile(fileA,fileB)
  
#  fileA='TablesTemplates/CMIP6_coordinate.json'
#  #fileB='cmor/Tables/CMIP6_coordinate.json'
#  fileB='cmip6-cmor-tables/Tables/CMIP6_'+table+'.json'
#  if filecmp.cmp(fileA,fileB):
#    pass
#  else:
#    copyfile(fileA,fileB)
#  
#  fileA='TablesTemplates/CMIP6_CV.json'
#  #fileB='cmor/Tables/CMIP6_CV.json'
#  fileB='cmip6-cmor-tables/Tables/CMIP6_'+cmor_table+'.json'
#  if filecmp.cmp(fileA,fileB):
#    pass
#  else:
#    copyfile(fileA,fileB)
  
  tables=[]
  tables.append(cmor.load_table('cmip6-cmor-tables/Tables/CMIP6_'+table+'.json'))
  tables.append(cmor.load_table('cmip6-cmor-tables/Tables/CMIP6_grids.json'))
  tables.append(cmor.load_table('cmip6-cmor-tables/Tables/CMIP6_coordinate.json'))

  #tables.append(cmor.load_table('cmor/Tables/CMIP6_Omon.json'))
  #tables.append(cmor.load_table('cmor/Tables/CMIP6_Amon.json'))
  #tables.append(cmor.load_table('cmor/Tables/CMIP6_'+table+'.json'))
  
  #print(inputs)
  #print(type(inputs))
  
  #tables.append(cmor.load_table('cmor/Tables/CMIP6_grids.json'))
  #tables.append(cmor.load_table('cmor/Tables/CMIP6_coordinate.json'))
  
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
  
  #print(ybeg)
  #print(yend)
  
  #print(ybeg_min)
  #print(yend_max)
  
#!  if(ybeg<ybeg_min or ybeg>yend_max or yend<ybeg_min or yend>yend_max):
#!    raise SystemExit('Problem with ybeg/yend ybeg_min/yend_max',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
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
  
#!  nmy=12
  
#!  total_months_beg_to_end=(nmy-mbeg)+1 + (yend-ybeg+1-2)*nmy + mend
  
#!  ybeg_now=ybeg
#!  yend_now=yend
  
#!  mbeg_now=mbeg
#!  mend_now=mend
  
#!  print('total_months_beg_to_end=',total_months_beg_to_end,file=fh_printfile)
  
#!  print('ybeg_now=',ybeg_now,' yend_now=',yend_now,file=fh_printfile)
  
#!  sstr,times_in_season,tindex_select_maxyears_by_nmy_0or1=filemonth_index(season,ybeg_now,yend_now,mbeg_now,mend_now,fh_printfile) #MON special case where times_in_season=1, so always reading/writing one month at a time...
  
  #iii=np.arange(total_months_beg_to_end).reshape((yend-ybeg+1),12)
  #tindex_select_maxyears_by_nmy_0or1=np.zeros(iii.shape)
  #tindex_select_maxyears_by_nmy_0or1[index_start]=1
  #tindex_select_maxyears_by_nmy_0or1[index_end]=1
  #print(iii,file=fh_printfile)
#!  print('tindex_select_maxyears_by_nmy_0or1=',tindex_select_maxyears_by_nmy_0or1,file=fh_printfile)
  
#!  print('total_months_beg_to_end,total_months_beg_to_end,index_start,end=',total_months_beg_to_end,total_months_beg_to_end,file=fh_printfile)
  #,index_start,index_end)
  #raise SystemExit('Forced exit.')
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
#!  month_in_file_total_months_beg_to_end=np.ones(total_months_beg_to_end,dtype=np.int) #132, this will have to change depending on the layout of the input files...
  
#!  y=ybeg
  
#!  if(Forecast):
#!    idir_extra='/'+str('{0:04d}'.format(y))+str('{0:02d}'.format(mbeg))+str('{0:02d}'.format(1)) #probably can use 
#!  else:
#!    idir_extra=''
  
#!  if(Forecast):
#!    ifil=realm+'_'+frequency+'_'+str('{0:04d}'.format(y))+'_'+str('{0:02d}'.format(mbeg))+'.nc'
#!  else:
#!    ifil=realm+'_'+frequency+'_'+str('{0:04d}'.format(y))+'_'+str('{0:02d}'.format(1))+'.nc' #always 1
  
#!  print(y,' ',idir+idir_extra+'/'+ifil,file=fh_printfile)
#!  #raise SystemExit('Forced exit.')
#!  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
#!  f=netCDF4.Dataset(idir+idir_extra+'/'+ifil)
#!  time=f.variables['time']
  
#!  #here var_dims is just dummy as complete requirements depend on the output variable definition.
#!  
#!  if(realm=='ocean' and ( OutputVarStructure=='time_lat_lon' or OutputVarStructure=='time_depth_lat_lon' or OutputVarStructure=='time_reduceddepth_lat_lon' or OutputVarStructure=='time' or OutputVarStructure=='time_oline' or OutputVarStructure=='depth_lat_lon' or OutputVarStructure=='time_basin_depth_lat')):
#!
#!    ivar=f.variables[inputs[0]]
#!    var_dims=f.variables[inputs[0]].dimensions
#!    var_size=f.variables[inputs[0]].shape
#!    if(len(inputs)>=2):
#!      ivar2=f.variables[inputs[1]]
#!      var_dims2=f.variables[inputs[1]].dimensions
#!      var_size2=list(f.variables[inputs[1]].shape)
#!  
#!      if(len(inputs)>=3):
#!        ivar3=f.variables[inputs[2]]
#!        var_dims3=f.variables[inputs[2]].dimensions
#!        var_size3=list(f.variables[inputs[2]].shape)
#!  
#!  elif(realm=='atmos' and ( OutputVarStructure=='time_lat_lon' or OutputVarStructure=='time_plev_lat_lon' or OutputVarStructure=='time_reducedplev_lat_lon' or OutputVarStructure=='time' or OutputVarStructure=='time_lon') ):
#!    ivar=f.variables[inputs[0]]
#!    var_dims=f.variables[inputs[0]].dimensions
#!    #var_size=f.variables[inputs[0]].shape
#!    var_size=list(f.variables[inputs[0]].shape) #dont want a tuple, want a list use []
#!    #print(type(var_size))
#!    #print(var_size)
#!    #print('aaa')
#!    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
#!    if(len(inputs)>=2):
#!      ivar2=f.variables[inputs[1]]
#!      var_dims2=f.variables[inputs[1]].dimensions
#!      var_size2=list(f.variables[inputs[1]].shape)
#!  
#!      if(len(inputs)>=3):
#!        ivar3=f.variables[inputs[2]]
#!        var_dims3=f.variables[inputs[2]].dimensions
#!        var_size3=list(f.variables[inputs[2]].shape)
#!  
#!  nvar_dims=len(var_dims)
#!  
#!  #print('var_size=',var_size,file=fh_printfile)
#!  #print(var_dims,file=fh_printfile)
#!  #print(nvar_dims,file=fh_printfile)
#!  #print('dvar=',dvar,file=fh_printfile)
#!  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
#!  
#!  if(nvar_dims == 4):
#!      nlev=var_size[1]
#!      nlat=var_size[2]
#!      nlon=var_size[3]
#!  elif(nvar_dims == 3):
#!      nlat=var_size[1]
#!      nlon=var_size[2]
#!  else:
#!      nlat=0
#!      nlon=0
#!  
#!  #nlev=0
#!  #levels=0
#!  
#!  print('var_size=',var_size,file=fh_printfile)
#!  print('var_dims=',var_dims,file=fh_printfile)
  
  #if(levs=='gn1'):
  #  levels=[0,3,5]
  #  nlev=len(levels)
  #elif(levs=='gn2'):
  #  levels=[0,3]
  #  nlev=len(levels)
  #elif(levs=='gn3'):
  #  levels=[0,35,36]
  #  #levels=[1,5,36]
  #  nlev=len(levels)
  ##elif(levs=='gn5'):
  ##  levels=[xxx]
  ##  #levels=[1,5,36]
  ##  nlev=len(levels)
  #else:
  #  #levels=np.range(0,var_size[1])
  #  levels=np.array(range(0,var_size[1]-0))
  #  nlev=len(levels)
  
  #if(realm == 'ocean' and ( OutputVarStructure=='time_lat_lon' or OutputVarStructure=='time')):
  #  #or dvar=='tos' or dvar=='sos' or dvar=='sftof' or dvar=='nino34' or dvar=='iod'):
  #  levels=0
  #  nlev=1
  #elif(realm=='atmos' and OutputVarStructure=='time_lat_lon'):
  #  #dvar=='zg500' or dvar=='psl' or dvar=='ps' or dvar=='rws500' or dvar=='tauu' or dvar=='tauv' or dvar=='pr'):
  #  levels=0
  #  nlev=0
  
#!  if not 'levels' in locals():
#!    levels=range(0,var_size[1])
#!    nlev=len(levels)
#!  
#!  #print(levels)
#!  
#!  cmor.set_table(tables[1])
#!  
#!  ibeg=0
#!  
#!  refString='days since 0001-01-01'
  
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
#!  if(table=='fx_old' or table=='Ofx_old'):
#!    print('As this is a table fx parameter, all time information will be ignored.',file=fh_printfile)
#!    input_fhs={}
#!    input_fhs[0]=netCDF4.Dataset(idir+'/'+realm+'_'+frequency+'_'+str('{0:04d}'.format(ybeg_now))+'_'+'01'+'.nc')
#!  else:
#!    ybeg_now=ybeg
#!    yend_now=yend
  
#!    tindex=0
#!    input_files={}
#!    input_fhs={}
#!    for y in range(ybeg_now,yend_now+1):
#!      mend_now=1 #1 files per year of 12 months each.
#!      if(y==ybeg_now):
#!        mbeg_now=1 #need to fix
#!        mend_now=12
#!        mbeg_now=mbeg
#!      elif(y==yend_now):
#!        mbeg_now=1
#!        mend_now=mend #12 files per year of 1 months each.
#!      else:
#!        mbeg_now=1
#!        mend_now=12 #12 files per year of 1 months each.
#!      #print(mbeg_now,mend_now,file=fh_printfile)
#!      #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
#!  
#!      if(not Forecast):
#!        mbeg_now=1 #always 1 for 12 months per file.
#!        mend_now=1 #always 1 for 12 months per file.
#!  
#!      for m in range(mbeg_now,mend_now+1):
#!        if(Forecast): #has 1 month per file...
#!          idir_extra='/'+str('{0:04d}'.format(y))+str('{0:02d}'.format(m))+str('{0:02d}'.format(1))
#!        else:
#!          idir_extra=''
#!        iend=ibeg+12
#!        print(' y=',y,' m=',m,' mend_now=',mend_now,' ibeg=',ibeg,',',' iend=',iend,file=fh_printfile)
#!        ifila=realm+'_'+frequency+'_'+str('{0:04d}'.format(y))+'_'+str('{0:02d}'.format(m))+'.nc'
#!        print(y,' ',idir+idir_extra+'/'+ifila,file=fh_printfile)
#!        input_files[tindex]=idir+idir_extra+'/'+ifila
#!        if not os.path.exists(idir+idir_extra+'/'+ifila):
#!          raise SystemExit('Missing '+idir+idir_extra+'/'+ifila+'.')
#!        input_fhs[tindex]=netCDF4.Dataset(input_files[tindex])
#!        tindex+=1
  
#!    print('input files=',input_files,file=fh_printfile)
#!    #print(len(input_files),file=fh_printfile)
#!    print('tindex_select_maxyears_by_nmy_0or1=',tindex_select_maxyears_by_nmy_0or1,file=fh_printfile)
#!    #print(tindex_select_maxyears_by_nmy_0or1.shape,file=fh_printfile)
#!    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
#!  
#!    findex_select_maxyears_by_nmy_b1_withminus1s=np.copy(tindex_select_maxyears_by_nmy_0or1)
#!  
#!    if(Forecast):
#!      findex_select_maxyears_by_nmy_b1_withminus1s=findex_select_maxyears_by_nmy_b1_withminus1s*0-1 #set to -1, means no file at this position in year,month array.
#!    else:
#!      findex_select_maxyears_by_nmy_b1_withminus1s=findex_select_maxyears_by_nmy_b1_withminus1s*0-1
#!  
#!    print('findex_select_maxyears_by_nmy_b1_withminus1s=',findex_select_maxyears_by_nmy_b1_withminus1s,file=fh_printfile)
#!  
#!    yindex_select_maxyears_by_nmy=np.copy(tindex_select_maxyears_by_nmy_0or1)
#!  
#!    if(Forecast): #this is where picks up granularity of files, ie whether 1, 3, 12 months per year.
#!      fff=0
#!      for y in range(ybeg_now,yend_now+1):
#!    
#!        mend_now=1 #1 files per year of 12 months each.
#!        if(y==ybeg_now):
#!          #mbeg_now=1 #need to fix
#!          mbeg_now=mbeg
#!          mend_now=12
#!        elif(y==yend_now):
#!          mbeg_now=1
#!          mend_now=mend #12 files per year of 1 months each.
#!        else:
#!          mbeg_now=1
#!          mend_now=12 #12 files per year of 1 months each.
#!        for m in range(mbeg_now,mend_now+1):
#!          print('y,fff,y*,m*,mbeg,mend_now=',y,fff,y-ybeg_now,m-mbeg_now,mbeg_now,mend_now,file=fh_printfile)
#!          if(tindex_select_maxyears_by_nmy_0or1[y-ybeg_now,m-1]!=0):
#!            findex_select_maxyears_by_nmy_b1_withminus1s[y-ybeg_now,m-1]=tindex_select_maxyears_by_nmy_0or1[y-ybeg_now,m-1]*fff + 1
#!          else:
#!            findex_select_maxyears_by_nmy_b1_withminus1s[y-ybeg_now,m-1]=0
#!          fff+=1
#!    else:
#!      y=ybeg_now
#!      for fff in range(len(input_files)):
#!        print(fff,file=fh_printfile)
#!        #if(tindex_select_maxyears_by_nmy_0or1[y-ybeg_now,m-1]!=0):
#!        #  findex_select_maxyears_by_nmy_b1_withminus1s[fff,:]=tindex_select_maxyears_by_nmy_0or1[fff,:]*fff + 1
#!        #else:
#!        #  findex_select_maxyears_by_nmy_b1_withminus1s[y-ybeg_now,m-1]=0
#!        findex_select_maxyears_by_nmy_b1_withminus1s[fff,:]=(tindex_select_maxyears_by_nmy_0or1[fff,:]*fff + 1)*tindex_select_maxyears_by_nmy_0or1[fff,:]
#!        y+=1
#!  
#!    print('findex_select_maxyears_by_nmy_b1_withminus1s=',findex_select_maxyears_by_nmy_b1_withminus1s,file=fh_printfile)
#!  
#!    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
#!  
#!    tindex_select_maxyears_by_nmy_0or1_flat=tindex_select_maxyears_by_nmy_0or1.reshape((yend_now-ybeg_now+1)*12)
#!    print('tindex_select_maxyears_by_nmy_0or1_flat=',tindex_select_maxyears_by_nmy_0or1_flat,file=fh_printfile)
#!    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
#!  
#!    numtims=int(np.sum(tindex_select_maxyears_by_nmy_0or1_flat))
#!  
#!    print('number of times used in each season definition, times_in_season=',times_in_season,file=fh_printfile)
#!    print('total number of times (months) read in including any partial begin and end year, total_months_beg_to_end=',total_months_beg_to_end,file=fh_printfile)
#!    print('number of times used from input file, numtims=',numtims,file=fh_printfile)
#!  #  print('total number of seasons written out, numseas=',numseas,file=fh_printfile)
#!  
#!  #file_index_maxyears_by_nmy_b1_withminus1s is an array year,month. elements corresonding to the valid input months/years are inserted (0...max-1), a -1 means that no file is present or included. file_index_maxyears_by_nmy_b1_withminus1s_flat is vector version of file_index_maxyears_by_nmy_b1_withminus1s.
#!  #file_index_maxyears_by_nmy_b1_nominus1s_flat is list from 0...max-1 number of files, gets rid of any -1s indicating missing months.
#!  #month_index_ntims is an vector year...month with ONLY valid year,month (values going from 0..11 only corresponding to month.
#!  #year_index_ntims, similar to month_index_ntims, only now years, actual years corresponding to each of the months in month_index_ntims
  
#!    file_index_maxyears_by_nmy_b1_withminus1s,month_index_ntims=np.where(tindex_select_maxyears_by_nmy_0or1==1)
#!  
#!    print('file_index_maxyears_by_nmy_b1_withminus1s=',file_index_maxyears_by_nmy_b1_withminus1s,file=fh_printfile)
#!    print('file_index_maxyears_by_nmy_b1_withminus1s.size=',file_index_maxyears_by_nmy_b1_withminus1s.size,file=fh_printfile)
#!  
#!    year_index_ntims=file_index_maxyears_by_nmy_b1_withminus1s+ybeg_now
#!  
#!    file_index_maxyears_by_nmy_b1_withminus1s=findex_select_maxyears_by_nmy_b1_withminus1s.astype(int) #try, why do I overwrite definition above?
#!  
#!    file_index_maxyears_by_nmy_b1_withminus1s=np.where(file_index_maxyears_by_nmy_b1_withminus1s>0,file_index_maxyears_by_nmy_b1_withminus1s+0,file_index_maxyears_by_nmy_b1_withminus1s) #add 1 to values > 0
#!  
#!    print('file_index_maxyears_by_nmy_b1_withminus1s=',file_index_maxyears_by_nmy_b1_withminus1s,file=fh_printfile)
#!    print('file_index_maxyears_by_nmy_b1_withminus1s.size=',file_index_maxyears_by_nmy_b1_withminus1s.size,file=fh_printfile)
#!  
#!    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
#!  
#!    print('month_index_ntims=',month_index_ntims,file=fh_printfile)
#!    print('month_index_ntims.size=',month_index_ntims.size,file=fh_printfile)
#!    print('year_index_ntims=',year_index_ntims,file=fh_printfile)
#!    print('year_index_ntims.size=',year_index_ntims.size,file=fh_printfile)
#!  
#!    file_index_maxyears_by_nmy_b1_withminus1s_flat=file_index_maxyears_by_nmy_b1_withminus1s.flatten()
#!  
#!    print('file_index_maxyears_by_nmy_b1_withminus1s_flat=',file_index_maxyears_by_nmy_b1_withminus1s_flat,file=fh_printfile)
#!  
#!    file_index_maxyears_by_nmy_b1_nominus1s_flat=file_index_maxyears_by_nmy_b1_withminus1s_flat[np.where(file_index_maxyears_by_nmy_b1_withminus1s_flat>0,True,False)]
#!  
#!    print('file_index_maxyears_by_nmy_b1_nominus1s_flat=',file_index_maxyears_by_nmy_b1_nominus1s_flat,file=fh_printfile)
#!  
#!    locate_file_index_Ntimes_b1_nominus1s_flat=file_index_maxyears_by_nmy_b1_nominus1s_flat[np.where(file_index_maxyears_by_nmy_b1_nominus1s_flat>0)]
#!  
#!    print('locate_file_index_Ntimes_b1_nominus1s_flat=',locate_file_index_Ntimes_b1_nominus1s_flat,file=fh_printfile)
#!    print('locate_file_index_Ntimes_b1_nominus1s_flat.shape=',locate_file_index_Ntimes_b1_nominus1s_flat.shape,file=fh_printfile)
#!  
#!    cnt_file_index_maxyears_by_nmy_b1_nominus1s_flat=len(locate_file_index_Ntimes_b1_nominus1s_flat)
#!    print('cnt_file_index_maxyears_by_nmy_b1_nominus1s_flat=',cnt_file_index_maxyears_by_nmy_b1_nominus1s_flat,file=fh_printfile)
#!    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
#!  
#!    tbeg=[]
#!    tend=[]
#!    tavg=[]
#!    ind_beg=0
#!    #will need to improve when ending time is December as will need to increment year by 1 too.
#!    day1=1
#!  
#!    if(season=='MON'):
#!      ttt=total_months_beg_to_end
#!    else:
#!      ttt=cnt_file_index_maxyears_by_nmy_b1_nominus1s_flat/times_in_season #this should be equal to number of valid months/3
#!  
#!    print('ttt=',ttt,' times_in_season=',times_in_season,file=fh_printfile)
#!  
#!    for n in range(0,ttt):
#!      #ind_end=ind_beg+times_in_season-1
#!  
#!      if(season=='MON'):
#!        #ind_end=ind_beg+times_in_season
#!        ind_end=ind_beg #always 1 month at a time for MON
#!      else:
#!        ind_end=ind_beg+times_in_season-1
  
#!      #print('n,ind_beg,ind_end,year_beg,month_beg,year_end,month_end=',n,ind_beg,ind_end,year_index_ntims[ind_beg],month_index_ntims[ind_beg],year_index_ntims[ind_end],month_index_ntims[ind_end],file=fh_printfile)
#!  
#!      month_index_beg=month_index_ntims[ind_beg]+1
#!      year_index_beg=year_index_ntims[ind_beg]
  
      #print('year,month_index_beg=',year_index_beg,month_index_beg,file=fh_printfile)
  
#!      tbeg.append(cdtime.comptime(year_index_beg,month_index_beg,day1).torel(refString).value)
#!      #print(month_index_ntims[ind_beg],file=fh_printfile)
#!  
#!      if(season=='MON'):
#!        if(n==0):
#!          #print('n==0',file=fh_printfile)
#!          month_index_end=month_index_beg+1
#!          year_index_end=year_index_beg
#!        else:
#!          #print('n!=0',file=fh_printfile)
#!          month_index_end=month_index_beg+1
#!          year_index_end=year_index_beg
#!      elif(season=='ANN'):
#!        if(n==ttt-1): #last one special
#!          month_index_end=month_index_ntims[ind_end-1]+1+1+1
#!          year_index_end=year_index_ntims[ind_end-1]
#!        else:
#!          month_index_end=month_index_ntims[ind_end]+1+1
#!          year_index_end=year_index_ntims[ind_end]
#!      else:
#!        if(n==ttt-1): #last one special
#!          month_index_end=month_index_ntims[ind_end-1]+1+1
#!          year_index_end=year_index_ntims[ind_end-1]
#!        else:
#!          month_index_end=month_index_ntims[ind_end]+1
#!          year_index_end=year_index_ntims[ind_end]
#!  
#!      if(month_index_end>nmy):
#!         month_index_end=month_index_end-nmy
#!         year_index_end+=1
#!  
#!      print('n=',n,' ind_beg=',ind_beg,' ind_end=',ind_end,' year_index_beg=',year_index_beg,' month_index_beg=',month_index_beg,' year_index_end=',year_index_end,' month_index_end=',month_index_end,file=fh_printfile)
#!  
#!      tdelta=1.0
#!      tdelta=0.0
#!  
#!      #tdelta=0
#!      #tdelta=1
#!  
#!      tend.append(cdtime.comptime(year_index_end,month_index_end,day1).torel(refString).value-tdelta) #assume in days, -1 gets numer of days of wanted month (ie. prior month without having to know number of days in month)
#!      #print('tbeg,tend=',tbeg,tend,file=fh_printfile)
#!  
#!      #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
#!      ind_beg=ind_end+1
#!      if(season=='MON'):
#!        ind_beg=ind_end+1
#!      else:
#!        ind_beg=ind_end+1
#!  
#!    tbeg=np.array(tbeg)
#!    tend=np.array(tend)
#!    tavg=(tbeg+tend)/2.0
#!    tval_bounds=np.column_stack((tbeg,tend))
  
#!    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
#!    #print('tbeg,tend,tavg=',tbeg,tend,tavg)
#!    timestamp_avg=netCDF4.num2date(tavg,units=refString,calendar=calendar)
#!    timestamp_beg=netCDF4.num2date(tbeg,units=refString,calendar=calendar)
#!    timestamp_end=netCDF4.num2date(tend,units=refString,calendar=calendar)
#!  
#!    print('timestamp_avg,beg,end:',file=fh_printfile)
#!    for n in range(0,ttt):
#!      print(timestamp_avg[n],timestamp_beg[n],timestamp_end[n],file=fh_printfile)
#!  
#!    #print('timestamp_avg=',timestamp_avg,timestamp_beg)
#!  
#!    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
#!  
#!    #tables[0]=cmor.load_table('cmor/Tables/CMIP6_Amon.json')
#!    cmor.set_table(tables[0])
#!    #itime=cmor.axis(table_entry= 'time', length=5, units=refString, coord_vals=tavg[:], cell_bounds=tval_bounds[:], interval=None)
#!    #itime=cmor.axis(table_entry= 'time', length=5, units=refString, coord_vals=tavg[:], cell_bounds=tval_bounds[:])
#!    #itime=cmor.axis('time', units=refString, coord_vals=tavg[:], cell_bounds=tval_bounds[:])
#!  
#!    #print('tavg=',tavg,file=fh_printfile)
#!    #print('tval_bounds=',tval_bounds,file=fh_printfile)
#!  
#!    time_axis_id=cmor.axis('time', units=refString, coord_vals=tavg, cell_bounds=tval_bounds)

###############################################################################

#ProcTime variables related to input and output files and specifically the broadcasting of uniquely defined seasons or their average..

  ProcTimeseason=season

  ProcTimeexperiment=cafe_experiment

  ProcTimerealm=realm

  ProcTimefrequency=frequency

  Diagnostic=False

  #Delete these variables, if they are not set then the full range based on input files will be used.
  if('ProcTimeybeg_season_process' in locals()): del(ProcTimeybeg_season_process)
  if('ProcTimeyend_season_process' in locals()): del(ProcTimeyend_season_process)
  if('ProcTimembeg_season_process' in locals()): del(ProcTimembeg_season_process)
  if('ProcTimemend_season_process' in locals()): del(ProcTimemend_season_process)

  if(ProcTimeexperiment=='coupled_da/OUTPUT-2step-nobreeding-carbon2'):
    ProcTimehours=360.0 #this helps to identify year/month from the time-stamps. This experiment time-stamp is at the end of the month.
    #ProcTimeybeg_season_process,ProcTimeyend_season_process,ProcTimembeg_season_process,ProcTimemend_season_process=2002,2016,1,12 #potential for 2002,2016 for DecJan cross over seasons else 2012,2016. These would be the years required for the seasonal averages if wanting to truncate the entire output, an error will occur if they do not exist. Default would be all years. mbeg,end really only applies to situations with season=MON or single month defined seasons.
    ProcTimeidir='/short/v14/tok599/coupled/ao_am2/coupled_da/workdir2/OUTPUT-2step-nobreeding-carbon2'
    ProcTimeinput_directories=sorted(glob.glob(ProcTimeidir+'/'+'????????/'))
  
    ProcTimeinput_files=[]
    for ProcTimei,ProcTimeinput_directory in enumerate(ProcTimeinput_directories):
      if(Diagnostic): print('ProcTimei,ProcTimeinput_directory=',ProcTimei,ProcTimeinput_directory) #get rid of not.
      ProcTimelist_of_files=sorted((glob.glob(ProcTimeinput_directory+'/'+ProcTimerealm+'_'+ProcTimefrequency+'_????_??.nc')))
      ProcTimeinput_files.append(ProcTimelist_of_files[0])
    
  elif(ProcTimeexperiment=='v1_forecast'):
    #with this kind of experiment we would have to loop over each 2/5 year experiment as well as ensemble, producing one output file for each.
    ProcTimehours=0.0 #this helps to identify year/month from the time-stamps. This experiment time-stamp is at the middle of that month.
    ProcTimeybeg_season_process,ProcTimeyend_season_process,ProcTimembeg_season_process,ProcTimemend_season_process=2003,2004,1,12 #potential for 2002,2004
    ProcTimeinput_directory='/g/data1/v14/forecast/v1/yr2002/mn2/OUTPUT.1'
    ProcTimeinput_files=sorted((glob.glob(ProcTimeinput_directory+'/'+ProcTimerealm+'_'+ProcTimefrequency+'_????_??.nc')))

  elif(ProcTimeexperiment=='v2'):
    #with this kind of experiment might want to supply just a subset of years to speed initialisatin of processing.
    #or supply all years and use processing scalars to reduce set.
  
    ProcTimehours=0.0 #this helps to identify year/month from the time-stamps. This experiment time-stamp is at the middle of that month.
    ProcTimeybeg_season_process,ProcTimeyend_season_process,ProcTimembeg_season_process,ProcTimemend_season_process=1,500,1,12 #potential for 1,500,1,12
    ProcTimeinput_directory='/g/data1/v14/coupled_model/v2/OUTPUT'
    ProcTimeinput_files=sorted((glob.glob(ProcTimeinput_directory+'/'+ProcTimerealm+'_'+ProcTimefrequency+'_????_??.nc'))) #all files
    #ProcTimeinput_files=sorted(glob.glob(ProcTimeinput_directory+'/'+ProcTimerealm+'_'+ProcTimefrequency+'_049?_??.nc')+glob.glob(ProcTimeinput_directory+'/'+ProcTimerealm+'_'+ProcTimefrequency+'_0500_??.nc')) #last 10 years.
  
    #print(type(input_files))
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  else:
    raise Exception('Don\'t know experiment '+ProcTimeexperiment+' file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  #if they are defined use them, else the full range of years/months based on input files will be used.
  if('ybeg' in locals()):
    ProcTimeybeg_season_process,ProcTimeyend_season_process,ProcTimembeg_season_process,ProcTimemend_season_process=ybeg,yend,mbeg,mend

  if(Diagnostic): #get rid of not.
    print('ProcTimeinput_directories=',ProcTimeinput_directories)

  if(not Diagnostic): #get rid of not.
    print('ProcTimeinput_files=',ProcTimeinput_files)
  
  #print(list_of_files)
    #for i,input_file in enumerate(input_files):
#  print('i,input_file=',i,input_file)
#input_files=input_files[5:-5] #can take off input files from beginning/end to see impact on calculation of seasonal quantities. 5,-5 would take off first and last 5 months.

  ProcTimeseason_broadcast_override=False
  #ProcTimeseason_broadcast_override=True #we might want to write out invididual months of a season rather than forming the seasonal average, override as this is not the usual.

  ProcTimeseason_map={\
              'DJF':[12,1,2],\
              'MAM':[3,4,5],\
              'JJA':[6,7,8],\
              'SON':[9,10,11],\
              'JJAS':[6,7,8,9],\
              'ANN':[1,2,3,4,5,6,7,8,9,10,11,12],\
              'DecJan':[12,1],\
              'JunJul':[6,7],\
              'MON':[1,2,3,4,5,6,7,8,9,10,11,12],\
              'Jan':[1],\
              'Feb':[2],\
              'Mar':[3],\
              'Apr':[4],\
              'May':[5],\
              'Jun':[6],\
              'Jul':[7],\
              'Aug':[8],\
              'Sep':[9],\
              'Oct':[10],\
              'Nov':[11],\
              'Dec':[12],\
              } #months required for each seasonal definition, avoid ambiguity by using lowercase letters where necessary.

  ProcTimeseason_broadcast={\
              'DJF':False,\
              'MAM':False,\
              'JJA':False,\
              'SON':False,\
              'JJAS':False,\
              'ANN':False,\
              'DecJan':False,\
              'JunJul':False,\
              'MON':True,\
              'Jan':True,\
              'Feb':True,\
              'Mar':True,\
              'Apr':True,\
              'May':True,\
              'Jun':True,\
              'Jul':True,\
              'Aug':True,\
              'Sep':True,\
              'Oct':True,\
              'Nov':True,\
              'Dec':True,\
            } #True means to broadcast all inputs times to the output, else it would be an average of all times.

  if(Diagnostic):
    print('ProcTimeseason_map.keys()=',ProcTimeseason_map.keys())
    print('ProcTimeseason_broadcast.keys()=',ProcTimeseason_broadcast.keys())

  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  #various integrity test on season_map:
  for ProcTimekey in ProcTimeseason_map.iterkeys():
    if(ProcTimekey not in ProcTimeseason_broadcast):
      raise Exception('Missing matching ProcTimekey',ProcTimekey,' in ProcTimeseason_broadcast dictionary file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    ProcTimeunique_season_map_key=list(set(ProcTimeseason_map[ProcTimekey]))
    #print(sorted(ProcTimeunique_season_map_key),sorted(ProcTimeseason_map[ProcTimekey]))
    if(not sorted(ProcTimeunique_season_map_key)==sorted(ProcTimeseason_map[ProcTimekey])):
      raise Exception('ProcTimeseason_map must have unique numbers in it file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    ProcTimetest_season_map_key=array("i",ProcTimeseason_map[ProcTimekey])
    if(min(ProcTimetest_season_map_key)<0 or max(ProcTimetest_season_map_key)>12):
      raise Exception('Month indices must be between 1 and 12 file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  #various tests on season_broadcast
  for ProcTimekey in ProcTimeseason_broadcast.iterkeys():
    if(ProcTimekey not in ProcTimeseason_map):
      raise Exception('Missing matching ProcTimekey',ProcTimekey,' in ProcTimeseason_map dictionary file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    if(type(ProcTimeseason_broadcast[ProcTimekey])!=types.BooleanType):
      raise Exception('ProcTimeseason_broadcast must be True or False file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    
  if(ProcTimeseason in ProcTimeseason_map):
    print('Found season definition',ProcTimeseason,' in ProcTimeseason_map with indices ',ProcTimeseason_map[ProcTimeseason],' file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  else:
    raise Exception('Season definition not in ProcTimeseason_map file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  if(ProcTimeseason_broadcast_override and ProcTimeseason_broadcast[ProcTimeseason]): 
    raise Exception('ProcTimeseason_broadcast and chosen season already broadcast, perhaps set ProcTimeseason_broadcast_override=False :'+__file__+' line number: '+str(inspect.stack()[0][2]))

  if(ProcTimeseason_broadcast_override and not ProcTimeseason_broadcast[ProcTimeseason]): #this must occur after previous test.
    print('Overriding default ProcTimeseason_broadcast setting, i.e. broadcasting seasonal values rather than this season\'s normal averaging.')
    ProcTimeseason_broadcast[ProcTimeseason]=True


  if(ProcTimeseason_broadcast[ProcTimeseason] and ProcTimeseason=='ANN'):
    raise Exception('Doesn\'t make sense to broadcast season ANN, use season MON instead file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  print('ProcTimeseason_brodcast=',ProcTimeseason_broadcast)
  
  ProcTimemonth_indices=ProcTimeseason_map[ProcTimeseason]
  ProcTimenpmonth_indices=np.array(ProcTimemonth_indices)

  if('ProcTimembeg_season_process' in locals()):
    if(ProcTimembeg_season_process<1 or ProcTimembeg_season_process>12 or ProcTimemend_season_process<1 or ProcTimemend_season_process>12):
      raise Exception('Processing months must be between 1 and 12.')

  if(ProcTimeseason_broadcast[ProcTimeseason] and (len(ProcTimeseason_map[ProcTimeseason])>1 and len(ProcTimeseason_map[ProcTimeseason])<12)):
    raise Exception('Note that cmor will not easily write out b/w 2 and 11 months out due to time_axis restrictions, however, might be something we can do in the future.')
    #print(len(ProcTimeseason_map[ProcTimeseason]))

  if(Diagnostic):
    print('Using month indices=',ProcTimemonth_indices)

  if('ProcTimeybeg_season_process' in locals()):
    if(ProcTimeybeg_season_process>ProcTimeyend_season_process):
      raise Exception('ProcTimeybeg_season>ProcTimeyend_season file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

###############################################################################

  ProcTimeifhN=netCDF4.MFDataset(ProcTimeinput_files)
  ProcTimetime=ProcTimeifhN.variables['time'] #note that time-stamp appears to be last time in the month which has the next month ID.
  ProcTimenum_stamps=netCDF4.num2date(ProcTimetime[:],ProcTimetime.units,ProcTimetime.calendar) - datetime.timedelta(hours=ProcTimehours) #take away 360 hours, 15 days which is a time approximately in the middle of the month to enable proper year/month determination.
  
  #ProcTimeifhN.close() #would not close if within cafepp.
  
  ProcTimeyears=[]
  ProcTimemonths=[]
  ProcTimeis=[]
  ProcTimeisp1=[]
  ProcTimeMonfromStart=[]
  
  for ProcTimei,ProcTimenum_stamp in enumerate(ProcTimenum_stamps):
    ProcTimeyears.append(ProcTimenum_stamp.year)
    ProcTimemonths.append(ProcTimenum_stamp.month)
    ProcTimeMonfromStart.append(ProcTimenum_stamps[0].month+ProcTimei)
    ProcTimeis.append(ProcTimei)
    ProcTimeisp1.append(ProcTimei+1)
    
  if(not Diagnostic): #get rid of not.
    for ProcTimei,ProcTimenum_stamp in enumerate(ProcTimenum_stamps):
      print('ProcTimei,ProcTimei+1,ProcTimeMonfromStart,ProcTimeyear,ProcTimemonth,ProcTimenum_stamp=',ProcTimei,ProcTimei+1,ProcTimeMonfromStart[ProcTimei],ProcTimeyears[ProcTimei],ProcTimemonths[ProcTimei],ProcTimenum_stamps[ProcTimei])
  
  ProcTimenpyears=np.array(ProcTimeyears)
  ProcTimenpmonths=np.array(ProcTimemonths)
  #print(ProcTimenpmonths)
  #exit()
  
  ProcTimeybeg_min=np.min(ProcTimenpyears) #first year in the original time-series
  ProcTimeyend_max=np.max(ProcTimenpyears) #last year in the original time-series
  
  ProcTimeindex_mbeg_min=np.argmin(ProcTimenpyears)
  ProcTimeindex_mend_max=np.argmax(ProcTimenpyears[::-1])
  
  ProcTimenpmonths_reverse=ProcTimenpmonths[::-1]
  ProcTimembeg_min=ProcTimenpmonths[ProcTimeindex_mbeg_min] #minimum month in first year of the original time-series.
  ProcTimemend_max=ProcTimenpmonths_reverse[ProcTimeindex_mend_max] #maximum month in last year of the original time-series.
  
  #print(npmonth_indices.size)
  
  if(ProcTimenpmonth_indices.size>1 and any(np.gradient(ProcTimenpmonth_indices)<0)):
    ProcTimeSeasonCrossDecJan=True
  else:
    ProcTimeSeasonCrossDecJan=False
  
  if(ProcTimeSeasonCrossDecJan):
    if(Diagnostic): print('Season definition includes December/January and so one year is lost cf. to the total number of years present.')
    ProcTimeybeg_season_min=ProcTimeybeg_min+1
  else:
    ProcTimeybeg_season_min=ProcTimeybeg_min

  if('ProcTimeybeg_season_process' not in locals()):
    ProcTimeybeg_season_process=ProcTimeybeg_min
    ProcTimeyend_season_process=ProcTimeyend_max
    ProcTimembeg_season_process=ProcTimembeg_min
    ProcTimemend_season_process=ProcTimemend_max
  
  if(not Diagnostic):
    print('ProcTimeybeg_min,ProcTimeyend_max,ProcTimembeg_min,ProcTimemend_max,ProcTimeybeg_season_min=',ProcTimeybeg_min,ProcTimeyend_max,ProcTimembeg_min,ProcTimemend_max,ProcTimeybeg_season_min)
  
  if(not Diagnostic):
    print('ProcTimeybeg_season_process,ProcTimeyend_season_process,ProcTimembeg_season_process,ProcTimemend_season_process=',ProcTimeybeg_season_process,ProcTimeyend_season_process,ProcTimembeg_season_process,ProcTimemend_season_process)

###############################################################################

  if(not Diagnostic):
    print('ProcTimeybeg_min,ProcTimeyend_max,ProcTimembeg_min,ProcTimemend_max,ProcTimeybeg_season_min=',ProcTimeybeg_min,ProcTimeyend_max,ProcTimembeg_min,ProcTimemend_max,ProcTimeybeg_season_min)
  
  if(not Diagnostic):
    print('ProcTimeybeg_season_process,ProcTimeyend_season_process,ProcTimembeg_season_process,ProcTimemend_season_process=',ProcTimeybeg_season_process,ProcTimeyend_season_process,ProcTimembeg_season_process,ProcTimemend_season_process)
  
  ProcTimelen_months=len(ProcTimemonths) #or years
  ProcTimelen_month_indices=len(ProcTimemonth_indices)
  
  if(ProcTimeseason_broadcast[ProcTimeseason]):
    print('Here we are broadcasting, for MON will print out all available months unless mbeg_season_process,mend_season_process defined otherwies.')
  
  print('ProcTimebroadcast=',ProcTimeseason_broadcast[ProcTimeseason])
  print('ProcTimeseason=',ProcTimeseason)
  
  if(ProcTimeseason=='MON'):
    print('Special case, print out all months unless restricted by mbeg_season_process,mend_season_process.')
  
    #modify monthly min/max to process, if appropriate:
    if(ProcTimeybeg_season_process<ProcTimeybeg_min and ProcTimembeg_season_process<ProcTimembeg_min):
      raise SystemExit('Processing year/month is less than what is available: '+__file__+' line number: '+str(inspect.stack()[0][2]))
      
    if(ProcTimeyend_season_process>ProcTimeyend_max and ProcTimemend_season_process>ProcTimemend_max):
      raise SystemExit('Processing year/month is greater than what is available: '+__file__+' line number: '+str(inspect.stack()[0][2]))
  
    if(ProcTimeybeg_season_process==ProcTimeybeg_min and ProcTimembeg_season_process<ProcTimembeg_min):
      print('First year to be processed is less that available, setting to be same.')
      ProcTimembeg_season_process=ProcTimembeg_min
    
    if(ProcTimeyend_season_process==ProcTimeyend_max and ProcTimemend_season_process>ProcTimemend_max):
      print('Last year to be processed is more than available, setting to be same.')
      ProcTimemend_season_process=ProcTimemend_max
      
    if(not Diagnostic):
      print('ProcTimeybeg_season_process,ProcTimeyend_season_process,ProcTimembeg_season_process,ProcTimemend_season_process=',ProcTimeybeg_season_process,ProcTimeyend_season_process,ProcTimembeg_season_process,ProcTimemend_season_process)
  
    #raise Exception('STOP!')
      
    #ProcTimembeg_season_process=ProcTimembeg_min
    #if(ProcTimeyend_season_process<=ProcTimeyend_max): ProcTimemend_season_process=ProcTimemend_max
    
    ProcTimejjj=np.where(ProcTimenpyears==ProcTimeybeg_season_process,1,0)
    ProcTimekkk=np.where(ProcTimenpmonths==ProcTimembeg_season_process,1,0)
    ProcTimelll=ProcTimejjj+ProcTimekkk
    ProcTimebegpos=np.argmax(ProcTimelll)
    #print('ProcTimejjj=',ProcTimejjj)
    #print('len(ProcTimejjj)=',len(ProcTimejjj))
    #print('ProcTimekkk=',ProcTimekkk)
    #print('len(ProcTimekkk)=',len(ProcTimekkk))
    print('ProcTimelll=',ProcTimelll)
    
    ProcTimejjj=np.where(ProcTimenpyears==ProcTimeyend_season_process,1,0)
    ProcTimekkk=np.where(ProcTimenpmonths==ProcTimemend_season_process,1,0)
    ProcTimelll=ProcTimejjj+ProcTimekkk
    ProcTimeendpos=np.argmax(ProcTimelll)
    #print('ProcTimejjj=',ProcTimejjj)
    #print('len(ProcTimejjj)=',len(ProcTimejjj))
    #print('ProcTimekkk=',ProcTimekkk)
    #print('len(ProcTimekkk)=',len(ProcTimekkk))
    print('ProcTimelll=',ProcTimelll)
    
    print('ProcTimebegpos,ProcTimeendpos=',ProcTimebegpos,ProcTimeendpos)
    
    ProcTimeyears_defined=sorted(set(ProcTimenpyears[ProcTimebegpos:ProcTimeendpos+1]))
    print('ProcTimeyears_defined=',ProcTimeyears_defined)
    #print(ProcTimenpyears[ProcTimebegpos:ProcTimeendpos+1],ProcTimenpmonths[ProcTimebegpos:ProcTimeendpos+1],ProcTimeMonfromStart[ProcTimebegpos:ProcTimeendpos+1])
    
    ProcTimelistA,ProcTimelistB=[],[]
    ProcTimeseason_indices_defined=[]
    ProcTimeseason_month_indices_defined=[]
    
    yearNow=ProcTimenpyears[ProcTimebegpos]
    #print('yearNow=',yearNow)
    for ProcTimeiii,ProcTimeppp in enumerate(range(ProcTimebegpos,ProcTimeendpos+1)): #loop over the years & months of interest only with ProcTimebegpos & ProcTimeendpos
      print('ProcTimeiii,ProcTimenpyears[ProcTimeppp],ProcTimenpmonths[ProcTimeppp],ProcTimeMonfromStart[ProcTimeppp]',ProcTimeppp,ProcTimenpyears[ProcTimeppp],ProcTimenpmonths[ProcTimeppp],ProcTimeMonfromStart[ProcTimeppp])
  
      #yearNow=ProcTimenpyears[ProcTimeppp]
      #print('ProcTimelistA,ProcTimelistB=',ProcTimelistA,ProcTimelistB)
      #raise Exception('XXX!')
      
      #print(type(ProcTimenpyears[ProcTimeppp]),type(yearNow))
      if(ProcTimenpyears[ProcTimeppp]!=yearNow):
        #print('ProcTimelistA,ProcTimelistB=',ProcTimelistA,ProcTimelistB)
        ProcTimeseason_indices_defined.append(ProcTimelistA)
        ProcTimeseason_month_indices_defined.append(ProcTimelistB)
        ProcTimelistA,ProcTimelistB=[],[]
        ProcTimelistA.append(ProcTimenpmonths[ProcTimeppp])
        ProcTimelistB.append(ProcTimeMonfromStart[ProcTimeppp])
        yearNow=ProcTimenpyears[ProcTimeppp]
      else:
        #raise Exception('XXX!')
        ProcTimelistA.append(ProcTimenpmonths[ProcTimeppp])
        ProcTimelistB.append(ProcTimeMonfromStart[ProcTimeppp])
  
    #last ones are not picked up by if/else, need to do here or change logic above a bit.
    ProcTimeseason_indices_defined.append(ProcTimelistA)
    ProcTimeseason_month_indices_defined.append(ProcTimelistB)
  
        #yearNow=ProcTimenpyears[ProcTimeiii]
        #print('listA,listB=',listA,listB)
      #raise Exception('XXX!')
    #print('ProcTimeseason_indices_defined (#'+str(len(ProcTimeseason_indices_defined))+') =',ProcTimeseason_indices_defined)
    #print('ProcTimeseason_month_indices_defined (#'+str(len(ProcTimeseason_month_indices_defined))+') =',ProcTimeseason_month_indices_defined)
    #raise Exception('STOP!')
    
  else: #seasons!='MON'
  
    ProcTimeseason_indices_defined = []
    ProcTimeseason_month_indices_defined = [] #new
    ProcTimeyears_defined = [] #based on success of season indice matching.
  
    for ProcTimei in range(ProcTimelen_months): #maybe use xrange
      ProcTimesegment=ProcTimenpmonths[ProcTimei:ProcTimei+ProcTimelen_month_indices]
      #print('type(segment)=',type(segment))
      #jjj=set(segment)
      #kkk=set(npmonth_indices)
      #print('jjj,kkk=',jjj,kkk)
      
      if (np.array_equal(ProcTimesegment,ProcTimenpmonth_indices)):
        #print('yes')
        ProcTimeseason_month_indices_defined.append((range(ProcTimei+1, ProcTimei+ProcTimelen_month_indices+1)))
        ProcTimeseason_indices_defined.append(ProcTimemonths[ProcTimei:ProcTimei+ProcTimelen_month_indices]) #new, this will be used to work out monthly weights in cafepp.
        ProcTimeyears_defined.append(ProcTimeyears[ProcTimei])
        
    if(Diagnostic):   
      print('ProcTimeseason_indices_defined=',ProcTimeseason_indices_defined)
      print('ProcTimeseason_month_indices_defined=',ProcTimeseason_month_indices_defined)
      print('ProcTimeyears_defined=',ProcTimeyears_defined)
    
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
      
    ProcTimeyears_season_valid=[] #can use this to determine if a valid minimum or maximum year is selected, the default would be all years.
    
    for ProcTimeyear in range(ProcTimeybeg_season_min,ProcTimeyend_max+1):
      ProcTimeyears_season_valid.append(ProcTimeyear)
  
  if(not ProcTimeSeasonCrossDecJan):
    ProcTimeabc_beg=ProcTimeyears_defined.index(ProcTimeybeg_season_process)
    ProcTimeabc_end=ProcTimeyears_defined.index(ProcTimeyend_season_process)
  
    if(Diagnostic):
      print('ProcTimeabc_beg,end=',ProcTimeabc_beg,ProcTimeabc_end)
  
    #overwrite if necessary based on processed years indices ProcTimeabc_beg,end found above:
    ProcTimeseason_indices_defined=ProcTimeseason_indices_defined[ProcTimeabc_beg:ProcTimeabc_end+1]
    ProcTimeseason_month_indices_defined=ProcTimeseason_month_indices_defined[ProcTimeabc_beg:ProcTimeabc_end+1]
    ProcTimeyears_defined=ProcTimeyears_defined[ProcTimeabc_beg:ProcTimeabc_end+1]
  
    if(Diagnostic):
      print('ProcTimeseason_indices_defined (#'+str(len(ProcTimeseason_indices_defined))+') =',ProcTimeseason_indices_defined)
      print('ProcTimeseason_month_indices_defined (#'+str(len(ProcTimeseason_month_indices_defined))+') =',ProcTimeseason_month_indices_defined)
      print('ProcTimeyears_defined (#'+str(len(ProcTimeyears_defined))+') =',ProcTimeyears_defined)
    
      #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    
  elif(ProcTimeSeasonCrossDecJan): #need to add one for seasons that cross the Dec/Jan divide.
    ProcTimenparray_years_defined=np.array(ProcTimeyears_defined)
    ProcTimenparray_years_defined+=1
    ProcTimeyears_defined = []
    for ProcTimei,ProcTimeyear in enumerate(ProcTimenparray_years_defined): #the reassign back to year_defined, nparray_years not needed anymore.
      ProcTimeyears_defined.append(ProcTimeyear)
    del(ProcTimenparray_years_defined)
  
    ProcTimeabc_beg=ProcTimeyears_defined.index(ProcTimeybeg_season_process)
    ProcTimeabc_end=ProcTimeyears_defined.index(ProcTimeyend_season_process)
  
    ProcTimeseason_indices_defined=ProcTimeseason_indices_defined[ProcTimeabc_beg:ProcTimeabc_end+1]
    ProcTimeseason_month_indices_defined=ProcTimeseason_month_indices_defined[ProcTimeabc_beg:ProcTimeabc_end+1]
    ProcTimeyears_defined=ProcTimeyears_defined[ProcTimeabc_beg:ProcTimeabc_end+1]
    
  if(not Diagnostic):
    #print('ProcTimenparray_years_defined=',ProcTimenparray_years_defined)
    if('ProcTimeyears_season_valid' in locals()): print('ProcTimeyears_season_valid (#'+str(len(ProcTimeyears_season_valid))+') =',ProcTimeyears_season_valid) #can't trust this b/c although might have final year, all months may not be present.
    print('ProcTimeseason_indices_defined (#'+str(len(ProcTimeseason_indices_defined))+') =',ProcTimeseason_indices_defined)
    print('ProcTimeseason_month_indices_defined (#'+str(len(ProcTimeseason_month_indices_defined))+') =',ProcTimeseason_month_indices_defined)
    print('ProcTimeyears_defined (#'+str(len(ProcTimeyears_defined))+') =',ProcTimeyears_defined)
  
  if(ProcTimeseason != 'MON' and (ProcTimeybeg_season_process not in ProcTimeyears_season_valid or ProcTimeyend_season_process not in ProcTimeyears_season_valid)):
    raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  print('ProcTimemonth_indices=',ProcTimemonth_indices)
  
  print(' So now we could loop over years_defined, each vector of season_indices_defined can be used then be used to broadcast/average.')

###############################################################################

  #for ProcTimei,ProcTimeyear in enumerate(ProcTimeyears_defined):
  #  print('ProcTimei,ProcTimeyear,ProcTimeseason_indices_defined[ProcTimei]=',ProcTimei,ProcTimeyear,ProcTimeseason_indices_defined[ProcTimei])
  print('ProcTimeybeg_season_process,ProcTimeyend_season_process,ProcTimembeg_season_process,ProcTimemend_season_process=',ProcTimeybeg_season_process,ProcTimeyend_season_process,ProcTimembeg_season_process,ProcTimemend_season_process)
  #print('ProcTimeyears_defined.index(ProcTimeybeg_season_process=',ProcTimeyears_defined.index(ProcTimeybeg_season_process))

  for ProcTimei,ProcTimeyear in enumerate(range(ProcTimeybeg_season_process,ProcTimeyend_season_process+1)):
    #print(ProcTimeseason_indices_defined[ProcTimeyears_defined.index(ProcTimeyear)])
    ProcTimevalues=ProcTimeseason_indices_defined[ProcTimeyears_defined.index(ProcTimeyear)]
    print('ProcTimei,ProcTimeyear,values=',ProcTimei,ProcTimeyear,ProcTimevalues)
  
###############################################################################

#!  tbeg,tend=[],[]

#  time_stamp_beg=datetime.datetime(this_year,1,1) + datetime.timedelta(hours=0.0)
#  time_beg=netCDF4.date2num(time_stamp_beg,time_string,calendar)

  ProcTimetime_stamp_beg,ProcTimetime_stamp_end=[],[]
  
  if(ProcTimeseason_broadcast[ProcTimeseason]): #broadcast 
    for ProcTimei,ProcTimeyear in enumerate(range(ProcTimeybeg_season_process,ProcTimeyend_season_process+1)):
      #print('ProcTimeyear=',ProcTimeyear)
      ProcTimenpvalues=np.array(ProcTimeseason_indices_defined[ProcTimeyears_defined.index(ProcTimeyear)])-1
      ProcTimenpvalues2=np.array(ProcTimeseason_month_indices_defined[ProcTimeyears_defined.index(ProcTimeyear)])-1
      #print('ProcTimenpvalues=',ProcTimenpvalues)
      #print('ProcTimenpvalues2=',ProcTimenpvalues2)
      #print(ProcTimenum_stamps[ProcTimenpvalues])
      #print('ProcTimenpyears[ProcTimenpvalues]',ProcTimenpyears[ProcTimenpvalues2])
      #print('ProcTimenpmonths[ProcTimenpvalues]=',ProcTimenpmonths[ProcTimenpvalues2])
    
      #print('ProcTimenpyears=',ProcTimenpyears)
      #if(ProcTimei==1): raise SystemExit('STOP!')
    
      for ProcTimej,ProcTimenpyear in enumerate(ProcTimenpyears[ProcTimenpvalues2]):
        #print('ProcTimej,ProcTimenpyear,ProcTimenpmonths[ProcTimenpvalues2][ProcTimej]=',ProcTimej,ProcTimenpyear,ProcTimenpmonths[ProcTimenpvalues][ProcTimej])
        ProcTimetime_stamp_beg.append(datetime.datetime(ProcTimenpyear,ProcTimenpmonths[ProcTimenpvalues][ProcTimej],1) + datetime.timedelta(hours=0.0))
  
        #raise SystemExit('STOP!')
        
        ProcTimemmm=ProcTimenpmonths[ProcTimenpvalues][ProcTimej]+1
        if(ProcTimemmm>12):
          ProcTimemmm=1
          ProcTimeyyy=ProcTimenpyear+1
        else:
          ProcTimeyyy=ProcTimenpyear
          
        ProcTimetime_stamp_end.append(datetime.datetime(ProcTimeyyy,ProcTimemmm,1) + datetime.timedelta(hours=0.0))
  
    #raise SystemExit('STOP!')
  
  #  for ProcTimek,dummy in enumerate(ProcTimetime_stamp_beg):                       
  #    print('ProcTimek,ProcTimetime_stamp_beg[ProcTimek],ProcTimetime_stamp_end[ProcTimek]=',ProcTimek,ProcTimetime_stamp_beg[ProcTimek],ProcTimetime_stamp_end[ProcTimek])
                         
  else: #not broadcast=seasonal average
    for ProcTimei,ProcTimeyear in enumerate(range(ProcTimeybeg_season_process,ProcTimeyend_season_process+1)):
      ProcTimenpvalues=np.array(ProcTimeseason_indices_defined[ProcTimeyears_defined.index(ProcTimeyear)])-1
      ProcTimenpvalues2=np.array(ProcTimeseason_month_indices_defined[ProcTimeyears_defined.index(ProcTimeyear)])-1
      
      print('ProcTimenpvalues,ProcTimenpvalues2,ProcTimenpyears[ProcTimenpvalues],ProcTimenpmonths[ProcTimenpvalues]=',ProcTimenpvalues,ProcTimenpvalues2,ProcTimenpyears[ProcTimenpvalues2],ProcTimenpmonths[ProcTimenpvalues])
  
      ProcTimetime_stamp_beg.append(datetime.datetime(ProcTimenpyears[ProcTimenpvalues2[0]],ProcTimenpmonths[ProcTimenpvalues[0]],1) + datetime.timedelta(hours=0.0))
  
      ProcTimemmm=ProcTimenpmonths[ProcTimenpvalues[-1]]+1
      if(ProcTimemmm>12):
        ProcTimemmm=1
        ProcTimeyyy=ProcTimenpyears[ProcTimenpvalues2[-1]]+1
      else:
        ProcTimeyyy=ProcTimenpyears[ProcTimenpvalues2[-1]]
      
      ProcTimetime_stamp_end.append(datetime.datetime(ProcTimeyyy,ProcTimemmm,1) + datetime.timedelta(hours=0.0))
  
  #continue on
  ProcTimetime_beg=netCDF4.date2num(ProcTimetime_stamp_beg,ProcTimetime.units,ProcTimetime.calendar)
  ProcTimetime_end=netCDF4.date2num(ProcTimetime_stamp_end,ProcTimetime.units,ProcTimetime.calendar)
  
  #I could do an average of the year/month stamp rather than an aveage of beg/end, might be same.
  
  ProcTimetime_avg=(ProcTimetime_beg+ProcTimetime_end)/2.0
  
  ProcTimetime_bounds=np.column_stack((ProcTimetime_beg,ProcTimetime_end))
  
  ProcTimetime_stamp_avg=netCDF4.num2date(ProcTimetime_avg,ProcTimetime.units,ProcTimetime.calendar)
  if(not Diagnostic):
    for dummyi,dummy in enumerate(ProcTimetime_stamp_beg):
      print('i,ProcTimetime_stamp_beg,avg,end=',dummyi,ProcTimetime_stamp_beg[dummyi],ProcTimetime_stamp_avg[dummyi],ProcTimetime_stamp_end[dummyi])

###############################################################################

  cmor.set_table(tables[0])

  #print('aaa')
  time_axis_id=cmor.axis('time', units=ProcTimetime.units, coord_vals=ProcTimetime_avg, cell_bounds=ProcTimetime_bounds)

  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  #print('ProcTimetime_beg=',ProcTimetime_beg)
  #print('ProcTimetime_stamp_beg=',ProcTimetime_stamp_beg)
   #time_stamp_beg=datetime.datetime(ProcTimeyear,1,1) + datetime.timedelta(hours=0.0) 

  cmor.set_table(tables[1])
  
  if(realm=='ocean' and ( OutputVarStructure=='time_lat_lon' or OutputVarStructure=='time_depth_lat_lon' or OutputVarStructure=='depth_lat_lon')):
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
  
  elif(realm=='ocean' and (OutputVarStructure=='time_reduceddepth_lat_lon' or OutputVarStructure=='time_basin_depth_lat')):
    #dvar=='thetao100m' or dvar=='so100m' or dvar=='uo100m' or dvar=='vo100m'):
    cmor.set_table(tables[0])
  
    zt=xfh.variables['zt']
    zb=xfh.variables['zb']
  
    if 'newlevs' in locals():
      print(newlevs)
      levels=newlevs
      nlev=len(levels)
      zt=zt[levels]
      zb=zb[levels]
  
    nzb=len(zb[:])
    z0=np.zeros((nzb))
    z0[0]=0
    z0[1:nzb]=zb[0:nzb-1]
    zbounds=np.column_stack((z0,zb))
    z=zb-z0
  
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  elif(realm=='atmos' or realm=='ocean'):
  #elif(realm=='ocean'):
  
    if(ReGrid):
      lat_vals = outgrid.getLatitude() 
      lon_vals = outgrid.getLongitude()
    else:
      if(realm=='ocean' and (OutputVarStructure=='time' or OutputVarStructure=='time_oline' or OutputVarStructure=='time_lon') ):
      #dvar=='nino34' or dvar=='iod' or dvar=='pp' or dvar=='nflux' or dvar=='ep'):
        lat_vals=f.variables['yt_ocean']
        lon_vals=f.variables['xt_ocean']
      else:
        lat_vals=f.variables['lat'] #lat
        lon_vals=f.variables['lon'] #lon
  
    min_vals=np.append((1.5*lat_vals[0] - 0.5*lat_vals[1]), (lat_vals[0:-1] + lat_vals[1:])/2)
    max_vals=np.append((lat_vals[0:-1] + lat_vals[1:])/2, 1.5*lat_vals[-1] - 0.5*lat_vals[-2])
    lat_vals_bounds=np.column_stack((min_vals, max_vals))
  
    min_vals=np.append((1.5*lon_vals[0] - 0.5*lon_vals[1]), (lon_vals[0:-1] + lon_vals[1:])/2)
    max_vals=np.append((lon_vals[0:-1] + lon_vals[1:])/2, 1.5*lon_vals[-1] - 0.5*lon_vals[-2])
    lon_vals_bounds=np.column_stack((min_vals, max_vals))
  
  #if(realm=='ocean'):
  if 'newlevs' in locals():
    levels=newlevs
    nlev=len(levels)
    if(len(inputs)==2):
      levels2=levels
      nlev2=len(levels2)
  else:
    levels2=levels
    nlev2=len(levels2)
  
  if(realm=='atmos' and (OutputVarStructure=='time_lat_lon' or OutputVarStructure=='time_plev_lat_lon' or OutputVarStructure=='time_reducedplev_lat_lon') and (plev_type=='pfull' or plev_type=='phalf')):
  #if(realm=='atmos' and (OutputVarStructure=='time_lat_lon' or OutputVarStructure=='time_plev_lat_lon' or OutputVarStructure=='time_reducedplev_lat_lon') and (plev_type=='pfull' or plev_type=='phalf')):
  
    if 'newlevs' in locals():
      levels=newlevs
      nlev=len(levels)
      if(len(inputs)==2):
        levels2=levels
        nlev2=len(levels2)
    else:
      levels2=levels
      nlev2=len(levels2)
    
    #print(levels)
    #print(levels2)
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  if(realm=='atmos' and ( OutputVarStructure=='time_plev_lat_lon' or OutputVarStructure=='time_reducedplev_lat_lon') ):
    if(plev_type=='pfull'):
      zt=f.variables['pfull'][:]*100.0
    else:
      zt=f.variables['phalf'][:]*100.0
    min_vals=np.append((1.5*zt[0] - 0.5*zt[1]), (zt[0:-1] + zt[1:])/2)
    max_vals=np.append((zt[0:-1] + zt[1:])/2, (1.5*zt[-1] - 0.5*zt[-2]))
    zbounds =np.column_stack((min_vals, max_vals))
    zbounds=np.where(zbounds<0.0,0.0,zbounds)
  
    #print('zt=',zt[:],file=fh_printfile)
    #print('zt.shape=',zt.shape,file=fh_printfile)
    #print('zbounds=',zbounds[:],file=fh_printfile)
    #print('tables=',tables,file=fh_printfile)
    #print(levels)
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    
    cmor.set_table(tables[2]) #working zg
    cmor.set_table(tables[0])
  
    if 'plevN' in locals():
      if(aaa_newlevs_type=='int'):
        newlevs=zt[newlevs]
      #else: #float
      #  newlevs=levels
      #print(newlevs)
      #print('aaa')
      z_axis_id=cmor.axis(plevN,'Pa',coord_vals=newlevs[:])
      #levels=newlevs
    elif(plev_type=='pfull'):
      z_axis_id=cmor.axis('plev24','Pa',coord_vals=zt[:])
    elif(plev_type=='phalf'):
      z_axis_id=cmor.axis('plev25','Pa',coord_vals=zt[:])
    else:
      raise SystemExit('Check atm levels :'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
    nlev=len(levels)
  
    if(len(inputs)>=2):
      if(inputs_shape[1]==inputs_shape[0]):
        levels2=levels
        nlev2=len(levels2)
  
      if(len(inputs)>=3):
        if(inputs_shape[2]==inputs_shape[0]):
          levels3=levels
          nlev3=len(levels3)
        else:
          levels3=[0]
          nlev3=0
  
    #print(inputs)
    #print(inputs_shape)
    #print(levels)
    #print(levels2)
    #print(levels3)
  #  print(nlev)
  #  print(nlev2)
  #  print(plevN)
  #  #print(newlevs)
  #  raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  if(realm=='atmos' and (OutputVarStructure=='time' or OutputVarStructure=='time_lat_lon' or OutputVarStructure=='time_plev_lat_lon' or OutputVarStructure=='time_reducedplev_lat_lon' or OutputVarStructure=='time_lon') ):
  #  lat_axis=f.variables['lat']
  #  lon_axis=f.variables['lon']
  
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
  
    cmor.set_table(tables[0]) #working zg500
    #cmor.set_table(tables[2])
  
    lat_axis_id=cmor.axis(table_entry='latitude', units='degrees_north', coord_vals=lat_vals[:], cell_bounds=lat_vals_bounds)
  
    lon_axis_id=cmor.axis(table_entry='longitude', units='degrees_east', coord_vals=lon_vals[:], cell_bounds=lon_vals_bounds)
  
  if(realm=='ocean' and OutputVarStructure=='time_oline'):
  #dvar=='mfo'):
    lines=['barents_opening','bering_strait','canadian_archipelago','denmark_strait',\
                  'drake_passage','english_channel','pacific_equatorial_undercurrent',\
                  'faroe_scotland_channel','florida_bahamas_strait','fram_strait','iceland_faroe_channel',\
                  'indonesian_throughflow','mozambique_channel','taiwan_luzon_straits','windward_passage']
  
    nlines=len(lines)
    #cmor.set_table(tables[2])
    cmor.set_table(tables[0])
  
    oline_axis_id = cmor.axis(table_entry='oline', units='', length=len(lines), coord_vals=lines)
    print(oline_axis_id,file=fh_printfile)
  
  elif(realm=='ocean' and OutputVarStructure=='time_basin_depth_lat'):
  #elif(dvar=='msftyyz'):
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
  
    print('time_axis_id=', time_axis_id,file=fh_printfile)
    print('basin_axis_id=', basin_axis_id,file=fh_printfile)
    print('z_axis_id=', z_axis_id,file=fh_printfile)
    print('lat_axis_id=', lat_axis_id,file=fh_printfile)
  
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  elif(realm=='ocean' and (OutputVarStructure=='time_depth_lat_lon' or OutputVarStructure=='time_reduceddepth_lat_lon')):
  
    #if(dvar=='umo'):
    #  lat_vals=xfh.variables['y_T']
    #  lon_vals=xfh.variables['x_C']
    #elif(dvar=='vmo'):
    #  lat_vals=xfh.variables['y_C']
    #  lon_vals=xfh.variables['x_T']
    #else:
    #  lat_vals=xfh.variables['y_T']
    #  lon_vals=xfh.variables['x_T']
    lat_vals=xfh.variables[lat_lon_type[0]]
    lon_vals=xfh.variables[lat_lon_type[1]]
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
  
  elif(realm=='ocean' and OutputVarStructure=='time_lat_lon'):
  
  #  if(dvar=='umo'):
  #    lat_vals=xfh.variables['y_T']
  #    lon_vals=xfh.variables['x_C']
  #  elif(dvar=='vmo'):
  #    lat_vals=xfh.variables['y_C']
  #    lon_vals=xfh.variables['x_T']
  #  else:
  #    lat_vals=xfh.variables['y_T']
  #    lon_vals=xfh.variables['x_T']
    lat_vals=xfh.variables[lat_lon_type[0]]
    lon_vals=xfh.variables[lat_lon_type[1]]
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
  if(realm=='ocean' and OutputVarStructure=='time_oline'):
    axis_ids=np.array([time_axis_id, oline_axis_id])
    #print('axis_ids=',axis_ids,file=fh_printfile)
    #print(dvar,file=fh_printfile)
    #print(ounits)
    data_id.append(cmor.variable(dvar[0], ounits, axis_ids=axis_ids, missing_value=-1e20))
  
  elif(realm=='ocean' and OutputVarStructure=='time_lat_lon'):
    axis_ids=[i_axis_id,j_axis_id,time_axis_id]
    axis_ids=[time_axis_id]
    axis_ids=[0]
    axis_ids=[time_axis_id,j_axis_id,i_axis_id]
    axis_ids=np.array([time_axis_id,j_axis_id,i_axis_id])
    axis_ids=np.array([j_axis_id,i_axis_id])
    axis_ids=[0,-100]
    axis_ids=[grid_id]
    axis_ids=[time_axis_id,grid_id] #working
    data_id.append(cmor.variable(dvar[0], ounits, axis_ids=axis_ids, missing_value=-1e20))
  
  elif(table=='fx'):
    axis_ids=[1,-100]
    data_id.append(cmor.variable(dvar[0], ounits, axis_ids=axis_ids, missing_value=-1e20))
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  elif(realm=='ocean' and ( OutputVarStructure=='time_depth_lat_lon' or OutputVarStructure=='time_reduceddepth_lat_lon')):
    #axis_ids=[time_axis_id,grid_id]
    #axis_ids=[0,1,2,3]
    #axis_ids=[time_axis_id,z_axis_id,grid_id]
    #axis_ids=[0,-100]
    #axis_ids=[0,2,-100] #works but prob.
    axis_ids=[0,1,-100]
    data_id.append(cmor.variable(dvar[0], ounits, axis_ids=axis_ids, missing_value=-1e20))
  
  elif(realm=='atmos' and OutputVarStructure=='time_lat_lon'):
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
  
    data_id.append(cmor.variable(dvar[0], ounits, axis_ids=axis_ids, missing_value=-1e20,positive=positive))
  
  elif(realm=='atmos' and ( OutputVarStructure=='time_plev_lat_lon' or OutputVarStructure=='time_reducedplev_lat_lon')):
    #cmor.set_table(tables[2])
    #cmor.set_table(tables[1])
    #cmor.set_table(tables[0])
    #axis_ids=[time_axis_id,z_axis_id,lat_axis_id,lon_axis_id]
    axis_ids=np.array([time_axis_id,z_axis_id,lat_axis_id,lon_axis_id])
    print('axis_ids=',axis_ids,file=fh_printfile)
    print('dvar=',dvar,' ounits=',ounits,file=fh_printfile)
  
    #print(ovars)
    #print(outputs_string)
  
    for o in range(0,len(ovars)):
      data_id.append(cmor.variable(ovars[o], ounits[o], axis_ids=axis_ids, missing_value=-1e20))
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  elif(realm=='atmos' and ( OutputVarStructure=='time_lon')):
    axis_ids=np.array([time_axis_id,lon_axis_id])
    for o in range(0,len(ovars)):
      data_id.append(cmor.variable(ovars[o], ounits[o], axis_ids=axis_ids, missing_value=-1e20))
  
  elif((realm=='ocean' or realm=='atmos') and OutputVarStructure=='time'):
    #dvar=='nino34' or dvar=='temptotal' or dvar=='salttotal' or dvar=='iod' or dvar=='pp' or dvar=='nflux' or dvar=='ep'):
    #axis_ids=[time_axis_id,grid_id]
    #axis_ids=[grid_id]
    axis_ids=[]
    axis_ids=[time_axis_id]
    axis_ids=np.array([time_axis_id])
    axis_ids=[0] #working
    #data_id=cmor.variable(dvar, ounits,  missing_value=-1e20)
    data_id.append(cmor.variable(dvar[0], ounits, axis_ids=axis_ids, missing_value=-1e20))
  
  elif(realm=='ocean' and OutputVarStructure=='time_basin_depth_lat'):
    axis_ids=np.array([time_axis_id, basin_axis_id, z_axis_id, lat_axis_id])
    data_id.append(cmor.variable(dvar[0], ounits, axis_ids=axis_ids, missing_value=-1e20))
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  #elif(dvar=='volcello' or dvar=='thkcello'):
  #  axis_ids=[0,1,-100]
  #  axis_ids=[0,-100]
  #  data_id.append(cmor.variable(dvar, ounits, axis_ids=axis_ids, missing_value=-1e20))
  #elif(dvar=='areacello' or dvar=='sftof' or dvar=='deptho'):
  #  axis_ids=[0,1,-100]
  #  axis_ids=[0,-100]
  #  axis_ids=[-100]
  #  data_id.append(cmor.variable(dvar, ounits, axis_ids=axis_ids, missing_value=-1e20))
  #elif(dvar=='msftyyz'):
  #  axis_ids=[0,-100]
  #  axis_ids=np.array([basin_axis_id, z_axis_id, lat_axis_id])
  #  axis_ids=np.array([time_axis_id, basin_axis_id, z_axis_id, lat_axis_id])
  #  data_id.append(cmor.variable(dvar, ounits, axis_ids=axis_ids, missing_value=-1e20))
  #elif(dvar=='mfo'):
  #  axis_ids=np.array([time_axis_id, oline_axis_id])
  #  print('axis_ids=',axis_ids,file=fh_printfile)
  #  data_id.append(cmor.variable(dvar, ounits, axis_ids=axis_ids, missing_value=-1e20))
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  #elif(dvar=='nhbi'):
  #  axis_ids=np.array([time_axis_id, lon_axis_id])
  #  print('axis_ids=',axis_ids,file=fh_printfile)
  #  data_id.append(cmor.variable(dvar, ounits, axis_ids=axis_ids, missing_value=-1e20))
  #  data_id.append(cmor.variable('GHGS','1.0',axis_ids=axis_ids, missing_value=-1e20))
  #  data_id.append(cmor.variable('GHGN','1.0',axis_ids=axis_ids, missing_value=-1e20))

  print(ProcTimeyears_defined)
  print(ProcTimeyears_defined[0])
  print(type(ProcTimeyears_defined[0]))

  print(ProcTimeyears_defined[-1])
  print(type(ProcTimeyears_defined[-1]))

  print(ProcTimeseason_month_indices_defined)
  print(ProcTimeseason_month_indices_defined[0][0])
  print(ProcTimeseason_month_indices_defined[-1][-1])

  #print(ProcTimenparray_months_defined[ProcTimeseason_month_indices_defined[0][0]])
  #print(ProcTimenparray_months_defined[ProcTimeseason_month_indices_defined[-1][-1]])

  print(ProcTimenpmonths[ProcTimeseason_month_indices_defined[0][0]-1])
  print(ProcTimenpmonths[ProcTimeseason_month_indices_defined[-1][-1]-1])

#ProcTimenpmonths

#  exit()

  odir=[]
  ofil=[]
  ofil_modified=[]

  odir.append('CMIP6/CMIP'+'/'+institution_id+'/'+source_id+'/'+experiment_id+'/'+ripf+'/'+table+'/'+ovars[0]+'/'+grid_label+'/'+version)

  ybeg_ofil=str('{0:04d}'.format(ProcTimeyears_defined[0]))
  yend_ofil=str('{0:04d}'.format(ProcTimeyears_defined[-1]))

  print('yend_ofil=',yend_ofil)

  if(season=='MON'):
    mbeg_ofil=str('{0:02d}'.format(ProcTimenpmonths[ProcTimeseason_month_indices_defined[0][0]-1]))
    mend_ofil=str('{0:02d}'.format(ProcTimenpmonths[ProcTimeseason_month_indices_defined[-1][-1]-1]))

    ofil.append(ovars[0]+'_'+table+'_'+experiment_id+'_'+source_id+'_'+ripf+'_'+grid_label+'_'+ybeg_ofil+mbeg_ofil+'-'+yend_ofil+mend_ofil+'.nc')
    ofil_modified.append(ovars[0]+'_'+table+'_'+experiment_id+'_'+source_id+'_'+ripf+'_'+grid_label+'_'+ybeg_ofil+mbeg_ofil+'-'+yend_ofil+mend_ofil+'.nc')

    #print(ofil_modified)
    #exit()

  else:
    ofil.append(ovars[0]+'_'+table+'_'+experiment_id+'_'+source_id+'_'+ripf+'_'+grid_label+'_'+ybeg_ofil+'-'+yend_ofil+'.nc')
    ofil_modified.append(ovars[0]+'_'+table+'_'+experiment_id+'_'+source_id+'_'+ripf+'_'+grid_label+'_'+ybeg_ofil+'-'+yend_ofil+'_'+season+'.nc')

  #print(odir_ofil+'/'+ofil_ofil)
  
  #ofil,ofil_modified=create_ofils(season,table,ovars,experiment_id,source_id,ripf,grid_label,ybeg,yend,mbeg,mend,0,0) #don't need to worry about dbeg,dend, always monthly data input.
  
  #print('odir=',odir,file=fh_printfile)
  #print('ofil=',ofil,file=fh_printfile)
  #print('ofil_modified=',ofil_modified,file=fh_printfile)
  #print('ovars=',ovars,file=fh_printfile)
  
  print('len(ovars)=',len(ovars),file=fh_printfile)
  for o in range(0,len(ovars)):
    print('Output CMIP6 file:',odir[o]+'/'+ofil_modified[o],file=fh_printfile)
  
  for o in range(0,len(ovars)):
    if(os.path.exists(odir[o]+'/'+ofil_modified[o]) and NoClobber):
      #raise SystemExit('No Clobber set and ',odir[o]+'/'+ofil_modified[o],' exist.')
      print('No Clobber set and ',odir[o]+'/'+ofil_modified[o],' exist.')
      return(0)
  
  for o in range(0,len(ovars)):
    if(os.path.exists(odir[o]+'/'+ofil[o]) and NoClobber):
      #raise SystemExit('No Clobber set and ',odir[o]+'/'+ofil_modified[o],' exist.')
      print('No Clobber set and ',odir[o]+'/'+ofil[o],' exist.')
      return(0)

  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  #  if(dvar=='volcello'):
  #    area=np.tile(np.expand_dims(xfh.variables['area_T'],0), (len(zt),1,1))
  #    thickness=np.expand_dims(np.expand_dims(z[:],1),2)
  #    thickness=np.tile( thickness ,(1,nlat,nlon))
  #    data=np.ma.array(input_fhs[0].variables[inputs[0]][0,:,:,:]/input_fhs[0].variables[inputs[0]][0,:,:,:]) * thickness*area
  
  #  if(dvar=='thkcello'):
  #    thickness=np.expand_dims(np.expand_dims(z[:],1),2)
  #    thickness=np.tile( thickness ,(1,nlat,nlon))
  #    data=np.ma.array(input_fhs[0].variables[inputs[0]][0,:,:,:]/input_fhs[0].variables[inputs[0]][0,:,:,:]) * thickness
  #
  #  elif(dvar=='areacello'):
  #    data=np.ma.array(input_fhs[0].variables[inputs[0]][0,0,:,:]/input_fhs[0].variables[inputs[0]][0,0,:,:]) * xfh.variables['area_T']
  #
  #  elif(dvar=='sftof'):
  #    data=np.float32(xfh.variables['wet'][:,:]*100.0)
  #
  #  elif(dvar=='deptho'):
  #    depths=np.expand_dims(np.expand_dims(z[:],1),2)
  #    depths=np.tile( depths,(1,nlat,nlon))
  #    data=np.ma.array(input_fhs[0].variables[inputs[0]][0,:,:,:]/input_fhs[0].variables[inputs[0]][0,:,:,:]) * depths
  #    data=np.sum(data,axis=0)
  #

  for ProcTimei,ProcTimeyear in enumerate(range(ProcTimeybeg_season_process,ProcTimeyend_season_process+1)):
    icnt=ProcTimei

    ProcTimevalues=ProcTimeseason_indices_defined[ProcTimeyears_defined.index(ProcTimeyear)]
    ProcTimenpvalues=np.array(ProcTimeseason_indices_defined[ProcTimeyears_defined.index(ProcTimeyear)])-1
    ProcTimenvalues=len(ProcTimevalues)
    ProcTimennpvalues=len(ProcTimenpvalues)

    ProcTimevalues2=ProcTimeseason_month_indices_defined[ProcTimeyears_defined.index(ProcTimeyear)]
    ProcTimenpvalues2=np.array(ProcTimeseason_month_indices_defined[ProcTimeyears_defined.index(ProcTimeyear)])-1
    ProcTimenvalues2=len(ProcTimevalues2)
    ProcTimennpvalues2=len(ProcTimenpvalues2)

    #print(ProcTimevalues)
    #print(ProcTimevalues2)

    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

#!  icnt=0
#!  ibeg=0
#!  ind_beg=0
#!  for n in range(0,ttt): #this code is copy from one above (need to add in icnt,ind_beg)
#!  
#!    if(season=='MON'):
#!      ind_end=ind_beg #always 1 month at a time for MON
#!    else:
#!      ind_end=ind_beg+times_in_season-1
#!  
#!    month_index_beg=month_index_ntims[ind_beg]+1
#!    year_index_beg=year_index_ntims[ind_beg]
#!  
#!    if(season=='MON'):
#!      if(n==0):
#!        month_index_end=month_index_beg+1
#!        year_index_end=year_index_beg
#!      else:
#!        month_index_end=month_index_beg+1
#!        year_index_end=year_index_end
#!    elif(season=='ANN'):
#!      if(n==ttt-1): #last one special
#!        month_index_end=month_index_ntims[ind_end-1]+1+1+1
#!        year_index_end=year_index_ntims[ind_end-1]
#!      else:
#!        month_index_end=month_index_ntims[ind_end]+1+1
#!        year_index_end=year_index_ntims[ind_end]
#!    else:
#!      if(n==ttt-1): #last one special
#!        month_index_end=month_index_ntims[ind_end-1]+1+1
#!        year_index_end=year_index_ntims[ind_end-1]
#!      else:
#!        month_index_end=month_index_ntims[ind_end]+1
#!        year_index_end=year_index_ntims[ind_end]
#!  
#!    if(month_index_end>12):
#!       month_index_end=month_index_end-nmy
#!       year_index_end+=1
#!  
#!    print('n=',n,' year_index_beg=',year_index_beg,' month_index_beg=',month_index_beg,' year_index_end=',year_index_end,' month_index_end=',month_index_end,' ind_beg,end=',ind_beg,ind_end,file=fh_printfile)
# 

    if(len(inputs)>=2):
      #print('levels=',levels,file=fh_printfile)
      #print('nlev=',nlev,file=fh_printfile)
      #if(realm=='atmos' and (OutputVarStructure=='time_plev_lat_lon' or OutputVarStructure=='time_reducedplev_lat_lon')):
      #  #nlev=0
      #  pass
      #elif(dvar=='rws500'):
      #  nlev=1
      #  levels=9
  
      #levels=[9]
      #lev2=len(levels)
  
      #print(levels)
      #print(nlev)
      #print(type(var_size))
      #print(var_size)
      #var_size[1]=5
      #print(var_size)
  
      data1=data_wavg(inputs[0],input_fhs,locate_file_index_Ntimes_b1_nominus1s_flat,ind_beg,ind_end,month_in_file_total_months_beg_to_end,levels,nlev,MonthlyWeights,month_index_ntims,fh_printfile,var_size)
  
      #nlev=0
      #levels2=[9]
      #nlev2=len(levels)
  
      data2=data_wavg(inputs[1],input_fhs,locate_file_index_Ntimes_b1_nominus1s_flat,ind_beg,ind_end,month_in_file_total_months_beg_to_end,levels2,nlev2,MonthlyWeights,month_index_ntims,fh_printfile,var_size2)
  
      #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
      if(len(inputs)>=3):
        data3=data_wavg(inputs[2],input_fhs,locate_file_index_Ntimes_b1_nominus1s_flat,ind_beg,ind_end,month_in_file_total_months_beg_to_end,levels3,nlev3,MonthlyWeights,month_index_ntims,fh_printfile,var_size3)
  
      #print('data1.shape=',data1.shape,file=fh_printfile)
      #print('data2.shape=',data2.shape,file=fh_printfile)
      #if(len(inputs)>=3):
        #print('data3.shape=',data3.shape,file=fh_printfile)
  
    else:
      #levels=[0]
      #nlev=1
      #data=np.zeros((ProcTimenvalues,300,360),dtype='f')
      #print(ProcTimennpvalues)
      #data=ProcTimeifhN.variables[inputs[0]][ProcTimenpvalues,]

      data=data_wavg_ProcTime(inputs[0],ProcTimeifhN,ProcTimenpvalues,ProcTimenpvalues2,ProcTimeseason_broadcast[ProcTimeseason])

      #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
      #print('data.shape=',data.shape)
      #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

#!      data=data_wavg(inputs[0],input_fhs,locate_file_index_Ntimes_b1_nominus1s_flat,ind_beg,ind_end,month_in_file_total_months_beg_to_end,levels,nlev,MonthlyWeights,month_index_ntims,fh_printfile,var_size)
  
    print('levels=',levels,file=fh_printfile)
    print('nlev=',nlev,file=fh_printfile)
  
    #print('data.shape=',data.shape)
  
    if(output_type=='diagnostic'):
  
      if(define_basin_mask and icnt==0): #only need to define the masks once...
        atlantic_arctic_mask,indoPac_mask,global_mask=make_mask3D(data1+data2,nbasins,nzb,nlats)
  
      #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
      #print('xxx dvar=',dvar)
      #print('vertical_interpolation_method=',vertical_interpolation_method)
      #print('newlevs=',newlevs)
  
     #print('aaa')
  
      diagnostic_args=(eval(diagnostic_args_string))
      function_name='diag_'+diagnostic_function_name
      if(len(inputs)==1):
        data=eval(function_name)(data,*diagnostic_args)
        print('len(data)=',len(data))
        #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
      elif(len(inputs)==2):
        if('vertical_interpolation_method' in locals() and vertical_interpolation_method!=None):
          data=atmos_vertical_interpolate(data1,zt,newlevs,data2,vertical_interpolation_method)
          data=eval(function_name)(data,*diagnostic_args)
        else:
          data=eval(function_name)(data1,data2,*diagnostic_args)
      elif(len(inputs)==3):
        if('vertical_interpolation_method' in locals() and vertical_interpolation_method!=None):
          data1=atmos_vertical_interpolate(data1,zt,newlevs,data3,vertical_interpolation_method)
          data2=atmos_vertical_interpolate(data2,zt,newlevs,data3,vertical_interpolation_method)
        data=eval(function_name)(data1,data2,*diagnostic_args)
  
      if(table=='fx'): #special case, no need to loop over all input times.
        file_name=[]
        for o in range(0,len(ovars)):
          print('o=',o,file=fh_printfile)
          print('file_name=',file_name,file=fh_printfile)
          cmor.write(var_id=data_id[o], data=data[:], ntimes_passed=0)
          file_name.append(cmor.close(var_id=data_id[o], file_name=True))
          finish(file_name[o],odir[o],ofil[o],ofil_modified[o],season,fh_printfile)
        raise SystemExit('Completed time-invaniant output, can exit: '+__file__+' line number: '+str(inspect.stack()[0][2]))
  
      #ovars=outputs_string
      #print(len(data))
  #    if(len(inputs)==3):
  #      print('data1.shape=',data1.shape,file=fh_printfile)
  #      print('data2.shape=',data2.shape,file=fh_printfile)
        #print('data=',data,file=fh_printfile)
        #print(len(data))
        #print(outputs_string)
        #j=('rws','div','eta','uchi','vchi')
        #print(j)
        #eval(j)=data
        #rws=data
        #print(rws.shape)
        #print(dvar)
        #print(ovars)
        #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  #    else:
        #print(data.shape)
        #print(data[:])
  #  if(dvar=='acc_drake'):
  #    data=diag_acc_drake(data,area_t,lat,lon)
  #  elif(dvar=='acc_africa'):
  #    data=diag_acc_africa(data,area_t,lat,lon)
  #  elif(dvar=='mozmbq'):
  #    data=diag_mozmbq(data,area_t,lat,lon)
  #  elif(dvar=='aabw'):
  #    data=diag_aabw(data,area_t,lat,lon)
  #  elif(dvar=='nadw'):
  #    data=diag_nadw(data,area_t,lat,lon)
  #  elif(dvar=='pp'):
  #    data=diag_pp(data,depth_edges,area_t,lat_vals,lon_vals)
  #  elif(dvar=='nflux'):
  #    data=diag_nflux(data,depth_edges,area_t,lat_vals,lon_vals)
  #  elif(dvar=='ep'):
  #    data=diag_ep(data,depth_edges,area_t,lat_vals,lon_vals)
  #  elif(dvar=='ssh'):
  #    data=diag_ssh(data1,data2,depth_edges,area_t,lat,lon)
  #  elif(dvar=='moc'):
  #    data=diag_moc(data1,data2,depth_edges,area_t,lat,lon)
  #  elif(dvar=='moc_atlantic'):
  #    data=diag_moc_atlantic(data1,data2,depth_edges,area_t,lat,lon)
  #  elif(dvar=='moc_pacific'):
  #    data=diag_moc_pacific(data1,data2,depth_edges,area_t,lat,lon)
  #  elif(dvar=='moc_indian'):
  #    data=diag_moc_indian(data1,data2,depth_edges,area_t,lat,lon)
  #  elif(dvar=='shice_cover'):
  #    data=diag_shice_cover(data,area_t,lat,lon)
  #  elif(dvar=='nhice_cover'):
  #    data=diag_nhice_cover(data,area_t,lat,lon)
  ##  elif(dvar=='nino34'):
  ##    data=diag_nino34(data,area_t,lat_vals,lon_vals,fh_printfile)
  #  elif(dvar=='iod'):
  #    data=diag_iod(data,area_t,lat_vals,lon_vals)
  #  elif(dvar=='nhbi'):
  #    data,var0,var1=diag_nhblocking_index(data,lat_vals,lon_vals)
  #  elif(dvar=='rws'):
  #    data=diag_rws(data1,data2,lat_vals[:],lon_vals[:])
  #  elif(realm=='ocean' and (OutputVarStructure=='time_depth_lat_lon' or OutputVarStructure=='time_lat_lon' or OutputVarStructure=='time_reduceddepth_lat_lon')):
  #    pass
  #  elif(dvar=='zg500' or dvar=='psl' or dvar=='ps' or dvar=='tauu' or dvar=='tauv' or dvar=='pr'):
  #    pass
  #  elif(dvar=='cl'):
  #    data=np.where(data<0.,0.,data*100.0)
  #  elif(dvar=='msftyyz'):
  #    if(icnt==0):
  #      atlantic_arctic_mask,indoPac_mask,global_mask=make_mask3D(data1+data2,nbasins,nzb,nlats)
  #    data=diag_msftyyz(data1+data2,atlantic_arctic_mask,indoPac_mask,global_mask,nbasins,nzb,nlats)
  #  elif(dvar=='mfo'):
  #     data=diag_mfo(data1,data2,nlines)
  #  elif(dvar=='rws500'):
  #     print('data1.shape=',data1.shape,file=fh_printfile)
  #     print('data2.shape=',data1.shape,file=fh_printfile)
  #     #data=diag_rws500(data1[9,:,:],data2[9,:,:],lat_vals[:],lon_vals[:])
  #     data=diag_rws500(data1,data2,lat_vals[:],lon_vals[:],fh_printfile)
  #  elif(dvar=='isothetao16c'):
  #    data=diag_isothetaoNc(data,zt[:],16.0)
  
  #  elif(dvar=='isothetao20c'):
  #    data=diag_isothetaoNc(data,zt[:],20.0)
  #    print(data.shape)
  #  elif(dvar=='isothetao22c'):
  #    data=diag_isothetaoNc(data,zt[:],22.0)
  #  elif(realm=='atmos' and (OutputVarStructure=='XXtime_plev_lat_lon' or OutputVarStructure=='time_reducedplev_lat_lon') and 'vertical_interpolation_method' in locals()):
  #   data=atmos_vertical_interpolate(data1,zt,newlevs,data2,vertical_interpolation_method)
     #print('data.shape=',data.shape)
     #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  #  if(season=='MON'):
  #    ntimes_passed=np.shape(data)[0]
  #  else:
#!    ntimes_passed=1

    if(ProcTimeseason_broadcast[ProcTimeseason]):
      ntimes_passed=ProcTimenvalues
    else:
      ntimes_passed=1
  
    if(OutputVarStructure=='time'):
      newdata=np.zeros((1,1),dtype='f')
      newdata[0,0]=data
      data=newdata
      for o in range(0,len(ovars)):
        cmor.write(var_id=data_id[o], data=data[:], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])
  
    elif(realm=='ocean' and (OutputVarStructure=='time_depth_lat_lon' or OutputVarStructure=='time_lat_lon' or OutputVarStructure=='time_reduceddepth_lat_lon' or OutputVarStructure=='time_oline' or OutputVarStructure=='time_basin_depth_lat')):
      #print('writing... levels=',levels,file=fh_printfile)
      #print('data.shape=',data.shape,file=fh_printfile)
      for o in range(0,len(ovars)):
        #cmor.write(var_id=data_id[o], data=data[:,:,:], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])
        if('outputs_string' in locals() and len(outputs_string)!=1):
          cmor.write(var_id=data_id[o], data=data[0], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]]) #tuple, multiple outputs.
        else:
          #print(ProcTimetime_bounds)
          #print(ProcTimetime_bounds.shape)
          #cmor.write(var_id=data_id[o], data=data, ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])
          #print('data.shape=',data.shape)
          #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

          if(ProcTimeseason_broadcast[ProcTimeseason]):
            cmor.write(var_id=data_id[o], data=data, ntimes_passed=ntimes_passed, time_bnds=ProcTimetime_bounds[ProcTimennpvalues])
          else:
            cmor.write(var_id=data_id[o], data=data, ntimes_passed=ntimes_passed, time_bnds=ProcTimetime_bounds[icnt])

          #file_name=[]
          #print('ovars=',ovars)
          #for o in range(0,len(ovars)):
          #  print('o=',o,file=fh_printfile)
          #  file_name.append(cmor.close(var_id=data_id[o], file_name=True))
          #  print('file_name=',file_name[o],file=fh_printfile)
        #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  #  elif(realm=='ocean' and (OutputVarStructure=='time_depth_lat_lon' or OutputVarStructure=='time_lat_lon')):
  #    for o in range(0,len(ovars)):
  #      cmor.write(var_id=data_id[o], data=data[:], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])
  
    elif(realm=='atmos' and (OutputVarStructure=='time_plev_lat_lon' or OutputVarStructure=='time_lat_lon' or OutputVarStructure=='time_reducedplev_lat_lon' or OutputVarStructure=='time_lon') ):
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
      #print('data[1].shape=',data[1].shape,file=fh_printfile)
      for o in range(0,len(ovars)):
        #cmor.write(var_id=data_id[o], data=data[:], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])
        #print('ntimes_passed=',ntimes_passed)
        if('outputs_string' in locals() and len(outputs_string)!=1):
          print('data_id=',data_id)
          cmor.write(var_id=data_id[o], data=data[0], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]]) #tuple, multiple outputs. Should this be data[o]
        else:
          cmor.write(var_id=data_id[o], data=data[:], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])
  
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  #  elif(dvar=='nhbi'):
  #    for o in range(0,len(ovars)):
  #      cmor.write(var_id=data_id[o], data=data[:], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])
  #  elif(dvar=='nino34' or dvar=='iod' or dvar=='pp' or dvar=='nflux' or dvar=='ep'):
  #    newdata=np.zeros((1,1),dtype='f')
  #    newdata[0,0]=data
  #    data=newdata
  #    for o in range(0,len(ovars)):
  #      cmor.write(var_id=data_id[o], data=data[:], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])
#!    icnt+=1
#!    ibeg=iend+1
#!    ind_beg=ind_end+1
  
  #print('ovars=',ovars,file=fh_printfile)
  #print('len(ovars)=',len(ovars),file=fh_printfile)
  
  file_name=[]
  print('ovars=',ovars)
  for o in range(0,len(ovars)):
    print('o=',o,file=fh_printfile)
    file_name.append(cmor.close(var_id=data_id[o], file_name=True))
    print('file_name=',file_name[o],file=fh_printfile)
  
  for o in range(0,len(ovars)):
    finish(file_name[o],odir[o],ofil[o],ofil_modified[o],season,ProcTimeseason_broadcast[ProcTimeseason],fh_printfile)
  
  #raise SystemExit('Finished O.K.')
  print('Finished O.K.')
  return(0)
  
  #end
