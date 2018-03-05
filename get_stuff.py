#!/usr/bin/env python

import os

igo=True
igo=False
if(igo):
  input_files=['CMIP6_Amon.json','CMIP6_Oday.json','CMIP6_Omon.json','CMIP6_day.json','CMIP6_CV.json','CMIP6_Ofx','CMIP6_coordinate.json','CMIP6_fx.json']
  for i,file in enumerate(input_files):
    command='scp mac599@raijin.nci.org.au:decadal/paper_analysis/TablesTemplates/'+ \
      file+' TablesTemplates/'
    print(command)
    os.system(command)

igo=False
igo=True
if(igo):
  input_files=['cafepp.json','cafepp_csiro-gfdl.json','cafepp_experiments.json','cafepp_vars.json']
  for i,file in enumerate(input_files):
    command='scp mac599@raijin.nci.org.au:decadal/paper_analysis/JsonTemplates/'+ \
      file+' JsonTemplates/'
    print(command)
    os.system(command)

igo=True
igo=False
if(igo):
    command='scp -r mac599@raijin.nci.org.au:decadal/paper_analysis/cmip6-cmor-tables/ ./'
    print(command)
    os.system(command)

igo=True
igo=False
if(igo):
  input_files=['app_funcs.py','cafepp_daily.py','decadal_diag.py']
  #input_files=['decadal_diag.py']
  for i,file in enumerate(input_files):
    command='scp mac599@raijin.nci.org.au:decadal/'+file+' ./'
    print(command)
    os.system(command)

igo=True
igo=False
if(igo):
  input_files=['cafepp_batch.ipynb','qjob.csh','cafepp_daily_assimilation.json','cafepp_daily_assimilation_year_month.py']
  input_files=['cafepp_daily_assimilation.json','cafepp_daily_assimilation_year_month.py']
  for i,file in enumerate(input_files):
    command='scp mac599@raijin.nci.org.au:decadal/paper_analysis/'+file+' ./'
    print(command)
    os.system(command)

exit(0)
