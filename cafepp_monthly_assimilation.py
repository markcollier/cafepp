#!/usr/bin/env python

from __future__ import print_function #this is to allow print(,file=xxx) feature
import sys

#def main(source_directory):
def main(rundir):
  import  sys
  import os
  #sys.path.insert(0,source_directory)
  sys.path.insert(0,rundir)

  import cafepp
  import inspect
  import shutil

  os.chdir(rundir)

  cafe_experiment='coupled_da/OUTPUT-2step-nobreeding-carbon2'
  dvar='tos'

  print('Processing cafepp_monthly_assimilation.json')
  ifh=open(rundir+'/'+'JsonTemplates/cafepp_monthly_assimilation.json')
  ofh=open(rundir+'/'+'JsonTemplates/cafepp.json','w')
  for i,line in enumerate(ifh):
    token1=[str(x) for x in line.split(':')]
    token2=(token1[0].replace(' ',''))
    token3=(token2.replace('"',''))
    if(token3=='dvar'):
      line='     "dvar":"'+dvar+'",\n'
    if(token3=='cafe_experiment'):
      line='     "cafe_experiment":"'+cafe_experiment+'",\n'
    print(line,file=ofh,end='')
  ifh.close()
  ofh.close()

  enow=1

  if(cafe_experiment=='coupled_da/OUTPUT-2step-nobreeding-carbon2'): #January and July are 5 year forecasts, else 2 years.
    top_directory_no2='/short/v14/tok599/coupled/ao_am2/coupled_da/workdir2/OUTPUT-2step-nobreeding-carbon2'
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
  if(len(sys.argv)==1):
    main('.') #my scripts are directory above, users will need to set as appropriate.
  elif(len(sys.argv)==2):
    main(sys.argv[1])
  else:
    print('Problem running main.')
    exit()
