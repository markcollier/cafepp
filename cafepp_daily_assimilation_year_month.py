#!/usr/bin/env python

from __future__ import print_function #this is to allow print(,file=xxx) feature
import sys
#import cafepp_daily

def main(source_directory):

  #print('hello')
  #return(0)
  
  TEST=True #to process a single day of data to speed up testing...
  TEST=False
  
  import sys
  sys.path.insert(0,source_directory)

  import cafepp_daily
  import inspect
  
  from decadal_diag import process_json
  from decadal_diag import get_daily_indices_for_monthlyave
  
  ybeg_min=2002 #2002
  ybeg_max=2015 #2015
  
  ybeg_now=ybeg_min
  
  while (ybeg_now<=ybeg_max):
  
    if(ybeg_now%4==0 and ybeg_now%100!=0 or ybeg_now%400==0):
      leap=True
    else:
      leap=False
  
    if(leap):
      days_in_month=[31,29,31,30,31,30,31,31,30,31,30,31]
    else:
      days_in_month=[31,28,31,30,31,30,31,31,30,31,30,31]
  
    dbeg_now=1
    mbeg_now=1
    mend_now=mbeg_now
  
    while (mbeg_now<=12):
  
      print('ybeg_now,mbeg_now=',ybeg_now,mbeg_now)
  
      dend_now=days_in_month[mbeg_now-1]
  
      YBEG_MIN_now=1 #these aren't relevent here but inserted so that JSON file is not corrupted in other parts.
      MBEG_MIN_now=1 #these aren't relevent here but inserted so that JSON file is not corrupted in other parts.
      REALISATION_now=1 #these aren't relevent here but inserted so that JSON file is not corrupted in other parts.
  
      process_json('cafepp_daily_forecast_experiments.json','JsonTemplates/cafepp_experiments.json',REALISATION_now,YBEG_MIN_now,YBEG_MIN_now,MBEG_MIN_now,MBEG_MIN_now,1,31,True)
  
      process_json('cafepp_daily_assimilation.json','JsonTemplates/cafepp.json',REALISATION_now,ybeg_now,ybeg_now,mbeg_now,mbeg_now,dbeg_now,dend_now,True)
  
      if(TEST):
        process_json('cafepp_daily_assimilation.json','JsonTemplates/cafepp.json',REALISATION_now,ybeg_now,ybeg_now,mbeg_now,mend_now,1,1,True)
  
      test_ok=cafepp_daily.main('cafepp.json')
  
      if(TEST):
        print('Finished O.K.:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
      #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
      mbeg_now+=1
      mend_now=mbeg_now
    ybeg_now+=1
  
  print('Finished O.K.:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  return(0)

#print(sys.argv)
#exit()

if __name__ == '__main__':
  if(len(sys.argv)==1):
    main('..') #my scripts are directory above, users will need to set as appropriate.
  elif(len(sys.argv)==2):
    main(sys.argv[1])
  else:
    print('Problem running main.')
    exit()
