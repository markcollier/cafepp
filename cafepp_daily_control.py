#!/usr/bin/env python

from __future__ import print_function #this is to allow print(,file=xxx) feature
import sys
#import cafepp_daily

#def main(source_directory):
def main(**kwargs):

  #print('hello')
  #return(0)
  
  TEST=True #to process a single day of data to speed up testing...
  TEST=False
  
  import sys,os
  import cafepp_daily
  import inspect
  import shutil
  
  from decadal_diag import process_json
  from decadal_diag import get_daily_indices_for_monthlyave
  from decadal_diag import get_idir_from_experimet_json

#"daily_data_layout":"noleap_1fileperyear",

  NoClobber_check=dvar_check=cafe_experiment_check=rundir_check=ybeg_check=yend_check=mbeg_first_check=mend_last_check=daily_data_layout=False
  NoClobber='True'

  for key, value in kwargs.iteritems():
    if(key=='cafe_experiment'):
      cafe_experiment=value
      cafe_experiment_check=True
    elif(key=='dvar'):
      dvar=value
      dvar_check=True
    elif(key=='rundir'):
      rundir=value
      rundir_check=True
    elif(key=='ybeg'):
      ybeg=int(value)
      ybeg_check=True
    elif(key=='yend'):
      yend=int(value)
      yend_check=True
    elif(key=='mbeg_first'):
      mbeg_first=int(value)
      mbeg_first_check=True
    elif(key=='mend_last'):
      mend_last=int(value)
      mend_last_check=True
    elif(key=='daily_data_layout'):
      daily_data_layout=value
      daily_data_layout_check=True
    elif(key=='NoClobber'):
      NoClobber=value
      #print('option NoClobber chosen',NoClobber)
      NoClobber_check=True
    else:
      raise SystemExit('option '+key+' not known:'+__file__+' line number: '+str(inspect.stack()[0][2]))


  if(not rundir_check):SystemExit('Set rundir:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not cafe_experiment_check):SystemExit('Set cafe_experiment:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not dvar_check): SystemExit('Set dvar:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  sys.path.insert(0,rundir)
  os.chdir(rundir)

#    process_json('cafepp_experiments.json','JsonTemplates/cafepp_experiments.json',1,ybeg,yend,mbeg_first,mend_last,1,31,True)

    #process_json('cafepp_daily_assimilation.json','JsonTemplates/cafepp.json',1,ybeg,yend,mbeg_first,mend_last,1,31,True)

  #print('top_directory_no2=',top_directory_no2)
  print('Processing cafepp_experiments.json')
  ifh=open(rundir+'/'+'cafepp_experiments.json')
  ofh=open(rundir+'/'+'JsonTemplates'+'/'+'cafepp_experiments.json','w')
  for i,line in enumerate(ifh):
    token1=[str(x) for x in line.split(':')]
    token2=(token1[0].replace(' ',''))
    token3=(token2.replace('"',''))
    #if(token3=='top_directory_no2'):
    #  line='     "top_directory_no2":"'+top_directory_no2+'",\n'
    #elif(token3=='realisation'):
    #  line='     "realisation":'+str(enow)+',\n'
    #elif(token3=='physics'):
    #  line='     "physics":'+str(physics)+',\n'
    print(line,file=ofh,end='')
  ifh.close()
  ofh.close()

  #jjj=get_idir_from_experimet_json(rundir+'/'+'JsonTemplates','cafepp_experiments.json',cafe_experiment)
  #print('cafepp_daily_control.py: jjj=',jjj)

  output='cafepp_daily_control.txt'
  if(os.path.exists(output)):
      os.remove(output)
  ofh=open(output,'w')

  if(daily_data_layout=='noleap_1fileperyear'):
    print('doing it...')
    idir=get_idir_from_experimet_json(rundir+'/'+'JsonTemplates','cafepp_experiments.json',cafe_experiment)
    #if(cafe_experiment=='v0'):
      #idir='/g/data1/v14/coupled_model/v0/OUTPUT'
      #idir='/OSM/CBR/OA_DCFP/data/CAFEPP/g/data1/v14/coupled_model/v0/OUTPUT'
    #  idir=get_idir_from_experimet_json(rundir+'/'+'JsonTemplates','cafepp_experiments.json',cafe_experiment)
    #elif(cafe_experiment=='v1'):
    #  #idir='/g/data1/v14/coupled_model/v1/OUTPUT'
    #  #idir='/OSM/CBR/OA_DCFP/data/CAFEPP/g/data1/v14/coupled_model/v1/OUTPUT'
    #  idir=get_idir_from_experimet_json(rundir+'/'+'JsonTemplates','cafepp_experiments.json',cafe_experiment)
    #elif(cafe_experiment=='v2'):
    #  #idir='/g/data1/v14/coupled_model/v2/OUTPUT'
    #  #idir='/OSM/CBR/OA_DCFP/data/CAFEPP/g/data1/v14/coupled_model/v2/OUTPUT'
    #  idir=get_idir_from_experimet_json(rundir+'/'+'JsonTemplates','cafepp_experiments.json',cafe_experiment)

    for ynow in range(ybeg,yend+1):
      #print('ynow=',ynow)
      #ifil='ocean_daily_'+str('{0:04d}'.format(ynow))+'_01_01.nc'
      ifil='REALM_daily_'+str('{0:04d}'.format(ynow))+'_01_01.nc'
      print(idir+'/'+ifil,file=ofh,end='\n')
    ofh.close()

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
      line='     "cafe_experiment":"'+cafe_experiment+'",\n'
    elif(token3=='ybeg'):
      line='    "ybeg":"'+str(ybeg)+'",\n'
    elif(token3=='yend'):
      line='    "yend":"'+str(yend)+'",\n'
    elif(token3=='mbeg'):
      line='    "mbeg":"'+str(mbeg_first)+'",\n'
    elif(token3=='mend'):
      line='    "mend":"'+str(mend_last)+'",\n'
    elif(token3=='dbeg'):
      line='    "dbeg":1,\n'
    elif(token3=='dend'):
      line='    "dend":31,\n'
#    elif(token3=='#ProcessFileTxt'):
#        line='    "ProcessFileTxt":"cafepp_daily_forecast.txt",\n'
    elif(token3=='#ProcessFileTxt'):
      line='    "ProcessFileTxt":"cafepp_daily_control.txt",\n'
    elif(token3=='DailytoMonthlyOutput'):
      line='    "DailytoMonthlyOutput":"True",\n'
    elif(token3=='NoClobber'):
      #print('NoClobber yes',NoClobber)
      line='     "NoClobber":"'+NoClobber+'",\n'
    print(line,file=ofh,end='')
  ifh.close()
  ofh.close()

#    print('Processing cafepp.json')
#    ifh=open(rundir+'/'+'JsonTemplates'+'/'+'cafepp.json')
#    ofh=open(rundir+'/'+'JsonTemplates'+'/'+'cafepp_tmp.json','w')
#    for i,line in enumerate(ifh):
#      token1=[str(x) for x in line.split(':')]
#      token2=(token1[0].replace(' ',''))
#      token3=(token2.replace('"',''))
#      if(token3=='#ProcessFileTxt'):
#        line='    "ProcessFileTxt":"cafepp_daily_control.txt",\n'
#      if(token3=='DailytoMonthlyOutput'):
#        line='    "DailytoMonthlyOutput":"True",\n'
#      if(token3=='cafe_experiment'):
#        line='    "cafe_experiment":"v1",\n'
#      print(line,file=ofh,end='')
#    ifh.close()
#    ofh.close()
#    shutil.move(rundir+'/'+'JsonTemplates/cafepp_tmp.json',rundir+'/'+'JsonTemplates/cafepp.json')

  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  test_ok=cafepp_daily.main('cafepp.json')
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  print('Finished O.K.:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  return(0)

if __name__ == '__main__':

  kwargs=dict(x.split('=', 1) for x in sys.argv[1:])
  print('kwargs=',kwargs)

  main(**kwargs)
