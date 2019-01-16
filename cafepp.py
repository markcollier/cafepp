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
from decadal_diag import MustHaveAllLevs,diag_acc_drake,diag_acc_africa,diag_mozmbq,diag_aabw,diag_nadw,diag_pp,diag_nflux,diag_ep,diag_ssh,diag_moc,diag_moc_atlantic,diag_moc_pacific,diag_moc_indian,diag_shice_cover,diag_nhice_cover,diag_nino34,xtra_nino34,init_data,sum_data,avg_data,filemonth_index,data_wavg,time_avg,diag_nhblocking_index,diag_rws5,finish,diag_msftyz,make_mask3D,diag_mfo,transPort,diag_rws500,create_odirs,create_ofils,diag_iod,diag_iod,xtra_iod,atmos_vertical_interpolate,diag_isothetaoNc,calc_iso_surface,calc_isoN,grab_var_meta,diag_psl,diag_hfls,diag_heat_content,diag_salt_content,diag_north_heat_trans,diag_north_salt_trans,ocean_vertical_interpolate,diag_thetao0to80m,diag_varNl,uncomment_json,process_json,modify_json,get_daily_indices_for_monthlyave,get_timestamp_number,data_wavg_ProcTime

from decadal_diag import diag_maxdTbydz,diag_depmaxdTbydz,diag_dTbydz,shade_2d_simple,shade_2d_latlon,diag_zmld_boyer,zmld_boyer,sigmatheta,diag_zmld_so,zmld_so,diag_spice,spice,diag_bigthetao,diag_soabs,diag_spiciness,diag_potrho,diag_siconc

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

from ProcTime import ProcTime

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

  ybeg=yend=None
  
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  if 'json_input_instructions' in locals():
    #os.system('awk -f ~mac599/decadal/uncomment_json.awk JsonTemplates/'+json_input_instructions+' > '+json_input_instructions)
    uncomment_json('JsonTemplates/'+json_input_instructions,json_input_instructions,True)
    print('Running cafepp from JSON instructions: '+json_input_instructions)
    json_input_instructions_fh=open(json_input_instructions).read()
    json_input_instructions_data=json.loads(json_input_instructions_fh)
    #print('json_input_instructions_data=',json_input_instructions_data)
  else:
    print('Running cafepp from command line input:')
  
  if 'json_input_instructions' in locals():
    #print("Summary of JSON instructions: ",json.dumps(json_input_instructions_data,indent=4,sort_keys=True))
  
    #print(type(json_input_instructions_data))
  
    top_level_keys=json_input_instructions_data.keys()
  
    #print('Top level JSON instructions keys=',top_level_keys)
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
          elif(l=='num_months_truncate'): num_months_truncate=int(list_new[l])
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
          elif(l=='dummy'): pass
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
          elif(l=='dummy'): pass
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
          elif(l=='dummy'): pass
          else: raise SystemExit('Unknown monthly_specific,',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
          #else: raise SystemExit('Unknown defaults,',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  if 'printfile' in locals():
    fh_printfile=open(printfile,"w")
  else:
    fh_printfile=sys.stdout
  print('fh_printfile=',fh_printfile)

  if 'season' not in locals():
    season='MON' #default

  if(ProcessFileList and ProcessFileTxtTF):
    raise SystemExit('Cannot have both ProcessFileList and ProcessFileTxtTF True:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  #cafepp_experiments_meta='cafepp_experiments.json'
  #os.system('awk -f ~mac599/decadal/uncomment_json.awk JsonTemplates/'+cafepp_experiments_meta+' > '+cafepp_experiments_meta)
  uncomment_json('JsonTemplates/'+cafepp_experiments_meta,cafepp_experiments_meta,True)
  cafepp_experiments_fh=open(cafepp_experiments_meta).read()
  print('cafepp_experiments_fh=',cafepp_experiments_fh,file=fh_printfile)
  cafepp_experiments_data=json.loads(cafepp_experiments_fh)
  #print('cafepp_experiments_data=',cafepp_experiments_data,file=fh_printfile)
  
  #print("Summary of JSON experiments input: ",json.dumps(cafepp_experiments_data,indent=4,sort_keys=True),file=fh_printfile)
  
  top_level_keys=cafepp_experiments_data.keys()
  #print('Top level JSON experiments keys=',top_level_keys,file=fh_printfile)
  
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

        elif(l=='storage_machine_no4'): storage_machine_no4=str(list_new[l])
        elif(l=='top_directory_no4'):
          top_directory_no4=str(list_new[l])
        elif(l=='active_disk_no4'): active_disk_no4=str(list_new[l])
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
        elif(l=='calendar'): calendar=str(list_new[l])
        elif(l=='dummy'): pass
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
  
  if 'storage_machine_no4' in locals() and active_disk_no4=='yes':
    storage_machine_no4_split=storage_machine_no4.split('.')
    if re.match(storage_machine_no4_split[0],hostname):
      idir=top_directory_no4
  
  print('hostname=',hostname)
  print('storage_machine_no3=',storage_machine_no3)
  #idir=top_directory_no2 #this is hardwired until I sort out how to manage this on raijin's quque...
  
  if not 'idir' in locals():
    raise SystemExit('Could not determine input directory, idir ',' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  if not os.path.exists(idir):
    raise SystemExit('Input directory specified '+idir+' does not exist, file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
   
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
  #print('json_input_var_data=',json_input_var_data,file=fh_printfile)
  
  #print("Summary of JSON variable input: ",json.dumps(json_input_var_data,indent=4,sort_keys=True),file=fh_printfile)
  
  top_level_keys=json_input_var_data.keys()
  #print('Top level JSON variable keys=',top_level_keys,file=fh_printfile)
  
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
        elif(l=='dummy'): pass
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
        elif(l=='ounits'): ounits=[str(list_new[l])]
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
        elif(l=='dummy'): pass
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
  
  if('calendar' not in locals()):
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

  elif os.path.exists('/g/data/p66/mac599/CMIP5/ancillary_files/grid_spec.auscom.20110618.nc'):
    xfh=netCDF4.Dataset('/g/data/p66/mac599/CMIP5/ancillary_files/grid_spec.auscom.20110618.nc')
  else:
    xfh=netCDF4.Dataset('./grid_spec.auscom.20110618.nc')
  if(area_t):
    #afh=netCDF4.Dataset('/short/v19/mtc599/ao_am2/sep16f/OUTPUT/ocean_month_0001_01.nc')
    #area_t=afh.variables['area_t']
     area_t=xfh.variables['area_T'] #check ok
  if(area_u):
    #afh=netCDF4.Dataset('/short/v19/mtc599/ao_am2/sep16f/OUTPUT/ocean_month_0001_01.nc')
    #area_u=afh.variables['area_u']
     area_u=xfh.variables['area_C'] #check ok
  
###############################################################################

  #ProcTimeN=ProcTime(season=season,experiment=cafe_experiment,idir=idir,realm=realm,frequency=frequency,num_months_truncate=num_months_truncate) #create instance.

  ProcTimeN=None

  ProcTimeN=ProcTime(season=season,experiment=cafe_experiment,realm=realm,frequency=frequency,ybeg_season_process=ybeg,yend_season_process=yend,mbeg_season_process=mbeg,mend_season_process=mend,input_directory=idir,num_months_truncate=num_months_truncate) #create instance.

  ProcTimeN.step1()

  ProcTimeN.step2()

  ProcTimeN.step3()

  ProcTimeN.step4()

  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  cmor.set_table(tables[0])

  print('ProcTimeN.time_units=',ProcTimeN.time_units)

  time_axis_id=cmor.axis('time', units=ProcTimeN.time_units, coord_vals=ProcTimeN.time_avg, cell_bounds=ProcTimeN.time_bounds)

  try:
    ivar=ProcTimeN.ifh0.variables[inputs[0]]
    var_dims=ProcTimeN.ifh0.variables[inputs[0]].dimensions
    var_size=ProcTimeN.ifh0.variables[inputs[0]].shape
  except KeyError:
    ivar=ProcTimeN.ifh0.variables[inputs_alternative[0]]
    var_dims=ProcTimeN.ifh0.variables[inputs_alternative[0]].dimensions
    var_size=ProcTimeN.ifh0.variables[inputs_alternative[0]].shape

    if(len(inputs)>=2):
      ivar2=ProcTimeN.ifh0.variables[inputs[1]]
      var_dims2=ProcTimeN.ifh0.variables[inputs[1]].dimensions
      var_size2=list(ProcTimeN.ifh0.variables[inputs[1]].shape)

      if(len(inputs)>=3):
        ivar3=ProcTimeN.ifh0.variables[inputs[2]]
        var_dims3=ProcTimeN.ifh0.variables[inputs[2]].dimensions
        var_size3=list(ProcTimeN.ifh0.variables[inputs[2]].shape)

  print('var_size=',var_size)
  print('var_dims=',var_dims)

  if(len(var_size)==4 and (OutputVarStructure=='time_lat_lon') and output_type=='broadcast'):
    levels=[0]

  if not 'levels' in locals():
    if(len(var_size)==3):
      levels=None
    elif(len(var_size)==4):
      levels=range(0,var_size[1])
    else:
      levels=None

  if(type(levels)==type(None)):
    #print('aaa')
    nlev=None
  else:
    nlev=len(levels)

  print('levels=',levels)

  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  #print('ProcTimeN.time_beg=',ProcTimeN.time_beg)
  #print('ProcTimeN.time_stamp_beg=',ProcTimeN.time_stamp_beg)
   #time_stamp_beg=datetime.datetime(ProcTimeN.year,1,1) + datetime.timedelta(hours=0.0) 

  cmor.set_table(tables[1])
  
  if((realm =='ice' or realm=='ocean') and ( OutputVarStructure=='time_lat_lon' or OutputVarStructure=='time_depth_lat_lon' or OutputVarStructure=='depth_lat_lon')):
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
  
  elif(realm=='ice_obsolete'):
    '''
    lat_vals=ProcTimeN.ifh0.variables['yt'][:] #lat
    lon_vals=ProcTimeN.ifh0.variables['xt'][:] #lon

    lon_vals=np.roll(np.where( lon_vals<0., lon_vals+360., lon_vals), 82)

    min_vals=np.append((1.5*lat_vals[0] - 0.5*lat_vals[1]), (lat_vals[0:-1] + lat_vals[1:])/2)
    max_vals=np.append((lat_vals[0:-1] + lat_vals[1:])/2, 1.5*lat_vals[-1] - 0.5*lat_vals[-2])
    lat_vals_bounds=np.column_stack((min_vals, max_vals))

    min_vals=np.append( lon_vals[0] - (360. - lon_vals[-1] + lon_vals[1])*.5, (lon_vals[0:-1] + lon_vals[1:])/2 )
    max_vals=np.append((lon_vals[0:-1] + lon_vals[1:])/2, lon_vals[-1] + (360. - lon_vals[-1] + lon_vals[1])*.5)
    lon_vals_bounds=np.column_stack((min_vals, max_vals))
    lon_vals_bounds=np.where( lon_vals_bounds<0., lon_vals_bounds+360., lon_vals_bounds)
    lon_vals_bounds=np.where( lon_vals_bounds>360., lon_vals_bounds-360., lon_vals_bounds)

    np.set_printoptions(formatter={'all':lambda x: "%.4f" % x})
    lon_check=np.insert(lon_vals_bounds,0,range(len(lon_vals)),axis=1) #put in counter first column
    lon_check=np.insert(lon_check,3,lon_vals,axis=1) #put in lon vals last column
    print('lon_check=',lon_check)
    '''

#assume has ocean lat/lon (which I think it has, xt/yt look strange...esp xt.

    lat_vals=xfh.variables['grid_y_T']
    lon_vals=xfh.variables['grid_x_T']

    min_vals=np.append((1.5*lat_vals[0] - 0.5*lat_vals[1]), (lat_vals[0:-1] + lat_vals[1:])/2)
    max_vals=np.append((lat_vals[0:-1] + lat_vals[1:])/2, 1.5*lat_vals[-1] - 0.5*lat_vals[-2])
    lat_vals_bounds=np.column_stack((min_vals, max_vals))
  
    min_vals=np.append((1.5*lon_vals[0] - 0.5*lon_vals[1]), (lon_vals[0:-1] + lon_vals[1:])/2)
    max_vals=np.append((lon_vals[0:-1] + lon_vals[1:])/2, 1.5*lon_vals[-1] - 0.5*lon_vals[-2])
    lon_vals_bounds=np.column_stack((min_vals, max_vals))

  elif(realm=='atmos' or realm=='ocean' or realm=='ice'):
  
    if(ReGrid):
      lat_vals = outgrid.getLatitude() 
      lon_vals = outgrid.getLongitude()
    else:
      if(realm=='ocean' and (OutputVarStructure=='time' or OutputVarStructure=='time_oline' or OutputVarStructure=='time_lon') ):
      #dvar=='nino34' or dvar=='iod' or dvar=='pp' or dvar=='nflux' or dvar=='ep'):
        lat_vals=f.variables['yt_ocean']
        lon_vals=f.variables['xt_ocean']
      else:
        #lat_vals=f.variables['lat'] #lat
        #lon_vals=f.variables['lon'] #lon
        lat_vals=ProcTimeN.ifh0.variables['lat'] #lat
        lon_vals=ProcTimeN.ifh0.variables['lon'] #lon

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
  #else:
  #  levels2=levels
  #  nlev2=len(levels2)
  
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
      #zt=f.variables['pfull'][:]*100.0
      zt=ProcTimeN.ifh0.variables['pfull'][:]*100.0
    else:
      #zt=f.variables['phalf'][:]*100.0
      zt=ProcTimeN.ifh0.variables['phalf'][:]*100.0
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
  
    #nlev=len(levels)
  
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

  #print('levels=',levels)
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
    #print(inputs)
    #print(inputs_shape)
    #print(levels2)
    #print(levels3)
  #  print(nlev)
  #  print(nlev2)
  #  print(plevN)
  #  #print(newlevs)
  
  if(realm=='atmos' and (OutputVarStructure=='time' or OutputVarStructure=='time_lat_lon' or OutputVarStructure=='time_plev_lat_lon' or OutputVarStructure=='time_reducedplev_lat_lon' or OutputVarStructure=='time_lon') or realm=='ice_obsolete'):

    print('entering here...')

  #  lat_axis=f.variables['lat']
  #  lon_axis=f.variables['lon']
  
    #print('lat_vals.shape=',lat_vals.shape,file=fh_printfile)
    #print('lon_vals.shape=',lon_vals.shape,file=fh_printfile)
  
    #print('lat_vals_bounds.shape=',lat_vals_bounds.shape,file=fh_printfile)
    #print('lon_vals_bounds.shape=',lon_vals_bounds.shape,file=fh_printfile)

    print('aaa')

    lat_vals_bounds=np.where(lat_vals_bounds>90.0,90.0,lat_vals_bounds)
    lat_vals_bounds=np.where(lat_vals_bounds<-90.0,-90.0,lat_vals_bounds)
  
    #print('max=',np.max(lat_vals_bounds),file=fh_printfile)
    #print('min=',np.min(lat_vals_bounds),file=fh_printfile)
  
    nlats=lat_vals.shape[0] #check this
    nlons=lon_vals.shape[0] #check this, should it be 1?
  
    cmor.set_table(tables[0]) #working zg500
    #cmor.set_table(tables[2])

    print('lat_vals=',lat_vals)
    print('lat_vals_bounds=',lat_vals_bounds)
    print('lon_vals=',lon_vals)
    print('lon_vals_bounds=',lon_vals_bounds)
    print('bbb')

    lat_axis_id=cmor.axis(table_entry='latitude', units='degrees_north', coord_vals=lat_vals[:], cell_bounds=lat_vals_bounds)
  
    lon_axis_id=cmor.axis(table_entry='longitude', units='degrees_east', coord_vals=lon_vals[:], cell_bounds=lon_vals_bounds)

    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

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
  
  elif((realm=='ice' or realm=='ocean') and OutputVarStructure=='time_lat_lon'):
  
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
    data_id.append(cmor.variable(dvar[0], ounits[0], axis_ids=axis_ids, missing_value=-1e20))
  
  elif((realm=='ice' or realm=='ocean') and OutputVarStructure=='time_lat_lon'):
    axis_ids=[i_axis_id,j_axis_id,time_axis_id]
    axis_ids=[time_axis_id]
    axis_ids=[0]
    axis_ids=[time_axis_id,j_axis_id,i_axis_id]
    axis_ids=np.array([time_axis_id,j_axis_id,i_axis_id])
    axis_ids=np.array([j_axis_id,i_axis_id])
    axis_ids=[0,-100]
    axis_ids=[grid_id]
    axis_ids=[time_axis_id,grid_id] #working
    data_id.append(cmor.variable(dvar[0], ounits[0], axis_ids=axis_ids, missing_value=-1e20))
  
  elif(table=='fx'):
    axis_ids=[1,-100]
    data_id.append(cmor.variable(dvar[0], ounits[0], axis_ids=axis_ids, missing_value=-1e20))
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  elif(realm=='ocean' and ( OutputVarStructure=='time_depth_lat_lon' or OutputVarStructure=='time_reduceddepth_lat_lon')):
    #axis_ids=[time_axis_id,grid_id]
    #axis_ids=[0,1,2,3]
    #axis_ids=[time_axis_id,z_axis_id,grid_id]
    #axis_ids=[0,-100]
    #axis_ids=[0,2,-100] #works but prob.
    axis_ids=[0,1,-100]
    data_id.append(cmor.variable(dvar[0], ounits[0], axis_ids=axis_ids, missing_value=-1e20))
  
  elif((realm=='atmos' or realm =='ice_obsolete') and OutputVarStructure=='time_lat_lon'):
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
  
    data_id.append(cmor.variable(dvar[0], ounits[0], axis_ids=axis_ids, missing_value=-1e20,positive=positive))
  
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
      print('ovars[o]=',ovars[o])
      print('ounits[o]=',ounits[o])
      data_id.append(cmor.variable(ovars[o], ounits[o], axis_ids=axis_ids, missing_value=-1e20))
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  elif(realm=='atmos' and ( OutputVarStructure=='time_lon')):
    axis_ids=np.array([time_axis_id,lon_axis_id])
    for o in range(0,len(ovars)):
      data_id.append(cmor.variable(ovars[o], ounits[o], axis_ids=axis_ids, missing_value=-1e20))
  
  elif((realm=='ice' or realm=='ocean' or realm=='atmos') and OutputVarStructure=='time'):
    #dvar=='nino34' or dvar=='temptotal' or dvar=='salttotal' or dvar=='iod' or dvar=='pp' or dvar=='nflux' or dvar=='ep'):
    #axis_ids=[time_axis_id,grid_id]
    #axis_ids=[grid_id]
    axis_ids=[]
    axis_ids=[time_axis_id]
    axis_ids=np.array([time_axis_id])
    axis_ids=[0] #working
    #data_id=cmor.variable(dvar, ounits,  missing_value=-1e20)
    data_id.append(cmor.variable(dvar[0], ounits[0], axis_ids=axis_ids, missing_value=-1e20))
  
  elif(realm=='ocean' and OutputVarStructure=='time_basin_depth_lat'):
    axis_ids=np.array([time_axis_id, basin_axis_id, z_axis_id, lat_axis_id])
    data_id.append(cmor.variable(dvar[0], ounits[0], axis_ids=axis_ids, missing_value=-1e20))
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

  #print(ProcTimeN.years_defined)
  #print(ProcTimeN.years_defined[0])
  #print(type(ProcTimeN.years_defined[0]))
  #print(ProcTimeN.years_defined[-1])
  #print(type(ProcTimeN.years_defined[-1]))
  #print(ProcTimeN.season_month_indices_defined)
  #print(ProcTimeN.nparray_months_defined[ProcTimeN.season_month_indices_defined[0][0]])
  #print(ProcTimeN.nparray_months_defined[ProcTimeN.season_month_indices_defined[-1][-1]])

  print(ProcTimeN.season_month_indices_defined[0][0])
  print(ProcTimeN.season_month_indices_defined[-1][-1])
  print(ProcTimeN.npmonths)

  print(ProcTimeN.npmonths[ProcTimeN.season_month_indices_defined[0][0]-1-ProcTimeN.firstvalue])
  print(ProcTimeN.npmonths[ProcTimeN.season_month_indices_defined[-1][-1]-1-ProcTimeN.firstvalue])

  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  odir=[]
  ofil=[]
  ofil_modified=[]

  odir.append('CMIP6/CMIP'+'/'+institution_id+'/'+source_id+'/'+experiment_id+'/'+ripf+'/'+table+'/'+ovars[0]+'/'+grid_label+'/'+version)

  ybeg_ofil=str('{0:04d}'.format(ProcTimeN.years_defined[0]))
  yend_ofil=str('{0:04d}'.format(ProcTimeN.years_defined[-1]))

  print('yend_ofil=',yend_ofil)

  if(season=='MON'):
    mbeg_ofil=str('{0:02d}'.format(ProcTimeN.npmonths[ProcTimeN.season_month_indices_defined[0][0]-1-ProcTimeN.firstvalue]))
    mend_ofil=str('{0:02d}'.format(ProcTimeN.npmonths[ProcTimeN.season_month_indices_defined[-1][-1]-1-ProcTimeN.firstvalue]))

    ofil.append(ovars[0]+'_'+table+'_'+experiment_id+'_'+source_id+'_'+ripf+'_'+grid_label+'_'+ybeg_ofil+mbeg_ofil+'-'+yend_ofil+mend_ofil+'.nc')
    ofil_modified.append(ovars[0]+'_'+table+'_'+experiment_id+'_'+source_id+'_'+ripf+'_'+grid_label+'_'+ybeg_ofil+mbeg_ofil+'-'+yend_ofil+mend_ofil+'.nc')

    #print(ofil_modified)
    #exit()

  else:
    ofil.append(ovars[0]+'_'+table+'_'+experiment_id+'_'+source_id+'_'+ripf+'_'+grid_label+'_'+ybeg_ofil+'-'+yend_ofil+'.nc')
    ofil_modified.append(ovars[0]+'_'+table+'_'+experiment_id+'_'+source_id+'_'+ripf+'_'+grid_label+'_'+ybeg_ofil+'-'+yend_ofil+'_'+season+'.nc')

  #print(odir_ofil+'/'+ofil_ofil)

  print('ybeg,yend_ofil=',ybeg_ofil,yend_ofil)
  if(season=='MON'):
    print('mbeg,mend_ofil=',mbeg_ofil,mend_ofil)

  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
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

  ProcTimefirstvalue=ProcTimeN.season_indices_defined[ProcTimeN.years_defined.index(ProcTimeN.ybeg_season_process)][0]-1 #this is used for dealing with different months starting first year.
  print('ProcTimefirstvalue=',ProcTimefirstvalue)

  for ProcTimei,ProcTimeyear in enumerate(range(ProcTimeN.ybeg_season_process,ProcTimeN.yend_season_process+1)):
    icnt=ProcTimei

    ProcTimevalues=ProcTimeN.season_indices_defined[ProcTimeN.years_defined.index(ProcTimeyear)]
    ProcTimenpvalues=np.array(ProcTimeN.season_indices_defined[ProcTimeN.years_defined.index(ProcTimeyear)])-1

    ProcTimevalues2=ProcTimeN.season_month_indices_defined[ProcTimeN.years_defined.index(ProcTimeyear)]
    ProcTimenpvalues2=np.array(ProcTimeN.season_month_indices_defined[ProcTimeN.years_defined.index(ProcTimeyear)])-1

    ProcTimenvalues=len(ProcTimevalues)
    ProcTimennpvalues=len(ProcTimenpvalues)
    ProcTimenvalues2=len(ProcTimevalues2)
    ProcTimennpvalues2=len(ProcTimenpvalues2)

    ProcTimenpvalues2=ProcTimenpvalues2-ProcTimefirstvalue

    #print('ProcTimevalues=',ProcTimevalues)
    #print('ProcTimevalues2=',ProcTimevalues2)

    print('ProcTimenpvalues=',ProcTimenpvalues)
    print('ProcTimenpvalues2=',ProcTimenpvalues2)

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
      data1=data_wavg_ProcTime(inputs[0],ProcTimeN.ifhN,ProcTimenpvalues,ProcTimenpvalues2,ProcTimeN.season_broadcast[ProcTimeN.season],levels)
      data2=data_wavg_ProcTime(inputs[1],ProcTimeN.ifhN,ProcTimenpvalues,ProcTimenpvalues2,ProcTimeN.season_broadcast[ProcTimeN.season],levels)

      #data1=data_wavg(inputs[0],input_fhs,locate_file_index_Ntimes_b1_nominus1s_flat,ind_beg,ind_end,month_in_file_total_months_beg_to_end,levels,nlev,MonthlyWeights,month_index_ntims,fh_printfile,var_size)
      #data2=data_wavg(inputs[1],input_fhs,locate_file_index_Ntimes_b1_nominus1s_flat,ind_beg,ind_end,month_in_file_total_months_beg_to_end,levels2,nlev2,MonthlyWeights,month_index_ntims,fh_printfile,var_size2)
  
      if(len(inputs)>=3):
        #data3=data_wavg(inputs[2],input_fhs,locate_file_index_Ntimes_b1_nominus1s_flat,ind_beg,ind_end,month_in_file_total_months_beg_to_end,levels3,nlev3,MonthlyWeights,month_index_ntims,fh_printfile,var_size3)
        data3=data_wavg_ProcTime(inputs[2],ProcTimeN.ifhN,ProcTimenpvalues,ProcTimenpvalues2,ProcTimeN.season_broadcast[ProcTimeN.season],levels)
  
    else:
      #levels=[0]
      #nlev=1
      #data=np.zeros((ProcTimenvalues,300,360),dtype='f')
      #print(ProcTimennpvalues)
      #data=ProcTimeN.ifhN.variables[inputs[0]][ProcTimenpvalues,]

      try:
        data=data_wavg_ProcTime(inputs[0],ProcTimeN.ifhN,ProcTimenpvalues,ProcTimenpvalues2,ProcTimeN.season_broadcast[ProcTimeN.season],levels)
      except KeyError:
        data=data_wavg_ProcTime(inputs_alternative[0],ProcTimeN.ifhN,ProcTimenpvalues,ProcTimenpvalues2,ProcTimeN.season_broadcast[ProcTimeN.season],levels)

      #print('levels=',levels,file=fh_printfile)
      #print('nlev=',nlev,file=fh_printfile)
  
    #print('data.shape=',data.shape)
  
    if(output_type=='diagnostic'):
  
      if(define_basin_mask and icnt==0): #only need to define the masks once...
          atlantic_arctic_mask,indoPac_mask,global_mask=make_mask3D(data1+data2,nbasins,nzb,nlats)
  
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
  
#!    if(table=='fx'): #special case, no need to loop over all input times.
#!      file_name=[]
#!      for o in range(0,len(ovars)):
#!        print('o=',o,file=fh_printfile)
#!        print('file_name=',file_name,file=fh_printfile)
#!        cmor.write(var_id=data_id[o], data=data[:], ntimes_passed=0)
#!        file_name.append(cmor.close(var_id=data_id[o], file_name=True))
#!        finish(file_name[o],odir[o],ofil[o],ofil_modified[o],season,fh_printfile)
#!      raise SystemExit('Completed time-invaniant output, can exit: '+__file__+' line number: '+str(inspect.stack()[0][2]))

    if(ProcTimeN.season_broadcast[ProcTimeN.season]):
      ntimes_passed=ProcTimenvalues
    else:
      ntimes_passed=1
  
    if(OutputVarStructure=='time'):
      newdata=np.zeros((1,1),dtype='f')
      newdata[0,0]=data
      data=newdata
      for o in range(0,len(ovars)):
        cmor.write(var_id=data_id[o], data=data[:], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])
  
    elif(realm=='ocean' and (OutputVarStructure=='time_depth_lat_lon' or OutputVarStructure=='time_lat_lon' or OutputVarStructure=='time_reduceddepth_lat_lon' or OutputVarStructure=='time_oline' or OutputVarStructure=='time_basin_depth_lat') or realm=='atmos' and (OutputVarStructure=='time_plev_lat_lon' or OutputVarStructure=='time_lat_lon' or OutputVarStructure=='time_reducedplev_lat_lon' or OutputVarStructure=='time_lon') or realm=='ice' and (OutputVarStructure=='time_lat_lon')):
      for o in range(0,len(ovars)):
        if('outputs_string' in locals() and len(outputs_string)!=1):
          cmor.write(var_id=data_id[o], data=data[0], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]]) #tuple, multiple outputs.
        else:

          if(ProcTimeN.season_broadcast[ProcTimeN.season]):

             print('data.shape=',data.shape)
             print('ntimes_passed=',ntimes_passed)
             print('ProcTimennpvalues=',ProcTimennpvalues)
             print('ProcTimeN.time_bounds=',ProcTimeN.time_bounds)
             print('ProcTimeN.time_bounds[ProcTimennpvalues]=',ProcTimeN.time_bounds[ProcTimennpvalues])

             cmor.write(var_id=data_id[o], data=data, ntimes_passed=ntimes_passed, time_bnds=ProcTimeN.time_bounds[ProcTimennpvalues])
          else:
            cmor.write(var_id=data_id[o], data=data, ntimes_passed=ntimes_passed, time_bnds=ProcTimeN.time_bounds[icnt])

  file_name=[]
  print('ovars=',ovars)
  for o in range(0,len(ovars)):
    print('o=',o,file=fh_printfile)
    file_name.append(cmor.close(var_id=data_id[o], file_name=True))
    print('file_name=',file_name[o],file=fh_printfile)
  
  for o in range(0,len(ovars)):
    finish(file_name[o],odir[o],ofil[o],ofil_modified[o],season,ProcTimeN.season_broadcast[ProcTimeN.season],fh_printfile)
  
  #raise SystemExit('Finished O.K.')
  print('Finished O.K.')
  return(0)
  
  oend
