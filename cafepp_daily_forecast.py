#!/usr/bin/env python

from __future__ import print_function #this is to allow print(,file=xxx) feature
import sys

def main(**kwargs):

  realm='atmos' #temporary

  #print('kwargs=',kwargs)
  #print('hello')
  #return(0)
  
  TEST=True #to process a single day of data to speed up testing...
  TEST=False
  
  import sys,os
  import cafepp_daily
  import inspect
  import shutil
  import glob
  
  from decadal_diag import process_json
  from decadal_diag import get_daily_indices_for_monthlyave

  cafe_experiment_check=rundir_check=ybeg_check=yend_check=ybeg_first_check=yend_last_check=mbeg_first_check=mend_last_check=ebeg_check=eend_check=mbeg_norm_check=mend_norm_check=dvar_check=NoClobber=False
  NoClobber=True

  for key, value in kwargs.iteritems():
    if(key=='cafe_experiment'):
      cafe_experiment=value
      cafe_experiment_check=True
    elif(key=='rundir'):
      rundir=value
      rundir_check=True
    elif(key=='dvar'):
      dvar=value
      dvar_check=True
    elif(key=='ybeg'):
      ybeg=int(value)
      ybeg_check=True
    elif(key=='yend'):
      yend=int(value)
      yend_check=True
    elif(key=='ybeg_first'):
      ybeg_first=int(value)
      ybeg_first_check=True
    elif(key=='yend_last'):
      yend_last=int(value)
      yend_last_check=True
    elif(key=='mbeg_first'):
      mbeg_first=int(value)
      mbeg_first_check=True
    elif(key=='mend_last'):
      mend_last=int(value)
      mend_last_check=True
    elif(key=='ebeg'):
      ebeg=int(value)
      ebeg_check=True
    elif(key=='eend'):
      eend=int(value)
      eend_check=True
    elif(key=='mbeg_norm'):
      mbeg_norm=int(value)
      mbeg_norm_check=True
    elif(key=='mend_norm'):
      mend_norm=int(value)
      mend_norm_check=True
    elif(key=='NoClobber'):
      NoClobber=value
      NoClobber_check=True

  if(not rundir_check):SystemExit('Set rundir:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not cafe_experiment_check):SystemExit('Set cafe_experiment:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not dvar_check): SystemExit('Set dvar:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not ybeg_check):SystemExit('Set ybeg:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not yend_check):SystemExit('Set yend:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not mbeg_first_check):SystemExit('Set mbeg_first:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not mend_last_check):SystemExit('Set mend_last:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not ebeg_check):SystemExit('Set ebeg:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not eend_check):SystemExit('Set eend:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  sys.path.insert(0,rundir)
  os.chdir(rundir)

  print('Processing cafepp_daily_assimilation.json')
  ifh=open(rundir+'/'+'cafepp_daily_assimilation.json')
  ofh=open(rundir+'/'+'JsonTemplates'+'/'+'cafepp.json','w')
  for i,line in enumerate(ifh):
    token1=[str(x) for x in line.split(':')]
    token2=(token1[0].replace(' ',''))
    token3=(token2.replace('"',''))
    #print('token3=',token3)
    if(token3=='dvar'):
      line='     "dvar":"'+dvar+'",\n'
    elif(token3=='cafe_experiment'):
#      line='    "cafe_experiment":"v1_forecast",\n'
      line='     "cafe_experiment":"'+cafe_experiment+'",\n'
    elif(token3=='ybeg'):
      line='    "ybeg":2003,\n'
    elif(token3=='yend'):
      line='    "yend":2016,\n'
    elif(token3=='mbeg'):
      line='    "mbeg":1,\n'
    elif(token3=='mend'):
      line='    "mend":12,\n'
    elif(token3=='dbeg'):
      line='    "dbeg":1,\n'
    elif(token3=='dend'):
      line='    "dend":31,\n'
    elif(token3=='#ProcessFileTxt'):
        line='    "ProcessFileTxt":"cafepp_daily_forecast.txt",\n'
    elif(token3=='NoClobber'):
      line='     "NoClobber":"'+NoClobber+'",\n'
    print(line,file=ofh,end='')
  ifh.close()
  ofh.close()

  for ycnt,ynow in enumerate(range(ybeg,yend+1)):
    if(ynow==ybeg_first):
      mbeg=mbeg_first
      mend=12
    elif(ynow==yend_last):
      mbeg=1
      mend=mend_last
    else:
      mbeg=mbeg_norm
      mend=mend_norm
    for mcnt,mnow in enumerate(range(mbeg,mend+1)):
      for ecnt,enow in enumerate(range(ebeg,eend+1)):

        output='cafepp_daily_forecast.txt'
        if(os.path.exists(output)):
          os.remove(output)
        ofh=open(output,'w')

        if(cafe_experiment=='v0_forecast'): #January and July are 5 year forecasts, else 2 years.
          top_directory_no2='/g/data1/v14/forecast/v0/yr'+str(ynow)+'/mn'+str(mnow)+'/OUTPUT.'+str(enow)
          top_directory_no2='/OSM/CBR/OA_DCFP/data/model_output/CAFE/forecasts/v0/yr'+str(ynow)+'/mn'+str(mnow)+'/OUTPUT.'+str(enow)
          physics=4
        elif(cafe_experiment=='v1_forecast'): #January and July are 5 year forecasts, else 2 years.
          top_directory_no2='/g/data1/v14/forecast/v1/yr'+str(ynow)+'/mn'+str(mnow)+'/OUTPUT.'+str(enow)
          top_directory_no2='/OSM/CBR/OA_DCFP/data/model_output/CAFE/forecasts/v1/yr'+str(ynow)+'/mn'+str(mnow)+'/OUTPUT.'+str(enow)
          physics=1
        elif(cafe_experiment=='v2_forecast'): #January and July are 5 year forecasts, else 2 years.
          top_directory_no2='/g/data1/v14/forecast/v2/OUTPUT/'+str('{0:04d}'.format(ynow))+'/'+str('{0:02d}'.format(mnow))+'/OUTPUT.'+str('{0:02d}'.format(enow))
          top_directory_no2='/OSM/CBR/OA_DCFP/data/model_output/CAFE/forecasts/v2/OUTPUT/'+str('{0:04d}'.format(ynow))+'/'+str('{0:02d}'.format(mnow))+'/OUTPUT.'+str('{0:02d}'.format(enow))
          physics=3
        elif(cafe_experiment=='v3_forecast'): #January and July are 5 year forecasts, else 2 years.
          top_directory_no2='/OSM/CBR/OA_DCFP/data/model_output/CAFE/forecasts/v3/yr'+str(ynow)+'/mn'+str(mnow)+'/OUTPUT.'+str(enow)
          top_directory_no2='/g/data1/v14/forecast/v3/yr'+str(ynow)+'/mn'+str(mnow)+'/OUTPUT.'+str(enow)
          physics=16

        files_string=top_directory_no2+'/'+realm+'_daily_????_??_01.nc'
        files=glob.glob(files_string)
        files=sorted(files)
        files = [x.strip().replace(realm,'REALM') for x in files]
        print('files=',files)

        for file_now in files:
          #print('file_now=',file_now)
          print(file_now,file=ofh,end='\n')
        ofh.close()

        print('top_directory_no2=',top_directory_no2)
        print('Processing cafepp_experiments.json')
        ifh=open(rundir+'/'+'cafepp_experiments.json')
        ofh=open(rundir+'/'+'JsonTemplates'+'/'+'cafepp_experiments.json','w')
        for i,line in enumerate(ifh):
          token1=[str(x) for x in line.split(':')]
          token2=(token1[0].replace(' ',''))
          token3=(token2.replace('"',''))
          if(token3=='top_directory_no2'):
            line='     "top_directory_no2":"'+top_directory_no2+'",\n'
          elif(token3=='realisation'):
            line='     "realisation":'+str(enow)+',\n'
          elif(token3=='physics'):
            line='     "physics":'+str(physics)+',\n'
#          elif(token3=='ybeg_min'):
#            line='    "ybeg_min":2002,\n'
#          elif(token3=='yend_max'):
#            line='    "yend_max":2016,\n'
#          elif(token3=='mbeg_min'):
#            line='    "mbeg_min":1,\n'
#          elif(token3=='mend_max'):
#            line='    "mend_max":12,\n'
#          elif(token3=='dbeg_min'):
#            line='    "dbeg_min":1,\n'
#          elif(token3=='dend_max'):
#            line='    "dend_max":31,\n'
          print(line,file=ofh,end='')
        ifh.close()
        ofh.close()

        test_ok=cafepp_daily.main('cafepp.json')
        #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  print('Finished O.K.:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  return(0)

if __name__ == '__main__':

  kwargs=dict(x.split('=', 1) for x in sys.argv[1:])
  print('kwargs=',kwargs)

  main(**kwargs)
