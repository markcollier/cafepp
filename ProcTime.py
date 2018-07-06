class ProcTime:

  '''
  And what about if only a subset of the possible year range is required?
  Think about how this can be done in a simple way.

  Currently it matches the indices and requires a complete matching set to utilise the elements - in the case
  of MON where we are broadcasting, then perhaps more appropriate to write out months that are there even if a subet
  of the 12 months? Would not want to do this for seasonal definitions that lead to averaging.
  season=MON is really the special case as we might want to write out 1) partial years for first/last year 2) write out partial years even when there are 12 months, ie truncate - there are potential applications for this.

  Need to ensure variable names here are optimised before I introduce to cafepp.

  https://goodcode.io/articles/python-dict-object/

  Note that broadcasting multi-month seasons like DJF, SON will not work with cmor as cmor_axis time will fail
  b/c it doesn't understand why the gap is sometimes only 30 days and others 300 days...however, it is good to
  keep the functionality as there might be some workaround or change to cmor.

  Still but when ANN chosen (for e.g.) and processing over full range of years/months (e.g. when *process not set)
  as it will still try to process incomplete years, need to have way of restricting the range.
  If the actual years selected are OK then it will complete as expected.
  '''

  nmy=12
  #def __init__(self, season, experiment, realm, frequency):
  
  def __init__(self,**kwargs):
    season_check= experiment_check = realm_check = frequency_check = input_directory_check =       ybeg_season_process_check = yend_season_process_check =       mbeg_season_process_check = mend_season_process_check =       False
    for key, value in kwargs.items():
      if(key=='experiment'):
        self.experiment=value
        experiment_check=True  
      elif(key=='season'):
        self.season=value
        season_check=True 
      elif(key=='realm'):
        self.realm=value
        realm_check=True  
      elif(key=='frequency'):
        self.frequency=value
        frequency_check=True
      elif(key=='ybeg_season_process'):
        self.ybeg_season_process=value
        ybeg_season_process_check=True
      elif(key=='yend_season_process'):
        self.yend_season_process=value
        yend_season_process_check=True
      elif(key=='mbeg_season_process'):
        self.mbeg_season_process=value
        mbeg_season_process_check=True
      elif(key=='mend_season_process'):
        self.mend_season_process=value
        mend_season_process_check=True
      elif(key=='input_directory'):
        self.input_directory=value
        input_directory_check=True
      else:
        raise SystemExit('key unknown:'+__file__+' line number: '+str(inspect.stack()[0][2]))
        
        
    if '__file__' not in locals(): __file__='ProcTime'
      
    if(not experiment_check): raise SystemExit('Must set experiment:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    if(not season_check): raise SystemExit('Must set season:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    if(not realm_check): raise SystemExit('Must set realm:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    if(not frequency_check): raise SystemExit('Must set frequency:'+__file__+' line number: '+str(inspect.stack()[0][2]))

    #if('self.frequency' in locals()): print('yes')
      
    #print('dir(self)=',dir(self))
    
    #print('self.frequency=',self.frequency)
    
#    try:
#      frequency_test=dir(self).index('freuency')
#    except ValueError:
#      print('xxx') 
#    #print('frequency_test=',frequency_test)
    
#    raise SystemExit('STOP!:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    
    #print('season=',season)
    
    #self.season=season
    #self.experiment=experiment
    #self.realm=realm
    #self.frequency=frequency
    
    #__file__='processFileTxt_newvars.py' #__file__ doesn't exist with notebooks.
  
    #Diagnostic=True
    Diagnostic=False
    #Diagnostic=True
    #season='DecJan'
    #season='MAM'
    #season='JunJul'
    #season='JJA'
    #season='JJAS'
    #season='ANN'
    #season='MON'
    #season='DJF'
    #season='Jan'
    #season='Jun'
    #season='Jul'
    #season='SON'
    #season='Feb'
    #experiment='coupled_da/OUTPUT-2step-nobreeding-carbon2'
    #experiment='v1_forecast'
    #experiment='v2_forecast'
    #experiment='v2'
    #experiment='test'
    #realm='ocean'
    #frequency='month'

    #Delete these variables, if they are not set then the full range based on input files will be used.
    #if('self.ybeg_season_process' in locals()): del(self.ybeg_season_process)
    #if('self.yend_season_process' in locals()): del(self.yend_season_process)
    #if('self.mbeg_season_process' in locals()): del(self.mbeg_season_process)
    #if('self.mend_season_process' in locals()): del(self.mend_season_process)
    
    import glob
    import netCDF4
    import numpy as np
    import datetime
    from array import array
    import types
    import inspect
    
    if(self.experiment=='coupled_da/OUTPUT-2step-nobreeding-carbon2'):
      self.hours=360.0 #this helps to identify year/month from the time-stamps. This experiment time-stamp is at the end of the month.
      #self.ybeg_season_process,self.yend_season_process,self.mbeg_season_process,self.mend_season_process=2002,2015,1,12 #potential for 2002,2016 for DecJan cross over seasons else 2012,2016. These would be the years required for the seasonal averages if wanting to truncate the entire output, an error will occur if they do not exist. Default would be all years. mbeg,end really only applies to situations with season=MON or single month defined seasons.
      self.idir='/short/v14/tok599/coupled/ao_am2/coupled_da/workdir2/OUTPUT-2step-nobreeding-carbon2'
      self.input_directories=sorted(glob.glob(self.idir+'/'+'????????/'))

      self.input_files=[]
      for self.i,self.input_directory in enumerate(self.input_directories):
        if(Diagnostic): print('self.i,self.input_directory=',self.i,self.input_directory) #get rid of not.
        self.list_of_files=sorted((glob.glob(self.input_directory+'/'+self.realm+'_'+self.frequency+'_????_??.nc')))
        self.input_files.append(self.list_of_files[0])
    
    elif(self.experiment=='v1_forecast'): #julian
      #with this kind of experiment we would have to loop over each 2/5 year experiment as well as ensemble, producing one output file for each.
      self.hours=0.0 #this helps to identify year/month from the time-stamps. This experiment time-stamp is at the middle of that month.
      #self.ybeg_season_process,self.yend_season_process,self.mbeg_season_process,self.mend_season_process=2003,2004,1,12 #potential for 2002,2004
      self.input_directory='/g/data1/v14/forecast/v1/yr2002/mn2/OUTPUT.1'
      self.input_directory='/g/data1/v14/forecast/v1/yr2003/mn1/OUTPUT.1'
      self.input_files=sorted((glob.glob(self.input_directory+'/'+self.realm+'_'+self.frequency+'_????_??.nc')))

    elif(self.experiment=='v2_forecast'): #noleap
      #with this kind of experiment we would have to loop over each 2/5 year experiment as well as ensemble, producing one output file for each.
      self.hours=0.0 #this helps to identify year/month from the time-stamps. This experiment time-stamp is at the middle of that month.
      #self.ybeg_season_process,self.yend_season_process,self.mbeg_season_process,self.mend_season_process=2003,2004,1,12 #potential for 2002,2004
      self.input_directory='/g/data1/v14/forecast/v2/OUTPUT/2000/01/OUTPUT.01'
      self.input_files=sorted((glob.glob(self.input_directory+'/'+self.realm+'_'+self.frequency+'_????_??.nc')))
      
    elif(self.experiment=='v0'):

      self.hours=0.0 #this helps to identify year/month from the time-stamps. This experiment time-stamp is at the middle of that month.
      if(not input_directory_check):
        self.input_directory='/g/data1/v14/coupled_model/v0/OUTPUT'
      self.input_files=sorted((glob.glob(self.input_directory+'/'+self.realm+'_'+self.frequency+'_????_??.nc'))) #all files
      
    elif(self.experiment=='v1'):

      self.hours=0.0 #this helps to identify year/month from the time-stamps. This experiment time-stamp is at the middle of that month.
      if(not input_directory_check):
        self.input_directory='/g/data1/v14/coupled_model/v1/OUTPUT'
      self.input_files=sorted((glob.glob(self.input_directory+'/'+self.realm+'_'+self.frequency+'_????_??.nc'))) #all files
      #self.input_files=sorted((glob.glob(self.input_directory+'/'+self.realm+'_'+self.frequency+'_?47?_??.nc'))) #all files
      
    elif(self.experiment=='v2'):
      #with this kind of experiment might want to supply just a subset of years to speed initialisatin of processing.
      #or supply all years and use processing scalars to reduce set.
  
      self.hours=0.0 #this helps to identify year/month from the time-stamps. This experiment time-stamp is at the middle of that month.
      #self.ybeg_season_process,self.yend_season_process,self.mbeg_season_process,self.mend_season_process=496,500,1,12 #potential for 1,500,1,12
      if(not input_directory_check):
        self.input_directory='/g/data1/v14/coupled_model/v2/OUTPUT'
      self.input_files=sorted((glob.glob(self.input_directory+'/'+self.realm+'_'+self.frequency+'_????_??.nc'))) #all files
      #self.input_files=sorted(glob.glob(self.input_directory+'/'+self.realm+'_'+self.frequency+'_049?_??.nc')+glob.glob(self.input_directory+'/'+realm+'_'+frequency+'_0500_??.nc')) #last 10 years.
  
      #print(type(input_files))
      #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    elif(self.experiment=='v3'):
      self.hours=0.0 #this helps to identify year/month from the time-stamps. This experiment time-stamp is at the middle of that month.
      if(not input_directory_check):
        self.input_directory='/g/data1/v14/coupled_model/v3/OUTPUT'
      self.input_files=sorted((glob.glob(self.input_directory+'/'+self.realm+'_'+self.frequency+'_0???_??.nc')))
      #self.input_files=sorted((glob.glob(self.input_directory+'/'+self.realm+'_'+self.frequency+'_04??_??.nc'))) #netCDF4 MDFDatasret seemed to fail so restricted list.
    else:
      raise Exception('Don\'t know experiment '+self.experiment+' file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
    if(Diagnostic): #get rid of not.
      print('self.input_directories=',self.input_directories)

    self.Ninput_files_orig=len(self.input_files)

      #print(list_of_files)
        #for i,input_file in enumerate(input_files):
    #  print('i,input_file=',i,input_file)
    #self.input_files=self.input_files[5:-5] #can discard input files from beginning/end to see impact on calculation of seasonal quantities. 5,-5 would take off first and last 5 months.

    #self.input_files=self.input_files[1::] #discard first time

    #self.input_files=self.input_files[2::] #discard first two times

    self.Ninput_files=len(self.input_files)
    if(not Diagnostic): #get rid of not.
      print('Number of original/new input files=',self.Ninput_files_orig,self.Ninput_files)

    if(not Diagnostic): #get rid of not.
      print('self.input_files=',self.input_files)
  
    self.season_broadcast_override=False
    #self.season_broadcast_override=True #we might want to write out invididual months of a season rather than forming the seasonal average, override as this is not the usual.

    self.season_map={            'DJF':[12,1,2],            'MAM':[3,4,5],            'JJA':[6,7,8],            'SON':[9,10,11],            'JJAS':[6,7,8,9],            'ANN':[1,2,3,4,5,6,7,8,9,10,11,12],            'DecJan':[12,1],            'JunJul':[6,7],            'MON':[1,2,3,4,5,6,7,8,9,10,11,12],            'Jan':[1],            'Feb':[2],            'Mar':[3],            'Apr':[4],            'May':[5],            'Jun':[6],            'Jul':[7],            'Aug':[8],            'Sep':[9],            'Oct':[10],            'Nov':[11],            'Dec':[12],            } #months required for each seasonal definition, avoid ambiguity by using lowercase letters where necessary.

    self.season_broadcast={            'DJF':False,            'MAM':False,            'JJA':False,            'SON':False,            'JJAS':False,            'ANN':False,            'DecJan':False,            'JunJul':False,            'MON':True,            'Jan':True,            'Feb':True,            'Mar':True,            'Apr':True,            'May':True,            'Jun':True,            'Jul':True,            'Aug':True,            'Sep':True,            'Oct':True,            'Nov':True,            'Dec':True,            } #True means to broadcast all inputs times to the output, else it would be an average of all times.

    if(Diagnostic):
      print('self.season_map.keys()=',self.season_map.keys())
      print('self.season_broadcast.keys()=',self.season_broadcast.keys())

    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
    #various integrity test on season_map:
    for self.key in self.season_map.iterkeys():
      if(self.key not in self.season_broadcast):
        raise Exception('Missing matching self.key',self.key,' in self.season_broadcast dictionary file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
      self.unique_season_map_key=list(set(self.season_map[self.key]))
    #print(sorted(self.unique_season_map_key),sorted(self.season_map[self.key]))
      if(not sorted(self.unique_season_map_key)==sorted(self.season_map[self.key])):
        raise Exception('self.season_map must have unique numbers in it file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
      self.test_season_map_key=array("i",self.season_map[self.key])
      if(min(self.test_season_map_key)<0 or max(self.test_season_map_key)>12):
        raise Exception('Month indices must be between 1 and 12 file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

    #various tests on season_broadcast
    for self.key in self.season_broadcast.iterkeys():
      if(self.key not in self.season_map):
        raise Exception('Missing matching self.key',self.key,' in self.season_map dictionary file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
      if(type(self.season_broadcast[self.key])!=types.BooleanType):
        raise Exception('self.season_broadcast must be True or False file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    
    if(self.season in self.season_map):
      print('Found season definition',self.season,' in self.season_map with indices ',self.season_map[self.season],' file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    else:
      raise Exception('Season definition not in self.season_map file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

    if(self.season_broadcast_override and self.season_broadcast[self.season]):
      raise Exception('self.season_broadcast and chosen season already broadcast, perhaps set self.season_broadcast_override=False :'+__file__+' line number: '+str(inspect.stack()[0][2]))
 
    if(self.season_broadcast_override and not self.season_broadcast[self.season]): #this must occur after previous test.
      print('Overriding default self.season_broadcast setting, i.e. broadcasting seasonal values rather than this season\'s normal averaging.')
      self.season_broadcast[self.season]=True
  
    if(self.season_broadcast[self.season] and self.season=='ANN'):
      raise Exception('Doesn\'t make sense to broadcast season ANN, use season MON instead file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

    #print('self.season_brodcast=',self.season_broadcast)
  
    self.month_indices=self.season_map[self.season]
    self.npmonth_indices=np.array(self.month_indices)
  
    try:
      mbeg_season_process_test=dir(self).index('mbeg_season_process')
    except ValueError:
      mbeg_season_process_test=-1
      
    try:
      mend_season_process_test=dir(self).index('mend_season_process')
    except ValueError:
      mend_season_process_test=-1
      
    if(mbeg_season_process_test>=0 and mend_season_process_test>=0):
      if(self.mbeg_season_process<1 or self.mbeg_season_process>12 or self.mend_season_process<1 or self.mend_season_process>12):
        raise Exception('Processing months must be between 1 and 12.')
    else:
      raise Exception('mbeg_season_process and/or mend_season_process not set.')

    #print('mbeg_season_process_test=',mbeg_season_process_test)
    
    #raise SystemExit('STOP!:'+__file__+' line number: '+str(inspect.stack()[0][2]))

#    if('self.mbeg_season_process' in locals()):
#      if(self.mbeg_season_process<1 or self.mbeg_season_process>12 or self.mend_season_process<1 or self.mend_season_process>12):
#        raise Exception('Processing months must be between 1 and 12.')
  
    if(self.season_broadcast[self.season] and (len(self.season_map[self.season])>1 and len(self.season_map[self.season])<12)):
      raise Exception('Note that cmor will not easily write out b/w 2 and 11 months out due to time_axis restrictions, however, might be something we can do in the future.')
      #print(len(self.season_map[self.season]))

    if(Diagnostic):
      print('Using month indices=',self.month_indices)
      
    try:
      ybeg_season_process_test=dir(self).index('ybeg_season_process')
    except ValueError:
      ybeg_season_process_test=-1

    try:
      yend_season_process_test=dir(self).index('yend_season_process')
    except ValueError:
      yend_season_process_test=-1
      
    if(ybeg_season_process_test>=0 and yend_season_process_test>=0):
      if(self.ybeg_season_process>self.yend_season_process):
        raise Exception('self.ybeg_season>self.yend_season file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
        
#    if('self.ybeg_season_process' in locals()):
#      if(self.ybeg_season_process>self.yend_season_process):
#        raise Exception('self.ybeg_season>self.yend_season file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
        
  def step1(self):
    '''
    Here we generate various time related vectors that will be used to select data from the inputs.
    We also need to calculate the min/max possible years as well as the min year if season crosses
    Dec/Jan monthly divide.
    '''
    import netCDF4
    import datetime
    import numpy as np
    #Diagnostic=True
    Diagnostic=False
    #Diagnostic=True

    self.ifhN=netCDF4.MFDataset(self.input_files)
    self.ifh0=netCDF4.Dataset(self.input_files[0])
    self.time=self.ifhN.variables['time'] #note that time-stamp appears to be last time in the month which has the next month ID.
    self.time_units=self.time.units
    self.time_calendar=self.time.calendar
    self.ntime_orig=len(self.time)

    try:
      num_months_truncate_test=dir(self).index('num_months_truncate')
    except ValueError:
      num_months_truncate_test=-1
      
#    if('self.num_months_truncate' in locals()):
    if(num_months_truncate_test>=0):
    
      max_ntimes=min(len(self.time),self.num_months_truncate) #truncate to maximum of 5 years.

      print('max_ntimes=',max_ntimes)

      self.time=self.time[0:max_ntimes]

    print('self.time.shape=',self.time.shape)
    print('self.time=',self.time)
    
    self.num_stamps=netCDF4.num2date(self.time[:],self.time_units,self.time_calendar) - datetime.timedelta(hours=self.hours) #take away 360 hours, 15 days which is a time approximately in the middle of the month to enable proper year/month determination.
    #self.ifhN.close() #would not close if within cafepp as would need to read data arrays too.

    #print('self.time=',self.time[:])

    self.timegrad=np.gradient(self.time[:])

    print('self.timegrad=',self.timegrad)

    check_days=np.where(self.timegrad.any()>30. and self.timegrad.any()<29.)

    #print('check_days.size=',check_days.size)
    print('check_days=',check_days)
    #print('len(check_days)=',len(check_days))

    self.years=[]
    self.months=[]
    self.iS=[]
    self.iSp1=[]
    self.MonfromStart=[]

    for _i,_num_stamp in enumerate(self.num_stamps):
      self.years.append(_num_stamp.year)
      self.months.append(_num_stamp.month)
      self.MonfromStart.append(self.num_stamps[0].month+_i)
      self.iS.append(_i)
      self.iSp1.append(_i+1)
  
    if(Diagnostic): #get rid of not.
      for _i,_num_stamp in enumerate(self.num_stamps):
        print('_i,_i+1,self.MonfromStart,self.year,self.month,_num_stamp=',_i,_i+1,self.MonfromStart[_i],self.years[_i],self.months[_i],_num_stamps[_i])

    self.npyears=np.array(self.years)
    self.npmonths=np.array(self.months)

    self.ybeg_min=np.min(self.npyears) #first year in the original time-series
    self.yend_max=np.max(self.npyears) #last year in the original time-series

    self.index_mbeg_min=np.argmin(self.npyears)
    self.index_mend_max=np.argmax(self.npyears[::-1])

    self.npmonths_reverse=self.npmonths[::-1]
    self.mbeg_min=self.npmonths[self.index_mbeg_min] #minimum month in first year of the original time-series.
    self.mend_max=self.npmonths_reverse[self.index_mend_max] #maximum month in last year of the original time-series.

    #print(npmonth_indices.size)

    if(self.npmonth_indices.size>1 and any(np.gradient(self.npmonth_indices)<0)):
      self.SeasonCrossDecJan=True
    else:
      self.SeasonCrossDecJan=False

    if(self.SeasonCrossDecJan):
      if(Diagnostic): print('Season definition includes December/January and so one year is lost cf. to the total number of years present.')
      self.ybeg_season_min=self.ybeg_min+1
    else:
      self.ybeg_season_min=self.ybeg_min

    try:
      ybeg_season_process_test=dir(self).index('ybeg_season_process')
    except ValueError:
      ybeg_season_process_test=-1
      
    if(ybeg_season_process_test==-1): #if one missing then assume all set to full range.
      print('deleting process ranges...')
      self.ybeg_season_process=self.ybeg_min
      self.yend_season_process=self.yend_max
      self.mbeg_season_process=self.mbeg_min
      self.mend_season_process=self.mend_max
  
    if(not Diagnostic):
      print('self.ybeg_min,self.yend_max,self.mbeg_min,self.mend_max,self.ybeg_season_min=',self.ybeg_min,self.yend_max,self.mbeg_min,self.mend_max,self.ybeg_season_min)

    if(not Diagnostic):
      print('self.ybeg_season_process,self.yend_season_process,self.mbeg_season_process,self.mend_season_process=',self.ybeg_season_process,self.yend_season_process,self.mbeg_season_process,self.mend_season_process)
    
    print('END of STEP1')
    
    return
  
  def step2(self):
    #Diagnostic=True
    Diagnostic=False
    #Diagnostic=True
    import netCDF4
    import numpy as np

    if(not Diagnostic):
      print('self.ybeg_min,self.yend_max,self.mbeg_min,self.mend_max,self.ybeg_season_min=',self.ybeg_min,self.yend_max,self.mbeg_min,self.mend_max,self.ybeg_season_min)

    if(not Diagnostic):
      print('self.ybeg_season_process,self.yend_season_process,self.mbeg_season_process,self.mend_season_process=',self.ybeg_season_process,self.yend_season_process,self.mbeg_season_process,self.mend_season_process)

    self.len_months=len(self.months) #or years
    self.len_month_indices=len(self.month_indices)

    if(self.season_broadcast[self.season]):
      print('Here we are broadcasting, for MON will print out all available months unless mbeg_season_process,mend_season_process defined otherwies.')

    print('self.broadcast=',self.season_broadcast[self.season])
    print('season=',self.season)

    if(self.season=='MON'):
      print('Special case, print out all months unless restricted by mbeg_season_process,mend_season_process.')

      #modify monthly min/max to process, if appropriate:
      if(self.ybeg_season_process<self.ybeg_min and self.mbeg_season_process<self.mbeg_min):
        raise SystemExit('Processing year/month is less than what is available: '+__file__+' line number: '+str(inspect.stack()[0][2]))
    
      if(self.yend_season_process>self.yend_max and self.mend_season_process>self.mend_max):
        raise SystemExit('Processing year/month is greater than what is available: '+__file__+' line number: '+str(inspect.stack()[0][2]))

      if(self.ybeg_season_process==self.ybeg_min and self.mbeg_season_process<self.mbeg_min):
        print('First year to be processed is less than available, setting to be same.')
        self.mbeg_season_process=self.mbeg_min
  
      if(self.yend_season_process==self.yend_max and self.mend_season_process>self.mend_max):
        print('Last year to be processed is more than available, setting to be same.')
        self.mend_season_process=self.mend_max
    
      if(not Diagnostic):
        print('self.ybeg_season_process,self.yend_season_process,self.mbeg_season_process,self.mend_season_process=',self.ybeg_season_process,self.yend_season_process,self.mbeg_season_process,self.mend_season_process)

      #raise Exception('STOP!')
    
      #self.mbeg_season_process=self.mbeg_min
      #if(self.yend_season_process<=self.yend_max): self.mend_season_process=self.mend_max
  
      _jjj=np.where(self.npyears==self.ybeg_season_process,1,0)
      _kkk=np.where(self.npmonths==self.mbeg_season_process,1,0)
      _lll=_jjj+_kkk
      _begpos=np.argmax(_lll)
      #print('_jjj=',_jjj)
      #print('len(_jjj)=',len(_jjj))
      #print('_kkk=',_kkk)
      #print('len(_kkk)=',len(_kkk))
      print('_lll=',_lll)
  
      _jjj=np.where(self.npyears==self.yend_season_process,1,0)
      _kkk=np.where(self.npmonths==self.mend_season_process,1,0)
      _lll=_jjj+_kkk
      _endpos=np.argmax(_lll)
      #print('_jjj=',_jjj)
      #print('len(_jjj)=',len(_jjj))
      #print('_kkk=',_kkk)
      #print('len(_kkk)=',len(_kkk))
      print('_lll=',_lll)
  
      print('_begpos,_endpos=',_begpos,_endpos)
  
      self.years_defined=sorted(set(self.npyears[_begpos:_endpos+1]))
      print('self.years_defined=',self.years_defined)
      #print(self.npyears[_begpos:_endpos+1],self.npmonths[_begpos:_endpos+1],self.MonfromStart[_begpos:_endpos+1])
  
      _listA,_listB=[],[]
      self.season_indices_defined=[]
      self.season_month_indices_defined=[]
  
      yearNow=self.npyears[_begpos]
      #print('yearNow=',yearNow)
      for _iii,_ppp in enumerate(range(_begpos,_endpos+1)): #loop over the years & months of interest only with _begpos & _endpos
        print('_iii,self.npyears[_ppp],self.npmonths[_ppp],self.MonfromStart[_ppp]',_ppp,self.npyears[_ppp],self.npmonths[_ppp],self.MonfromStart[_ppp])

        #yearNow=self.npyears[_ppp]
        #print('_listA,_listB=',_listA,_listB)
        #raise Exception('XXX!')
    
        #print(type(self.npyears[_ppp]),type(yearNow))
        if(self.npyears[_ppp]!=yearNow):
          #print('_listA,_listB=',_listA,_listB)
          self.season_indices_defined.append(_listA)
          self.season_month_indices_defined.append(_listB)
          _listA,_listB=[],[]
          _listA.append(self.npmonths[_ppp])
          _listB.append(self.MonfromStart[_ppp])
          yearNow=self.npyears[_ppp]
        else:
          #raise Exception('XXX!')
          _listA.append(self.npmonths[_ppp])
          _listB.append(self.MonfromStart[_ppp])

      #last ones are not picked up by if/else, need to do here or change logic above a bit.
      self.season_indices_defined.append(_listA)
      self.season_month_indices_defined.append(_listB)

          #yearNow=self.npyears[_iii]
          #print('_listA,_listB=',_listA,_listB)
        #raise Exception('XXX!')
      #print('self.season_indices_defined (#'+str(len(self.season_indices_defined))+') =',self.season_indices_defined)
      #print('self.season_month_indices_defined (#'+str(len(self.season_month_indices_defined))+') =',self.season_month_indices_defined)
      #raise Exception('STOP!')
  
    else: #seasons!='MON'

      self.season_indices_defined = []
      self.season_month_indices_defined = [] #new
      self.years_defined = [] #based on success of season indice matching.

      for _i in range(self.len_months): #maybe use xrange
        self.segment=self.npmonths[_i:_i+self.len_month_indices]
        #print('type(segment)=',type(segment))
        #jjj=set(segment)
        #kkk=set(npmonth_indices)
        #print('jjj,kkk=',jjj,kkk)
    
        if (np.array_equal(self.segment,self.npmonth_indices)):
          #print('yes')
          self.season_month_indices_defined.append((range(_i+1, _i+self.len_month_indices+1)))
          self.season_indices_defined.append(self.months[_i:_i+self.len_month_indices]) #new, this will be used to work out monthly weights in cafepp.
          self.years_defined.append(self.years[_i])
      
      if(Diagnostic):   
        print('self.season_indices_defined=',self.season_indices_defined)
        print('self.season_month_indices_defined=',self.season_month_indices_defined)
        print('self.years_defined=',self.years_defined)
  
      #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    
      self.years_season_valid=[] #can use this to determine if a valid minimum or maximum year is selected, the default would be all years.
  
      for _year in range(self.ybeg_season_min,self.yend_max+1):
        self.years_season_valid.append(_year)

    if(not self.SeasonCrossDecJan):
      self.cross_beg=self.years_defined.index(self.ybeg_season_process) #cross may not be good choice but better than vague one I had.
      self.cross_end=self.years_defined.index(self.yend_season_process)

      if(Diagnostic):
        print('self.cross_beg,end=',self.cross_beg,self.cross_end)

      #overwrite if necessary based on processed years indices self.cross_beg,end found above:
      self.season_indices_defined=self.season_indices_defined[self.cross_beg:self.cross_end+1]
      self.season_month_indices_defined=self.season_month_indices_defined[self.cross_beg:self.cross_end+1]
      self.years_defined=self.years_defined[self.cross_beg:self.cross_end+1]

      if(Diagnostic):
        print('self.season_indices_defined (#'+str(len(self.season_indices_defined))+') =',self.season_indices_defined)
        print('self.season_month_indices_defined (#'+str(len(self.season_month_indices_defined))+') =',self.season_month_indices_defined)
        print('self.years_defined (#'+str(len(self.years_defined))+') =',self.years_defined)
  
        #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
    elif(self.SeasonCrossDecJan): #need to add one for seasons that cross the Dec/Jan divide.
      self.nparray_years_defined=np.array(self.years_defined)
      self.nparray_years_defined+=1
      self.years_defined = []
      for _i,_year in enumerate(self.nparray_years_defined): #the reassign back to year_defined, nparray_years not needed anymore.
        self.years_defined.append(_year)
      del(self.nparray_years_defined)

      self.cross_beg=self.years_defined.index(self.ybeg_season_process)
      self.cross_end=self.years_defined.index(self.yend_season_process)

      self.season_indices_defined=self.season_indices_defined[self.cross_beg:self.cross_end+1]
      self.season_month_indices_defined=self.season_month_indices_defined[self.cross_beg:self.cross_end+1]
      self.years_defined=self.years_defined[self.cross_beg:self.cross_end+1]
  
    if(not Diagnostic):
      #print('self.nparray_years_defined=',self.nparray_years_defined)
      try:
        years_season_valid_test=dir(self).index('years_season_valid')
      except ValueError:
        years_season_valid_test=-1
      
      if(years_season_valid_test>=0): print('self.years_season_valid (#'+str(len(self.years_season_valid))+') =',self.years_season_valid) #can't trust this b/c although might have final year, all months may not be present.
      print('self.season_indices_defined (#'+str(len(self.season_indices_defined))+') =',self.season_indices_defined)
      print('self.season_month_indices_defined (#'+str(len(self.season_month_indices_defined))+') =',self.season_month_indices_defined)
      print('self.years_defined (#'+str(len(self.years_defined))+') =',self.years_defined)

    if(self.season != 'MON' and (self.ybeg_season_process not in self.years_season_valid or self.yend_season_process not in self.years_season_valid)):
      raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

    print('self.month_indices=',self.month_indices)

    print(' So now we could loop over years_defined, each vector of season_indices_defined can be used then be used to broadcast/average.')
        
    print('END of STEP2')
    
    return
  
  def step3(self):
    '''
    Here, show how these vectors can be used to select our the times from the inputs files. 
    years_defined and season_indices_defined are of the same size, years_seson_valid are the 
    possible year range that can be selected between. Actually, the indices are already provided 
    in season_indices_defined. Each set will provide a value for the year defined in years_defined.
    '''
    Diagnostic=False
    #for _i,_year in enumerate(self.years_defined):
    #  print('_i,_year,self.season_indices_defined[self.i]=',_i,_year,self.season_indices_defined[self.i])
    #print('self.ybeg_season_process,self.yend_season_process,self.mbeg_season_process,self.mend_season_process=',self.ybeg_season_process,self.yend_season_process,self.mbeg_season_process,self.mend_season_process)
    #print('self.years_defined.index(self.ybeg_season_process=',self.years_defined.index(self.ybeg_season_process))

    for _i,_year in enumerate(range(self.ybeg_season_process,self.yend_season_process+1)):
      #print(self.season_indices_defined[self.years_defined.index(_year)])
      self.values=self.season_indices_defined[self.years_defined.index(_year)]
      self.values2=self.season_month_indices_defined[self.years_defined.index(_year)]
      print('_i,_year,self.values,self.values2=',_i,_year,self.values,self.values2)
    
    print('END of STEP3')

    return
  
  def step4(self):
    import netCDF4
    import datetime
    import numpy as np
    Diagnostic=False
    self.time_stamp_beg,self.time_stamp_end=[],[]

    if(self.season_broadcast[self.season]): #broadcast 
      for _i,_year in enumerate(range(self.ybeg_season_process,self.yend_season_process+1)):
        #print('_year=',_year)
        self.npvalues=np.array(self.season_indices_defined[self.years_defined.index(_year)])-1
        self.npvalues2=np.array(self.season_month_indices_defined[self.years_defined.index(_year)])-1
    
        self.firstvalue=self.season_indices_defined[self.years_defined.index(self.ybeg_season_process)][0]-1 #this is used for dealing with different months starting first year.
    
        print('self.firstvalue=',self.firstvalue)
        #raise SystemExit('STOP!')
    
        #try this
        #if(self.i==0):
        #  self.npvalues=self.npvalues-1
        #if(self.firstvalue>=1):
        self.npvalues2=self.npvalues2-self.firstvalue
      
        print('self.npvalues=',self.npvalues)
        print('self.npvalues2=',self.npvalues2)
    
        #print(self.num_stamps[self.npvalues])
        #print('self.npyears[self.npvalues]',self.npyears[self.npvalues2])
        #print('self.npmonths[self.npvalues]=',self.npmonths[self.npvalues2])
  
        #print('self.npyears=',self.npyears)
        #if(self.i==1): raise SystemExit('STOP!')
  
        for _j,self.npyear in enumerate(self.npyears[self.npvalues2]):
          print('_j,self.npyear,self.npmonths[self.npvalues2][_j]=',_j,self.npyear,self.npmonths[self.npvalues2][_j])
          self.time_stamp_beg.append(datetime.datetime(self.npyear,self.npmonths[self.npvalues2][_j],1) + datetime.timedelta(hours=0.0))

          #raise SystemExit('STOP!')
      
          _mmm=self.npmonths[self.npvalues2][_j]+1
          if(_mmm>12):
            _mmm=1
            _yyy=self.npyear+1
          else:
            _yyy=self.npyear
        
          self.time_stamp_end.append(datetime.datetime(_yyy,_mmm,1) + datetime.timedelta(hours=0.0))

      #raise SystemExit('STOP!')

    #  for self.k,dummy in enumerate(self.time_stamp_beg):                       
    #    print('self.k,self.time_stamp_beg[self.k],self.time_stamp_end[self.k]=',self.k,self.time_stamp_beg[self.k],self.time_stamp_end[self.k])
                       
    else: #not broadcast=seasonal average
      for _i,_year in enumerate(range(self.ybeg_season_process,self.yend_season_process+1)):
        self.npvalues=np.array(self.season_indices_defined[self.years_defined.index(_year)])-1
        self.npvalues2=np.array(self.season_month_indices_defined[self.years_defined.index(_year)])-1
    
        print('self.npvalues,self.npvalues2,self.npyears[self.npvalues],self.npmonths[self.npvalues]=',self.npvalues,self.npvalues2,self.npyears[self.npvalues],self.npmonths[self.npvalues])

        self.time_stamp_beg.append(datetime.datetime(self.npyears[self.npvalues2[0]],self.npmonths[self.npvalues[0]],1) + datetime.timedelta(hours=0.0))

        _mmm=self.npmonths[self.npvalues[-1]]+1
        if(_mmm>12):
          _mmm=1
          _yyy=self.npyears[self.npvalues2[-1]]+1
        else:
          _yyy=self.npyears[self.npvalues2[-1]]
    
        self.time_stamp_end.append(datetime.datetime(_yyy,_mmm,1) + datetime.timedelta(hours=0.0))

    #continue on
    self.time_beg=netCDF4.date2num(self.time_stamp_beg,self.time_units,self.time_calendar)
    self.time_end=netCDF4.date2num(self.time_stamp_end,self.time_units,self.time_calendar)

    #I could do an average of the year/month stamp rather than an aveage of beg/end, might be same.

    self.time_avg=(self.time_beg+self.time_end)/2.0

    self.time_bounds=np.column_stack((self.time_beg,self.time_end))

    self.time_stamp_avg=netCDF4.num2date(self.time_avg,self.time_units,self.time_calendar)
    if(not Diagnostic):
      for _dummyi,_dummy in enumerate(self.time_stamp_beg):
        print('_dummyi,self.time_stamp_beg,avg,end=',_dummyi,self.time_stamp_beg[_dummyi],self.time_stamp_avg[_dummyi],self.time_stamp_end[_dummyi])
    
    print('END of STEP4')

    return
