#!/usr/bin/env python

from __future__ import print_function #this is to allow print(,file=xxx) feature
import sys

def main(source_directory):
  import  sys
  import os
  sys.path.insert(0,source_directory)

  import cafepp
  import inspect
  import shutil

  rundir='/home/599/mac599/decadal/paper_analysis'
  
  os.chdir(rundir)

  shutil.copyfile(rundir+'/'+'cafepp_monthly_assimilation.json',rundir+'/'+'JsonTemplates/cafepp.json')

  test_ok=cafepp.main('cafepp.json')

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
