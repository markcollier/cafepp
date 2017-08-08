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

def usage(script_name):
    """usage"""
    print('Usage: ',script_name,' -h,help -v input_var -i importance (1-5) --ybeg=process begin year --yend=process end year --ybeg_min=min. year available --yend_max=max. year available --idir=input directory')

try:
    opts, args=getopt.getopt(sys.argv[1:], "wxdCAhv:i:rl:",["help","ybeg=","yend=","ybeg_min=","yend_max=","mbeg=","mend=","mbeg_min=","mend_max=","dbeg=","dend=","dbeg_min=","dend_max=","realisation=","initialisation=","physics=","forcings=","idir=","vertical_interpolation_method=","version=","cmorlogfile=","new_ovars=","new_units="])
except getopt.GetoptError as err:
    print(err,file=fh_printfile)
    usage(os.path.realpath(__file__))
    sys.exit(2)

fh_printfile=sys.stdout
#fh_printfile=sys.stderr

ReGrid=False
NoClobber=False
importance=5
cmorlogfile='log'
for o, a in opts:
    #print(o,file=fh_printfile)
    if o in ('-h', '--help'):
        usage(os.path.realpath(__file__))
        sys.exit()
    elif o == '-x':
        NoClobber=True
    elif o == '-i':
        importance=int(a)
    elif o == '-l':
         printfile=a
         fh_printfile=open(printfile,"w")
    elif o == '-v':
         dvar=a
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
        dbeg_min=int(a)
    elif o == '--dend_max':
        dend_max=int(a)
    elif o == '--cbeg':
        cbeg=int(a)
    elif o == '--cend':
        cend=int(a)
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
    elif o == '-r':
        ReGrid=True
    elif o == '--version':
        version=a
    elif o == '--cmorlogfile':
        cmorlogfile=a
    elif o == '--new_ovars':
        new_ovars=[str(x) for x in a.split(',')]
    elif o == '--new_units':
        new_units=[str(x) for x in a.split(',')]
    else:
        assert False, 'unhandled option'

netcdf='NETCDF4_CLASSIC'
netcdf='NETCDF3_64BIT'
netcdf='NETCDF3_CLASSIC'
netcdf='NETCDF4'

print(sys.argv,file=fh_printfile)

nmy=12

#area_u=False
#area_t=False

frequency='daily'
realm,table,inputs,units,ovars,area_t,area_u,diag_dims,grid_label,grid,vertical_interpolation_method=grab_var_meta(dvar,frequency)

if 'new_ovars' in locals():
  ovars=new_ovars

if 'new_units' in locals():
  units=new_units

#print(ovars,file=fh_printfile)
#print(units,file=fh_printfile)
#raise SystemExit('Finished O.K.')

#cdtime.DefaultCalendar=cdtime.NoLeapCalendar
#cdtime.DefaultCalendar=cdtime.GregorianCalendar
cdtime.DefaultCalendar=cdtime.JulianCalendar
cmor.setup(inpath='Tables',netcdf_file_action=cmor.CMOR_REPLACE_4,logfile=cmorlogfile)

dfp_defs='dfp_csiro-gfdl.json'
cmor.dataset_json(dfp_defs)
json_data=open(dfp_defs).read()
#pprint.pprint(json_data,width=1)
dfp_data=json.loads(json_data)
institution_id=dfp_data['institution_id']
source_id=dfp_data['source_id']
experiment_id=dfp_data['experiment_id']

cafe_experiment=os.environ.get('CAFE_EXPERIMENT')

if not 'realisation' in locals(): realisation=1
if not 'initialisation' in locals(): initialisation=1
if not 'physics' in locals(): physics=1
if not 'forcings' in locals(): forcings=1

ripf='r'+str(realisation)+'i'+str(initialisation)+'p'+str(physics)+'f'+str(forcings)

grid_label='gn'
grid='native grid'
season='None'

if(dvar=='ta5' or dvar=='ua5' or dvar=='va5' or dvar=='zg5' or dvar=='hus5' or dvar=='rws5'):
  grid_label='gn5'
  grid='3D vars use plev5, 300, 500, 700 and 850hPa'

if not 'version' in locals(): version='v'+str('{0:04d}'.format(t[0])) + str('{0:02d}'.format(t[1])) + str('{0:02d}'.format(t[2]))

odir=create_odirs(ovars,institution_id,source_id,experiment_id,ripf,table,grid_label,version)

ofil,ofil_modified=create_ofils(season,table,ovars,experiment_id,source_id,ripf,grid_label,ybeg,yend,mbeg,mend,dbeg,dend)

#raise SystemExit('Finished O.K.')

for o in range(0,len(ovars)):
  print('Output CMIP6 file:',odir[o]+'/'+ofil_modified[o],file=fh_printfile)

#raise SystemExit('Finished O.K.')

for o in range(0,len(ovars)):
  if(os.path.exists(odir[o]+'/'+ofil_modified[o]) and NoClobber):
    raise SystemExit('No Clobber set and ',odir[o]+'/'+ofil_modified[o],' exists')

for o in range(0,len(ovars)):
  if(os.path.exists(odir[o]+'/'+ofil[o]) and NoClobber):
    raise SystemExit('No Clobber set and ',odir[o]+'/'+ofil_modified[o],' exists')

cmor.set_cur_dataset_attribute('grid_label',grid_label)
cmor.set_cur_dataset_attribute('grid',grid)
cmor.set_cur_dataset_attribute('realization',realisation)
cmor.set_cur_dataset_attribute('initialization_index',initialisation)
cmor.set_cur_dataset_attribute('realization_index',realisation)
cmor.set_cur_dataset_attribute('version',version)
cmor.set_cur_dataset_attribute('calendar','julian')

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
#raise SystemExit('forced break')
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

cmor.set_table(tables[1])

refString='days since 0001-01-01'

ydiff=yend-ybeg+1

tindex=0
input_files={}
input_fhs={}

year_vec=[]
month_vec=[]
day_vec=[]

tavg_str=[]

for ynow in range(ybeg,yend+1):
  #print("y="+str(ynow),file=fh_printfile)

  days_in_month=[31,28,31,30,31,30,31,31,30,31,30,31]
  #print(days_in_month,file=fh_printfile)
  #raise SystemExit('Finished O.K.')
  if(ynow%4==0):
   #days_in_month[1]=28#noleap
   days_in_month[1]=29

  #print('ydiff=',ydiff,file=fh_printfile)
  #raise SystemExit('Finished O.K.')

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

    dbeg_now=1
    if(ynow==ybeg and mnow==mbeg):
      dbeg_now=dbeg

    dend_now=days_in_month[mnow-1]
    if(ynow==yend and mnow==mend):
      dend_now=dend

    for dnow in range(dbeg_now,dend_now+1):
      #print("ynow=",ynow," mnow=",mnow," dnow=",dnow,file=fh_printfile)
      day_vec.append(dnow)
      month_vec.append(mnow)
      year_vec.append(ynow)
      tavg_str.append(cdtime.comptime(ynow,mnow,dnow).torel(refString).value)
      ifila=realm+'_'+frequency+'_'+str('{0:04d}'.format(ynow))+'_'+str('{0:02d}'.format(mnow))+'_'+str('{0:02d}'.format(dnow))+'.nc'
      input_files[tindex]=idir+'/'+ifila
      if not os.path.exists(idir+'/'+ifila):
        #print(input_files,file=fh_printfile)
        raise SystemExit('Missing '+idir+'/'+ifila+'.')
      input_fhs[tindex]=netCDF4.Dataset(input_files[tindex])
      tindex+=1

  ind_beg=0

#print(input_files[0],file=fh_printfile)
print('input files=',input_files,file=fh_printfile)
#raise SystemExit('Finished O.K.')

#day1=1
#print("year,month,day=",tbeg,year_vec,month_vec,day_vec,file=fh_printfile)

tavg=np.array(tavg_str)
#print(tavg)

tbeg=tavg-0.5
tend=tavg+0.5

tval_bounds=np.column_stack((tbeg,tend))

#print('refString=',refString,file=fh_printfile)
#print('tavg=',tavg,file=fh_printfile)
#print('tval_bounds=',tval_bounds,file=fh_printfile)

cmor.set_table(tables[0])

time_axis_id=cmor.axis('time', units=refString, coord_vals=tavg, cell_bounds=tval_bounds)

#raise SystemExit('Finished O.K. abc')

#print(tbeg,tend,tavg,file=fh_printfile)

cmor.set_table(tables[1])

#if(dvar=='tos' or dvar=='psl' or dvar=='pr' or dvar=='tas' or dvar=='huss'):
#  levels=0
#  nlev=1

if(dvar=='tos'):
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

if(dvar=='nino34'):
  lat_vals=xfh.variables['y_T'][:,0]
  lon_vals=xfh.variables['x_T'][0,]

  #print('lat_vals=',lat_vals)
  #print('lon_vals=',lon_vals)
  #raise SystemExit('Forced exit.')
elif(dvar=='tos'):
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

  nlats=lat_vals.shape[0]
  nlons=lon_vals.shape[1]

  #print(nlats,nlons,file=fh_printfile)
  #raise SystemExit('Finished O.K.')

  cmor.set_table(tables[1])

  j_axis_id=cmor.axis('j_index','1',coord_vals=np.arange(nlats))
  i_axis_id=cmor.axis('i_index','1',coord_vals=np.arange(nlons))

  #print('j_axis_id=',j_axis_id,file=fh_printfile)
  #print('i_axis_id=',i_axis_id,file=fh_printfile)

  lon_vertices=np.mod(get_vertices('geolon_t'),360)
  lat_vertices=get_vertices('geolat_t')

  axis_ids=np.array([j_axis_id, i_axis_id])
  grid_id=cmor.grid(axis_ids=axis_ids, latitude=lat_vals[:], longitude=lon_vals_360[:], latitude_vertices=lat_vertices[:], longitude_vertices=lon_vertices[:])

elif(dvar=='psl' or dvar=='pr' or dvar=='tas' or dvar=='huss' or dvar=='zg' or dvar=='hfss' or dvar=='rlut' or dvar=='sfcWind' or dvar=='tslsi' or dvar=='hfls' or dvar=='uas' or dvar=='vas' or dvar=='ua' or dvar=='va' or dvar=='ta' or dvar =='hus' or dvar=='zg500' or dvar=='zg700' or dvar=='ta10' or dvar=='zg10' or dvar=='ua10' or dvar=='va10' or dvar=='ta5' or dvar=='ua5' or dvar=='va5' or dvar=='zg5' or dvar=='hus5' or dvar=='rws5'):

  if(ReGrid):
    lat_vals = outgrid.getLatitude()
    lon_vals = outgrid.getLongitude()
  else:
    if(dvar=='nino34'):
      #lat_vals=input_fhs[0].variables['yt_ocean']
      #lon_vals=input_fhs[0].variables['xt_ocean']
      levels=0
      nlev=1
    else:
      lat_vals=input_fhs[0].variables['lat']
      lon_vals=input_fhs[0].variables['lon']

  min_vals=np.append((1.5*lat_vals[0] - 0.5*lat_vals[1]), (lat_vals[0:-1] + lat_vals[1:])/2)
  max_vals=np.append((lat_vals[0:-1] + lat_vals[1:])/2, 1.5*lat_vals[-1] - 0.5*lat_vals[-2])
  lat_vals_bounds=np.column_stack((min_vals, max_vals))

  min_vals=np.append((1.5*lon_vals[0] - 0.5*lon_vals[1]), (lon_vals[0:-1] + lon_vals[1:])/2)
  max_vals=np.append((lon_vals[0:-1] + lon_vals[1:])/2, 1.5*lon_vals[-1] - 0.5*lon_vals[-2])
  lon_vals_bounds=np.column_stack((min_vals, max_vals))

if(dvar=='zg' or dvar=='ua' or dvar=='va' or dvar=='ta' or dvar =='hus' or dvar=='zg700'):
  if(dvar=='zg'):
    zt=input_fhs[0].variables['phalf'][:]*100.0
  else:
    zt=input_fhs[0].variables['pfull'][:]*100.0
  min_vals=np.append((1.5*zt[0] - 0.5*zt[1]), (zt[0:-1] + zt[1:])/2)
  max_vals=np.append((zt[0:-1] + zt[1:])/2, (1.5*zt[-1] - 0.5*zt[-2]))
  zbounds =np.column_stack((min_vals, max_vals))
  zbounds=np.where(zbounds<0.0,0.0,zbounds)

  cmor.set_table(tables[2]) #working zg
  cmor.set_table(tables[0])

  if(dvar=='zg'):
    z_axis_id=cmor.axis('plev25','Pa',coord_vals=zt[:])
  else:
    z_axis_id=cmor.axis('plev24','Pa',coord_vals=zt[:])

if(dvar=='ta5' or dvar=='zg5' or dvar=='ua5' or dvar=='va5' or dvar=='hus5' or dvar=='hur5' or dvar=='rws5'):
  if(dvar=='zg5'):
    zt=input_fhs[0].variables['phalf'][:]*100.0
  else:
    zt=input_fhs[0].variables['pfull'][:]*100.0
  #print('zt=',zt,file=fh_printfile)

  newlevs=np.array([30000., 50000., 70000., 85000., 92500.])

  cmor.set_table(tables[0])
  z_axis_id=cmor.axis('plev5','Pa',coord_vals=newlevs[:])

if(dvar=='psl' or dvar=='pr' or dvar=='tas' or dvar=='huss' or dvar=='zg' or dvar=='hfss' or dvar=='rlut' or dvar=='sfcWind' or dvar=='tslsi' or dvar=='hfls' or dvar=='uas' or dvar=='vas' or dvar=='ua' or dvar=='va' or dvar=='ta' or dvar =='hus'  or dvar=='ta5' or dvar=='ua5' or dvar=='va5' or dvar=='zg5' or dvar=='hus5'or dvar=='zg500' or dvar=='zg700' or dvar=='rws5'):
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

cmor.set_table(tables[0]) #working

data_id=[]
if(dvar=='nino34'):
  axis_ids=[0] #working
  #data_id=cmor.variable(dvar, units,  missing_value=-1e20)
  data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20))
elif(dvar=='tos'):
  axis_ids=[time_axis_id,grid_id] #working
  data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20))
elif(dvar=='psl' or dvar=='pr' or dvar=='tas' or dvar=='huss' or dvar=='hfss' or dvar=='rlut' or dvar=='sfcWind' or dvar=='tslsi' or dvar=='hfls' or dvar=='uas' or dvar=='vas' or dvar=='zg500' or dvar=='zg700'):
  axis_ids=[time_axis_id,lat_axis_id,lon_axis_id] #working zg500
  #print('axis_ids=',axis_ids,file=fh_printfile)
  if(dvar=='hfss' or dvar=='tauu' or dvar=='tauv' or dvar=='rlut' or dvar=='hfls'):
    positive="up"
  else:
    positive=None
  if(dvar=='hfls'):
    data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20,positive=positive,comment='Converted from evap using 28.9, assuming latent heat of vaporization of 2.5 MJ/kg'))
  if(dvar=='zg700'):
    data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20,positive=positive,comment='Note that level extracted is 691.673132hPa, approximately 700hPa'))
  else:
    data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20,positive=positive))
elif(dvar=='zg' or dvar=='ua' or dvar=='va' or dvar =='hus' or dvar=='ta' or dvar=='ta5' or dvar=='ua5' or dvar=='va5' or dvar=='zg5' or dvar=='hus5' or dvar=='rws5'):
  axis_ids=np.array([time_axis_id,z_axis_id,lat_axis_id,lon_axis_id])
  for o in range(0,len(ovars)):
    data_id.append(cmor.variable(ovars[o], units[o], axis_ids=axis_ids, missing_value=-1e20))

#data=np.zeros((300,360),dtype='f')
ntimes_passed=1
for icnt in range(0,len(tavg)):

  print('icnt=',icnt,' input_fhs[]=',input_fhs[icnt],' tbeg[]=',tbeg[icnt],' tend[]=',tend[icnt],file=fh_printfile)

  #float temp(time, st_ocean, yt_ocean, xt_ocean) ;
  if(dvar=='nino34'):
    data=input_fhs[icnt].variables[inputs[0]][0,0,]
    data=np.expand_dims(data,axis=0)
    #print('data=',data)
    #print('data.shape=',data.shape)
    data=diag_nino34(data,area_t,lat_vals[:],lon_vals[:],fh_printfile)
    #print('data=',data)
    #print('data.shape=',data.shape)
    #raise SystemExit('forced break')


  elif(dvar=='tos'):
    data=input_fhs[icnt].variables[inputs[0]][0,0,]
  elif(dvar=='psl' or dvar=='pr' or dvar=='tas' or dvar=='huss' or dvar=='zg' or dvar=='hfss' or dvar=='rlut' or dvar=='sfcWind' or dvar=='tslsi' or dvar=='uas' or dvar=='vas' or dvar=='ua' or dvar=='va' or dvar =='hus' or dvar=='ta') or dvar=='zg500':
    data=input_fhs[icnt].variables[inputs[0]][0,]
  elif(dvar=='hfls'):
    data=input_fhs[icnt].variables[inputs[0]][0,]
    data=data/28.9 #assuming latent heat of vaporization of 2.5 MJ/kg
    cmor.set_cur_dataset_attribute('comment','abc')
    #see document ~sjj554/CMIP5/scripts/Variable_examples/RUN_post_processor_atmos_monthly_2D_E1.bash.variable_hfls.table_CMIP5_Amon
  elif(dvar=='zg700'):
    data=input_fhs[icnt].variables[inputs[0]][0,12]
  elif(dvar=='ta5' or dvar=='zg5' or dvar=='ua5' or dvar=='va5' or dvar=='hus5'):
    data1=input_fhs[icnt].variables[inputs[0]][0,]
    data2=input_fhs[icnt].variables[inputs[1]][0,]
    #print(data.shape,file=fh_printfile)
    #raise SystemExit('forced break')
    data=vertical_interpolate(data1,zt,newlevs,data2,vertical_interpolation_method)
    del data1,data2

  elif(dvar=='rws5'):
    data1=input_fhs[icnt].variables[inputs[0]][0,]#ucomp
    data2=input_fhs[icnt].variables[inputs[1]][0,]#vcomp
    data3=input_fhs[icnt].variables[inputs[2]][0,]#ps

    data1=np.expand_dims(data1,axis=0)
    data2=np.expand_dims(data2,axis=0)
    data3=np.expand_dims(data3,axis=0)

    print('data1.shape=',data1.shape,file=fh_printfile)

    data1a=vertical_interpolate(data1,zt,newlevs,data3,vertical_interpolation_method)
    #raise SystemExit('Forced exit.')
    data2a=vertical_interpolate(data2,zt,newlevs,data3,vertical_interpolation_method)
    del data1,data2,data3
    #rws_string=('rws','div','eta','uchi','vchi')
    #jjj="rws,div,eta,uchi,vchi"

    #rws,div,eta,uchi,vchi=diag_rws(data1a,data2a,lat_vals[:],lon_vals[:],rws_string)
    #print(jjj,file=fh_printfile)
    #eval(jjj)=diag_rws(data1a,data2a,lat_vals[:],lon_vals[:],rws_string)
    #rws_tuple=diag_rws(data1a,data2a,lat_vals[:],lon_vals[:],rws_string)
    rws_tuple=diag_rws(data1a,data2a,lat_vals[:],lon_vals[:],new_ovars)
    #print(rws_tuple.shape,file=fh_printfile)
    #print(len(rws_tuple),file=fh_printfile)
    #print(len(rws_tuple[0]),file=fh_printfile)
    del data1a,data2a
    #raise SystemExit('Forced exit.')

  if(dvar=='psl' or dvar=='pr' or dvar=='tas' or dvar=='huss' or dvar=='tos' or dvar=='zg' or dvar=='hfss' or dvar=='rlut' or dvar=='sfcWind' or dvar=='tslsi' or dvar=='hfls' or dvar=='uas' or dvar=='vas' or dvar=='ua' or dvar=='va' or dvar=='ta' or dvar =='hus' or dvar=='zg500' or dvar=='zg700' or dvar=='ta5' or dvar=='ua5' or dvar=='va5' or dvar=='zg5' or dvar=='hus5'):
    for o in range(0,len(ovars)):
      cmor.write(var_id=data_id[o], data=data[:], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])

  if(dvar=='nino34'):
    newdata=np.zeros((1,1),dtype='f')
    newdata[0,0]=data
    data=newdata
    for o in range(0,len(ovars)):
      cmor.write(var_id=data_id[o], data=data[:], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])

  elif(dvar=='rws5'):
    #print(rws_string,file=fh_printfile)
    #print(data_id,file=fh_printfile)
    for o in range(0,len(ovars)):
      #data_now=eval(rws_string[o])
      #data_now=rws_tuple[0,:,:,:]
      #data_now=rws_tuple[0]
      print(len(rws_tuple),file=fh_printfile)
      #cmor.write(var_id=data_id[o], data=rws_tuple[0], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])
      if(len(rws_tuple)==0):
        print("abc",file=fh_printfile)
        cmor.write(var_id=data_id[o], data=rws_tuple, ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])
      else:
        cmor.write(var_id=data_id[o], data=rws_tuple[0], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])
    #raise SystemExit('Forced exit here.')

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
