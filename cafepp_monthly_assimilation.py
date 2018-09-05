#!/usr/bin/env python

from __future__ import print_function #this is to allow print(,file=xxx) feature
import sys

#def main(source_directory):
#def main(rundir):
def main(**kwargs):
  import  sys
  import os
  #sys.path.insert(0,source_directory)

  import cafepp
  import inspect
  import shutil
  from decadal_diag import get_idir_from_experimet_json

  rundir=dvar=ybeg=yend=mbeg=mend=NoClobber=cafe_experiment=None
  for key, value in kwargs.iteritems():
    if(key=='rundir'):
      rundir=value
    elif(key=='dvar'):
      dvar=value
    elif(key=='ybeg'):
      ybeg=value
    elif(key=='yend'):
      yend=value
    elif(key=='mbeg'):
      mbeg=value
    elif(key=='mend'):
      mend=value
    elif(key=='NoClobber'):
      NoClobber=bool(value)
    elif(key=='cafe_experiment'):
      cafe_experiment=value
    else:
      raise SystemExit('Dont know that key.'+__file__+' line number: '+str(inspect.stack()[0][2]))

  if(type(rundir)==type(None)):
    raise SystemExit('Need to supply rundir.'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(type(dvar)==type(None)):
    raise SystemExit('Need to supply dvar.'+__file__+' line number: '+str(inspect.stack()[0][2]))
    
  #cafe_experiment='coupled_da/OUTPUT-2step-nobreeding-carbon2'
  #dvar='tos'
  #dvar='t20d'

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
    elif(token3=='cafe_experiment'):
      line='     "cafe_experiment":"'+cafe_experiment+'",\n'
    elif(token3=='ybeg' and type(ybeg)!=type(None)):
      line='     "ybeg":"'+str(ybeg)+'",\n'
    elif(token3=='yend' and type(yend)!=type(None)):
      line='     "yend":"'+str(yend)+'",\n'
    elif(token3=='mbeg' and type(mbeg)!=type(None)):
      line='     "mbeg":"'+str(mbeg)+'",\n'
    elif(token3=='mend' and type(mend)!=type(None)):
      line='     "mend":"'+str(mend)+'",\n'
    elif(token3=='#ybeg' and type(ybeg)!=type(None)):
      line='     "ybeg":"'+str(ybeg)+'",\n'
    elif(token3=='#yend' and type(yend)!=type(None)):
      line='     "yend":"'+str(yend)+'",\n'
    elif(token3=='#mbeg' and type(mbeg)!=type(None)):
      line='     "mbeg":"'+str(mbeg)+'",\n'
    elif(token3=='#mend' and type(mend)!=type(None)):
      line='     "mend":"'+str(mend)+'",\n'
    elif(token3=='NoClobber' and type(NoClobber)!=type(NoClobber)):
      line='     "NoClobber":"'+NoClobber+'",\n'
    print(line,file=ofh,end='')
  ifh.close()
  ofh.close()

  enow=1

  #top_directory_no2_try=get_idir_from_experimet_json(rundir+'/'+'JsonTemplates','cafepp_experiments.json',cafe_experiment)

  if(cafe_experiment=='coupled_da/OUTPUT-2step-nobreeding-carbon2'): #January and July are 5 year forecasts, else 2 years.
    #top_directory_no2='/short/v14/tok599/coupled/ao_am2/coupled_da/workdir2/OUTPUT-2step-nobreeding-carbon2'
    top_directory_no3='/OSM/CBR/OA_DCFP/data/CAFEPP/short/v14/tok599/coupled/ao_am2/coupled_da/workdir2/OUTPUT-2step-nobreeding-carbon2'
  print('Processing cafepp_experiments.json')
  ifh=open(rundir+'/'+'JsonTemplates'+'/'+'cafepp_experiments.json')
  ofh=open(rundir+'/'+'JsonTemplates'+'/'+'cafepp_experiments_tmp.json','w')
  for i,line in enumerate(ifh):
    token1=[str(x) for x in line.split(':')]
    token2=(token1[0].replace(' ',''))
    token3=(token2.replace('"',''))
    if(token3=='top_directory_no3'):
      line='     "top_directory_no3":"'+top_directory_no3+'",\n'
    elif(token3=='realisation'):
      line='     "realisation":"'+str(enow)+'",\n'
    print(line,file=ofh,end='')
  ifh.close()
  ofh.close()
  shutil.move(rundir+'/'+'JsonTemplates/cafepp_experiments_tmp.json',rundir+'/'+'JsonTemplates/cafepp_experiments.json')

  test_ok=cafepp.main('cafepp.json')

  return(0)

if __name__ == '__main__':

  kwargs=dict(x.split('=', 1) for x in sys.argv[1:])
  print('kwargs=',kwargs)

  main(**kwargs)

#print('sys.argv=',sys.argv)
#exit()

#if __name__ == '__main__':
#  if(len(sys.argv)==1):
#    main('.') #my scripts are directory above, users will need to set as appropriate.
#  elif(len(sys.argv)==2):
#    main(sys.argv[1])
#  else:
#    print('Problem running main.')
#    exit()
