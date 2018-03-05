#!/usr/bin/env python

##!/short/v14/mac599/anaconda3/envs/cafepp_27/bin/python
##!/short/v14/mac599/anaconda3/envs/cafepp_36_cmds/bin/python
##!/apps/python/2.7.6/bin/python
##!/short/p66/mac599/anaconda3/bin/ipython
# Filename : cafepp_daily.py

from __future__ import print_function #this is to allow print(,file=xxx) feature

#import sys
#sys.path.insert(0, '/home/599/mac599/decadal')

#from __future__ import division, absolute_import, print_function, unicode_literals #carefule some of these might negatively affect python2*
#import six

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
#import sys
import getopt
import string
from decadal_diag import MustHaveAllLevs,diag_acc_drake,diag_acc_africa,diag_mozmbq,diag_aabw,diag_nadw,diag_pp,diag_nflux,diag_ep,diag_ssh,diag_moc,diag_moc_atlantic,diag_moc_pacific,diag_moc_indian,diag_shice_cover,diag_nhice_cover,diag_nino34,xtra_nino34,init_data,sum_data,avg_data,filemonth_index,data_wavg,time_avg,diag_nhblocking_index,diag_rws5,finish,diag_msftyyz,make_mask3D,diag_mfo,transPort,diag_rws500,create_odirs,create_ofils,diag_iod,diag_iod,xtra_iod,atmos_vertical_interpolate,diag_isothetaoNc,calc_iso_surface,calc_isoN,grab_var_meta,diag_psl,diag_hfls,diag_heat_content,diag_salt_content,diag_north_heat_trans,diag_north_salt_trans,ocean_vertical_interpolate,diag_thetao0to80m,diag_varNl,uncomment_json,process_json,get_daily_indices_for_monthlyave

from decadal_diag import diag_maxdTbydz,diag_depmaxdTbydz,diag_dTbydz,shade_2d_simple,shade_2d_latlon,diag_zmld_boyer,zmld_boyer,sigmatheta,diag_zmld_so,zmld_so,diag_spice,spice,diag_bigthetao,diag_soabs,diag_spiciness,diag_potrho
#,diag_thetao10l,diag_so5l
import cmor
import cdtime
from app_funcs import *
import json
import pprint
from datetime import date
import filecmp
from shutil import copyfile
import cdms2
#from regrid2 import Regridder
import inspect
import socket
#from glob import re
import glob
#from matplotlib.mlab import griddata #could try https://docs.scipy.org/doc/scipy-0.16.0/reference/generated/scipy.interpolate.griddata.html
from matplotlib.mlab import griddata
#from scipy.interpolate import griddata
import scipy.sparse as sps
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from cartopy.util import add_cyclic_point
import matplotlib as mpl
#print(matplotlib.get_backend())

#import pylab
mpl.rcParams['mathtext.default'] = 'regular'
import matplotlib.pyplot as plt
#plt.switch_backend("TkAgg")
from gridfill import fill as poisson_fill

#if(len(sys.argv)!=2):
#  raise SystemExit('CAFEPP_DAILY only takes one argument, the JSON instruction file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

def main(json_input_instructions):

  print('MAIN')

  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
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
  ProcessFileList=False
  ProcessFileTxtTF=False
  importance=5
  
  cafepp_defs='cafepp_csiro-gfdl.json'
  cafepp_experiments='cafepp_experiments.json'
  json_input_var_meta='cafepp_vars_day.json'
  #json_input_instructions='cafepp.json'
  #json_input_instructions=sys.argv[1]
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
    #os.system('awk -f ~mac599/decadal/uncomment_json.awk JsonTemplates/'+json_input_instructions+' > '+json_input_instructions)
    uncomment_json('JsonTemplates/'+json_input_instructions,json_input_instructions,True)
    print('Running cafepp from JSON instructions: '+json_input_instructions)
    json_input_instructions_fh=open(json_input_instructions).read()
    json_input_instructions_data=json.loads(json_input_instructions_fh)
    #print('json_input_instructions_data=',json_input_instructions_data)
  else:
    print('Running cafepp from command line input:')
  
  if 'json_input_instructions' in locals():
    #print('Summary of JSON instructions: ',json.dumps(json_input_instructions_data,indent=4,sort_keys=True))
  
    #print(type(json_input_instructions_data))
  
    top_level_keys=json_input_instructions_data.keys()
  
  #  print('Top level JSON instructions keys=',top_level_keys)
  #  print(json_input_instructions_data)
    #for key_now in json_input_instructions_data.iteritems():
    for key_now in json_input_instructions_data.items():
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
          elif(l=='force_hostname'): force_hostname=str(list_new[l])
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
            dvar=string.split(str(list_new[l]))
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
          elif(l=='ProcessFileTxt'):
            ProcessFileTxt=str(list_new[l])
            ProcessFileTxtTF=True
          elif(l=='cafepp_machine'): cafepp_machine=str(list_new[l])
          else: raise SystemExit('Unknown option_with_argument,',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
      elif(key_now0=='options_no_arguments'):
        list_new=(json_input_instructions_data[key_now0])
        for l in list_new: #used to be list_new2
          if(l=='name'): name=str(list_new[l])
          elif(l=='info'): info=str(list_new[l])
  #        elif(l=='Forecast'): 
  #          if(list_new[l]=='True'): Forecast=list_new[l]
  #        elif(l=='Regrid'):
  #          if(list_new[l]=='True'): Regrid=True
  #        elif(l=='MonthlyWeights'): 
  #          if(list_new[l]=='True'): MonthlyWeights=True
          elif(l=='NoClobber'): 
            if(list_new[l]=='True'): NoClobber=list_new[l]
          elif(l=='ProcessFileList'): 
            if(list_new[l]=='True'): ProcessFileList=list_new[l]
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
          elif(l=='vertical_interpolation_method'):
            if(str(list_new[l])=='None'): vertical_interpolation_method=None
  #vertical_interpolation_method=str(list_new[l])
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
  
  if(ProcessFileList and ProcessFileTxtTF):
    raise SystemExit('Cannot have both ProcessFileList and ProcessFileTxtTF True:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  #cafepp_experiments_meta='cafepp_experiments.json'
  #os.system('awk -f ~mac599/decadal/uncomment_json.awk JsonTemplates/'+cafepp_experiments_meta+' > '+cafepp_experiments_meta)
  uncomment_json('JsonTemplates/'+cafepp_experiments_meta,cafepp_experiments_meta,True)
  cafepp_experiments_fh=open(cafepp_experiments_meta).read()
  #print('cafepp_experiments_fh=',cafepp_experiments_fh,file=fh_printfile)
  cafepp_experiments_data=json.loads(cafepp_experiments_fh)
  #print('cafepp_experiments_data=',cafepp_experiments_data,file=fh_printfile)
  
  #print('Summary of JSON experiments input: ',json.dumps(cafepp_experiments_data,indent=4,sort_keys=True),file=fh_printfile)
  
  top_level_keys=cafepp_experiments_data.keys()
  #print('Top level JSON experiments keys=',top_level_keys,file=fh_printfile)
  
  cafepp_experiment_found=False
  #for key_now in cafepp_experiments_data.iteritems():
  for key_now in cafepp_experiments_data.items():
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
        elif(l=='source'): source=str(list_new[l])
        elif(l=='source_id'): source_id=str(list_new[l])
        else: raise SystemExit('Unknown variable metadata',l,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    else:
      pass
  
  #storage_machine_no2_split=storage_machine_no2.split('.')
  #storage_machine_no2_split=storage_machine_no2.split('.')
  #print(storage_machine_no2_split)
  #print(type(storage_machine_no2))
  #print(str.split(storage_machine_no2),sep='.')
  #print(string.join(storage_machine_no2),sep='')
  #        #erange=[str(x) for x in a.split(',')]
  
  if 'force_hostname' in locals():
    hostname=force_hostname
  
  #print(hostname)
  #print(active_disk_no1)
  #print(storage_machine_no1)
  
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
    if re.match(storage_machine_no3[0],hostname):
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
  
  print('hostname=',hostname)
  print('storage_machine_no1=',storage_machine_no1)
  
  #idir=top_directory_no2 #this is hardwired until I sort out how to manage this on raijin's quque...
  
  if not 'idir' in locals():
    raise SystemExit('Could not determine input dir in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  if(not cafepp_experiment_found):
    raise SystemExit('Could not find CAFEPP experiment',' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  netcdf='NETCDF4_CLASSIC'
  netcdf='NETCDF3_64BIT'
  netcdf='NETCDF3_CLASSIC'
  netcdf='NETCDF4'
  
  print(sys.argv,file=fh_printfile)
  
  define_basin_mask=False
  #json_input_var_meta='cafepp_vars_day.json'
  #os.system('awk -f ~mac599/decadal/uncomment_json.awk JsonTemplates/'+json_input_var_meta+' > '+json_input_var_meta)
  uncomment_json('JsonTemplates/'+json_input_var_meta,json_input_var_meta,True)
  json_input_var_fh=open(json_input_var_meta).read()
  #print('json_input_var_fh=',json_input_var_fh,file=fh_printfile)
  json_input_var_data=json.loads(json_input_var_fh)
  #print('json_input_var_data=',json_input_var_data,file=fh_printfile)
  
  #print('Summary of JSON variable input: ',json.dumps(json_input_var_data,indent=4,sort_keys=True),file=fh_printfile)
  
  top_level_keys=json_input_var_data.keys()
  #print('Top level JSON variable keys=',top_level_keys,file=fh_printfile)
  
  #for key_now in json_input_var_data.iteritems():
  for key_now in json_input_var_data.items():
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
      for l in sorted(list_new):
        #print(l,file=fh_printfile)
        if(l=='info'): info=str(list_new[l])
        elif(l=='area_t'): 
            if(list_new[l]=='True'): area_t=True
        elif(l=='area_u'): 
            if(list_new[l]=='True'): area_u=True
        elif(l=='inputs'): inputs=string.split(str(list_new[l]),sep=",") #python2
        #elif(l=='inputs'): inputs=str.split(str(list_new[l]),sep=",") #python3
        elif(l=='inputs_alternative'): inputs_alternative=string.split(str(list_new[l]))
          #newinputs=str.split(inputs)
          #print('inputs=',inputs)
          #print('newinputs=',newinputs)
        elif(l=='realm'): realm=str(list_new[l])
  #      elif(l=='diag_dims'): diag_dims=str.split(str(list_new[l]))
        elif(l=='ounits'): ounits=str(list_new[l])
  #      elif(l=='table'): table_tmp=str(list_new[l])
        elif(l=='table'): table_tmp=string.split(str(list_new[l]),sep=',')
        elif(l=='table_frequency'): table_frequency=string.split(str(list_new[l]),sep=',')
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
        #elif(l=='outputs_string'): outputs_string=str.split(str(list_new[l]),sep=",")
        #elif(l=='outputs_units_string'): outputs_units_string=str.split(str(list_new[l]),sep=",")
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
          #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
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
  
  if(output_type=="diagnostic" and not 'diagnostic_args_string' in locals()):
    raise SystemExit('When generating a diagnostic, must define a diagnostic_args_string to go with it: '+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  if(output_type=='diagnostic' and not 'diagnostic_function_name' in locals()):
    diagnostic_function_name=dvar[0]
  
  if 'interp_fill_options' in locals():
    comment='interp_fill_options='+','.join(interp_fill_options)
  elif not 'comment' in locals():
    comment=None
  
  #print(interp_fill_options)
  #print('interp_fill_options=',','.join(interp_fill_options))
  
  #print(comment)
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
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
  
  #print('printDefinedDiagnostics=',printDefinedDiagnostics,file=fh_printfile)
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
  #realm,table,inputs,units,ovars,area_t,area_u,diag_dims,grid_label,grid,vertical_interpolation_method,OutputVarStructure=grab_var_meta(dvar,frequency)
  
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
  
  #cmor.setup(inpath='Tables',netcdf_file_action=cmor.CMOR_REPLACE_4,logfile=cmorlogfile)
  cmor.setup(inpath='cmip6-cmor-tables/Tables',netcdf_file_action=cmor.CMOR_REPLACE_4,logfile=cmorlogfile)
  
  #cafepp_defs='cafepp_csiro-gfdl.json'
  #os.system('awk -f ~mac599/decadal/uncomment_json.awk JsonTemplates/'+cafepp_defs+' > '+cafepp_defs)
  uncomment_json('JsonTemplates/'+cafepp_defs,cafepp_defs,True)
  #json_input_var_meta()
  #print('cafepp_defs=',cafepp_defs)
  #cafepp_defs=
  #print(type(cafepp_defs))

  #print('Present Working Directory=',os.getcwd())
  
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
  
  #print(grid_label)
  
  if(grid_label=='gr1'):
    lat_vals_regrid=np.linspace(-89,89,90)
    lon_vals_regrid=np.linspace(1,359,180)
    lats_min_vals_regrid=np.linspace(-90,88,90)
    lats_max_vals_regrid=np.linspace(-88,90,90)
  
    lons_min_vals_regrid=np.linspace(0,358,180)
    lons_max_vals_regrid=np.linspace(2,360,180)
    regrid_resolution="2x2"
  
  elif( grid_label=='gr2'):
    lat_vals_regrid=np.linspace(-89.5,89.5,180)
    lon_vals_regrid=np.linspace(.5,359.5,360)
  
    lats_min_vals_regrid=np.linspace(-90,89,180)
    lats_max_vals_regrid=np.linspace(-89,90,180)
  
    lons_min_vals_regrid=np.linspace(0,359,360)
    lons_max_vals_regrid=np.linspace(1,360,360)
    regrid_resolution="1x1"
  
  elif( grid_label=='gr3'):
    lat_vals_regrid=np.linspace(-87.5,87.5,36)
    lon_vals_regrid=np.linspace(2.5,357.5,72)
  
    lats_min_vals_regrid=np.linspace(-90,85,36)
    lats_max_vals_regrid=np.linspace(-85,90,36)
  
    lons_min_vals_regrid=np.linspace(0,355,72)
    lons_max_vals_regrid=np.linspace(5,360,72)
    regrid_resolution="5x5"
  
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  if(grid_label=='gr1' or grid_label=='gr2' or grid_label=='gr3'):
    ReGrid=True
  
    idirfil_lsm='/short/v14/mac599/data/dst'+regrid_resolution+'_lsm.nc'
    if(realm=='ocean'):
      idirfil_wgt='/short/v14/mac599/data/curvilinear'+regrid_resolution+'_wgt_SCRIP_outmask.nc'
    else:
      idirfil_wgt='/short/v14/mac599/data/rectilinear'+regrid_resolution+'_wgt_SCRIP_noinmasknooutmask.nc'
  
    nlats_regrid=lat_vals_regrid.size
    nlons_regrid=lon_vals_regrid.size
  
    lat_vals_bounds_regrid=np.column_stack((lats_min_vals_regrid, lats_max_vals_regrid))
    lon_vals_bounds_regrid=np.column_stack((lons_min_vals_regrid, lons_max_vals_regrid))
  
    ifh_lsm=netCDF4.Dataset(idirfil_lsm)
    ls_mask_regrid = ma.masked_equal(ifh_lsm.variables['OutMask'], 0.).astype(float)
    #print(ls_mask_regrid.view)
    ls_mask_regrid.set_fill_value(1e20)
  
    #print(realm)
    ifh_wgt=netCDF4.Dataset(idirfil_wgt)
  
    #print(lat_vals_bounds[:])
    #np.set_printoptions(threshold='nan') #will print out whole array
    #print(S[:])
    #print(S.shape) 
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  if not 'version' in locals(): version='v'+str('{0:04d}'.format(t[0])) + str('{0:02d}'.format(t[1])) + str('{0:02d}'.format(t[2]))
  
  #print(ripf)
  
  if(not ProcessFileList):
  
    odir=create_odirs(ovars,institution_id,source_id,experiment_id,ripf,table,grid_label,version)
  
    ofil,ofil_modified=create_ofils(season,table,ovars,experiment_id,source_id,ripf,grid_label,ybeg,yend,mbeg,mend,dbeg,dend)
  
    #raise SystemExit('Finished O.K.')
  
    for o in range(0,len(ovars)):
      print('Output CMIP6 file:',odir[o]+'/'+ofil_modified[o],file=fh_printfile)
  
    for o in range(0,len(ovars)):
      if(os.path.exists(odir[o]+'/'+ofil_modified[o]) and NoClobber):
        print('No Clobber set and ',odir[o]+'/'+ofil_modified[o],' exists')
        #raise SystemExit('No Clobber set and ',odir[o]+'/'+ofil_modified[o],' exists')
        return(0)
  
    for o in range(0,len(ovars)):
      if(os.path.exists(odir[o]+'/'+ofil[o]) and NoClobber):
        print('No Clobber set and ',odir[o]+'/'+ofil_modified[o],' exists')
        return(0)
        #raise SystemExit('No Clobber set and ',odir[o]+'/'+ofil_modified[o],' exists')
  
  #calendar='julian'
  cmor.set_cur_dataset_attribute('grid_label',grid_label)
  cmor.set_cur_dataset_attribute('grid',grid)
  cmor.set_cur_dataset_attribute('physics',physics)
  cmor.set_cur_dataset_attribute('physics_index',physics)
  cmor.set_cur_dataset_attribute('forcing',forcing)
  cmor.set_cur_dataset_attribute('forcing_index',forcing)
  cmor.set_cur_dataset_attribute('realization',realisation)
  cmor.set_cur_dataset_attribute('realization_index',realisation)
  cmor.set_cur_dataset_attribute('initialization',initialisation)
  cmor.set_cur_dataset_attribute('initialization_index',initialisation)
  cmor.set_cur_dataset_attribute('version',version)
  
  #cmor.set_cur_dataset_attribute('experiment',experiment)
  #cmor.set_cur_dataset_attribute('experiment_id',experiment_id)
  #cmor.set_cur_dataset_attribute('parent_experiment_id',parent_experiment_id)
  #cmor.set_cur_dataset_attribute('history',history)
  #cmor.set_cur_dataset_attribute('institution',institution)
  #cmor.set_cur_dataset_attribute('institution_id',institution_id)
  
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
    #fileB='cmor/Tables/CMIP6_'+table+'.json'
    fileB='cmip6-cmor-tables/Tables/CMIP6_'+table+'.json'
    if filecmp.cmp(fileA,fileB):
      pass
    else:
      copyfile(fileA,fileB)
  
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
  
  #print('cmor/Tables/CMIP6_'+table+'.json',file=fh_printfile)
  
  print('cmip6-cmor-tables/Tables/CMIP6_'+table+'.json')
  
  tables=[]
  tables.append(cmor.load_table('cmip6-cmor-tables/Tables/CMIP6_'+table+'.json'))
  #tables.append(cmor.load_table('cmip6-cmor-tables/Tables/CMIP6_Oday.json'))
  
  tables.append(cmor.load_table('cmip6-cmor-tables/Tables/CMIP6_grids.json'))
  tables.append(cmor.load_table('cmip6-cmor-tables/Tables/CMIP6_coordinate.json'))
  
  if os.path.exists('CMIP5/ancillary_files/grid_spec.auscom.20110618.nc'):
    xfh=netCDF4.Dataset('CMIP5/ancillary_files/grid_spec.auscom.20110618.nc')
  elif os.path.exists('/home/mon137/cafepp/cafepp/CMIP5/ancillary_files/grid_spec.auscom.20110618.nc'):
    xfh=netCDF4.Dataset('/home/mon137/cafepp/cafepp/CMIP5/ancillary_files/grid_spec.auscom.20110618.nc')
  else:
    xfh=netCDF4.Dataset('/g/data/p66/mac599/CMIP5/ancillary_files/grid_spec.auscom.20110618.nc')
  if(area_t):
     area_t=xfh.variables['area_T'] #check ok
     ds_02_22_T=xfh.variables['ds_02_22_T'] #northward T-cell edge width (m)
  if(area_u):
     area_u=xfh.variables['area_C'] #check ok
  
  #print(ybeg,yend)
  
  if(ybeg<ybeg_min or ybeg>yend_max or yend<ybeg_min or yend>yend_max):
    raise SystemExit('Problem with ybeg/yend ybeg_min/yend_max.')
  
  cmor.set_table(tables[1]) #grids
  
  refString='days since 0001-01-01'
  
  #print(ProcessFileList)
  
  if(ProcessFileTxtTF):
    print('Try')
    with open(ProcessFileTxt) as ProcessFileTxtFH:
      input_files = ProcessFileTxtFH.readlines()
  # you may also want to remove whitespace characters like `\n` at the end of each line
    #input_files = [x.strip() for x in input_files] 
    input_files = [x.strip().replace('REALM',realm) for x in input_files] 
    print(input_files)
    #print(input_files.replace('REALM',realm))
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  #will need to come up with a system for naming the OUTPUT file...
  
  if(ProcessFileList):
    print('idir=',idir)
    input_files=sorted(glob.glob(idir+'/'+realm+'_daily_????_??_01.nc'))
  #  input_files=input_files[0:2] #limit number for testing purposes...
    print(input_files)
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    #print(len(input_files))
  
  if(ProcessFileList or ProcessFileTxtTF):
    input_fhsN=netCDF4.MFDataset(input_files)
    input_fhs0=netCDF4.Dataset(input_files[0])
  
    #j=input_fhs0.variables['time'].ncattrs() #working 
    #j=input_fhs0.variables['time'].getncattr('units') 
    #print('j=',j)
  
  #might need to have calendar resourced here too.
    refString=input_fhs0.variables['time'].getncattr('units')
  
    #print('input_files=',input_files)
    #print(input_fhsN)
  
    #j=input_fhsN.variables['time'][:]
    #print(j)
  
    tavg=np.array(input_fhsN.variables['time'][:]) #had to put [:] on end now, change.
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
    tval_bounds=np.array(input_fhsN.variables['time_bounds'][:])
  
    print(tavg)
    print(tavg[:].size)
    print(tavg[:])
  
    timestamp_avg_beg=netCDF4.num2date(tavg[0],units=refString,calendar=calendar)
    timestamp_avg_end=netCDF4.num2date(tavg[-1],units=refString,calendar=calendar)
  
    #print(timestamp_avg_beg)
    #print(timestamp_avg_end)
    #print(timestamp_avg_end.year)
  
    print('Overwriting original output file name.')
  
    odir=create_odirs(ovars,institution_id,source_id,experiment_id,ripf,table,grid_label,version)
  
    ofil,ofil_modified=create_ofils(season,table,ovars,experiment_id,source_id,ripf,grid_label,timestamp_avg_beg.year,timestamp_avg_end.year,timestamp_avg_beg.month,timestamp_avg_end.month,timestamp_avg_beg.day,timestamp_avg_end.day)
  
    for o in range(0,len(ovars)):
      print('Output CMIP6 file:',odir[o]+'/'+ofil_modified[o],file=fh_printfile)
  
    for o in range(0,len(ovars)):
      if(os.path.exists(odir[o]+'/'+ofil_modified[o]) and NoClobber):
        raise SystemExit('No Clobber set and ',odir[o]+'/'+ofil_modified[o],' exists')
  
    for o in range(0,len(ovars)):
      if(os.path.exists(odir[o]+'/'+ofil[o]) and NoClobber):
        raise SystemExit('No Clobber set and ',odir[o]+'/'+ofil_modified[o],' exists')
  
    #print(odir)
    #print(ofil)
  
    #print(tval_bounds)
  
    #print(tval_bounds[:])
    tbeg=tval_bounds[:,0]
    tend=tval_bounds[:,1]
    fh_number=np.zeros(len(input_files),dtype=np.int)
    #print(fh_number)
    #print(fc_number)
    fr_number=np.array(range(0,tavg[:].size))
    fc_number=np.array(range(0,tavg[:].size))
  
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  if(not (ProcessFileList or ProcessFileTxtTF) ):
  
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
  
        idir_extra=''
  
        ifila=realm+'_'+frequency+'_'+str('{0:04d}'.format(ynow))+'_01_01.nc'
        input_files[ynow-ybeg]=idir+idir_extra+'/'+ifila
        if not os.path.exists(idir+idir_extra+'/'+ifila):
          #print(input_files,file=fh_printfile)
          #raise SystemExit('Missing '+idir+'/'+ifila+'.')
          raise SystemExit('Missing '+idir+'/'+ifila,' in file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
          #pass
        else:
          print('input file: ',idir+'/'+ifila,file=fh_printfile)
          #input_fhs[ynow-ybeg]=netCDF4.Dataset(input_files[ynow-ybeg])
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
        else:
         days_in_month[1]=28
  
        #print('ydiff=',ydiff,file=fh_printfile)
  
        #day_range_end=day_range_beg+ndy-1
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
          if(Forecast):
            idir_extra='/'+str('{0:04d}'.format(ynow))+str('{0:02d}'.format(mnow))+str('{0:02d}'.format(1))
          else:
            idir_extra=''
          print(idir_extra)
          #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
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
              print('input file: ',idir+idir_extra+'/'+ifila,' cnt_total=',cnt_total)
            #input_fhs[cnt_total]=netCDF4.Dataset(input_files[cnt_total])
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
  
    input_fhs0=netCDF4.Dataset(input_files[0])
    #raise SystemExit('Finished O.K.')
  
    #day1=1
    #print('year,month,day=',tbeg,year_vec,month_vec,day_vec,file=fh_printfile)
  
    tavg=np.array(tavg_str)
    #print(tavg)
  
    tbeg=tavg-0.5
    tend=tavg+0.5
  
    tbeg=tavg-0.0
    tend=tavg+1.0
  
    tavg=tavg+0.5
  
    tval_bounds=np.column_stack((tbeg,tend))
  
  #end of not (ProcessFileList or ProcessFileTxtTF)
  
  timestamp_avg=netCDF4.num2date(tavg,units=refString,calendar=calendar)
  timestamp_beg=netCDF4.num2date(tbeg,units=refString,calendar=calendar)
  timestamp_end=netCDF4.num2date(tend,units=refString,calendar=calendar)
  
  ttt=len(tavg)
  #print('timestamp_avg,beg,end:',file=fh_printfile)
  for n in range(0,ttt):
    print(timestamp_avg[n],timestamp_beg[n],timestamp_end[n],file=fh_printfile)
  #print(input_files)
  
  #print('refString=',refString,file=fh_printfile)
  #print('tavg=',tavg,file=fh_printfile)
  #print('tval_bounds=',tval_bounds,file=fh_printfile)
  
  cmor.set_table(tables[0]) #cmor table
  
  time_axis_id=cmor.axis('time', units=refString, coord_vals=tavg, cell_bounds=tval_bounds)
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  #raise SystemExit('Finished O.K. abc')
  
  #print(tbeg,tend,tavg,file=fh_printfile)
  
  cmor.set_table(tables[1]) #grids
  
  #if(dvar=='tos' or dvar=='psl' or dvar=='pr' or dvar=='tas' or dvar=='huss'):
  #  levels=0
  #  nlev=1
  
  if(realm=='ocean'):
  
  #dvar=='tos'):
    cmor.set_table(tables[0]) #cmor table
  
    if(OutputVarStructure=='time_basin_depth_lat'):
      basins=np.array(['atlantic_arctic_ocean','indian_pacific_ocean','global_ocean'])
      nbasins=len(basins)
      basin_axis_id = cmor.axis(table_entry='basin', units='', length=len(basins), coord_vals=basins)
  
    zt=xfh.variables['zt']
    zb=xfh.variables['zb']
  
    if 'newlevs' in locals():
      #print(newlevs)
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
    nzt=zt.size
  
    #trial!!!!!!
    #zt=
    #print(levels)
    #ztX=zt[[0,10,20]]
    #zboundsX=zbounds[[0,10,20],:]
  
  if(realm=='ocean'):
  
    if(ReGrid):
        lat_vals=xfh.variables[lat_lon_type[0]]
        lon_vals=xfh.variables[lat_lon_type[1]]
        lat_vals2df=xfh.variables[lat_lon_type[0]][:].flatten()
        lon_vals2df=xfh.variables[lat_lon_type[1]][:].flatten()
        lon_vals2df_360=np.mod(lon_vals2df,360)
        #print(lat_vals2df.shape)
    else:
      if(OutputVarStructure=='time'):
        lat_vals=xfh.variables[lat_lon_type[0]][:,0]
        lon_vals=xfh.variables[lat_lon_type[1]][0,]
        lon_vals_360=np.mod(lon_vals,360)
      elif(OutputVarStructure=='time_basin_depth_lat'):
        lat_vals=xfh.variables['grid_y_T']
        lon_vals=xfh.variables['grid_x_C']
        lon_vals_360=np.mod(lon_vals,360)
        min_vals=np.append((1.5*lat_vals[0] - 0.5*lat_vals[1]), (lat_vals[0:-1] + lat_vals[1:])/2)
        max_vals=np.append((lat_vals[0:-1] + lat_vals[1:])/2, 1.5*lat_vals[-1] - 0.5*lat_vals[-2])
        lat_vals_bounds=np.column_stack((min_vals, max_vals))
  
        #lat_axis_id=cmor.axis(table_entry='latitude', units='degrees_north', coord_vals=lat_vals[:], cell_bounds=lat_vals_bounds)
      else:
        lat_vals=xfh.variables[lat_lon_type[0]]
        lon_vals=xfh.variables[lat_lon_type[1]]
        lon_vals_360=np.mod(lon_vals,360)
    #np.set_printoptions(threshold='nan') #will print out whole array
    #print(lon_vals_360)
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
    if(OutputVarStructure=='time_lat_lon' or OutputVarStructure=='time_depth_lat_lon' or OutputVarStructure=='time_depthreduced_lat_lon' or OutputVarStructure=='time_basin_depth_lat'):
  #new
      cmor.set_table(tables[0])
  
      if 'zt0b_new' in locals():
        #print(zt0b_new)
  
        if(len(zt0b_new)%3 != 0):
          raise SystemExit('zt0b_new error:'+__file__+' line number: '+str(inspect.stack()[0][2]))
        else:
          zt0b_newX=np.reshape(zt0b_new,(3,len(zt0b_new)/3))
  
          #XXX=np.reshape(zt0b_new,(3,5))[0,:]
  
          #print(zt0b_newX)
          zt_new=zt0b_newX[0,]
          z0_new=zt0b_newX[1,]
          zb_new=zt0b_newX[2,]
  
          #print(zt_new)
          #print(z0_new)
          #print(zb_new)
  
          #zt_new=np.array([5., 10., 20., 30.,55.])
          #z0_new=np.array([0.,  7.5,15.5,25.,40.])
          #zb_new=np.array([7.5,15.5,25., 40.,60.])
          #zbounds_new=np.column_stack((z0_new,zb_new)).flatten()
          zbounds_new=np.column_stack((z0_new,zb_new))
          #print(zbounds_new)
          #print(zbounds_new.flatten())
  
          nzt_new=zt_new.size
          z_axis_id=cmor.axis('depth_coord','m',coord_vals=zt_new[:],cell_bounds=zbounds_new[:])
          #print('hello')
      else:
          #print('there')
          print(zt)
          print(zbounds)
          z_axis_id=cmor.axis('depth_coord','m',coord_vals=zt[:],cell_bounds=zbounds[:])
  
  
      #zbounds_new=np.array([0.,6000.]) #temporary
      #print(zbounds_new)
  #dvar=='nino34'):
    #lat_vals=np.squeeze(xfh.variables[lat_lon_type[0]][:,0])
    #lon_vals=xfh.variables[lat_lon_type[1]][0,]
    #raise SystemExit('Finished O.K.')
      #print(zbounds_new)
      #z_axis_id=cmor.axis('depth_coord','m',coord_vals=zt_new[:],cell_bounds=zbounds_new[:])
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
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
  
    #print(lat_vals.size)
    #print(lon_vals_360.size)
  
    #if(not ReGrid):
    if(OutputVarStructure=='time'):
       nlats=lat_vals.size
       nlons=lon_vals_360.size
    elif(OutputVarStructure=='time_basin_depth_lat'):
       nlats=len(lat_vals)
       nlons=len(lon_vals)
    else:
       nlats=lat_vals[:,0].size
       nlons=lon_vals_360[0,].size
  
    #nlats=lat_vals.size
    #nlons=lon_vals_360.size
  
    #nlats=300
    #nlons=360
  
    #print('nlats,nlons=',nlats,nlons,file=fh_printfile)
  
    lon_vertices=np.mod(get_vertices('geolon_t'),360)
    lat_vertices=get_vertices('geolat_t')
  
    if(OutputVarStructure=='time_basin_depth_lat'):
      lat_axis_id=cmor.axis(table_entry='latitude', units='degrees_north', coord_vals=lat_vals[:], cell_bounds=lat_vals_bounds)
      #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
    elif(ReGrid):
      cmor.set_table(tables[0]) #cmor #working zg500
      #cmor.set_table(tables[2])
  
      #print(lat_vals[:])
      #print(lat_vals_bounds[:])
      #print(lat_vals.shape)
      #print(lat_vals.shape)
      #nlats_regrid=lat_vals_regrid.size
      #nlons_regrid=lon_vals_regrid.size
  
      #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
      lat_axis_id=cmor.axis(table_entry='latitude', units='degrees_north', coord_vals=lat_vals_regrid[:], cell_bounds=lat_vals_bounds_regrid)
      lon_axis_id=cmor.axis(table_entry='longitude', units='degrees_east', coord_vals=lon_vals_regrid[:], cell_bounds=lon_vals_bounds_regrid)
  
    else:
  
      cmor.set_table(tables[1]) #grids
  
      j_axis_id=cmor.axis('j_index','1',coord_vals=np.arange(nlats))
      i_axis_id=cmor.axis('i_index','1',coord_vals=np.arange(nlons))
  
      #j_axis_id=cmor.axis('j_index','1',coord_vals=np.arange(108000))
      #i_axis_id=cmor.axis('i_index','1',coord_vals=np.arange(108000))
  
      #print('j_axis_id=',j_axis_id,file=fh_printfile)
      #print('i_axis_id=',i_axis_id,file=fh_printfile)
  
      axis_ids=np.array([j_axis_id, i_axis_id])
  
      if(OutputVarStructure!='time'):
        #print(lat_vals.shape)
        #print(lon_vals.shape)
        #print(lat_vertices.shape)
        #print(lon_vertices.shape)
        grid_id=cmor.grid(axis_ids=axis_ids, latitude=lat_vals[:], longitude=lon_vals_360[:], latitude_vertices=lat_vertices[:], longitude_vertices=lon_vertices[:])
  
  elif(realm=='atmos' and (OutputVarStructure=='time_lat_lon' or OutputVarStructure=='time_plev_lat_lon' or OutputVarStructure=='time_reducedplev_lat_lon')):
  #dvar=='psl' or dvar=='pr' or dvar=='tas' or dvar=='huss' or dvar=='zg' or dvar=='hfss' or dvar=='rlut' or dvar=='sfcWind' or dvar=='tslsi' or dvar=='hfls' or dvar=='uas' or dvar=='vas' or dvar=='ua' or dvar=='va' or dvar=='ta' or dvar =='hus' or dvar=='zg500' or dvar=='zg700' or dvar=='ta10' or dvar=='zg10' or dvar=='ua10' or dvar=='va10' or dvar=='ta5' or dvar=='ua5' or dvar=='va5' or dvar=='zg5' or dvar=='hus5' or dvar=='rws5'):
  
  #  if(ReGrid):
  #    lat_vals = outgrid.getLatitude()
  #    lon_vals = outgrid.getLongitude()
  #  else:
  #    if(dvar=='nino34'):
  #      #lat_vals=input_fhs0.variables['yt_ocean']
  #      #lon_vals=input_fhs0.variables['xt_ocean']
  #      levels=0
  #      nlev=1
  #    else:
    lat_vals=input_fhs0.variables['lat']
    lon_vals=input_fhs0.variables['lon']
  
    nlats=lat_vals.shape[0] #check this
    nlons=lon_vals.shape[0] #check this
  
    #thickness=np.tile( thickness ,(1,nlats,nlons))
  
    lat_vals2df=np.tile( np.expand_dims(lat_vals,1), (1,nlons)).flatten()
    lon_vals2df=np.tile( np.expand_dims(lon_vals,0), (nlats,1)).flatten()
  
    #print(lat_vals2df.shape)
    #print(lon_vals2df.shape)
  
    #print(nlats)
  
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
    min_vals=np.append((1.5*lat_vals[0] - 0.5*lat_vals[1]), (lat_vals[0:-1] + lat_vals[1:])/2)
    max_vals=np.append((lat_vals[0:-1] + lat_vals[1:])/2, 1.5*lat_vals[-1] - 0.5*lat_vals[-2])
    lat_vals_bounds=np.column_stack((min_vals, max_vals))
  
    min_vals=np.append((1.5*lon_vals[0] - 0.5*lon_vals[1]), (lon_vals[0:-1] + lon_vals[1:])/2)
    max_vals=np.append((lon_vals[0:-1] + lon_vals[1:])/2, 1.5*lon_vals[-1] - 0.5*lon_vals[-2])
    lon_vals_bounds=np.column_stack((min_vals, max_vals))
  
  #if(realm=='atmos' and (OutputVarStructure=='time_lat_lon' or OutputVarStructure=='time_plev_lat_lon')):
  if(realm=='atmos' and (OutputVarStructure=='time_plev_lat_lon')):
  #dvar=='zg' or dvar=='ua' or dvar=='va' or dvar=='ta' or dvar =='hus' or dvar=='zg700'):
    zt=input_fhs0.variables[plev_type][:]*100.0
    #if(dvar=='zg'):
    #  zt=input_fhs0.variables['phalf'][:]*100.0
    #else:
    #  zt=input_fhs0.variables['pfull'][:]*100.0
  
    min_vals=np.append((1.5*zt[0] - 0.5*zt[1]), (zt[0:-1] + zt[1:])/2)
    max_vals=np.append((zt[0:-1] + zt[1:])/2, (1.5*zt[-1] - 0.5*zt[-2]))
    zbounds =np.column_stack((min_vals, max_vals))
    zbounds=np.where(zbounds<0.0,0.0,zbounds)
  
    cmor.set_table(tables[2]) #working zg
    cmor.set_table(tables[0]) #cmor
  
    #print(zt)
    #print(plev_type)
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
    if(plev_type=='phalf'):
    #if(dvar=='zg'):
      z_axis_id=cmor.axis('plev25','Pa',coord_vals=zt[:])
    else:
      z_axis_id=cmor.axis('plev24','Pa',coord_vals=zt[:])
  
  if(realm=='atmos' and OutputVarStructure=='time_reducedplev_lat_lon'):
  #dvar=='ta5' or dvar=='zg5' or dvar=='ua5' or dvar=='va5' or dvar=='hus5' or dvar=='hur5' or dvar=='rws5'):
    zt=input_fhs0.variables[plev_type][:]*100.0
    #if(dvar=='zg5'):
    #  zt=input_fhs0.variables['phalf'][:]*100.0
    #else:
    #  zt=input_fhs0.variables['pfull'][:]*100.0
    #print('zt=',zt,file=fh_printfile)
  
    newlevs=np.array([30000., 50000., 70000., 85000., 92500.])
  
    cmor.set_table(tables[0]) #cmor
    z_axis_id=cmor.axis('plev5','Pa',coord_vals=newlevs[:])
  
  if(realm=='atmos' and (OutputVarStructure=='time_lat_lon' or OutputVarStructure=='time_plev_lat_lon' or OutputVarStructure=='time_reducedplev_lat_lon')):
  #dvar=='psl' or dvar=='pr' or dvar=='tas' or dvar=='huss' or dvar=='zg' or dvar=='hfss' or dvar=='rlut' or dvar=='sfcWind' or dvar=='tslsi' or dvar=='hfls' or dvar=='uas' or dvar=='vas' or dvar=='ua' or dvar=='va' or dvar=='ta' or dvar =='hus'  or dvar=='ta5' or dvar=='ua5' or dvar=='va5' or dvar=='zg5' or dvar=='hus5'or dvar=='zg500' or dvar=='zg700' or dvar=='rws5'):
    #print('lat_vals.shape=',lat_vals.shape,file=fh_printfile)
    #print('lon_vals.shape=',lon_vals.shape,file=fh_printfile)
  
    #print('lat_vals_bounds.shape=',lat_vals_bounds.shape,file=fh_printfile)
    #print('lon_vals_bounds.shape=',lon_vals_bounds.shape,file=fh_printfile)
    lat_vals_bounds=np.where(lat_vals_bounds>90.0,90.0,lat_vals_bounds)
    lat_vals_bounds=np.where(lat_vals_bounds<-90.0,-90.0,lat_vals_bounds)
  
    #print('max=',np.max(lat_vals_bounds),file=fh_printfile)
    #print('min=',np.min(lat_vals_bounds),file=fh_printfile)
  
    if(OutputVarStructure=='time_plev_lat_lon' or OutputVarStructure=='time_reducedplev_lat_lon'): nzt=zt.size
    nlats=lat_vals.shape[0] #check this
    nlons=lon_vals.shape[0] #check this, should it be 1?
  
    #print(nlats,nlons)
  
    cmor.set_table(tables[0]) #cmor #working zg500
    #cmor.set_table(tables[2])
  
    if(ReGrid):
      lat_axis_id=cmor.axis(table_entry='latitude', units='degrees_north', coord_vals=lat_vals_regrid[:], cell_bounds=lat_vals_bounds_regrid)
      lon_axis_id=cmor.axis(table_entry='longitude', units='degrees_east', coord_vals=lon_vals_regrid[:], cell_bounds=lon_vals_bounds_regrid)
    else:
      lat_axis_id=cmor.axis(table_entry='latitude', units='degrees_north', coord_vals=lat_vals[:], cell_bounds=lat_vals_bounds)
      lon_axis_id=cmor.axis(table_entry='longitude', units='degrees_east', coord_vals=lon_vals[:], cell_bounds=lon_vals_bounds)
  
  cmor.set_table(tables[0]) #cmor #working
  
  if not 'positive' in locals() and positive!='None':
    positive=None
  
  data_id=[]
  if(realm=='ocean' and OutputVarStructure=='time_basin_depth_lat'):
    axis_ids=np.array([time_axis_id, basin_axis_id, z_axis_id, lat_axis_id])
    data_id.append(cmor.variable(dvar[0], ounits, axis_ids=axis_ids, missing_value=-1e20,comment=comment))
  
  elif(realm=='ocean' and OutputVarStructure=='time_lat_lon'):
    if(ReGrid):
      axis_ids=[time_axis_id,lat_axis_id,lon_axis_id] #working zg500
    else:
      axis_ids=[time_axis_id,grid_id] #working
    data_id.append(cmor.variable(dvar[0], ounits, axis_ids=axis_ids, missing_value=-1e20,comment=comment))
  
  elif(realm=='ocean' and OutputVarStructure=='time_depth_lat_lon'):
    if(ReGrid):
      axis_ids=np.array([time_axis_id,z_axis_id,lat_axis_id,lon_axis_id])
    else:
      #print('aaa')
      axis_ids=[time_axis_id,grid_id]
      axis_ids=[0,1,-100]
      axis_ids=[time_axis_id,z_axis_id,grid_id] #try
      #axis_ids=[0,-100] #try
    #print('time_axis_id,z_axis_id,grid_id=',time_axis_id,z_axis_id,grid_id)
    #print('dvar[0]=',dvar[0])
    #comment=None
    data_id.append(cmor.variable(dvar[0], ounits, axis_ids=axis_ids, missing_value=-1e20, comment=comment))
  
  elif(OutputVarStructure=='time'):
  #dvar=='nino34'):
    axis_ids=[0] #working
    #data_id=cmor.variable(dvar, ounits,  missing_value=-1e20)
    data_id.append(cmor.variable(dvar[0], ounits, axis_ids=axis_ids, missing_value=-1e20, comment=comment))
  #elif(dvar=='tos'):
  #  axis_ids=[time_axis_id,grid_id] #working
  #  data_id.append(cmor.variable(dvar, ounits, axis_ids=axis_ids, missing_value=-1e20))
  
  elif(realm=='atmos' and (OutputVarStructure=='time_plev_lat_lon' or OutputVarStructure=='time_reducedplev_lat_lon')):
  
    axis_ids=np.array([time_axis_id,z_axis_id,lat_axis_id,lon_axis_id])
  
  #  for o in range(0,len(ovars)):
  #    print(type(ounits))
  #    print(ounits[o])
  #    data_id.append(cmor.variable(ovars[o], ounits[o], axis_ids=axis_ids, missing_value=-1e20))
    #print(ovars[:])
    #print(ounits)
    data_id.append(cmor.variable(ovars[0], ounits, axis_ids=axis_ids, missing_value=-1e20, comment=comment))
  
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  elif(realm=='atmos' and OutputVarStructure=='time_lat_lon'):
  #dvar=='psl' or dvar=='pr' or dvar=='tas' or dvar=='huss' or dvar=='hfss' or dvar=='rlut' or dvar=='sfcWind' or dvar=='tslsi' or dvar=='hfls' or dvar=='uas' or dvar=='vas' or dvar=='zg500' or dvar=='zg700'):
    #print('xxx')
    #print(positive)
    axis_ids=[time_axis_id,lat_axis_id,lon_axis_id] #working zg500
    #print('positive=',positive)
    #positive=None
    #if(positive==None):
    #  data_id.append(cmor.variable(dvar[0], ounits, axis_ids=axis_ids, missing_value=-1e20,comment=comment))
    #else:
    data_id.append(cmor.variable(dvar[0], ounits, axis_ids=axis_ids, missing_value=-1e20,positive=positive,comment=comment))
    #print('axis_ids=',axis_ids,file=fh_printfile)
    #if(dvar=='hfss' or dvar=='tauu' or dvar=='tauv' or dvar=='rlut' or dvar=='hfls'):
    #  positive='up'
    #else:
    #  positive=None
  #  if(dvar=='hfls'):
  #    data_id.append(cmor.variable(dvar, ounits, axis_ids=axis_ids, missing_value=-1e20,positive=positive,comment='Converted from evap using 28.9, assuming latent heat of vaporization of 2.5 MJ/kg'))
  #  if(dvar=='zg700'):
  #    data_id.append(cmor.variable(dvar, ounits, axis_ids=axis_ids, missing_value=-1e20,positive=positive,comment='Note that level extracted is 691.673132hPa, approximately 700hPa'))
  #  else:
  #    data_id.append(cmor.variable(dvar[0], ounits, axis_ids=axis_ids, missing_value=-1e20,positive=positive))
  #elif(dvar=='zg' or dvar=='ua' or dvar=='va' or dvar =='hus' or dvar=='ta' or dvar=='ta5' or dvar=='ua5' or dvar=='va5' or dvar=='zg5' or dvar=='hus5' or dvar=='rws5'):
  #  axis_ids=np.array([time_axis_id,z_axis_id,lat_axis_id,lon_axis_id])
  #  for o in range(0,len(ovars)):
  #    data_id.append(cmor.variable(ovars[o], ounits[o], axis_ids=axis_ids, missing_value=-1e20))
  
  print(input_files)
  #print(fh_number)
  
  if(ReGrid):
    #print('nlats=',nlats)
    #print('nlats_regrid=',nlats_regrid)
    #if(realm=='ocean'):
    #N_in=nlats_nlons
    #elif(realm=='atmos'):
    N_in=nlats*nlons
    N_out=nlats_regrid*nlons_regrid
  
    #print('N_in,N_out=',N_in,N_out)
  
    col = ifh_wgt['col'][:] - 1  # Python starts with 0
    row = ifh_wgt['row'][:] - 1
    S = ifh_wgt['S']
    A = sps.coo_matrix((S, (row, col)), shape=[N_out, N_in])
  
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
    #print(lat_vals_bounds[:])
    #np.set_printoptions(threshold='nan') #will print out whole array
    #print(S[:])
    #print(S.shape) 
  
  #data=np.zeros((300,360),dtype='f')
  ntimes_passed=1
  for icnt in range(0,len(tavg)):
    #print('len(tavg)=',len(tavg),'icnt=',icnt)
  
    if(not (ProcessFileList or ProcessFileTxtTF) ):
      input_fhsN=netCDF4.Dataset(input_files[fh_number[icnt]])
  
    if 'dummy_shape' in locals():
      var_size=dummy_shape
      var_dims=dummy_dimensions
    #develop system whereby if inputs are missing then dummy values are created of the corect dimensionality so that functions can be tested.
      #print(dummy_shape)
      #print(dummy_dimensions)
      #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    else:
  
      try:
        var_size=input_fhsN.variables[inputs[0]].shape
      except KeyError:
        var_size=input_fhsN.variables[inputs_alternative[0]].shape
      #except NameError:
      #  print('aaa')
  
      #print('fr_number=',fr_number)
      #print('fh_number=',fh_number)
      #print('fc_number=',fc_number)
  
      try:
        var_size=input_fhs0.variables[inputs[0]].shape
        var_dims=input_fhs0.variables[inputs[0]].dimensions
      except KeyError:
        var_size=input_fhs0.variables[inputs_alternative[0]].shape
        var_dims=input_fhs0.variables[inputs_alternative[0]].dimensions
      nvar_dims=len(var_dims)
      #print('var_size=',var_size)
      #print(type(var_size))
  
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
    #print('icnt=',icnt,' input_fhs[]=',input_fhs[fh_number[icnt]],' tbeg[]=',tbeg[icnt],' tend[]=',tend[icnt],file=fh_printfile)
    #print('icnt=',icnt,' input_fhsN=',input_fhsN,' tbeg[]=',tbeg[icnt],' tend[]=',tend[icnt],file=fh_printfile)
  
    if(output_type=='diagnostic'):
  
      if 'dummy_shape' in locals():
        #print(dummy_shape)
        data=np.zeros(dummy_shape)
        if(len(inputs)==2):
          data2=np.zeros(dummy_shape)
        #print('data.shape=',data.shape)
        #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
      else:
  
      #print(len(inputs))
        try:
          data=np.expand_dims(input_fhsN.variables[inputs[0]][fr_number[icnt],], axis=0)
        except KeyError:
          data=np.expand_dims(input_fhsN.variables[inputs_alternative[0]][fr_number[icnt],], axis=0)
  
        if(len(inputs)==2):
          try:
            data2=np.expand_dims(input_fhsN.variables[inputs[1]][fr_number[icnt],], axis=0)
          except KeyError:
            data2=np.expand_dims(input_fhsN.variables[inputs_alternative[1]][fr_number[icnt],], axis=0)
  
      if(define_basin_mask and icnt==0): #only need to define the masks once...
        atlantic_arctic_mask,indoPac_mask,global_mask=make_mask3D(data+data2,nbasins,nzb,nlats)
  
      #print(data.shape)
      #print(atlantic_arctic_mask.shape)
      #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  #need to consider order. now we interpolate 3d to new grid then diagnose a quantity. Might be better to diagnose quantity then interpolate reduced quantity.
  
      #if(ReGrid):
      #  #if(OutputVarStructure=='time_depth_lat_lon' or OutputVarStructure=='time_lat_lon'):
      #  if(OutputVarStructure=='time_depth_lat_lon'):
      #    #print(nzt,nlats,nlons)
      #    #print(nzt_new)
      #    #if 'zt0b_new' in locals(): nzt=nzt_new
      #    newdata = np.zeros((1,nzt,nlats_regrid,nlons_regrid),dtype='f')
      #    #print(newdata.shape)
      #    #print(lat_vals2df.shape)
      #    #print(lon_vals2df_360.shape)
      #    #print(lat_vals.shape)
      #    #print(lon_vals.shape)
      #    #for zlevel in range(0,4): #temporary
      #    for zlevel in range(0,nzt):
      #      #print(z)
      #      newdata[0,zlevel,:] = griddata(lon_vals2df_360, lat_vals2df, ma.filled(data[0,zlevel,:].flatten(),np.nan), lon_vals_regrid, lat_vals_regrid, interp='linear')
      #    data=ma.masked_equal(newdata,np.nan)
      #    #print(data[:])
      #  #else:
      #  #  print(lat_vals2df.shape)
      #  #  print(lon_vals2df_360.shape)
      #  #  print(data.shape)
      #  #  data = griddata(lon_vals2df_360, lat_vals2df, ma.filled(data.flatten(),np.nan), lon_vals_regrid, lat_vals_regrid, interp='linear')
      #print('before call',data.shape) 
  
      #print('hello')
      diagnostic_args=(eval(diagnostic_args_string))
      function_name='diag_'+diagnostic_function_name
  
      if(len(inputs)==2):
        data=eval(function_name)(data,data2,*diagnostic_args)
      else:
        data=eval(function_name)(data,*diagnostic_args)
      #print('data.shape=',data.shape)
      #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
      if(ReGrid):
        #print('*******')
        #print(OutputVarStructure)
        #j=ma.filled(data.flatten(),np.nan)
        #np.set_printoptions(threshold='nan') #will print out whole array
        #print(ma.masked_equal(data,1e20).flatten())
        #print(data)
        #data=ma.masked_equal(data,-1e20)
        #data = griddata(lon_vals2df_360, lat_vals2df, ma.masked_equal(data,1e20).flatten(), lon_vals_regrid, lat_vals_regrid, interp='linear') #matplotlib version
        #print(j.shape)
        #print(latlon_points.shape)
        #https://docs.scipy.org/doc/scipy-0.16.0/reference/generated/scipy.interpolate.griddata.html
        #data = griddata(latlon_points, ma.masked_equal(data,1e20).flatten(), (lon_vals_regrid, lat_vals_regrid), method='linear') #scipy version
  
        #if 'poisson_fill' in interp_fill_options:
        #else:
  
        data=ma.masked_equal(data,1e20)
  
        if(OutputVarStructure=='time_lat_lon'):
          #print('aaaaaaaaaaaaaaa')
          if 'griddata_scipy' in interp_fill_options:
            data = griddata(lon_vals2df_360, lat_vals2df, data.flatten(), lon_vals_regrid, lat_vals_regrid, interp='linear') #matplotlib version
            data=np.expand_dims(data,0)
            #print(data.shape)
            #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
          if 'poisson_fill' in interp_fill_options:
            data,converged=poisson_fill(data,2,1,eps=1e-4, relax=0.6, itermax=1e4, initzonal=False, cyclic=True, verbose=True)
          if 'dot_weighting_regrid' in interp_fill_options:
            data=A.dot(data.reshape(-1, nlats*nlons).T).T.reshape([nlats_regrid,nlons_regrid])
            data=np.expand_dims(data,0)
          if 'apply_ls_mask_regrid' in interp_fill_options:
            data=data*ls_mask_regrid
        elif(OutputVarStructure=='time_depth_lat_lon' or OutputVarStructure=='time_plev_lat_lon'): #change to other int methods later...
          #print('nzt=',nzt)
          newdata = np.zeros((1,nzt,nlats_regrid,nlons_regrid),dtype='f')
          for zlevel in range(0,nzt):
          #for zlevel in range(0,4):
            #print(zlevel)
            newdata[0,zlevel,:] = griddata(lon_vals2df_360, lat_vals2df, ma.filled(data[zlevel,:].flatten(),np.nan), lon_vals_regrid, lat_vals_regrid, interp='linear')
          data=newdata
          #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
          #print(data.shape)
        #shade_2d_simple(data[0,])
        #shade_2d_latlon(data[0,],lat_vals_regrid,lon_vals_regrid,[-3,0,3,6,9,12,15,18,21,24])
  
    elif(output_type=='broadcast'):
      #print('hello')
      #print(len(inputs))
      if(len(inputs)==1):
        try:
          data=input_fhsN.variables[inputs[0]][fr_number[icnt],]
        except KeyError:
          data=input_fhsN.variables[inputs_alternative[0]][fr_number[icnt],]
      elif(len(inputs)==2):
        try:
          data1=input_fhsN.variables[inputs[0]][fr_number[icnt],]
          data2=input_fhsN.variables[inputs[1]][fr_number[icnt],]
        except KeyError:
          data1=input_fhsN.variables[inputs_alternative[0]][fr_number[icnt],]
          data2=input_fhsN.variables[inputs_alternative[1]][fr_number[icnt],]
  
      #print(data.shape)
      #print(lon_vals2df.shape)
      #print(lat_vals2df.shape)
      #print(lon_vals.shape)
      #print(lat_vals.shape)
      #print(data[:])
      #print(data.type)
      #np.set_printoptions(threshold='nan') #will print out whole array
      #data = data.filled(np.nan)
      #print(data.flatten().view)
      #j=data.flatten()
      #k=ma.filled(j,np.nan)
      #print(k[:])
      #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
      #data=ma.masked_equal(data,-1e20)
      #ddd=data.flatten()
      #print(ddd)
      #print(ddd.type)
  
      if(realm=='ocean' and ReGrid):
        if(OutputVarStructure=='time_depth_lat_lon'):
          #print(data.shape)
          #print(nlats)
          #print(nzt)
          newdata = np.zeros((nzt,nlats,nlons),dtype='f')
          #for zlevel in range(0,4): #temporary
          for zlevel in range(0,nzt):
            #print(zlevel)
            newdata[zlevel,:] = griddata(lon_vals2df_360, lat_vals2df, ma.filled(data[zlevel,:].flatten(),np.nan), lon_vals_regrid, lat_vals_regrid, interp='linear')
          data=newdata
          #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
        else:
          data=np.expand_dims(data,0)
          data=ma.masked_less(data,-1e19)
          #ls_mask_regrid.set_fill_value(1e20)
          #print(data.view)
          #data=np.expand_dims(ma.masked_less(data,-1e19),0)
          #print(data[:])
          #print(data.shape)
          #print(type(data))
          if 'griddata_scipy' in interp_fill_options:
            data = griddata(lon_vals2df_360, lat_vals2df, ma.filled(data.flatten(),np.nan), lon_vals_regrid, lat_vals_regrid, interp='linear')
            #print(data.shape)
            #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
            data=np.expand_dims(data,0)
          if 'poisson_fill' in interp_fill_options:
            data,converged=poisson_fill(data,2,1,eps=1e-4, relax=0.6, itermax=1e4, initzonal=False, cyclic=True, verbose=True)
          if 'dot_weighting_regrid' in interp_fill_options:
            data=A.dot(data.reshape(-1, nlats*nlons).T).T.reshape([nlats_regrid,nlons_regrid]) * ls_mask_regrid
            data=np.expand_dims(data,0)
          if 'apply_ls_mask_regrid' in interp_fill_options:
            data=data*ls_mask_regrid
  
          #print(ls_mask_regrid)
          #print(data.view)
          #print(type(data))
  
      if(realm=='atmos' and ReGrid):
        if(OutputVarStructure=='time_plev_lat_lon'):
          #print('pass')
          #print(data.shape)
          #print(lat_vals2df.shape)
          #print(lat_vals.shape)
  #regrid
          newdata = np.zeros((nzt,nlats_regrid,nlons_regrid),dtype='f')
          #for zlevel in range(0,4): #temporary
          for zlevel in range(0,nzt):
            print(zlevel)
            newdata[zlevel,:] = griddata(lon_vals2df, lat_vals2df, ma.filled(data[zlevel,:].flatten(),np.nan), lon_vals_regrid, lat_vals_regrid, interp='linear')
          data=newdata
        else:
          pass
          #print(data.shape)
          #print(lat_vals2df.shape)
          #print(lat_vals.shape)
  
          if 'griddata_scipy' in interp_fill_options:
            data = griddata(lon_vals2df, lat_vals2df, ma.filled(data.flatten(),np.nan), lon_vals_regrid, lat_vals_regrid, interp='linear')
          if 'dot_weighting_regrid' in interp_fill_options:
            data=A.dot(data.reshape(-1, nlats*nlons).T).T.reshape([nlats_regrid,nlons_regrid])
            data=np.expand_dims(data,0)
          #print(data.shape)
          if 'apply_ls_mask_regrid' in interp_fill_options:
            data=data*ls_mask_regrid
          #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
      #print(data.view)
      #print(data.shape)
      #data=np.zeros((1,90,180),dtype='f')
      #print(data1.shape)
      #print(data2.shape)
      #print(zt.shape)
      #np.squeeze
      #print('vertical_interpolation_method=',vertical_interpolation_method)
      #print(type(vertical_interpolation_method))
      #if(vertical_interpolation_method is None):
      #  print('abc')
  
      if(realm=='atmos' and 'vertical_interpolation_method' in locals() and vertical_interpolation_method!=None):
        print('data1.shape=',data1.shape)
        print('data2.shape=',data2.shape)
        print('zt.shape=',zt.shape)
        print('newlevs.shape=',newlevs.shape)
        data=atmos_vertical_interpolate(np.expand_dims(data1,axis=0),zt,newlevs,np.expand_dims(data2,axis=0),vertical_interpolation_method)
  
    elif(OutputVarStructure=='time'):
    #dvar=='nino34'):
      data=input_fhsN.variables[inputs[0]][0,0,]
      data=np.expand_dims(data,axis=0)
      #print('data=',data)
      #print('data.shape=',data.shape)
      data=diag_nino34(data,area_t,lat_vals[:],lon_vals[:],fh_printfile)
      #print('data=',data)
      #print('data.shape=',data.shape)
  
    elif(realm=='ocean' and OutputVarStructure=='time_lat_lon'):
    #dvar=='tos'):
      #data=input_fhs[fh_number[icnt]].variables[inputs[0]][0,0,]
      #data=input_fhs[fh_number[icnt]].variables[inputs[0]][0,]
      #print(fr_number[icnt],file=fh_printfile)
  
      if(nvar_dims==4):
        try:
          data=input_fhsN.variables[inputs[0]][fr_number[icnt],levels,]
        except KeyError:
          data=input_fhsN.variables[inputs_alternative[0]][fr_number[icnt],levels,]
      else:
        try:
          data=input_fhsN.variables[inputs[0]][fr_number[icnt],]
        except KeyError:
          data=input_fhsN.variables[inputs_alternative[0]][fr_number[icnt],]
  
      #input_fhs[fh_number[icnt]].close()
      #print('data.shape=',data.shape)
  
    elif(realm=='atmos' and (OutputVarStructure=='time_lat_lon' or OutputVarStructure=='time_plev_lat_lon')):
    #dvar=='psl' or dvar=='pr' or dvar=='tas' or dvar=='huss' or dvar=='zg' or dvar=='hfss' or dvar=='rlut' or dvar=='sfcWind' or dvar=='tslsi' or dvar=='uas' or dvar=='vas' or dvar=='ua' or dvar=='va' or dvar =='hus' or dvar=='ta') or dvar=='zg500':
      data=input_fhsN.variables[inputs[0]][0,]
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
  #    data=atmos_vertical_interpolate(data1,zt,newlevs,data2,vertical_interpolation_method)
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
  #    data1a=atmos_vertical_interpolate(data1,zt,newlevs,data3,vertical_interpolation_method)
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
  
    if( (realm=='atmos' and (OutputVarStructure=='time_lat_lon' or OutputVarStructure=='time_plev_lat_lon' or OutputVarStructure=='time_reducedplev_lat_lon')) or (realm=='ocean' and (OutputVarStructure=='time_lat_lon' or OutputVarStructure=='time_depth_lat_lon' or OutputVarStructure=='time_depthreduced_lat_lon' or OutputVarStructure=='time_basin_depth_lat')) ):
    #dvar=='psl' or dvar=='pr' or dvar=='tas' or dvar=='huss' or dvar=='tos' or dvar=='zg' or dvar=='hfss' or dvar=='rlut' or dvar=='sfcWind' or dvar=='tslsi' or dvar=='hfls' or dvar=='uas' or dvar=='vas' or dvar=='ua' or dvar=='va' or dvar=='ta' or dvar =='hus' or dvar=='zg500' or dvar=='zg700' or dvar=='ta5' or dvar=='ua5' or dvar=='va5' or dvar=='zg5' or dvar=='hus5'):
      for o in range(0,len(ovars)):
        #print('a',o)
        #print('b',data.shape)
        #print('c',ntimes_passed)
        #print(tbeg[icnt],tend[icnt])
        #print(data.shape)
        cmor.write(var_id=data_id[o], data=data[:], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])
  
    if(OutputVarStructure=='time'):
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
    print('o=',o,file=fh_printfile)
    file_name.append(cmor.close(var_id=data_id[o], file_name=True))
  
  for o in range(0,len(ovars)):
    finish(file_name[o],odir[o],ofil[o],ofil_modified[o],season,fh_printfile)
  
  #raise SystemExit('Finished O.K.')
  print('Finished O.K.')
  return(0)
  
#if __name__ == "__main__":
#    main()
#end
