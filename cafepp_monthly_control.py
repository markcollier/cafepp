#!/usr/bin/env python

from __future__ import print_function #this is to allow print(,file=xxx) feature
import sys

#def main(source_directory):
def main(**kwargs):
  #print('**kwargs=',kwargs)
  #exit()

  import sys
  import os
  #sys.path.insert(0,source_directory)
  #sys.path.insert(0,rundir)

  import cafepp
  import inspect
  import shutil
  from decadal_diag import get_idir_from_experimet_json

  rundir_check=dvar_check=cafe_experiment_check=rundir_check=ybeg_check=yend_check=mbeg_check=mend_check=NoClobber_check=False
  NoClobber=True
  for key, value in kwargs.iteritems():
    #print("%s = %s" % (key, value))
    if(key=='rundir'):
      rundir=value
      rundir_check=True
    elif(key=='dvar'):
      dvar=value
      dvar_check=True
    elif(key=='cafe_experiment'):
      cafe_experiment=value
      cafe_experiment_check=True
    elif(key=='ybeg'):
      ybeg=value
      ybeg_check=True
    elif(key=='yend'):
      yend=value
      yend_check=True
    elif(key=='mbeg'):
      mbeg=value
      mbeg_check=True
    elif(key=='mend'):
      mend=value
      mend_check=True
    elif(key=='NoClobber'):
      NoClobber=value
      NoClobber_check=True

  if(not rundir_check): SystemExit('Set rundir:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not dvar_check): SystemExit('Set dvar:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not cafe_experiment_check): SystemExit('Set cafe_experiment:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not ybeg_check): SystemExit('Set ybeg:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not yend_check): SystemExit('Set yend:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not mbeg_check): SystemExit('Set mbeg:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  if(not mend_check): SystemExit('Set mend:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  print('ybeg,yend,mbeg,mend=',ybeg,yend,mbeg,mend)

  sys.path.insert(0,rundir)
  os.chdir(rundir)

  #cafe_experiment='v2'
  #dvar='tos'

  #ybeg,yend,mbeg,mend=491,500,1,12
  #ybeg,yend,mbeg,mend=391,400,1,12
  #ybeg,yend,mbeg,mend=291,300,1,12
  #ybeg,yend,mbeg,mend=191,200,1,12
  #ybeg,yend,mbeg,mend=91,100,1,12

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
    elif(token3=='ybeg'):
      line='     "ybeg":"'+str(ybeg)+'",\n'
    elif(token3=='yend'):
      line='     "yend":"'+str(yend)+'",\n'
    elif(token3=='mbeg'):
      line='     "mbeg":"'+str(mbeg)+'",\n'
    elif(token3=='mend'):
      line='     "mend":"'+str(mend)+'",\n'
    elif(token3=='#ybeg'):
      line='     "ybeg":"'+str(ybeg)+'",\n'
    elif(token3=='#yend'):
      line='     "yend":"'+str(yend)+'",\n'
    elif(token3=='#mbeg'):
      line='     "mbeg":"'+str(mbeg)+'",\n'
    elif(token3=='#mend'):
      line='     "mend":"'+str(mend)+'",\n'
    elif(token3=='NoClobber'):
      line='     "NoClobber":"'+NoClobber+'",\n'
#    if(token3=='num_months_truncate'):
#      line='     "#num_months_truncate":"'+str(120000)+'",\n'
    print(line,file=ofh,end='')
  ifh.close()
  ofh.close()

  enow=1

  top_directory_no2=get_idir_from_experimet_json(rundir+'/'+'JsonTemplates','cafepp_experiments.json',cafe_experiment)

#  if(cafe_experiment=='v0'):
#    top_directory_no2='/g/data1/v14/coupled_model/v0/OUTPUT'
#  elif(cafe_experiment=='v1'):
#    top_directory_no2='/g/data1/v14/coupled_model/v1/OUTPUT'
#  elif(cafe_experiment=='v2'):
#    top_directory_no2='/g/data1/v14/coupled_model/v2/OUTPUT'
#  elif(cafe_experiment=='v3'):
#    top_directory_no2='/g/data1/v14/coupled_model/v3/OUTPUT'
#  elif(cafe_experiment=='nov17n'):
#    top_directory_no2='/short/v19/mtc599/ao_am2/nov17n/out23/OUTPUT'
#  elif(cafe_experiment=='jul18b'):
#    top_directory_no2='/short/v19/mtc599/ao_am2/jul18b/OUTPUT'

  print('Processing cafepp_experiments.json')
  ifh=open(rundir+'/'+'JsonTemplates'+'/'+'cafepp_experiments.json')
  ofh=open(rundir+'/'+'JsonTemplates'+'/'+'cafepp_experiments_tmp.json','w')
  for i,line in enumerate(ifh):
    token1=[str(x) for x in line.split(':')]
    token2=(token1[0].replace(' ',''))
    token3=(token2.replace('"',''))
    if(token3=='top_directory_no2'):
      line='     "top_directory_no2":"'+top_directory_no2+'",\n'
    if(token3=='realisation'):
      line='     "realisation":"'+str(enow)+'",\n'
    print(line,file=ofh,end='')
  ifh.close()
  ofh.close()
  shutil.move(rundir+'/'+'JsonTemplates/cafepp_experiments_tmp.json',rundir+'/'+'JsonTemplates/cafepp_experiments.json')

  test_ok=cafepp.main('cafepp.json')

  return(0)

#print('sys.argv=',sys.argv)
#exit()

if __name__ == '__main__':

  #print('len(sys.argv)=',len(sys.argv))
  #print('sys.argv=',sys.argv)

  #exec(''.join(sys.argv[1:]))
  #x=','.join(sys.argv[1:])

  kwargs=dict(x.split('=', 1) for x in sys.argv[1:])
  print('kwargs=',kwargs)

  main(**kwargs)

  #main(a=1,b=2)
  #main()
  #main(*sys.argv[1])
  #if(len(sys.argv)==1):
  #  main('.') #my scripts are directory above, users will need to set as appropriate.
  #elif(len(sys.argv)==2):
  #  main(sys.argv[1::])
  #else:
  #  print('Problem running main.')
  #  exit()
