#!/usr/bin/env python

from __future__ import print_function #this is to allow print(,file=xxx) feature
import sys

#def main(source_directory):
#def main(rundir,**kwargs):
def main(**kwargs):

#doesn't make sense to have mbeg/mend on input unless over a single year...think about this.

  import  sys
  import os
  #sys.path.insert(0,source_directory)
  #sys.path.insert(0,rundir)

  import cafepp
  import inspect
  import shutil

  rundir_check=cafe_experiment_check = num_months_truncate_check = dvar_check = \
    ybeg_check = yend_check = mbeg_check = mend_check = \
    ybeg_first_check = yend_first_check = mbeg_first_check = mend_first_check = \
    ebeg_check = eend_check= NoClobber_check = \
    False
  NoClobber=StopAfterOne=False
  for key, value in kwargs.iteritems():
    #print("%s = %s" % (key, value))
    if(key=='rundir'):
      rundir=value
      rundir_check=True
    elif(key=='cafe_experiment'):
      cafe_experiment=value
      cafe_experiment_check=True
    elif(key=='num_months_truncate'):
      num_months_truncate=value
      num_months_truncate_check=True
    elif(key=='dvar'):
      dvar=value
      dvar_check=True
    elif(key=='ybeg'):
      ybeg=int(value)
      ybeg_check=True
    elif(key=='yend'):
      yend=int(value)
      yend_check=True
    elif(key=='mbeg_norm'):
      mbeg_norm=int(value)
      mbeg_norm_check=True
    elif(key=='mend_norm'):
      mend_norm=int(value)
      mend_norm_check=True
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
    elif(key=='NoClobber'):
      NoClobber=value
      NoClobber_check=True
    elif(key=='StopAfterOne'):
      StopAfterOne=bool(value)

  print('StopAfterOne=',StopAfterOne)

  if(not rundir_check):SystemExit('Set rundir:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not cafe_experiment_check):SystemExit('Set cafe_experiment:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not num_months_truncate_check): num_months_truncate=120000 #some large number
  if(not dvar_check): SystemExit('Set dvar:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not ybeg_check): SystemExit('Set ybeg:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not yend_check): SystemExit('Set yend:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not mbeg_check): SystemExit('Set mbeg:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not mend_check): SystemExit('Set mend:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not ybeg_first_check): SystemExit('Set ybeg_first:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not yend_last_check): SystemExit('Set yend_last:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not mend_first_check): SystemExit('Set mend_first:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not mend_last_check): SystemExit('Set mend_last:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not ebeg_check): SystemExit('Set ebeg:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not eend_check): SystemExit('Set eend:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  print('cafe_experiment,dvar,ybeg,yend,mbeg_norm,mend_norm,ybeg_first,yend_last,mbeg_first,mend_last,ebeg,eend=',\
    cafe_experiment,dvar,ybeg,yend,mbeg_norm,mend_norm,ybeg_first,yend_last,mbeg_first,mend_last,ebeg,eend)

  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  sys.path.insert(0,rundir)
  os.chdir(rundir)

  print('Processing cafepp_monthly_assimilation.json')
  ifh=open(rundir+'/'+'JsonTemplates/cafepp_monthly_assimilation.json')
  ofh=open(rundir+'/'+'JsonTemplates/cafepp.json','w')
  for i,line in enumerate(ifh):
    token1=[str(x) for x in line.split(':')]
    token2=(token1[0].replace(' ',''))
    token3=(token2.replace('"',''))
    if(token3=='dvar'):
      line='     "dvar":"'+dvar+'",\n'
    elif(token3=='num_months_truncate'):
      line='     "num_months_truncate":"'+num_months_truncate+'",\n'
    elif(token3=='cafe_experiment'):
      line='     "cafe_experiment":"'+cafe_experiment+'",\n'
    elif(token3=='ybeg'): #these will ensure all data will be used from the input directory...
      line='     #"ybeg":"2002",\n'
    elif(token3=='yend'):
      line='     #"yend":"2016",\n'
    elif(token3=='mbeg'):
      line='     #"mbeg":"1",\n'
    elif(token3=='mend'):
      line='     #"mend":"12",\n'
    elif(token3=='NoClobber'):
      line='     "NoClobber":"'+NoClobber+'",\n'
    print(line,file=ofh,end='')
  ifh.close()
  ofh.close()

  #return(0)

  print('hello')
  for ycnt,ynow in enumerate(range(ybeg,yend+1)):
    mbeg,mend=mbeg_norm,mend_norm

    if(ynow==ybeg_first and mbeg_first < mbeg_norm): #skip this month/year then...
      continue
    if(ynow==yend_last and mend_last > mend_norm): #skip this month/year then...
      continue

    if(ynow==ybeg_first):
      mbeg=max(mbeg_first,mbeg_norm)
    elif(ynow==yend_last):
      mend=min(mend_last,mend_norm)

    for mcnt,mnow in enumerate(range(mbeg,mend+1)):

      for ecnt,enow in enumerate(range(ebeg,eend+1)):
   
        if(cafe_experiment=='v0_forecast'): #January and July are 5 year forecasts, else 2 years.
          top_directory_no2='/g/data1/v14/forecast/v0/yr'+str(ynow)+'/mn'+str(mnow)+'/OUTPUT.'+str(enow)
          top_directory_no2='/OSM/CBR/OA_DCFP/data/model_output/CAFE/forecasts/v0/yr'+str(ynow)+'/mn'+str(mnow)+'/OUTPUT.'+str(enow)
          top_directory_no3='/OSM/CBR/OA_DCFP/data/model_output/CAFE/forecasts/v0/yr'+str(ynow)+'/mn'+str(mnow)+'/OUTPUT.'+str(enow)
        elif(cafe_experiment=='v1_forecast'): #January and July are 5 year forecasts, else 2 years.
          top_directory_no2='/g/data1/v14/forecast/v1/yr'+str(ynow)+'/mn'+str(mnow)+'/OUTPUT.'+str(enow)
          top_directory_no3='/OSM/CBR/OA_DCFP/data/model_output/CAFE/forecasts/v1/yr'+str(ynow)+'/mn'+str(mnow)+'/OUTPUT.'+str(enow)
	elif(cafe_experiment=='v2_forecast'): #January and July are 5 year forecasts, else 2 years.
          top_directory_no2='/g/data1/v14/forecast/v2/OUTPUT/'+str('{0:04d}'.format(ynow))+'/'+str('{0:02d}'.format(mnow))+'/OUTPUT.'+str('{0:02d}'.format(enow))
        if(cafe_experiment=='v3_forecast'): #All 2 year forecasts.
          top_directory_no2='/OSM/CBR/OA_DCFP/data/model_output/CAFE/forecasts/v0/yr'+str(ynow)+'/mn'+str(mnow)+'/OUTPUT.'+str(enow)
          top_directory_no3='/OSM/CBR/OA_DCFP/data/model_output/CAFE/forecasts/v0/yr'+str(ynow)+'/mn'+str(mnow)+'/OUTPUT.'+str(enow)
          top_directory_no1='/g/data1/v14/forecast/v3/yr'+str(ynow)+'/mn'+str(mnow)+'/OUTPUT.'+str(enow)
          top_directory_no2='/g/data1/v14/forecast/v3/yr'+str(ynow)+'/mn'+str(mnow)+'/OUTPUT.'+str(enow)
          top_directory_no3='/g/data1/v14/forecast/v3/yr'+str(ynow)+'/mn'+str(mnow)+'/OUTPUT.'+str(enow)
        else:
          raise SystemExit('Dont know that experiment:'+__file__+' line number: '+str(inspect.stack()[0][2]))

        print('top_directory_no1=',top_directory_no1)
        print('top_directory_no2=',top_directory_no2)
        print('top_directory_no3=',top_directory_no3)
        print('Processing cafepp_experiments.json')
        ifh=open(rundir+'/'+'JsonTemplates'+'/'+'cafepp_experiments.json')
        ofh=open(rundir+'/'+'JsonTemplates'+'/'+'cafepp_experiments_tmp.json','w')
        for i,line in enumerate(ifh):
          token1=[str(x) for x in line.split(':')]
          token2=(token1[0].replace(' ',''))
          token3=(token2.replace('"',''))
          if(token3=='top_directory_no1'):
            line='     "top_directory_no1":"'+top_directory_no1+'",\n'
          if(token3=='top_directory_no2'):
            line='     "top_directory_no2":"'+top_directory_no2+'",\n'
          elif(token3=='top_directory_no3'):
            line='     "top_directory_no3":"'+top_directory_no3+'",\n'
          elif(token3=='realisation'):
            line='     "realisation":"'+str(enow)+'",\n'
          print(line,file=ofh,end='')
        ifh.close()
        ofh.close()
        shutil.move(rundir+'/'+'JsonTemplates/cafepp_experiments_tmp.json',rundir+'/'+'JsonTemplates/cafepp_experiments.json')

        test_ok=cafepp.main('cafepp.json')
        #if(StopAfterOne): raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  return(0)

#print('sys.argv=',sys.argv)
#exit()

if __name__ == '__main__':

  kwargs=dict(x.split('=', 1) for x in sys.argv[1:])
  print('kwargs=',kwargs)

  main(**kwargs)

#  if(len(sys.argv)==1):
#    main('.') #my scripts are directory above, users will need to set as appropriate.
#  elif(len(sys.argv)==2):
#    main(sys.argv[1])
#  else:
#    print('Problem running main.')
#    exit()
