#!/usr/bin/env python

from __future__ import print_function #this is to allow print(,file=xxx) feature

def main(**kwargs):

  #realm='atmos' #temporary
  physics=2 #temporary, shouldn't be necessary as set only once in cafepp_experiments.json

  import sys,os
  import cafepp_daily
  import inspect
  import shutil
  import glob

  from decadal_diag import process_json
  from decadal_diag import get_daily_indices_for_monthlyave

  cafe_experiment_check=rundir_check=dvar_check=ybeg_check=yend_check=ybeg_first_check=yend_last_check=mbeg_first_check=mend_last_check=mbeg_norm_check=mend_norm_check=False

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
    elif(key=='mbeg_norm'):
      mbeg_norm=int(value)
      mbeg_norm_check=True
    elif(key=='mend_norm'):
      mend_norm=int(value)
      mend_norm_check=True

  if(not rundir_check):SystemExit('Set rundir:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not cafe_experiment_check):SystemExit('Set cafe_experiment:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not dvar_check):SystemExit('Set dvar:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not ybeg_check):SystemExit('Set ybeg:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not yend_check):SystemExit('Set yend:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not ybeg_first_check):SystemExit('Set ybeg_first:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not yend_last_check):SystemExit('Set yend_last:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not mbeg_first_check):SystemExit('Set mbeg_first:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not mend_last_check):SystemExit('Set mend_last:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not mbeg_norm_check):SystemExit('Set mbeg_norm:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not mend_norm_check):SystemExit('Set mend_norm:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  sys.path.insert(0,rundir)
  os.chdir(rundir)

  top_directory_no2='/short/v14/tok599/coupled/ao_am2/coupled_da/workdir2/OUTPUT-2step-nobreeding-carbon2/20020101' #dummy value

  print('Processing cafepp_experiments.json')
  ifh=open(rundir+'/'+'cafepp_experiments.json')
  ofh=open(rundir+'/'+'JsonTemplates'+'/'+'cafepp_experiments.json','w')
  for i,line in enumerate(ifh):
    token1=[str(x) for x in line.split(':')]
    token2=(token1[0].replace(' ',''))
    token3=(token2.replace('"',''))
    if(token3=='top_directory_no2'):
      line='     "top_directory_no2":"'+top_directory_no2+'",\n'
    elif(token3=='physics'):
      line='     "physics":'+str(physics)+',\n'
    print(line,file=ofh,end='')
  ifh.close()
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
      line='    "cafe_experiment":"'+cafe_experiment+'",\n'
    elif(token3=='ybeg'):
      line='    "ybeg":2002,\n'
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
        line='    "ProcessFileTxt":"cafepp_daily_assimilation.txt",\n'
    elif(token3=='ProcessFileTxt'):
        line='    "ProcessFileTxt":"cafepp_daily_assimilation.txt",\n'
    print(line,file=ofh,end='')
  ifh.close()
  ofh.close()

  output='cafepp_daily_assimilation.txt'
  if(os.path.exists(output)):
    os.remove(output)
  ofh=open(output,'w')

  for ycnt,ynow in enumerate(range(ybeg,yend+1)):

    if(ynow%4==0 and ynow%100!=0 or ynow%400==0):
      leap=True
    else:
      leap=False
  
    if(leap):
      days_in_month=[31,29,31,30,31,30,31,31,30,31,30,31]
    else:
      days_in_month=[31,28,31,30,31,30,31,31,30,31,30,31]

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

      top_directory_no2='/short/v14/tok599/coupled/ao_am2/coupled_da/workdir2/OUTPUT-2step-nobreeding-carbon2/'+ \
        str('{0:04d}'.format(ynow))+str('{0:02d}'.format(mnow))+'01'

      for dcnt,dnow in enumerate(range(1,days_in_month[mnow-1]+1)):

        ifil='REALM_daily_'+str('{0:04d}'.format(ynow))+'_'+str('{0:02d}'.format(mnow))+'_'+str('{0:02d}'.format(dnow))+'.nc'
        print(top_directory_no2+'/'+ifil,file=ofh,end='\n')
  ofh.close()

  test_ok=cafepp_daily.main('cafepp.json')

  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  print('Finished O.K.:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  return(0)

if __name__ == '__main__':

  kwargs=dict(x.split('=', 1) for x in sys.argv[1:])
  print('kwargs=',kwargs)

  main(**kwargs)
