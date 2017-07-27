#!/apps/python/2.7.6/bin/python
##!/short/p66/mac599/anaconda3/bin/ipython
# Filename : cafepp.py

"""
CAFE Post-Processor for monthly inputs
--------------------------

Compute extended time-series of monthly/seasonal data from breeding ACCESS coupled experiments.

Inputs can start from a month other than January and end in a month other than December. Outputs will be over available months. For monthly outputs this is trivial, however, for seasonal outputs this is non-trivial.

There are 3 kinds of outputs:

1. MONTHLY: input and output are monthly, process one month at a time.
2. SEASONAL: e.g. DJF, MAM, SO input are monthly and read in for a "years" season at a time and processed by wavg. A single time is written out at a time.
3. ANN: 12 continuous months (January to December) are read in at a time. A single time is written out at a time. Partial years are ignored.

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
from decadal_diag import MustHaveAllLevs,diag_acc_drake,diag_acc_africa,diag_mozmbq,diag_aabw,diag_nadw,diag_pp,diag_nflux,diag_ep,diag_ssh,diag_moc,diag_moc_atlantic,diag_moc_pacific,diag_moc_indian,diag_shice_cover,diag_nhice_cover,diag_nino34,xtra_nino34,init_data,sum_data,avg_data,filemonth_index,data_wavg,time_avg,diag_nhblocking_index,diag_rws,finish,diag_msftyyz,make_mask3D,diag_mfo,transPort,diag_rws500,create_odirs,create_ofils,diag_iod,diag_iod,xtra_iod,vertical_interpolate,diag_isothetaoNc,calc_iso_surface,calc_isoN
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
    print('Usage: ',script_name,' -h,help -v input_var -i importance (1-5) --ybeg=process begin year --yend=process end year --ybeg_min=min. year available --yend_max=max. year available --levs=one of pre-defined set --idir=input directory --season="MON"')

try:
    opts, args=getopt.getopt(sys.argv[1:], "wxdCAhv:i:rF",["help","ybeg=","yend=","ybeg_min=","yend_max=","mbeg=","mend=","mbeg_min=","mend_max=","dbeg=","dend=","dbeg_min=","dend_max=","levs=","realisation=","initialisation=","physics=","forcings=","season=","idir=","vertical_interpolation_method=","version="])
except getopt.GetoptError as err:
    print(err)
    usage(os.path.realpath(__file__))
    sys.exit(2)

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
    elif o == '-v':
         dvar=a
         #ivarS=[str(x) for x in a.split(',')]
         #print('ivarS=',ivarS)
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
#    elif o == '--stdlev':
#        StdLev=True
    elif o == '-F':
        Forecast=True
    else:
        assert False, 'unhandled option'

    try:
        erange
    except NameError:
        erange=('1','2','3','4','5')
    else:
        pass

netcdf='NETCDF4_CLASSIC'
netcdf='NETCDF3_64BIT'
netcdf='NETCDF3_CLASSIC'
netcdf='NETCDF4'

#if(delClim and not Anom):
#  raise SystemExit('If choose -d then must chose -A.')

#if not MonthlyWeights:
#  weights=np.array([1,1,1,1,1,1,1,1,1,1,1,1])

#if CMIP6:
#  print('Generating CMIP6 like netCDF output.')
#else:
#  print('Generating basic netCDF output.')

#print(levels)
#raise SystemExit('Forced exit.')

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
#print(getattr(ivarS,diag))

area_t=False
area_u=False
frequency='month'
if(dvar=='thetao'):
  #diag=True
  realm='ocean'
  #inputs=dvar
  table='Omon'
  inputs=['temp']
  units='degC'
  ovars=[dvar]

elif(dvar=='eta_t' or dvar=='tx_trans_int_z'):
  #diag=True
  realm='ocean'
  inputs=dvar
  table='Omon'
  ovars=[dvar]

elif(dvar=='olr' or dvar=='pr' or dvar=='precip' or dvar=='h500'):
  #diag=False
  area_t=False
  inputs=['precip']
  realm='atmos'
  diag_dims=['time','lat','lon']
  units='kg m-2 s-1'
  table='Amon'
  ovars=[dvar]

elif(dvar=='o2'):
  #diag=False
  realm='ocean_bgc'
  ovars=[dvar]

elif(dvar=='acc_drake' or dvar=='acc_africa'):
  #diag=True
  inputs=['tx_trans_int_z']
  realm='ocean'
  diag_dims=['time']
  dvar='tx_trans_int_z'
  levels=0
  ovars=[dvar]

elif(dvar=='mozmbq'):
  #diag=True
  inputs=['ty_trans_int_z']
  realm='ocean'
  diag_dims=['time']
  ovars=[dvar]

elif(dvar=='aabw'):
  #diag=True
  inputs=['ty_trans','ty_trans_gm']
  realm='ocean'
  diag_dims=['time']
  ovars=[dvar]

elif(dvar=='nadw'):
  #diag=True
  inputs=['ty_trans','ty_trans_gm']
  realm='ocean'
  diag_dims=['time']
  ovars=[dvar]

elif(dvar=='pp'):
  #diag=True
  area_t=True
  inputs=['pprod_gross']
  realm='ocean_bgc'
  diag_dims=['time']
  units='Pg(C)/yr'
  table='Omon'
  ovars=[dvar]
  frequency='month'

elif(dvar=='nflux'):
  #diag=True
  area_t=True
  inputs=['stf07']
  realm='ocean_bgc'
  diag_dims=['time']
  units='Pg(C)/yr'
  table='Omon'
  ovars=[dvar]
  frequency='month'

elif(dvar=='ep'):
  #diag=True
  area_t=True
  inputs=['det']
  realm='ocean_bgc'
  diag_dims=['time']
  units='Pg(C)/yr'
  table='Omon'
  ovars=[dvar]
  frequency='month'

elif(dvar=='ssh'):
  #diag=True
  area_t=True
  inputs=['temp','salt']
  realm='ocean'
  diag_dims=['time','yt_ocean','xt_ocean']
  dvar='ssh'
  ovars=[dvar]

elif(dvar=='moc' or dvar=='moc_atlantic' or dvar=='moc_pacific' or dvar=='moc_indian'):
  #diag=True
  #inputs=['v']
  inputs=['tx_trans','tx_trans_gm']
  realm='ocean'
  #diag_dims=['time','st_ocean','yu_ocean']
  diag_dims=['time','st_ocean','yt_ocean']
  area_t=True
  area_u=True
  dvar='tx_trans'
  ovars=[dvar]

elif(dvar=='shice_cover' or dvar=='nhice_cover'):
  #diag=True
  inputs=['CN']
  realm='ice'
  diag_dims=['time']
  area_t=True
  dvar='CN'
  ovars=[dvar]

elif(dvar=='nhbi'):
  #diag=True
  inputs=['h500']
  realm='atmos'
  diag_dims=['time','lon']
  area_t=True
  #dvar='h500'
  levels=0
  nlev=0
  table='Amon'
  units='1.0'
  ovars=[dvar,'GHGS','GHGN']

elif(dvar=='rws'):
  #diag=True
  inputs=['ucomp','vcomp']
  realm='atmos'
  diag_dims=['time','pfull','lat','lon']
  #area_t=True
  #dvar='ucomp'
  units='s-2'
  table='Amon'
  #levels=8,9
  #nlev=2
  ovars=[dvar]

elif(dvar=='tos'):
  #diag=True
  area_t=True
  inputs=['temp']
  realm='ocean'
  diag_dims=['time','yt_ocean','xt_ocean']
  units='degC'
  table='Omon'
  ovars=[dvar]

elif(dvar=='sos'):
  #diag=True
  area_t=True
  inputs=['salt']
  realm='ocean'
  diag_dims=['time','yt_ocean','xt_ocean']
  units='psu'
  units='0.001'
  table='Omon'
  ovars=[dvar]

elif(dvar=='zg500'):
  #diag=True
  area_t=False
  inputs=['h500']
  realm='atmos'
  diag_dims=['time','lat','lon']
  units='m'
  table='Amon'
  ovars=[dvar]

elif(dvar=='psl'):
  #diag=True
  area_t=False
  inputs=['slp']
  realm='atmos'
  diag_dims=['time','lat','lon']
  units='hPa'
  table='Amon'
  ovars=[dvar]

elif(dvar=='ps'):
  #diag=True
  area_t=False
  inputs=['ps']
  realm='atmos'
  diag_dims=['time','lat','lon']
  units='hPa'
  table='Amon'
  ovars=[dvar]

elif(dvar=='zg'):
  #diag=True
  area_t=False
  inputs=['hght']
  realm='atmos'
  diag_dims=['time','phalf','lat','lon']
  units='m'
  table='Amon'
  ovars=[dvar]

elif(dvar=='temptotal'):
  #diag=True
  area_t=False
  inputs=['temp_total']
  realm='ocean'
  frequency='scalar'
  diag_dims=['time']
  units='Joule/1e25'
  table='Omon'
  ovars=[dvar]

elif(dvar=='salttotal'):
  #diag=True
  area_t=False
  inputs=['salt_total']
  realm='ocean'
  frequency='scalar'
  diag_dims=['time']
  units='kg/1e18'
  table='Omon'
  ovars=[dvar]

elif(dvar=='nino34'):
  #diag=True
  area_t=True
  inputs=['temp']
  realm='ocean'
  diag_dims=['time']
  units='degC'
  table='Omon'
  ovars=[dvar]
  frequency='month'
  levels=0
  nlev=0

elif(dvar=='iod'):
  #diag=True
  area_t=True
  inputs=['temp']
  realm='ocean'
  diag_dims=['time']
  units='degC'
  table='Omon'
  ovars=[dvar]
  frequency='month'
  levels=0
  nlev=0
  #print('len(ovars)=',len(ovars))
  #raise SystemExit('Forced exit.')

elif(dvar=='ua'):
  #diag=True
  area_t=False
  inputs=['ucomp']
  realm='atmos'
  diag_dims=['time','pfull','lat','lon']
  units='m/sec'
  table='Amon'
  frequency='month'
  ovars=[dvar]

elif(dvar=='va'):
  #diag=True
  area_t=False
  inputs=['vcomp']
  realm='atmos'
  diag_dims=['time','pfull','lat','lon']
  units='m/sec'
  table='Amon'
  frequency='month'
  ovars=[dvar]

elif(dvar=='pv'):
  #diag=True
  area_t=False
  inputs=['pv']
  realm='atmos'
  diag_dims=['time','phalf','lat','lon']
  units='1/s'
  table='Amon'
  ovars=[dvar]

elif(dvar=='divg'):
  #diag=True
  area_t=False
  inputs=['divg']
  realm='atmos'
  diag_dims=['time','phalf','lat','lon']
  units='1/s'
  table='Amon'
  ovars=[dvar]

elif(dvar=='vort'):
  #diag=True
  area_t=False
  inputs=['vort']
  realm='atmos'
  diag_dims=['time','phalf','lat','lon']
  units='1/s'
  table='Amon'
  ovars=[dvar]

elif(dvar=='mlotst'):
  #diag=True
  area_t=True
  inputs=['mld']
  realm='ocean'
  diag_dims=['time','yt_ocean','xt_ocean']
  units='m'
  table='Omon'
  ovars=[dvar]

elif(dvar=='mlotstsq'):
  #diag=True
  area_t=True
  inputs=['mld_sq']
  realm='ocean'
  diag_dims=['time','yt_ocean','xt_ocean']
  units='m'
  table='Omon'
  ovars=[dvar]

elif(dvar=='umo'):
  #diag=True
  area_t=False
  inputs=['tx_trans']
  realm='ocean'
  diag_dims=['time','yt_ocean','xu_ocean']
  units='kg s-1'
  table='Omon'
  frequency='month'
  ovars=[dvar]

elif(dvar=='vmo'):
  #diag=True
  area_t=False
  inputs=['tx_trans']
  realm='ocean'
  diag_dims=['time','yu_ocean','xt_ocean']
  units='kg s-1'
  table='Omon'
  frequency='month'
  ovars=[dvar]

elif(dvar=='volcello'):
  #diag=True
  area_t=False
  inputs=['temp']
  realm='ocean'
  diag_dims=['time','yu_ocean','xt_ocean']
  units='m3'
  table='fx'
  frequency='month'
  ovars=[dvar]

elif(dvar=='areacello'):
  area_t=False
  inputs=['temp']
  realm='ocean'
  diag_dims=['time','yu_ocean','xt_ocean']
  units='m2'
  table='Ofx'
  frequency='month'
  ovars=[dvar]

elif(dvar=='cl'):
  #diag=True
  area_t=False
  inputs=['cld_amt']
  realm='atmos'
  diag_dims=['time','phalf','lat','lon']
  units='%'
  table='Amon'
  ovars=[dvar]

elif(dvar=='sftof'):
  inputs=['temp']
  realm='ocean'
  diag_dims=['yu_ocean','xt_ocean']
  units='%'
  table='fx'
  frequency='month'
  ovars=[dvar]

elif(dvar=='thkcello'):
  inputs=['temp']
  realm='ocean'
  diag_dims=['st_ocean','yu_ocean','xt_ocean']
  units='m'
  table='fx'
  frequency='month'
  ovars=[dvar]

elif(dvar=='deptho'):
  inputs=['temp']
  realm='ocean'
  diag_dims=['st_ocean','yu_ocean','xt_ocean']
  units='m'
  table='Ofx'
  frequency='month'
  ovars=[dvar]

elif(dvar=='msftyyz'):
  inputs=['ty_trans','ty_trans_gm']
  diag_dims=['time', 'basin', 'st_ocean','yu_ocean']
  realm='ocean'
  units='10^-9 kg s-1'
  units='kg s-1'
  table='Omon'
  frequency='month'
  ovars=[dvar]

elif(dvar=='mfo'):
  inputs=['tx_trans','ty_trans']
  realm='ocean'
  diag_dims=['time', 'oline']
  units='kg s-1'
  table='Omon'
  frequency='month'
  ovars=[dvar]

elif(dvar=='so'):
  #diag=True
  realm='ocean'
  #inputs=dvar
  table='Omon'
  #area_t=True
  inputs=['salt']
  #realm='ocean'
  diag_dims=['time','st_ocean','yt_ocean','xt_ocean']
  units='psu'
  units='0.001'
  table='Omon'
  ovars=[dvar]

elif(dvar=='rws500'):
  #diag=True
  area_t=False
  inputs=['ucomp','vcomp']
  realm='atmos'
  diag_dims=['time','lat','lon']
  units='s-2'
  table='Amon'
  ovars=[dvar]

elif(dvar=='ta10'):
  #diag=True
  area_t=False
  inputs=['temp','ps']
  realm='atmos'
  diag_dims=['time','pfull','lat','lon']
  units='K'
  table='Amon'
  frequency='month'
  ovars=[dvar]
  if not 'vertical_interpolation_method' in locals(): vertical_interpolation_method='log_linear'

elif(dvar=='ta'):
  #diag=True
  area_t=False
  inputs=['temp']
  realm='atmos'
  diag_dims=['time','pfull','lat','lon']
  units='K'
  table='Amon'
  frequency='month'
  ovars=[dvar]

elif(dvar=='ua10'):
  #diag=True
  area_t=False
  inputs=['ucomp','ps']
  realm='atmos'
  diag_dims=['time','pfull','lat','lon']
  units='m/sec'
  table='Amon'
  frequency='month'
  ovars=[dvar]
  if not 'vertical_interpolation_method' in locals(): vertical_interpolation_method='linear'

elif(dvar=='va10'):
  #diag=True
  area_t=False
  inputs=['vcomp','ps']
  realm='atmos'
  diag_dims=['time','pfull','lat','lon']
  units='m/sec'
  table='Amon'
  frequency='month'
  ovars=[dvar]
  if not 'vertical_interpolation_method' in locals(): vertical_interpolation_method='linear'

elif(dvar=='zg10'):
  #diag=True
  area_t=False
  inputs=['hght','ps']
  realm='atmos'
  diag_dims=['time','phalf','lat','lon']
  units='m'
  table='Amon'
  ovars=[dvar]
  if not 'vertical_interpolation_method' in locals(): vertical_interpolation_method='log_linear'

elif(dvar=='hur10'):
  #diag=True
  area_t=False
  inputs=['rhum','ps']
  realm='atmos'
  diag_dims=['time','pfull','lat','lon']
  units='%'
  table='Amon'
  ovars=[dvar]
  if not 'vertical_interpolation_method' in locals(): vertical_interpolation_method='linear'

elif(dvar=='hus10'):
  #diag=True
  area_t=False
  inputs=['sphum','ps']
  realm='atmos'
  diag_dims=['time','pfull','lat','lon']
  units='1.0'
  table='Amon'
  ovars=[dvar]
  if not 'vertical_interpolation_method' in locals(): vertical_interpolation_method='pressure_cubed'

elif(dvar=='hur'):
  #diag=True
  area_t=False
  inputs=['rhum']
  realm='atmos'
  diag_dims=['time','pfull','lat','lon']
  units='%'
  table='Amon'
  ovars=[dvar]

elif(dvar=='hus'):
  #diag=True
  area_t=False
  inputs=['sphum']
  realm='atmos'
  diag_dims=['time','pfull','lat','lon']
  units='1.0'
  table='Amon'
  ovars=[dvar]

elif(dvar=='ta19'):
  #diag=True
  area_t=False
  inputs=['temp','ps']
  realm='atmos'
  diag_dims=['time','pfull','lat','lon']
  units='K'
  table='Amon'
  frequency='month'
  ovars=[dvar]
  if not 'vertical_interpolation_method' in locals(): vertical_interpolation_method='log_linear'

elif(dvar=='isothetao16c' or dvar=='isothetao20c' or dvar=='isothetao22c'):
  #diag=True
  area_t=True
  inputs=['temp']
  realm='ocean'
  diag_dims=['time','yt_ocean','xt_ocean']
  units='m'
  table='Omon'
  ovars=[dvar]

elif(dvar=='tauu'):
  #diag=True
  area_t=False
  inputs=['tau_x']
  realm='atmos'
  diag_dims=['time','lat','lon']
  units='Pa'
  table='Amon'
  ovars=[dvar]

elif(dvar=='tauv'):
  #diag=True
  area_t=False
  inputs=['tau_y']
  realm='atmos'
  diag_dims=['time','lat','lon']
  units='Pa'
  table='Amon'
  ovars=[dvar]

else:
  #diag=False
  inputs=['']
  #inputs=dvar
  dvarnow=[dvar]
  #exit

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

cmor.setup(inpath='Tables',netcdf_file_action=cmor.CMOR_REPLACE_4,logfile='log')

#print(dvar)

#print(inputs)
#raise SystemExit('Forced exit.')
dfp_defs='dfp_csiro-gfdl.json'
cmor.dataset_json(dfp_defs)
json_data=open(dfp_defs).read()
#pprint.pprint(json_data,width=1)
dfp_data=json.loads(json_data)
institution_id=dfp_data['institution_id']
source_id=dfp_data['source_id']
experiment_id=dfp_data['experiment_id']

cafe_experiment=os.environ.get('CAFE_EXPERIMENT')

if not cafe_experiment:
  raise SystemExit('Must set ENVIRONMENT VARIABLE CAFE_EXPERIMENT.')

if not 'realisation' in locals():
  if(cafe_experiment == 'v0'):
    realisation='1'
  elif(cafe_experiment == 'v1'):
    realisation='2'
  elif(cafe_experiment == 'v2'):
    realisation='3'
  elif(cafe_experiment == 'p0'):
    pass
    #realisation=ens
  else:
    raise SystemExit('cafe_experiment not known.')


#if(cafe_experiment == 'p0'):
#  pass
#else:
#  initialisation='1'
#  realisation='1'

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
  print('ingrid=',ingrid)

  #print(data)
  outgrid=cdms2.createUniformGrid(-88.875, 72, 2.5, 0, 144, 2.5)

  print('outgrid=',outgrid)

  #print(outgrid.getAxisList())

  #lat = outgrid.getLatitude() 
  #print(lat)

  #k=cdms2.regrid(a,regridTool='esmf',regridMethod='linear', coordSys='deg', diag={}, periodicity=1)
  regridfunc = Regridder(ingrid,outgrid)
  #newdata=regridFunc(data)

  #newdata=data.regrid(outgrid)
  newdata=regridfunc(data)
  print('newdata.shape=',newdata.shape)
  #raise SystemExit('Forced exit.')

elif(levs=='gn1'):
  grid_label='gn1'
  grid='3D vars level 0,3,5 using C-indexing'
elif(levs=='gn2'):
  grid_label='gn2'
  grid='3D vars level 0,3 using C-indexing'
elif(levs=='gn3'):
  grid_label='gn3'
  grid='3D vars level 0,35,36 using C-indexing'
elif(levs=='gn10'):
  grid_label='gn10'
  grid='3D vars use plev10'
elif(levs=='gn17'):
  grid_label='gn17'
  grid='3D vars use plev17'
else:
  grid_label='gn'
  grid='native grid'

today=date.today()
t=today.timetuple()
#print('today=',today)
#for i in t:
#  print('i=',i)
#version='v20170315'

if not 'version' in locals(): version='v'+str('{0:04d}'.format(t[0])) + str('{0:02d}'.format(t[1])) + str('{0:02d}'.format(t[2]))

odir=create_odirs(ovars,institution_id,source_id,experiment_id,ripf,table,grid_label,version)

#print('odir=',odir)
#raise SystemExit('Forced exit.')

#odir='CMIP6/CMIP/'+institution_id+'/'+source_id+'/'+experiment_id+'/'+ripf+'/'+table+'/'+dvar+'/'+grid_label+'/'+version

#print(mbeg)

#mbeg=2 #temporary
#mend=12 #temporary

mbeg=1 #temporary
mend=12 #temporary

#season='SON' #temporary
#season='JJA' #temporary
#season='DJF' #temporary

season='MON' #temporary
season='MAM' #temporary
season='ANN' #temporary

# OUTPUT FILE STUFF USED TO BE HERE MOVED DOWN TO PRIOR TO DATA WRITES...

cmor.set_cur_dataset_attribute('grid_label',grid_label)
cmor.set_cur_dataset_attribute('grid',grid)
cmor.set_cur_dataset_attribute('realization',realisation)
cmor.set_cur_dataset_attribute('initialization_index',initialisation)
cmor.set_cur_dataset_attribute('realization_index',realisation)
cmor.set_cur_dataset_attribute('version',version)

if(Forecast):
  cmor.set_cur_dataset_attribute('calendar','julian')
else:
  cmor.set_cur_dataset_attribute('calendar','noleap')

cmor.set_cur_dataset_attribute('importance',importance)
if 'vertical_interpolation_method' in locals(): cmor.set_cur_dataset_attribute('vertical_interpolation_method',vertical_interpolation_method)
if(cafe_experiment == 'v0'):
  cmor.set_cur_dataset_attribute('history','input data from experiment raijin:/g/data1/v14/coupled_model/v1/OUTPUT')
elif(cafe_experiment == 'v1'):
  cmor.set_cur_dataset_attribute('history','input data from experiment raijin:/g/data1/v14/coupled_model/v1/OUTPUT')
elif(cafe_experiment == 'v2'):
  cmor.set_cur_dataset_attribute('history','input data from experiment raijin:/short/v14/lxs599/coupled_model/feb17a/OUTPUT')

if(table=='fx' or table=='Ofx'):
  fileA='TablesTemplates/CMIP6_'+table+'.json'
  fileB='cmor/Tables/CMIP6_'+table+'.json'
  if filecmp.cmp(fileA,fileB):
    pass
  else:
    copyfile(fileA,fileB)
else:
  if(season=='MON'):
    os.system('awk -v number=35.00000 -f process.awk TablesTemplates/CMIP6_'+table+'.json > cmor/Tables/CMIP6_'+table+'.json')
    #awk -v number=35.00000 -f process.awk TablesTemplates/CMIP6_Amon.json
  else:
    os.system('awk -v number=400.00000 -f process.awk TablesTemplates/CMIP6_'+table+'.json > cmor/Tables/CMIP6_'+table+'.json')
    #call(['awk','-v number=400.00000 -f process.awk TablesTemplates/CMIP6_Amon.json'])
    #awk -v number=400.00000 -f process.awk TablesTemplates/CMIP6_Amon.json

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

#raise SystemExit('Forced exit.')

tables=[]
#tables.append(cmor.load_table('cmor/Tables/CMIP6_Omon.json'))
#tables.append(cmor.load_table('cmor/Tables/CMIP6_Amon.json'))
tables.append(cmor.load_table('cmor/Tables/CMIP6_'+table+'.json'))
tables.append(cmor.load_table('cmor/Tables/CMIP6_grids.json'))
tables.append(cmor.load_table('cmor/Tables/CMIP6_coordinate.json'))

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

if(ybeg<ybeg_min or ybeg>yend_max or yend<ybeg_min or yend>yend_max):
  raise SystemExit('Problem with ybeg/yend ybeg_min/yend_max.')

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

print('total_months_beg_to_end=',total_months_beg_to_end)

print('ybeg_now=',ybeg_now,' yend_now=',yend_now)

sstr,times_in_season,tindex_select_maxyears_by_nmy_0or1=filemonth_index(season,ybeg_now,yend_now,mbeg_now,mend_now) #MON special case where times_in_season=1, so always reading/writing one month at a time...

#iii=np.arange(total_months_beg_to_end).reshape((yend-ybeg+1),12)
#tindex_select_maxyears_by_nmy_0or1=np.zeros(iii.shape)
#tindex_select_maxyears_by_nmy_0or1[index_start]=1
#tindex_select_maxyears_by_nmy_0or1[index_end]=1
#print(iii)
print('tindex_select_maxyears_by_nmy_0or1=',tindex_select_maxyears_by_nmy_0or1)

print('total_months_beg_to_end,total_months_beg_to_end,index_start,end=',total_months_beg_to_end,total_months_beg_to_end)
#,index_start,index_end)
#raise SystemExit('Forced exit.')


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

print(y,' ',idir+idir_extra+'/'+ifil)
#raise SystemExit('Forced exit.')

f=netCDF4.Dataset(idir+idir_extra+'/'+ifil)
time=f.variables['time']

#here var_dims is just dummy as complete requirements depend on the output variable definition.
if(dvar=='acc_drake' or dvar=='acc_africa'):
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
  #print('hello')
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
elif(dvar=='tos' or dvar=='thetao' or dvar=='volcello' or dvar=='areacello' or dvar=='thkcello' or dvar=='sftof' or dvar=='deptho' or dvar=='isothetao16c' or dvar==dvar=='isothetao20c' or dvar=='isothetao22c'):
  ivar=f.variables['temp']
  var_dims=f.variables['temp'].dimensions
  var_size=f.variables['temp'].shape
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
elif(dvar=='ua' or dvar=='va' or dvar=='sos' or dvar=='ta' or dvar=='ta10' or dvar=='ua' or dvar=='ua10' or dvar=='va' or dvar=='va10' or dvar=='hur' or dvar=='hur10' or dvar=='hus' or dvar=='hus10' or dvar=='zg' or dvar=='zg10' or dvar=='ta19' or dvar=='tauu' or dvar=='tauv' or dvar=='pr'):
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
elif(dvar=='so'):
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

print('var_size=',var_size)
print(var_dims)
print(nvar_dims)
print('dvar=',dvar)
#raise SystemExit('Forced exit.')

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

print('var_size=',var_size)
print('var_dims=',var_dims)

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
else:
  #levels=np.range(0,var_size[1])
  levels=np.array(range(0,var_size[1]-0))
  nlev=len(levels)

if(dvar=='tos' or dvar=='sos' or dvar=='sftof' or dvar=='nino34' or dvar=='iod'):
  levels=0
  nlev=1
elif(dvar=='zg500' or dvar=='psl' or dvar=='ps' or dvar=='rws500' or dvar=='tauu' or dvar=='tauv' or dvar=='pr'):
  levels=0
  nlev=0

cmor.set_table(tables[1])

ibeg=0

refString='days since 0001-01-01'

#raise SystemExit('Forced exit.')

if(table=='fx' or table=='Ofx'):
  print('As this is a table fx parameter, all time information will be ignored.')
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
    #print(mbeg_now,mend_now)
    #raise SystemExit('Forced exit.')

    if(not Forecast):
      mbeg_now=1 #always 1 for 12 months per file.
      mend_now=1 #always 1 for 12 months per file.

    for m in range(mbeg_now,mend_now+1):
      if(Forecast): #has 1 month per file...
        idir_extra='/'+str('{0:04d}'.format(y))+str('{0:02d}'.format(m))+str('{0:02d}'.format(1))
      else:
        idir_extra=''
      iend=ibeg+12
      print(' y=',y,' m=',m,' mend_now=',mend_now,' ibeg=',ibeg,',',' iend=',iend)
      ifila=realm+'_'+frequency+'_'+str('{0:04d}'.format(y))+'_'+str('{0:02d}'.format(m))+'.nc'
      print(y,' ',idir+idir_extra+'/'+ifila)
      input_files[tindex]=idir+idir_extra+'/'+ifila
      if not os.path.exists(idir+idir_extra+'/'+ifila):
        raise SystemExit('Missing '+idir+idir_extra+'/'+ifila+'.')
      input_fhs[tindex]=netCDF4.Dataset(input_files[tindex])
      tindex+=1

  print('input files=',input_files)
  #print(len(input_files))
  print('tindex_select_maxyears_by_nmy_0or1=',tindex_select_maxyears_by_nmy_0or1)
  #print(tindex_select_maxyears_by_nmy_0or1.shape)
  #raise SystemExit('Forced exit.')

  findex_select_maxyears_by_nmy_b1_withminus1s=np.copy(tindex_select_maxyears_by_nmy_0or1)
  findex_select_maxyears_by_nmy_b1_withminus1s=findex_select_maxyears_by_nmy_b1_withminus1s*0-1 #set to -1, means no file at this position in year,month array.

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
        print('y,fff,y*,m*,mbeg,mend_now=',y,fff,y-ybeg_now,m-mbeg_now,mbeg_now,mend_now)
        if(tindex_select_maxyears_by_nmy_0or1[y-ybeg_now,m-1]!=0):
          findex_select_maxyears_by_nmy_b1_withminus1s[y-ybeg_now,m-1]=tindex_select_maxyears_by_nmy_0or1[y-ybeg_now,m-1]*fff + 1
        else:
          findex_select_maxyears_by_nmy_b1_withminus1s[y-ybeg_now,m-1]=0
        fff+=1
  else:
    y=ybeg_now
    for fff in range(len(input_files)):
      #print(fff)
      if(tindex_select_maxyears_by_nmy_0or1[y-ybeg_now,m-1]!=0):
        findex_select_maxyears_by_nmy_b1_withminus1s[fff,:]=tindex_select_maxyears_by_nmy_0or1[fff,:]*fff + 1
      else:
        findex_select_maxyears_by_nmy_b1_withminus1s[y-ybeg_now,m-1]=0
      y+=1

  print('findex_select_maxyears_by_nmy_b1_withminus1s=',findex_select_maxyears_by_nmy_b1_withminus1s)

  #raise SystemExit('Forced exit.')

  tindex_select_maxyears_by_nmy_0or1_flat=tindex_select_maxyears_by_nmy_0or1.reshape((yend_now-ybeg_now+1)*12)
  print('tindex_select_maxyears_by_nmy_0or1_flat=',tindex_select_maxyears_by_nmy_0or1_flat)
  #raise SystemExit('Forced exit.')

  numtims=int(np.sum(tindex_select_maxyears_by_nmy_0or1_flat))

  print('number of times used in each season definition, times_in_season=',times_in_season)
  print('total number of times (months) read in including any partial begin and end year, total_months_beg_to_end=',total_months_beg_to_end)
  print('number of times used from input file, numtims=',numtims)
#  print('total number of seasons written out, numseas=',numseas)

#file_index_maxyears_by_nmy_b1_withminus1s is an array year,month. elements corresonding to the valid input months/years are inserted (0...max-1), a -1 means that no file is present or included. file_index_maxyears_by_nmy_b1_withminus1s_flat is vector version of file_index_maxyears_by_nmy_b1_withminus1s.
#file_index_maxyears_by_nmy_b1_nominus1s_flat is list from 0...max-1 number of files, gets rid of any -1s indicating missing months.
#month_index_ntims is an vector year...month with ONLY valid year,month (values going from 0..11 only corresponding to month.
#year_index_ntims, similar to month_index_ntims, only now years, actual years corresponding to each of the months in month_index_ntims

  file_index_maxyears_by_nmy_b1_withminus1s,month_index_ntims=np.where(tindex_select_maxyears_by_nmy_0or1==1)

  print('file_index_maxyears_by_nmy_b1_withminus1s=',file_index_maxyears_by_nmy_b1_withminus1s)
  print('file_index_maxyears_by_nmy_b1_withminus1s.size=',file_index_maxyears_by_nmy_b1_withminus1s.size)

  year_index_ntims=file_index_maxyears_by_nmy_b1_withminus1s+ybeg_now

  file_index_maxyears_by_nmy_b1_withminus1s=findex_select_maxyears_by_nmy_b1_withminus1s.astype(int) #try, why do I overwrite definition above?

  file_index_maxyears_by_nmy_b1_withminus1s=np.where(file_index_maxyears_by_nmy_b1_withminus1s>0,file_index_maxyears_by_nmy_b1_withminus1s+0,file_index_maxyears_by_nmy_b1_withminus1s) #add 1 to values > 0

  print('file_index_maxyears_by_nmy_b1_withminus1s=',file_index_maxyears_by_nmy_b1_withminus1s)
  print('file_index_maxyears_by_nmy_b1_withminus1s.size=',file_index_maxyears_by_nmy_b1_withminus1s.size)

  #raise SystemExit('Forced exit.')

  print('month_index_ntims=',month_index_ntims)
  print('month_index_ntims.size=',month_index_ntims.size)
  print('year_index_ntims=',year_index_ntims)
  print('year_index_ntims.size=',year_index_ntims.size)

  file_index_maxyears_by_nmy_b1_withminus1s_flat=file_index_maxyears_by_nmy_b1_withminus1s.flatten()

  print('file_index_maxyears_by_nmy_b1_withminus1s_flat=',file_index_maxyears_by_nmy_b1_withminus1s_flat)

  file_index_maxyears_by_nmy_b1_nominus1s_flat=file_index_maxyears_by_nmy_b1_withminus1s_flat[np.where(file_index_maxyears_by_nmy_b1_withminus1s_flat>0,True,False)]

  print('file_index_maxyears_by_nmy_b1_nominus1s_flat=',file_index_maxyears_by_nmy_b1_nominus1s_flat)

  locate_file_index_Ntimes_b1_nominus1s_flat=file_index_maxyears_by_nmy_b1_nominus1s_flat[np.where(file_index_maxyears_by_nmy_b1_nominus1s_flat>0)]

  print('locate_file_index_Ntimes_b1_nominus1s_flat=',locate_file_index_Ntimes_b1_nominus1s_flat)
  print('locate_file_index_Ntimes_b1_nominus1s_flat.shape=',locate_file_index_Ntimes_b1_nominus1s_flat.shape)

  cnt_file_index_maxyears_by_nmy_b1_nominus1s_flat=len(locate_file_index_Ntimes_b1_nominus1s_flat)
  print('cnt_file_index_maxyears_by_nmy_b1_nominus1s_flat=',cnt_file_index_maxyears_by_nmy_b1_nominus1s_flat)
  #raise SystemExit('Forced exit.')

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

  print('ttt=',ttt,' times_in_season=',times_in_season)

  for n in range(0,ttt):
    #ind_end=ind_beg+times_in_season-1

    if(season=='MON'):
      #ind_end=ind_beg+times_in_season
      ind_end=ind_beg #always 1 month at a time for MON
    else:
      ind_end=ind_beg+times_in_season-1

    #print('n,ind_beg,ind_end,year_beg,month_beg,year_end,month_end=',n,ind_beg,ind_end,year_index_ntims[ind_beg],month_index_ntims[ind_beg],year_index_ntims[ind_end],month_index_ntims[ind_end])

    month_index_beg=month_index_ntims[ind_beg]+1
    year_index_beg=year_index_ntims[ind_beg]

    #print('year,month_index_beg=',year_index_beg,month_index_beg)

    tbeg.append(cdtime.comptime(year_index_beg,month_index_beg,day1).torel(refString).value)
    #print(month_index_ntims[ind_beg])

    if(season=='MON'):
      if(n==0):
        month_index_end=month_index_ntims[ind_beg]+1+1
        year_index_end=year_index_ntims[ind_beg]
      else:
        month_index_end=month_index_beg+1
        year_index_end=year_index_end
    if(season=='ANN'):
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

    print('n=',n,' ind_beg=',ind_beg,' ind_end=',ind_end,' year_index_beg=',year_index_beg,' month_index_beg=',month_index_beg,' year_index_end=',year_index_end,' month_index_end=',month_index_end)

    tdelta=1.0
    tdelta=0.0

    #tdelta=0
    #tdelta=1

    tend.append(cdtime.comptime(year_index_end,month_index_end,day1).torel(refString).value-tdelta) #assume in days, -1 gets numer of days of wanted month (ie. prior month without having to know number of days in month)
    #print('tbeg,tend=',tbeg,tend)

    #raise SystemExit('Forced exit.')
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

  print(tbeg,tend,tavg)
  #tables[0]=cmor.load_table('cmor/Tables/CMIP6_Amon.json')
  cmor.set_table(tables[0])
  #itime=cmor.axis(table_entry= 'time', length=5, units=refString, coord_vals=tavg[:], cell_bounds=tval_bounds[:], interval=None)
  #itime=cmor.axis(table_entry= 'time', length=5, units=refString, coord_vals=tavg[:], cell_bounds=tval_bounds[:])
  #itime=cmor.axis('time', units=refString, coord_vals=tavg[:], cell_bounds=tval_bounds[:])

  #print('tavg=',tavg)
  #print('tval_bounds=',tval_bounds)

  time_axis_id=cmor.axis('time', units=refString, coord_vals=tavg, cell_bounds=tval_bounds)
  #raise SystemExit('Forced exit.')

cmor.set_table(tables[1])

if(dvar=='tos' or dvar=='thetao' or dvar=='sos' or dvar=='mlotst' or dvar=='mlotstsq' or dvar=='umo' or dvar=='vmo' or dvar=='volcello' or dvar=='areacello' or dvar=='sftof' or dvar=='thkcello' or dvar=='deptho' or dvar=='msftyyz' or dvar=='mfo' or dvar=='so' or dvar=='isothetao16c' or dvar=='isothetao20c' or dvar=='isothetao22c'):
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

elif(dvar=='zg500' or dvar=='zg' or dvar=='psl' or dvar=='ps' or dvar=='ua' or dvar=='va' or dvar=='pv' or dvar=='divg' or dvar=='vort' or dvar=='cl' or dvar=='rws500' or dvar=='rws' or dvar=='nhbi' or dvar=='nino34' or dvar=='iod' or dvar=='pp' or dvar=='nflux' or dvar=='ep' or dvar=='ta' or dvar=='ta10' or dvar=='zg10' or dvar=='ua10' or dvar=='va10' or dvar=='hus10' or dvar=='hur10' or dvar=='hus' or dvar=='hur' or dvar=='ta19' or dvar=='tauu' or dvar=='tauv' or dvar=='pr'):

  if(ReGrid):
    lat_vals = outgrid.getLatitude() 
    lon_vals = outgrid.getLongitude()
  else:
    if(dvar=='nino34' or dvar=='iod' or dvar=='pp' or dvar=='nflux' or dvar=='ep'):
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

if(dvar=='zg' or dvar=='ua' or dvar=='va' or dvar=='pv' or dvar=='divg' or dvar=='vort' or dvar=='cl' or dvar=='rws' or dvar=='ta' or dvar=='hus' or dvar=='hur'):
  if(dvar=='zg'):
    zt=f.variables['phalf'][:]*100.0
  else:
    zt=f.variables['pfull'][:]*100.0
  min_vals=np.append((1.5*zt[0] - 0.5*zt[1]), (zt[0:-1] + zt[1:])/2)
  max_vals=np.append((zt[0:-1] + zt[1:])/2, (1.5*zt[-1] - 0.5*zt[-2]))
  zbounds =np.column_stack((min_vals, max_vals))
  zbounds=np.where(zbounds<0.0,0.0,zbounds)

  print('zt=',zt[:])
  print('zt.shape=',zt.shape)
  print('zbounds=',zbounds[:])
  print('tables=',tables)

  cmor.set_table(tables[2]) #working zg
  cmor.set_table(tables[0])
  #zt=np.array([1000., 5000., 10000., 25000., 50000., 70000., 85000., 100000.0])
  #zt=np.array([100000.,85000., 70000., 50000., 25000., 10000., 5000., 1000.])

  #z_axis_id=cmor.axis('plevs','Pa',coord_vals=zt[:],cell_bounds=zbounds[:])
  #z_axis_id=cmor.axis('plev25','Pa',coord_vals=zt[:],cell_bounds=zbounds[:])
  if(dvar=='zg'):
    z_axis_id=cmor.axis('plev25','Pa',coord_vals=zt[:])
  else:
    z_axis_id=cmor.axis('plev24','Pa',coord_vals=zt[:])
  #z_axis_id=cmor.axis('plev8','Pa',coord_vals=zt[:])
  #raise SystemExit('Forced exit.')

if(dvar=='ta10' or dvar=='zg10' or dvar=='ua10' or dvar=='va10' or dvar=='hus10' or dvar=='hur10'):
  if(dvar=='zg10'):
    zt=f.variables['phalf'][:]*100.0
  else:
    zt=f.variables['pfull'][:]*100.0
  print('zt=',zt)

  if(dvar=='ta19'):
    newlevs=np.array([100., 500., 1000., 2000., 3000., 5000., 7000., 10000., 15000., 20000., 25000., 30000., 40000., 50000., 60000., 70000., 85000., 92500., 100000.])
  else:
    newlevs=np.array([1000., 5000., 7000., 10000., 15000., 25000., 50000., 70000., 85000., 100000.])
  #print('newlevs=',newlevs)
  #raise SystemExit('Forced exit.')

  cmor.set_table(tables[0])
  z_axis_id=cmor.axis('plev10','Pa',coord_vals=newlevs[:])

if(dvar=='zg500' or dvar=='zg' or dvar=='psl' or dvar=='ps' or dvar=='ua' or dvar=='va' or dvar=='pv' or dvar=='vort' or dvar=='divg' or dvar=='cl' or dvar=='rws500' or dvar=='rws' or dvar=='nhbi' or dvar=='nino34' or dvar=='iod' or dvar=='pp' or dvar=='nflux' or dvar=='ep' or dvar=='ta' or dvar=='ta10' or dvar=='zg10' or dvar=='ua10' or dvar=='va10' or dvar=='hus10' or dvar=='hur10' or dvar=='hus' or dvar=='hur' or dvar=='ta19' or dvar=='tauu' or dvar=='tauv' or dvar=='pr'):
#  lat_axis=f.variables['lat']
#  lon_axis=f.variables['lon']

  print('lat_vals.shape=',lat_vals.shape)
  print('lon_vals.shape=',lon_vals.shape)

  print('lat_vals_bounds.shape=',lat_vals_bounds.shape)
  print('lon_vals_bounds.shape=',lon_vals_bounds.shape)
  lat_vals_bounds=np.where(lat_vals_bounds>90.0,90.0,lat_vals_bounds)
  lat_vals_bounds=np.where(lat_vals_bounds<-90.0,-90.0,lat_vals_bounds)

  print('max=',np.max(lat_vals_bounds))
  print('min=',np.min(lat_vals_bounds))

  nlats=lat_vals.shape[0] #check this
  nlons=lon_vals.shape[0] #check this, should it be 1?

  cmor.set_table(tables[0]) #working zg500
  #cmor.set_table(tables[2])

  lat_axis_id=cmor.axis(table_entry='latitude', units='degrees_north', coord_vals=lat_vals[:], cell_bounds=lat_vals_bounds)

  lon_axis_id=cmor.axis(table_entry='longitude', units='degrees_east', coord_vals=lon_vals[:], cell_bounds=lon_vals_bounds)

if(dvar=='zg' or dvar=='ua' or dvar=='va' or dvar=='pv' or dvar=='vort' or dvar=='divg' or dvar=='cl' or dvar=='ta' or dvar=='ta10' or dvar=='zg10' or dvar=='ua10' or dvar=='va10' or dvar=='hus10' or dvar=='hur10' or dvar=='hus' or dvar=='hur' or dvar=='ta19'):
  pass
  #axis_ids=np.array([time_axis_id, lat_axis_id, lon_axis_id])
  #axis_ids=np.array([lat_axis_id, lon_axis_id])
  #axis_ids=np.array([z_axis_id, lat_axis_id, lon_axis_id])
  #axis_ids=np.array([time_axis_id, z_axis_id, lat_axis_id, lon_axis_id])
  #grid_id=cmor.grid(axis_ids=axis_ids, latitude=lat_vals[:], longitude=lon_vals[:])
  #raise SystemExit('Forced exit.')

if(dvar=='mfo'):
  lines=['barents_opening','bering_strait','canadian_archipelago','denmark_strait',\
                'drake_passage','english_channel','pacific_equatorial_undercurrent',\
                'faroe_scotland_channel','florida_bahamas_strait','fram_strait','iceland_faroe_channel',\
                'indonesian_throughflow','mozambique_channel','taiwan_luzon_straits','windward_passage']

  nlines=len(lines)
  #cmor.set_table(tables[2])
  cmor.set_table(tables[0])

  oline_axis_id = cmor.axis(table_entry='oline', units='', length=len(lines), coord_vals=lines)
  print oline_axis_id

elif(dvar=='msftyyz'):
  cmor.set_table(tables[0])

  basins=np.array(['atlantic_arctic_ocean','indian_pacific_ocean','global_ocean'])
  nbasins=len(basins)
  basin_axis_id = cmor.axis(table_entry='basin', units='', length=len(basins), coord_vals=basins)

  z_axis_id=cmor.axis('depth_coord','m',coord_vals=zt[:],cell_bounds=zbounds[:])

  lat_vals=xfh.variables['grid_y_T']
  lon_vals=xfh.variables['grid_x_C']
  lon_vals_360=np.mod(lon_vals,360)

  print('lon_vals=',lon_vals[:])

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

  print('time_axis_id=', time_axis_id)
  print('basin_axis_id=', basin_axis_id)
  print('z_axis_id=', z_axis_id)
  print('lat_axis_id=', lat_axis_id)

  #raise SystemExit('Forced exit.')

elif(dvar=='thetao' or dvar=='umo' or dvar=='vmo' or dvar=='volcello' or dvar=='areacello' or dvar=='sftof' or dvar=='thkcello' or dvar=='deptho' or dvar=='so'):

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

  #print('zt=',zt[:])
  #print('zt=',zt[[0,3,5]])
  #z_axis_id=cmor.axis('depth_coord','m',coord_vals=zt[[0,3,5]])
  #raise SystemExit('Forced exit.')

  cmor.set_table(tables[1])

  j_axis_id=cmor.axis('j_index','1',coord_vals=np.arange(300))
  i_axis_id=cmor.axis('i_index','1',coord_vals=np.arange(360))

  #print('time_axis_id=',time_axis_id)
  print('z_axis_id=',z_axis_id)
  print('j_axis_id=',j_axis_id)
  print('i_axis_id=',i_axis_id)

  lon_vertices=np.mod(get_vertices('geolon_t'),360)
  lat_vertices=get_vertices('geolat_t')

  #axis_ids=np.array([z_axis_id, j_axis_id, i_axis_id])
  axis_ids=np.array([j_axis_id, i_axis_id])

  grid_id=cmor.grid(axis_ids=axis_ids, latitude=lat_vals[:], longitude=lon_vals_360[:], latitude_vertices=lat_vertices[:], longitude_vertices=lon_vertices[:])

elif(dvar=='tos' or dvar=='sos' or dvar=='mlotst' or dvar=='mlotstsq' or dvar=='umo' or dvar=='vmo' or dvar=='volcello' or dvar=='areacello' or dvar=='sftof' or dvar=='thkcello' or dvar=='deptho' or dvar=='isothetao16c'or dvar=='isothetao20c'or dvar=='isothetao22c'):
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

  print('lat_vals.shape=',lat_vals.shape)
  print('lon_vals.shape=',lon_vals.shape)

  #print('lat_axis_bounds.shape=',lat_axis_bounds.shape)

  cmor.set_table(tables[1])

  j_axis_id=cmor.axis('j_index','1',coord_vals=np.arange(300))
  i_axis_id=cmor.axis('i_index','1',coord_vals=np.arange(360))

  print('j_axis_id=',j_axis_id)
  print('i_axis_id=',i_axis_id)

  lon_vertices=np.mod(get_vertices('geolon_t'),360)
  lat_vertices=get_vertices('geolat_t')

  axis_ids=np.array([j_axis_id, i_axis_id])
  grid_id=cmor.grid(axis_ids=axis_ids, latitude=lat_vals[:], longitude=lon_vals_360[:], latitude_vertices=lat_vertices[:], longitude_vertices=lon_vertices[:])
  print('grid_id=',grid_id)
  print('lat_vals.shape=',lat_vals.shape)
  print('lon_vals.shape=',lon_vals.shape)
  print('lat_vertices.shape=',lat_vertices.shape)
  print('lon_vertices.shape=',lon_vertices.shape)

cmor.set_table(tables[0]) #working

data_id=[]
if(dvar=='tos' or dvar=='sos' or dvar=='mlotst' or dvar=='mlotstsq' or dvar=='isothetao16c' or dvar=='isothetao20c' or dvar=='isothetao22c'):
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
elif(dvar=='thetao' or dvar=='umo' or dvar=='vmo' or dvar=='so'):
  axis_ids=[time_axis_id,grid_id]
  axis_ids=[0,1,2,3]
  axis_ids=[time_axis_id,z_axis_id,grid_id]
  axis_ids=[0,-100]
  axis_ids=[0,2,-100] #works but prob.
  axis_ids=[0,1,-100]
  data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20))
elif(dvar=='zg500' or dvar=='psl' or dvar=='ps' or dvar=='rws500' or dvar=='tauu' or dvar=='tauv' or dvar=='pr'):
  axis_ids=np.array([time_axis_id,lat_axis_id,lon_axis_id])
  axis_ids=np.array([lat_axis_id,lon_axis_id])
  axis_ids=[time_axis_id,lat_axis_id,lon_axis_id] #working zg500
  print('axis_ids=',axis_ids)
  if(dvar=='tauu' or dvar=='tauv'):
    positive="up"
  else:
    positive=None
  data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20,positive=positive))
elif(dvar=='zg' or dvar=='ua' or dvar=='va' or dvar=='pv' or dvar=='vort' or dvar=='divg' or dvar=='cl' or dvar=='rws' or dvar=='ta' or dvar=='ta10' or dvar=='zg10' or dvar=='ua10' or dvar=='va10' or dvar=='hus10' or dvar=='hur10' or dvar=='hus' or dvar=='hur' or dvar=='ta19'):
  #cmor.set_table(tables[2])
  #cmor.set_table(tables[1])
  #cmor.set_table(tables[0])
  #axis_ids=[time_axis_id,z_axis_id,lat_axis_id,lon_axis_id]
  axis_ids=np.array([time_axis_id,z_axis_id,lat_axis_id,lon_axis_id])
  print('axis_ids=',axis_ids)
  print('dvar=',dvar,' units=',units)
  data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20))

elif(dvar=='nino34' or dvar=='temptotal' or dvar=='salttotal' or dvar=='iod' or dvar=='pp' or dvar=='nflux' or dvar=='ep'):
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
  print('axis_ids=',axis_ids)
  data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20))
elif(dvar=='nhbi'):
  axis_ids=np.array([time_axis_id, lon_axis_id])
  print('axis_ids=',axis_ids)
  data_id.append(cmor.variable(dvar, units, axis_ids=axis_ids, missing_value=-1e20))
  data_id.append(cmor.variable('GHGS','1.0',axis_ids=axis_ids, missing_value=-1e20))
  data_id.append(cmor.variable('GHGN','1.0',axis_ids=axis_ids, missing_value=-1e20))

ofil,ofil_modified=create_ofils(season,table,ovars,experiment_id,source_id,ripf,grid_label,ybeg,yend,mbeg,mend,0,0) #don't need to worry about dbeg,dend, always monthly data input.

print('odir=',odir)
print('ofil=',ofil)
print('ofil_modified=',ofil_modified)

print('len(ovars)=',len(ovars))
for o in range(0,len(ovars)):
  print('Output CMIP6 file:',odir[o]+'/'+ofil_modified[o])

#print(NoClobber)
#raise SystemExit('Forced exit.')

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
    cmor.write(var_id=data_id[o], data=data[:], ntimes_passed=0)
    file_name.append(cmor.close(var_id=data_id[o], file_name=True))

    finish(file_name[o],odir[o],ofil[o],ofil_modified[o],season)

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
      month_index_end=month_index_ntims[ind_beg]+1+1
      year_index_end=year_index_ntims[ind_beg]
    else:
      month_index_end=month_index_beg+1
      year_index_end=year_index_end
  if(season=='ANN'):
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

  print('n=',n,' year_index_beg=',year_index_beg,' month_index_beg=',month_index_beg,' year_index_end=',year_index_end,' month_index_end=',month_index_end,' ind_beg,end=',ind_beg,ind_end)

  if(len(inputs)==2):
    if(dvar=='ta10' or dvar=='zg10' or dvar=='ua10' or dvar=='va10' or dvar=='hus10' or dvar=='hur10' or dvar=='ta19'):
      nlev=0
  else:
    print('levels=',levels)
    print('nlev=',nlev)

    data=data_wavg(inputs[0],input_fhs,locate_file_index_Ntimes_b1_nominus1s_flat,ind_beg,ind_end,month_in_file_total_months_beg_to_end,levels,MonthlyWeights,month_index_ntims)

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
    data=diag_nino34(data,area_t,lat_vals,lon_vals)
  elif(dvar=='iod'):
    data=diag_iod(data,area_t,lat_vals,lon_vals)
  elif(dvar=='nhbi'):
    data,var0,var1=diag_nhblocking_index(data,lat_vals,lon_vals)
  elif(dvar=='rws'):
    data=diag_rws(data1,data2,lat_vals[:],lon_vals[:])
  elif(dvar=='tos' or dvar=='thetao' or dvar=='sos' or dvar=='mlotst' or dvar=='mlotstsq' or dvar=='umo' or dvar=='vmo'):
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
     data=diag_rws500(data1[9,:,:],data2[9,:,:],lat_vals[:],lon_vals[:])
  elif(dvar=='isothetao16c'):
    data=diag_isothetaoNc(data,zt[:],16.0)
  elif(dvar=='isothetao20c'):
    data=diag_isothetaoNc(data,zt[:],20.0)

  elif(dvar=='isothetao22c'):
    data=diag_isothetaoNc(data,zt[:],22.0)

  elif(dvar=='ta10' or dvar=='zg10' or dvar=='ua10' or dvar=='va10' or dvar=='hus10' or dvar=='hur10' or dvar=='ta19'):

   data=vertical_interpolate(data1,zt,newlevs,data2,vertical_interpolation_method)

  if(season=='MON'):
    ntimes_passed=np.shape(data)[0]
  else:
    ntimes_passed=1

  if(dvar=='thetao'):
    print('levels=',levels)
    print('data.shape=',data.shape)
    for o in range(0,len(ovars)):
      cmor.write(var_id=data_id[o], data=data[:,:,:], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])
  elif(dvar=='tos' or dvar=='thetao' or dvar=='temptotal' or dvar=='salttotal' or dvar=='sos' or dvar=='mlotst' or dvar=='mlotstsq' or dvar=='umo' or dvar=='vmo' or dvar=='msftyyz' or dvar=='mfo' or dvar=='so' or dvar=='isothetao16c' or dvar=='isothetao20c' or dvar=='isothetao22c'):
    for o in range(0,len(ovars)):
      cmor.write(var_id=data_id[o], data=data[:], ntimes_passed=ntimes_passed, time_bnds=[tbeg[icnt],tend[icnt]])
      #raise SystemExit('Forced exit.')
  elif(dvar=='zg500' or dvar=='zg' or dvar=='psl' or dvar=='ps' or dvar=='ua' or dvar=='va' or dvar=='pv' or dvar=='vort' or dvar=='divg' or dvar=='cl' or dvar=='rws500' or dvar=='rws' or dvar=='ta' or dvar=='ta10' or dvar=='zg10' or dvar=='ua10' or dvar=='va10' or dvar=='hus10' or dvar=='hur10' or dvar=='hus' or dvar=='hur' or dvar=='ta19' or dvar=='tauu' or dvar=='tauv' or dvar=='pr'):
    print('data.shape=',data.shape)
    #raise SystemExit('Forced exit.')
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

print('ovars=',ovars)
print('len(ovars)=',len(ovars))
file_name=[]
for o in range(0,len(ovars)):
  #print('o=',o)
  #print('file_name=',file_name)
  file_name.append(cmor.close(var_id=data_id[o], file_name=True))

for o in range(0,len(ovars)):
  finish(file_name[o],odir[o],ofil[o],ofil_modified[o],season)

raise SystemExit('Finished O.K.')

#end
