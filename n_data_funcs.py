class n_data_funcs:
  '''
  Assumes:
  
  1. that all inputs have same horizontal resolution (latxlon). So if want to compare different products
  (e.g. models) will need to interpolate to the same grid.
  
  2. that all ensembles have the same number of times but not necessarily same input file structure (e.g. they could have different numbers of files).
  
  3. note that sometimes the Diag=True/False needs to be first in the argument list for the diagnostics to operate normally.
  
  '''
  import netCDF4
  import math
  import numpy as np
  import numpy.ma as ma
  import inspect
  import itertools

  nmy=12
  rad = 4.0*math.atan(1.0)/180.0
  days_in_month = [31,28,31,30,31,30,31,31,30,31,30,31]
  
  #def __init__(self, input_files, input_var_name, **kwargs):
  def __init__(self, **kwargs):
    import netCDF4
    import math
    import numpy as np
    import numpy.ma as ma
    import inspect
    import itertools
    #self.ensembles=False
    Diag=False
    dummy_mode=None
    self.dummy_mode = False
    for key, value in kwargs.items():
      if(key=='Diag'):
        Diag=bool(value)
      elif(key=='input_files'):
        input_files=value
        if(Diag): print('input_files=',input_files)
      elif(key=='input_var_name'):
        input_var_name=value
        if(Diag): print('input_var_name=',input_var_name)
      elif(key=='dummy_mode'):
        dummy_mode=value
        if(Diag): print('len(dummy_mode)=',len(dummy_mode))
      else:
        raise SystemExit('Dont know that key.'+__file__+' line number: '+str(inspect.stack()[0][2]))

    if(type(input_files)==type(None) or type(input_var_name)==type(None)):
      if(Diag): print('n_data_funcs.init: Dummy mode...')
#normally self.nfiles>1 for ensemble data, however, in monthly_clim_anom this is 
#is used to manage time functions, and as we are supplying a single time variable
#rather than a nested one as with normal ensemble data, it will work O.K.
      if(type(dummy_mode)!=type(None)):
        if(Diag): print('n_data_funcs.init: Get tuple here...')
        self.daily_to_monthly_test, _dummy_time_stamp, _dummy_num_stamp, _dummy_time_units, _dummy_calendar = dummy_mode
        #print('n_data_funcs.init: self.daily_to_monthly_test=',self.daily_to_monthly_test)        
        #print('n_data_funcs.init: _dummy_time_stamp=',_dummy_time_stamp)
        self.time_tfreq_units = _dummy_time_units
        self.time_tfreq_calendar = _dummy_calendar
        self.dummy_mode = True
        if(self.daily_to_monthly_test):
          self.date_time_stamp_monthly = _dummy_time_stamp
          self.num_stamp_monthly = _dummy_num_stamp #this comes from daily_to_monthly function
          #self.nfiles=None
        else:
          self.date_time_stamp_tfreq =_dummy_time_stamp
          self.time_tfreq = _dummy_num_stamp
          #self.nfiles=None
      else:
         raise SystemExit('n_data_funcs.init dummy_mode:'+__file__+' line number: '+str(inspect.stack()[0][2]))               
    else:
      self.daily_to_monthly_test=False 
      self.input_files = input_files
      self.input_files_flat = list(itertools.chain.from_iterable(input_files))
      self.input_var_name = input_var_name
      if(len(self.input_files)==1):
        print('n_data_funcs.init: no ensembles in this example.')
      elif(len(self.input_files)>1):
        print('n_data_funcs.init: ensembles in this example.')
      else:
        raise SystemExit('n_data_funcs.init issue with ensembles check:'+__file__+' line number: '+str(inspect.stack()[0][2])) 

    #self.ensembles=True
    #self.rad = 4.0*math.atan(1.0)/180.0
#  for sublist in cafe_files:
#      for item in sublist:
#        cafe_files_flat.append(item)      
    #setattr(self, input_files, input_files)
    #setattr(self, input_var_name, input_var_name)
    #print('len(input_files)=',len(input_files))
    #print(type(input_files))
    #print(input_files.__len__())
    #self.input_files = []
    #self.input_files_flat=[item for sublist in input_files for item in sublist]
    #self.nmy = 12
    #if(len(self.input_files)!=)
#    print('self.input_files=',self.input_files)
#    print('len(self.input_files)=',len(self.input_files))
#    print('self.input_files_flat=',self.input_files_flat)
#    print('len(self.input_files_flat)=',len(self.input_files_flat))

  def calculate_filedatetime_info_multiforc(self,nino,**kwargs):
    Diag=False
    for key, value in kwargs.items():
      if(key=='Diag'):
        Diag=bool(value)
      else:
        raise SystemExit('Dont know that key.'+__file__+' line number: '+str(inspect.stack()[0][2]))
        
    from ipywidgets import FloatProgress
    #%matplotlib inline
    floatprogress = FloatProgress(min=0, max=len(self.input_files), description='Loading...') 
    display(f)
    
    #print(nino.nindices_nino)
    #raise SystemExit('STOP!:'+__file__+' line number: '+str(inspect.stack()[0][2]))      
    
    self.nfiles=len(self.input_files)
    #print('nfiles=',self.nfiles)
    self.ens=[]
    #self.ifhs=[]
    
    self.date_time_stamps=[]
    self.times=[]
    self.mins=[]
    self.maxs=[]
    self.calendar=[]
    self.units=[]
      
    for cnt_i,input_file in enumerate(self.input_files):
      #print('i,input_file=',cnt_i,input_file)
      input_file_tail=os.path.basename(input_file)
      input_file_head=string.split(input_file,sep=input_file_tail)[0]
      var,table,experiment,model,ripf,grid,datetime=cmor_file_parts(input_file_tail)
      rval,ival,pval,fval=cmor_ripf_parts(ripf)
      version,grid,var,table,ripf,experiment,model,institution,activity,cmip=cmor_directory_parts(input_file_head)
      self.ens.append(rval)
      #self.ifhs.append(netCDF4.Dataset(input_file))
      ifhs=netCDF4.Dataset(input_file)
      
      #self.times.append(self.ifhs[cnt_i].variables['time'])        
      self.times.append(ifhs.variables['time'][:])
      dummy_times=ifhs.variables['time']
      
      self.units.append(dummy_times.units)
      self.calendar.append(dummy_times.calendar)
      #print(self.units)
      #raise SystemExit('STOP!:'+__file__+' line number: '+str(inspect.stack()[0][2]))      

      if(cnt_i==0):
        self.lat=ifhs.variables['latitude'][:,0]
        self.lon=ifhs.variables['longitude'][0,:]
        #self.ifhs0=netCDF4.Dataset(input_file)
      #ifhs.close()
      
      #print(self.times[cnt_i].calendar)
      if(cnt_i>0):  #check that same calendar/units are in use, otherwise would need to convert to common one.
        if(self.calendar[cnt_i]!=self.calendar[cnt_i-1]): raise SystemExit('calendars not matching:'+__file__+' line number: '+str(inspect.stack()[0][2]))
        if(self.units[cnt_i]!=self.units[cnt_i-1]): raise SystemExit('units not matching:'+__file__+' line number: '+str(inspect.stack()[0][2]))
      self.mins.append(min(self.times[cnt_i]))
      self.maxs.append(max(self.times[cnt_i]))
      self.date_time_stamps.append(netCDF4.num2date(self.times[cnt_i],self.units[cnt_i],self.calendar[cnt_i]))

      if(cnt_i==0):
        self.npdate_time_stamps=netCDF4.num2date(self.times[cnt_i],self.units[cnt_i],self.calendar[cnt_i])
      else:
        self.npdate_time_stamps=np.append(self.npdate_time_stamps,netCDF4.num2date(self.times[cnt_i],self.units[cnt_i],self.calendar[cnt_i]))
    
      ifhs.close()
      floatprogress.value += 1 
      #raise SystemExit('STOP!:'+__file__+' line number: '+str(inspect.stack()[0][2])) 
      
    self.nptimes=np.array(self.times)

    self.npftimes=self.nptimes.flatten()

    self.year_min=netCDF4.num2date(min(self.mins),self.units[0],self.calendar[0])
    self.year_max=netCDF4.num2date(max(self.maxs),self.units[0],self.calendar[0]) #not year maximum as need to consider end of each experiment.

    print('calculate_filedatetime_info_multiforc: Forecast start times go from ',min(self.mins),'to',max(self.maxs),'or',self.year_min,'to',self.year_max)
    print('calculate_filedatetime_info_multiforc: Ensembles go from ',min(self.ens),'to',max(self.ens)) #later on restrict to only valid ensembles to keep arrays compact eg 1,2,3,11 but not 1-11.

    self.npens=np.array(list(set(self.ens)))

    self.nens=len(self.npens)

    self.ybeg,self.yend=netCDF4.num2date(min(self.mins),self.units[0],self.calendar[0]).year,netCDF4.num2date(max(self.maxs),self.units[0],self.calendar[0]).year
    self.mbeg,self.mend=netCDF4.num2date(min(self.mins),self.units[0],self.calendar[0]).month,netCDF4.num2date(max(self.maxs),self.units[0],self.calendar[0]).month

    j,k,self.date,m,n,self.time=get_timestamp_number(self.ybeg,self.yend,self.mbeg,self.mend,self.units[0],self.calendar[0])

    self.ntime=len(self.time)

    self.year_fraction_monthly=fractional_year_from_num2date(self.date,self.calendar[0])

    self.beg,self.end=np.zeros(self.nfiles,dtype=int),np.zeros(self.nfiles,dtype=int) #these indices define beg/end time indices.

    self.beg_cnt,self.end_cnt=np.zeros((self.nens,(self.nfiles/self.nens)),dtype=int),np.zeros((self.nens,(self.nfiles/self.nens)),dtype=int) #these indices define beg/end time indices.

    #self.lat=self.ifhs[0].variables['latitude'][:,0]
    #self.lon=self.ifhs[0].variables['longitude'][0,:]
    #self.lat=self.ifhs0.variables['latitude'][:,0]
    #self.lon=self.ifhs0.variables['longitude'][0,:]

    self.clat=np.cos(self.lat[:]*self.rad)
    self.nlat=len(self.lat)
    self.nlon=len(self.lon)

  def calculate_quantity_multiforc(self,dvar,nino,**kwargs):
    Diag=False
    for key, value in kwargs.items():
      if(key=='Diag'):
        Diag=bool(value)
      else:
        raise SystemExit('Dont know that key.'+__file__+' line number: '+str(inspect.stack()[0][2]))
        
    from ipywidgets import FloatProgress
    #%matplotlib inline
    f = FloatProgress(min=0, max=len(self.input_files), description='Loading...') 
    display(f)
    
    self.ens_cnt=np.zeros(self.nens,dtype=int)
    
    nino_monthly=ma.masked_equal( np.zeros((self.ntime,nino.nindices_nino,self.nens,(self.nfiles/self.nens)),dtype=float), 0.0) #set them all to missing value, then assign the forecasts to the various segments in the array.\\

    self.check=ma.zeros((nino.nindices_nino,self.nens,self.nfiles),dtype=int) #can use this to see how the arrays are being populated or not.
    
    for cnt_i,input_file in enumerate(self.input_files):
      #print('i,input_file=',cnt_i,input_file)

      ifhs=netCDF4.Dataset(input_file)
      
      self.beg_date=self.date_time_stamps[cnt_i][0]
      self.end_date=self.date_time_stamps[cnt_i][-1]

      self.begend_time=[netCDF4.date2num(self.beg_date,self.units[cnt_i],self.calendar[cnt_i]), netCDF4.date2num(self.end_date,self.units[cnt_i],self.calendar[cnt_i])]
      self.loc_beg,self.loc_end=np.where(self.time[:]==self.begend_time[0],1,0),np.where(self.time[:]==self.begend_time[1],1,0)
  
      self.beg[cnt_i],self.end[cnt_i]=np.argmax(self.loc_beg),np.argmax(self.loc_end)

      self.ens_cnt[self.ens[cnt_i]-1]+=1 #this is used to put each forecast in a unique ensemble slot in the array, the array should end up with equal values if the experiment is consistent & complete.

      self.beg_cnt[self.ens[cnt_i]-1,self.ens_cnt[self.ens[cnt_i]-1]-1], self.end_cnt[self.ens[cnt_i]-1,self.ens_cnt[self.ens[cnt_i]-1]-1]=np.argmax(self.loc_beg),np.argmax(self.loc_end)

      for k,indice in enumerate(nino.indices_nino):

        imin,imax=nino.indices_i[k][0],nino.indices_i[k][1]
        jmin,jmax=nino.indices_j[k][0],nino.indices_j[k][1]

        self.check[k,self.ens[cnt_i]-1,cnt_i] = self.check[k,self.ens[cnt_i]-1,cnt_i] + 1 #can use this for checking. For example, onece an array is set to 1 it should not be set/reset again (no overlap).

        #nino_monthly[self.beg[cnt_i]:self.end[cnt_i]+1,k,self.ens[i]-1,self.ens_cnt[self.ens[cnt_i]-1]-1]= \
        #  np.average(np.average(self.ifhs[cnt_i].variables[dvar][:,jmin:jmax+1,imin:imax+1],axis=1,weights=self.clat[jmin:jmax+1]),axis=1)
        nino_monthly[self.beg[cnt_i]:self.end[cnt_i]+1,k,self.ens[cnt_i]-1,self.ens_cnt[self.ens[cnt_i]-1]-1]= \
          np.average(np.average(ifhs.variables[dvar][:,jmin:jmax+1,imin:imax+1],axis=1,weights=self.clat[jmin:jmax+1]),axis=1)
      ifhs.close()
      floatprogress.value += 1
      
    return(nino_monthly)

  def monthly_clim_anom_multiforc(self,nino,**kwargs):
    Diag=False
    for key, value in kwargs.items():
      if(key=='Diag'):
        Diag=bool(value)
      elif(key=='input_monthly'):
        input_monthly=value
      elif(key=='input_monthly_climatology'):
        input_monthly_climatology=value
      else:
        raise SystemExit('Dont know that key.'+__file__+' line number: '+str(inspect.stack()[0][2]))
        
    #print('input_monthly.shape=',input_monthly.shape)
    #print('input_monthly_climatology.shape=',input_monthly_climatology.shape)
    
    self.nexps=input_monthly_climatology.shape[-1] #perhaps a better solution can be found for this.
    
    nino_anomaly_step1=np.expand_dims(input_monthly,-1)

    nino_anomaly=np.tile(nino_anomaly_step1,(self.nexps))

    #print('nino_anomaly.shape=',nino_anomaly.shape)

    self.years,self.months,self.days,self.hours=[],[],[],[]
    self.yearsM1,self.monthsM1,self.daysM1,self.hoursM1=[],[],[],[]
    for i,self.date_now in enumerate(self.date):
      self.years.append(self.date_now.year)
      self.months.append(self.date_now.month)
      self.days.append(self.date_now.day)
      self.hours.append(self.date_now.hour)
      self.yearsM1.append(self.date_now.year-1)
      self.monthsM1.append(self.date_now.month-1)
      self.daysM1.append(self.date_now.day-1)
      self.hoursM1.append(self.date_now.hour-1)

    self.ens_cnt=np.zeros(self.nens,dtype=int)

    for i,input_file in enumerate(self.input_files):

      self.year_beg,self.year_end=self.years[self.beg[i]],self.years[self.end[i]]
      self.month_beg,self.month_end=self.months[self.beg[i]],self.months[self.end[i]]
      self.mbeg,self.mend=1,12
      self.ybeg,self.yend=self.year_beg,self.year_end
      if(self.month_beg!=1): self.ybeg,self.mbeg=self.year_beg+1,1
      if(self.month_end!=12): self.yend,self.mbeg=self.year_end-1,12
      self.ens_cnt[self.ens[i]-1]+=1
  
      for k,indice in enumerate(nino.indices_nino):
        for clim_cnt in range(self.nexps):
          nino_anomaly[self.beg[i]:self.end[i]+1,k,self.ens[i]-1,self.ens_cnt[self.ens[i]-1]-1,clim_cnt] = \
          nino_anomaly[self.beg[i]:self.end[i]+1,k,self.ens[i]-1,self.ens_cnt[self.ens[i]-1]-1,clim_cnt] - \
          input_monthly_climatology[self.monthsM1[self.beg[i]:self.end[i]+1],k,clim_cnt]
  
    return(nino_anomaly)
        
  def calculate_filedatetime_info(self,**kwargs):
    import netCDF4
    import math
    import numpy as np
    import numpy.ma as ma
    import inspect
    import itertools
    from decadal_diag import \
      fractional_year_from_num2date

#    if(len(self.input_files)==1):
#      print('n_data_fincs.init: no ensembles in this example.')
#    elif(len(self.input_files)>1):
#      print('n_data_funcs.init: ensembles in this example.')
#    else:
#      raise SystemExit('n_data_funcs.init issue with ensembles check:'+__file__+' line number: '+str(inspect.stack()[0][2])) 
      
  #def calculate(self, **kwargs):
    calendar_check=units_check=Diag=False
    
    for key, value in kwargs.items():
      #print('key,value=',key,value)
      if(key=='Diag'):
        Diag=bool(value)
      elif(key=='calendar'):
        self.time_tfreq_calendar=kwargs[key]
        calendar_check=True
      elif(key=='units'):
        self.time_tfreq_units=kwargs[key]
        units_check=True
      else:
        raise SystemExit('Dont know that key.'+__file__+' line number: '+str(inspect.stack()[0][2]))
        
    if(not calendar_check):
      print('calculate_filedatetime_info: Setting to default calendar: julian')
      self.time_tfreq_calendar='julian'
      
    #print('len(self.input_files)=',len(self.input_files))
    #print('len(self.input_files_flat)=',len(self.input_files_flat))          
    
    if(Diag): print('self.input_files=',self.input_files)
    
    self.nfiles=len(self.input_files)
    self.nfiles_flat=len(self.input_files_flat) 
    
    #print('self.nfiles,self.nfiles_flat=',self.nfiles,self.nfiles_flat)
    #print('self.input_files=',self.input_files)
    #print('self.input_files[0][0]=',self.input_files[0][0])
    #print('self.input_files[0][:]=',self.input_files[0][:])

    if(self.nfiles==1 and self.nfiles_flat==1):
      print('calculate_filedatetime_info: case 1: no ensembles, one input file.')
      if(Diag): print('self.input_files=',self.input_files)
      if(Diag): print('self.input_files[0][0]=',self.input_files[0][0])
      self.ifhN=netCDF4.Dataset(self.input_files[0][0])
      self.ifh0=[self.ifhN]
      self.time_tfreq=self.ifh0[0].variables['time']
      self.ntime_tfreq=len(self.time_tfreq)
      if(units_check):
        self.date_time_stamp_tfreq=netCDF4.num2date(self.time_tfreq[:],self.time_tfreq_units,self.time_tfreq_calendar)
      else:
        self.date_time_stamp_tfreq=netCDF4.num2date(self.time_tfreq[:],self.time_tfreq.units,self.time_tfreq_calendar)
      self.year_fraction_tfreq=fractional_year_from_num2date(self.date_time_stamp_tfreq,self.time_tfreq_calendar)
      
    elif(self.nfiles==1 and self.nfiles_flat>1):
      print('calculate_filedatetime_info: case 2: no ensembles, multiple input files.')
      self.ifhN=netCDF4.MFDataset(self.input_files[0][:])
      self.ifh0=[netCDF4.Dataset(self.input_files[0][0])]
      self.time_tfreq=self.ifhN.variables['time']
      self.ntime_tfreq=len(self.time_tfreq)
      self.date_time_stamp_tfreq=netCDF4.num2date(self.time_tfreq[:],self.time_tfreq.units,self.time_tfreq_calendar)
      self.year_fraction_tfreq=fractional_year_from_num2date(self.date_time_stamp_tfreq,self.time_tfreq_calendar)

    elif(self.nfiles>1 and self.nfiles_flat==self.nfiles):   
      print('calculate_filedatetime_info: case 3: ensembles but only one file for each ensemble.')
      
      self.ifhN,self.ifh0=[],[]
      for input_file in self.input_files:
        #print('input_file=',input_file)
        self.ifhN.append(netCDF4.Dataset(input_file[0]))
      #print(type(self.ifhN))
      self.ifh0=[self.ifhN]
      
      self.time_tfreq,self.ntime_tfreq=[],[]
      for cnt,ifh0 in enumerate(self.ifh0):
        self.time_tfreq.append(ifh0[0].variables['time'])
        self.ntime_tfreq.append(len(self.time_tfreq[cnt]))
    
      self.date_time_stamp_tfreq,self.year_fraction_tfreq=[],[]
      for cnt,time_tfreq in enumerate(self.time_tfreq):
        self.date_time_stamp_tfreq.append(netCDF4.num2date(time_tfreq[:],self.time_tfreq[0].units,self.time_tfreq_calendar))
        self.year_fraction_tfreq.append(fractional_year_from_num2date(self.date_time_stamp_tfreq[cnt],self.time_tfreq_calendar))
      
    elif(self.nfiles>1 and self.nfiles_flat>self.nfiles):   
      print('calculate_filedatetime_info: case 4: ensembles with more than one file for each ensemble.')
      
      self.ifhN,self.ifh0=[],[]
      for input_file in self.input_files:
        #print('input_file=',input_file)
        self.ifhN.append(netCDF4.MFDataset(input_file[:]))
        self.ifh0.append(netCDF4.Dataset(input_file[0]))
        
      self.time_tfreq,self.ntime_tfreq=[],[]
      for cnt,ifhN in enumerate(self.ifhN):
        self.time_tfreq.append(ifhN.variables['time'])
        self.ntime_tfreq.append(len(self.time_tfreq[cnt]))
        
      #print('self.time_tfreq[0].units=',self.time_tfreq[0].units)
      
      self.date_time_stamp_tfreq,self.year_fraction_tfreq=[],[]
      for cnt,time_tfreq in enumerate(self.time_tfreq):
        self.date_time_stamp_tfreq.append(netCDF4.num2date(time_tfreq[:],self.time_tfreq[0].units,self.time_tfreq_calendar))
        self.year_fraction_tfreq.append(fractional_year_from_num2date(self.date_time_stamp_tfreq[cnt],self.time_tfreq_calendar))
        
    else:
      raise SystemExit('calculate_filedatetime_info: Dont know this case:'+__file__+' line number: '+str(inspect.stack()[0][2]))      

    #assume all calendars are the same...
    #print('self.time_tfreq=',self.time_tfreq)
    #if(len(self.time_tfreq)>1):
    if(self.nfiles>1): #ensembles
      self.time_tfreq_units=self.time_tfreq[0].units
    else:
      self.time_tfreq_units=self.time_tfreq.units
      
    #print('self.time_tfreq_units=',self.time_tfreq_units)
    
    #raise SystemExit('STOP!:'+__file__+' line number: '+str(inspect.stack()[0][2]))      
#    if(self.nfiles>1):
#      self.ifhN=netCDF4.MFDataset(self.input_files)
#      self.ifh0=netCDF4.Dataset(self.input_files[0])
#    else:
#      self.ifhN=self.ifh0
#      self.ifh0=netCDF4.Dataset(self.input_files[0])
#    self.time_tfreq=self.ifhN.variables['time']
#    self.ntime_tfreq=len(self.time_tfreq)
    #self.time_tfreq_calendar='proleptic_gregorian'
#    self.date_time_stamp_tfreq=netCDF4.num2date(self.time_tfreq[:],self.time_tfreq.units,self.time_tfreq_calendar)
#    self.year_fraction_tfreq=fractional_year_from_num2date(self.date_time_stamp_tfreq,self.time_tfreq_calendar)
    #print(self.ifhN)

  def regrid_curv_to_rect_setup(self,**kwargs):
    import glob
    import numpy as np
    #import netCDF4

    interpolate_check=topdir_check=Diag=outmask_check=outmask=False
    for key, value in kwargs.items():
      if(key=='Diag'):
        Diag=bool(value)
      elif(key=='topdir'):
        topdir=value
        topdir_check=True
      elif(key=='outmask'):
        outmask=bool(value)
        outmask_check=True
        if(Diag): print('regrid_curv_to_rect_setup: outmask on')
      elif(key=='interpolate'):
        if(value=='1x1o2d' or value=='1x1o3d'):
          self.nlat_regrid=180
          self.nlon_regrid=360
          self.lat_regrid=np.linspace(-89.5,89.5,self.nlat_regrid)
          self.lon_regrid=np.linspace(.5,359.5,self.nlon_regrid)
          self.clat_regrid=np.cos(self.lat_regrid[:]*self.rad)
          
          if(value=='1x1o2d'):
            self.ls_mask_file=topdir+'/short/v14/mac599/data/dst1x1_lsm.nc'
            self.ls_mask_type='2d_ocean'
            if(outmask):
              self.weights_file=[topdir+'/short/v14/mac599/data/curvilinear1x1_wgt_SCRIP_outmask.nc'] #_00
            else:
              self.weights_file=[topdir+'/short/v14/mac599/data/curvilinear1x1_wgt_SCRIP_nooutmask.nc'] #_00                      
          elif(value=='1x1o3d'):
            self.ls_mask_file=topdir+'/short/v14/mac599/data/dst1x1o3d_lsm.nc'
            self.ls_mask_type='3d_ocean'
            if(outmask):
              if(Diag): print('regrid_curv_to_rect_setup: applying outmask')
              self.weights_file=sorted(glob.glob(topdir+'/short/v14/mac599/data/curvilinear1x1_wgt_SCRIP_outmask_??.nc'))
            else:
              if(Diag): print('regrid_curv_to_rect_setup: applying nooutmask')
              self.weights_file=sorted(glob.glob(topdir+'/short/v14/mac599/data/curvilinear1x1_wgt_SCRIP_nooutmask_??.nc'))
            self.nlev_regrid=50
            self.lev_regrid=np.linspace(0,self.nlev_regrid-1,self.nlev_regrid) #dummy value
          else:
            raise SystemExit('regrid_curv_to_rect_setup: lsm not known.'+__file__+' line number: '+str(inspect.stack()[0][2]))
        elif(value=='2x2o2d' or value=='2x2o3d'):
          self.nlat_regrid=90
          self.nlon_regrid=180
          self.lat_regrid=np.linspace(-89.,89.,self.nlat_regrid)
          self.lon_regrid=np.linspace(1.,359.,self.nlon_regrid)
          self.clat_regrid=np.cos(self.lat_regrid[:]*self.rad)
          #self.weights_file=topdir+'/short/v14/mac599/data/curvilinear_wgt_SCRIP.nc'
          if(outmask):
            self.weights_file=topdir+'/short/v14/mac599/data/curvilinear2x2_wgt_SCRIP_outmask.nc'
          else:
            self.weights_file=topdir+'/short/v14/mac599/data/curvilinear2x2_wgt_SCRIP_nooutmask.nc'
          if(value=='2x2o2d'):
            self.ls_mask_file=topdir+'/short/v14/mac599/data/dst2x2_lsm.nc'
            self.ls_mask_type='2d_ocean'
          elif(value=='2x2o3d'):
            self.ls_mask_file=topdir+'/short/v14/mac599/data/dst2x2o3d_lsm.nc'
            self.ls_mask_type='3d_ocean'
            self.nlev_regrid=50
            self.lev_regrid=np.linspace(0,self.nlev_regrid-1,self.nlev_regrid) #dummy value
          else:
            raise SystemExit('regrid_curv_to_rect_setup: lsm not known.'+__file__+' line number: '+str(inspect.stack()[0][2]))
        elif(value=='5x5o2d' or value=='5x5o3d'):
          self.nlat_regrid=36
          self.nlon_regrid=72
          self.lat_regrid=np.linspace(-87.5,87.5,self.nlat_regrid)
          self.lon_regrid=np.linspace(2.5,357.5,self.nlon_regrid)
          self.clat_regrid=np.cos(self.lat_regrid[:]*self.rad)
          if(outmask):
            self.weights_file=topdir+'/short/v14/mac599/data/curvilinear5x5_wgt_SCRIP_outmask.nc'
          else:
            self.weights_file=topdir+'/short/v14/mac599/data/curvilinear5x5_wgt_SCRIP_nooutmask.nc'            
          if(value=='5x5o2d'):
            self.ls_mask_file=topdir+'/short/v14/mac599/data/dst5x5_lsm.nc'
            self.ls_mask_type='2d_ocean'
          elif(value=='5x5o3d'):
            self.ls_mask_file=topdir+'/short/v14/mac599/data/dst5x5o3d_lsm.nc'
            self.ls_mask_type='3d_ocean'
            self.nlev_regrid=50
            self.lev_regrid=np.linspace(0,self.nlev_regrid-1,self.nlev_regrid) #dummy value
          else:
            raise SystemExit('regrid_curv_to_rect_setup: lsm not known.'+__file__+' line number: '+str(inspect.stack()[0][2]))
          
        else:
          raise SystemExit('regrid_curv_to_rect: Dont know this value:'+__file__+' line number: '+str(inspect.stack()[0][2]))
        interpolate_check=True
        if(Diag): print('cafe_control_file_var.lat_regrid=', \
          cafe_control_file_var.lat_regrid)
        if(Diag): print('cafe_control_file_var.lon_regrid=', \
          cafe_control_file_var.lon_regrid)  
      else:
        raise SystemExit('regrid_curv_to_rect_setup: Dont know this key:'+__file__+' line number: '+str(inspect.stack()[0][2]))
        
  def regrid_curv_to_rect_weights_mask(self,**kwargs):
    import netCDF4
    import numpy.ma as ma
    import scipy.sparse as sps

    interpolate_check=topdir_check=Diag=False
    for key, value in kwargs.items():
      if(key=='Diag'):
        Diag=bool(value)
      else:
        raise SystemExit('regrid_curv_to_rect_weights_mask: Dont know this key:'+__file__+' line number: '+str(inspect.stack()[0][2]))
        
      self.ls_mask_fh = netCDF4.Dataset(self.ls_mask_file)
      self.ls_mask = ma.masked_equal(self.ls_mask_fh.variables['OutMask'][:], 0.)
          
      self.N_out = self.nlon_regrid * self.nlat_regrid
      self.N_in = self.nlon * self.nlat

      if(len(self.weights_file)==1):
        self.weights_fh,self.col,self.row,self.S,self.A=[],[],[],[],[]
        self.weights_fh.append(netCDF4.Dataset(self.weights_file[0]))
        self.col.append(self.weights_fh[0].variables['col'][:] - 1)
        self.row.append(self.weights_fh[0].variables['row'][:] - 1)
        self.S.append(self.weights_fh[0].variables['S'])
        self.A.append(sps.coo_matrix((self.S[0], (self.row[0],self.col[0])), shape=[self.N_out, self.N_in]))
        assert self.nlon_regrid * self.nlat_regrid == self.A[0].shape[0], \
          ("regrid_curv_to_rect_weights_mask: self.nlon_regrid * self.nlat_regrid should equal self.A[0].shape[0]")
            
      elif(len(self.weights_file)>1):
        _weights_fh,_col,_row,_S,_A=[],[],[],[],[]
        for www,weight_file in enumerate(self.weights_file):
          _weights_fh.append(netCDF4.Dataset(weight_file))
          _col.append(_weights_fh[www].variables['col'][:] - 1)
          _row.append(_weights_fh[www].variables['row'][:] - 1)
          _S.append(_weights_fh[www].variables['S'])    
          _A.append(sps.coo_matrix((_S[www], (_row[www],_col[www])), shape=[self.N_out, self.N_in]))
          assert self.nlon_regrid * self.nlat_regrid == _A[www].shape[www], \
              ("regrid_curv_to_rect_weights_mask: self.nlon_regrid * self.nlat_regrid should equal self._A.shape[www]")
        self.col=tuple(_col)
        self.row=tuple(_row)
        self.S=tuple(_S)
        self.A=tuple(_A)
        _weights_fh=_col=_row=_S=_A=None
      else:
        raise SystemExit('regrid_curv_to_rect_weights_mask: input weights not >=0 :'+__file__+' line number: '+str(inspect.stack()[0][2]))

      if(Diag): print('self.ls_mask_file=',self.ls_mask_file)
      if(Diag): print('self.weights_file=',self.weights_file)

  def regrid_curv_to_rect(self,**kwargs):
    import numpy.ma as ma
    import numpy as np
    Diag=apply_lsmask=False
    for key, value in kwargs.items():
      if(key=='Diag'):
        Diag=bool(value)
      elif(key=='input'):
        input=value
      elif(key=='apply_lsmask'):
        apply_lsmask=bool(value)
        if(Diag): print('regrid_curv_to_rect: apply_lsmask='+str(apply_lsmask))
      else:
        raise SystemExit('regrid_curv_to_rect: Dont know this key:'+__file__+' line number: '+str(inspect.stack()[0][2]))

    if(Diag): print('self.ls_mask.shape=',self.ls_mask.shape)
    if(self.ls_mask_type=='3d_ocean'):
      if(len(input.shape)==3): #input is depth, lat, lon
        print('regrid_curv_to_rect: must be 3d ocean + zero time climatology')
        output=ma.zeros((self.nlev,self.nlat_regrid,self.nlon_regrid),dtype=float)
        for level in range(self.nlev): #temporary
          #print('level=',level)
          input_flat = input[level,].reshape(-1, self.nlon*self.nlat)
          #if(Diag): print('regrid_curv_to_rect: input_flat.shape=',input_flat.shape)
          output_flat = self.A[level].dot(input_flat.T).T
          #if(Diag): print('regrid_curv_to_rect: output_flat.shape=',output_flat.shape)
          output[level,]=output_flat.reshape([self.nlat_regrid,self.nlon_regrid])
        _ls_mask=self.ls_mask
        if(apply_lsmask): output=output*_ls_mask
        
      else: #input is time, depth, lat, lon
        print('regrid_curv_to_rect: must be 3d ocean + multi time anomaly')
        output=ma.zeros((input.shape[0],self.nlev,self.nlat_regrid,self.nlon_regrid),dtype=float)
        for level in range(self.nlev):
          #print('level=',level)
          input_flat = input[:,level,].reshape(-1, self.nlon*self.nlat)
          #if(Diag): print('regrid_curv_to_rect: input_flat.shape=',input_flat.shape)
          output_flat = self.A[level].dot(input_flat.T).T
          #if(Diag): print('regrid_curv_to_rect: output_flat.shape=',output_flat.shape)
          output[:,level,]=output_flat.reshape([input.shape[0],self.nlat_regrid,self.nlon_regrid])
        _ls_mask=ma.masked_equal( np.tile(self.ls_mask,[input.shape[0],1,1,1]), 0.)
        if(apply_lsmask): output=output*_ls_mask 
        
    elif(self.ls_mask_type=='2d_ocean'):
      if(Diag): print('self.ls_mask.shape=',self.ls_mask.shape)
      if(len(input.shape)==2): #input is lat, lon
        print('regrid_curv_to_rect: must be 2d ocean/seaice + zero time climatology')
        input_flat = input.reshape(-1, self.nlon*self.nlat)
        if(Diag): print('regrid_curv_to_rect: input_flat.shape=',input_flat.shape)
        output_flat = self.A[0].dot(input_flat.T).T
        if(Diag): print('regrid_curv_to_rect: output_flat.shape=',output_flat.shape)
        output=output_flat.reshape([self.nlat_regrid,self.nlon_regrid])
        _ls_mask=self.ls_mask
        if(apply_lsmask): output=output*_ls_mask
        
      else: #input is time, lat, lon
        print('regrid_curv_to_rect: must be 2d ocean/seaice + multi time anomaly')
        input_flat = input.reshape(-1, self.nlon*self.nlat)
        if(Diag): print('regrid_curv_to_rect: input_flat.shape=',input_flat.shape)
        output_flat = self.A[0].dot(input_flat.T).T
        if(Diag): print('regrid_curv_to_rect: output_flat.shape=',output_flat.shape)
        output=output_flat.reshape([input.shape[0],self.nlat_regrid,self.nlon_regrid])
        _ls_mask=ma.masked_equal( np.tile(self.ls_mask,[input.shape[0],1,1]), 0.)
        if(apply_lsmask): output=output*_ls_mask       
    else:
      raise SystemExit('regrid_curv_to_rect: only know 2/3d_ocean '+__file__+' line number: '+str(inspect.stack()[0][2]))  
      
    return(output)
  
  def get_latlon_info(self,**kwargs):
    import netCDF4
    import math
    import numpy as np
    import numpy.ma as ma
    import inspect
    import itertools
    lat_check=lon_check=Diag=False
    for key, value in kwargs.items():
      if(key=='Diag'):
        Diag=bool(value)
      elif(key=='lat'):
        if(self.nfiles==1):
          lat=self.ifh0[0].variables[value][:]
        else:
          lat=self.ifh0[0][0].variables[value][:]          
        lat_check=True
      elif(key=='lon'):
        if(type(value)==type(None)):
          lon=None
          lon_check=True
        else:
          if(self.nfiles==1):
            lon=self.ifh0[0].variables[value][:]    
          else:
            lon=self.ifh0[0][0].variables[value][:]    
          lon_check=True
      else:
        raise SystemExit('get_latlon_info: Dont know this key:'+__file__+' line number: '+str(inspect.stack()[0][2]))
        
    if(not lat_check):
        #print('self.ifh0=',self.ifh0)
        #print('type(self.ifh0)=',type(self.ifh0))

        if(self.nfiles==1):
          lat=self.ifh0[0].variables['lat'][:]
        else:
          lat=self.ifh0[0][0].variables['lat'][:]          

    if(not lon_check):
        if(self.nfiles==1):
          lon=self.ifh0[0].variables['lon'][:]
        else:
          lon=self.ifh0[0][0].variables['lon'][:]
        
    if(type(lat)==type(None)):
      self.lat2d = self.nlat2d = self.lat = self.nlat = None
    else:
      if(len(lat.shape)>1):
        self.lat2d=lat.copy()
        self.nlat2d=list(self.lat2d.shape)
        self.lat=lat[:,0]
        self.clat=np.abs(np.cos(self.lat[:]*self.rad))
        self.nlat=len(self.lat)
      else:
        self.lat=lat
        self.clat=np.abs(np.cos(self.lat[:]*self.rad))
        self.nlat=len(self.lat)
    
    if(type(lon)==type(None)):
      self.lon2d = self.nlon2d = self.lon = self.nlon = None
    else:
      if(len(lon.shape)>1):
        self.lon2d=lon.copy()
        self.nlon2d=list(self.lon2d.shape)
        self.lon=lon[0,:]
        self.nlon=len(self.lon)
      else:
        self.lon=lon
        self.nlon=len(self.lon)
  
  def get_lev_info(self,**kwargs):
    import netCDF4
    import math
    import numpy as np
    import numpy.ma as ma
    import inspect
    import itertools
    lev_check=Diag=False
    for key, value in kwargs.items():
      if(key=='Diag'):
        Diag=bool(value)
      elif(key=='lev'):
        if(Diag): print(len(self.ifh0))
        if(self.nfiles==1):
          lev=self.ifh0[0].variables[value][:]
        else:
          lev=self.ifh0[0][0].variables[value][:]
        lev_check=True
      else:
        raise SystemExit('get_lev_info: Dont know this key:'+__file__+' line number: '+str(inspect.stack()[0][2]))

    if(not lev_check):        
      #lev=self.ifh0.variables['lev'][:]
      if(self.nfiles>1): #ensembles
        if(self.nfiles_flat>1):
          lev=self.ifh0[0][0].variables['lev'][:]
        else:
          lev=self.ifh0[0].variables['lev'][:]
      else:
        if(self.nfiles_flat>1):
          lev=self.ifh0[0].variables['lev'][:]
        else:
          lev=self.ifh0[0].variables['lev'][:]
        
    self.lev=lev
    self.nlev=len(self.lev)

  def calculate_quantity(self,instance,**kwargs):
    '''
    Note that _input only set up for a couple of cases thus far, and also for non ensemble versions, testing purposes.
    Note that quantity='nino' almost deprecated as 'z20' option is more accurate as it can copy with issues such as box
    overlapping last longitude.
    Have set of z20 ensemble case, it relies on input data being in from time,ensemble,lat,lon ...
    '''
  #def calculate_quantity(self,instance_string,**kwargs):
    import string
    import netCDF4
    import math
    import numpy as np
    import numpy.ma as ma
    import inspect
    import itertools
    Diag=False
    _input=None
    for key, value in kwargs.items():
      #value_split=string.split(value,sep=",")
      #print('value_split=',value_split)
      #raise SystemExit('STOP!:'+__file__+' line number: '+str(inspect.stack()[0][2])) 
      if(Diag): print('calculate_quantity: key,value=',key,value)
      if(key=='Diag'):
        Diag=bool(value)
        if(Diag): print('calculate_quantity: Turning on diagnostics.')
        if(Diag): print('calculate_quantity: Diag=',Diag)
        #raise SystemExit('STOP!:'+__file__+' line number: '+str(inspect.stack()[0][2])) 

      elif(key=='input'): #this must appear before quantity...
        _input=value
        print('calculate_quantity: Reading data from input variable rather than file...testing')

      elif(key=='quantity'):
        if(Diag): print('calculate_quantity: calculating a quantity...')
        #value_split=string.split(value,sep=",") #python2
        value_split=value.split(",") #python3
        print('calculate_quantity: value_split=',value_split)
        
        if(value=='nino'):
          if(Diag): print('calculate_quantity: nino chosen.')
          #self.output_tfreq=ma.zeros((self.ntime_tfreq,instance.nindices_nino),dtype=float)
          #print('self.output_tfreq.shape=',self.output_tfreq.shape)
          #raise SystemExit('STOP!:'+__file__+' line number: '+str(inspect.stack()[0][2])) 
            
          if(self.nfiles>1): #ensembles
            _var_shape=self.ifhN[0].variables[self.input_var_name].shape
            _new_shape=[]
            _new_shape.append(_var_shape[0])
            _new_shape.append(self.nfiles)
            _new_shape.append(instance.nindices_nino)
            
            #print('_new_shape=',_new_shape)
            self.output_tfreq=ma.zeros(_new_shape,dtype=float) #e.g. ntimes, nensembles, nlats, nlons
            
            for k,indice in enumerate(instance.indices_nino):
              imin,imax=instance.indices_i[instance.indices_nino.index(indice)][0], \
                instance.indices_i[instance.indices_nino.index(indice)][1]
              jmin,jmax=instance.indices_j[instance.indices_nino.index(indice)][0], \
                instance.indices_j[instance.indices_nino.index(indice)][1]
              for n in range(self.nfiles):
                self.output_tfreq[:,n,k]=np.average(np.average(self.ifhN[n].variables[self.input_var_name][:,jmin:jmax+1,imin:imax+1], \
                  axis=1,weights=self.clat[jmin:jmax+1]),axis=1)
          else: #non ensembles case

            self.output_tfreq=ma.zeros((self.ntime_tfreq,instance.nindices_nino),dtype=float)

            for k,indice in enumerate(instance.indices_nino):
              
              imin,imax=instance.indices_i[instance.indices_nino.index(indice)][0], \
                instance.indices_i[instance.indices_nino.index(indice)][1]
              jmin,jmax=instance.indices_j[instance.indices_nino.index(indice)][0], \
                instance.indices_j[instance.indices_nino.index(indice)][1]
              if(type(_input)==type(None)):
                self.output_tfreq[:,k]=np.average(np.average(self.ifhN.variables[self.input_var_name][:,jmin:jmax+1,imin:imax+1],\
                axis=1,weights=self.clat[jmin:jmax+1]),axis=1)
              else:
                self.output_tfreq[:,k]=np.average(np.average(_input[:,jmin:jmax+1,imin:imax+1],\
                axis=1,weights=self.clat[jmin:jmax+1]),axis=1)
              
          #return(self.timeseries_tfreq)
        #elif(value_split[0]=='pacific_region'): #test/dummy case.
        elif(value_split[0]=='msftyz'):
            #print('self.nfiles=',self.nfiles)
            if(self.nfiles>1): #ensembles
              _var_shape=self.ifhN[0].variables[self.input_var_name].shape
              _new_shape=[]
              _new_shape.append(_var_shape[0])
              _new_shape.append(self.nfiles)
              for shape in _var_shape[1::]:
                _new_shape.append(shape)
              self.output_tfreq=ma.zeros(_new_shape,dtype=float) #e.g. ntimes, nensembles, nlats, nlons
              for n in range(self.nfiles):
                self.output_tfreq[:,n,]=self.ifhN[n].variables[self.input_var_name][:]
            else:
              #j=self.ifhN.variables[self.input_var_name][:]
              #print('j.shape=',j.shape)
              self.output_tfreq=self.ifhN.variables[self.input_var_name][:]
        elif(value_split[0]=='latlon_region'): #test/dummy case.

          if(Diag): print('calculate_quantity: latlon_region chosen.')
          #print('len(value_split)=',len(value_split))
          #print('self.nlat=',self.nlat)
          if(len(value_split)==1): #assume 1 or 5 only ATM.

            print('n_data_funcs.calculate_quantity: Using whole lat/lon region or that specified in instance.')
            if(type(instance)!=type('abc')): #set this up only for lat/lon boxes.
              if(instance.nboxes>1):
                raise SystemExit('n_data_funcs.calculate_quantity: instance.nboxes should equal 1.'+__file__+' line number: '+str(inspect.stack()[0][2])) #as arrays will become too big generally...
              else:
                self.jmin,self.jmax,self.imin,self.imax=instance.jmin[0],instance.jmax[0],instance.imin[0],instance.imax[0]
            #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
            else:
              self.jmin,self.jmax,self.imin,self.imax=0,self.nlat,0,self.nlon
            if('self.nlev' in locals()):
              self.kmin,self.kmax=0,self.nlev
          elif(len(value_split)==5): #assume 1 or 5 only ATM.
            self.jmin,self.jmax,self.imin,self.imax=tuple([int(x) for x in value_split[1::]]) 
          elif(len(value_split)==7): #assume 1 or 5 only ATM.
            self.kmin,self.kmax,self.jmin,self.jmax,self.imin,self.imax=tuple([int(x) for x in value_split[1::]]) 
          else:
            raise SystemExit('n_data_funcs.calculate_quantity: Only 1,5,7 known ATM.'+__file__+' line number: '+str(inspect.stack()[0][2]))

          #might want to make it so that if eg imin>imax then roll the array and associated coordinates, until this is not the case.

          if('self.imin' in locals()):
            if(self.imin>self.imax):
              raise SystemExit('n_data_funcs.calculate_quantity: self.imin>self.imax, this quantity not for extracting arrays that wrap.'+__file__+' line number: '+str(inspect.stack()[0][2]))

          if('self.jmin' in locals()):
            if(self.jmin>self.jmax):
              raise SystemExit('n_data_funcs.calculate_quantity: self.jmin>self.jmax, this quantity not for extracting arrays that wrap.'+__file__+' line number: '+str(inspect.stack()[0][2]))

          if('self.kmin' in locals()):
            if(self.kmin>self.kmax):
              raise SystemExit('n_data_funcs.calculate_quantity: self.kmin>self.kmax, this quantity not for extracting arrays that wrap.'+__file__+' line number: '+str(inspect.stack()[0][2]))

          if(self.nfiles>1): #ensembles
            _var_shape=self.ifhN[0].variables[self.input_var_name].shape
            _new_shape=[]
            _new_shape.append(_var_shape[0])
            _new_shape.append(self.nfiles)

            if(len(value_split)==7):
              _new_shape.append(self.kmax-self.kmin+1)
              _new_shape.append(self.jmax-self.jmin+1)
              _new_shape.append(self.imax-self.imin+1)
            elif(len(value_split)==5 or type(instance)!=type('abc')):
              _new_shape.append(self.jmax-self.jmin+1)
              _new_shape.append(self.imax-self.imin+1)
            else:
              for shape in _var_shape[1::]:
                _new_shape.append(shape)

            self.output_tfreq=ma.zeros(_new_shape,dtype=float) #e.g. ntimes, nensembles, nlats, nlons

            for n in range(self.nfiles):
              if(len(value_split)==7):
                self.output_tfreq[:,n,]=self.ifhN[n].variables[self.input_var_name][:,self.kmin:self.kmax+1,self.jmin:self.jmax+1,self.imin:self.imax+1]
              elif(len(value_split)==5):
                self.output_tfreq[:,n,]=self.ifhN[n].variables[self.input_var_name][:,self.jmin:self.jmax+1,self.imin:self.imax+1]
              else:
                self.output_tfreq[:,n,]=self.ifhN[n].variables[self.input_var_name][:,]
          else:  #non-ensembles
            if(len(value_split)==7):
              self.output_tfreq=self.ifhN.variables[self.input_var_name][:,self.kmin:self.kmax+1,self.jmin:self.jmax+1,self.imin:self.imax+1]
            elif(len(value_split)==5 or type(instance)!=type('abc')):
              #print('xxx',self.jmin,self.jmax,self.imin,self.imax)
              self.output_tfreq=self.ifhN.variables[self.input_var_name][:,self.jmin:self.jmax+1,self.imin:self.imax+1]
            else:
              self.output_tfreq=self.ifhN.variables[self.input_var_name][:,]
            
        elif(value_split[0]=='wwv'):

          if(len(value_split)==2):
            #print('aaa')
            ifh=netCDF4.Dataset(value_split[1])
          else:
            #print('bbb')
            ifh=netCDF4.Dataset('/OSM/CBR/OA_DCFP/data/CAFEPP/g/data/p66/mac599/CMIP5/ancillary_files/grid_spec.auscom.20110618.nc')
          _area_T = ifh.variables['area_T'][:]
          _wet = ifh.variables['wet'][:]

          if(Diag): print('calculate_quantity: wwv chosen.')

          #_var_shape=self.ifhN[0].variables[self.input_var_name].shape
          if(self.nfiles==1):
            _var_shape=self.ifhN.variables[self.input_var_name].shape
          else:
            _var_shape=self.ifhN[0].variables[self.input_var_name].shape

          _area_T_match = np.expand_dims(_area_T*_wet,0)
          _area_T_new = np.tile(_area_T_match,(_var_shape[0],1,1))
          print('_area_T_new.shape=',_area_T_new.shape)

          _new_shape=[]
          if(self.nfiles>1): #ensembles
            _new_shape.append(_var_shape[0])
            _new_shape.append(self.nfiles)
            _new_shape.append(instance.nboxes)
            print('_new_shape=',_new_shape)

            self.output_tfreq=ma.zeros(_new_shape,dtype=float)
            for n in range(self.nfiles):
              for b in range(instance.nboxes):

                if(instance.imin[b]>instance.imax[b]): #box wraps over end of longitude range, need to create average in parts. Note that this is only approx. as really need to take into account the width of the cell edges...
                  print('warning: lon wraps end, taking sum of two parts.')
                  _lon_A = self.lon[self.nlon-1] - self.lon[instance.imin[b]]
                  _lon_B = self.lon[instance.imax[b]] - self.lon[0]
                  _lon_total = _lon_A + _lon_B

                  self.output_tfreq[:,n,b,]= \
                    ( np.sum(np.sum(self.ifhN[n].variables[self.input_var_name][:,instance.jmin[b]:instance.jmax[b]+1,instance.imin[b]:self.nlon]*_area_T_new[:,instance.jmin[b]:instance.jmax[b]+1,instance.imin[b]:self.nlon],axis=1),axis=1)*_lon_A + \
                     np.sum(np.sum(self.ifhN[n].variables[self.input_var_name][:,instance.jmin[b]:instance.jmax[b]+1,0:instance.imax[b]+1]*_area_T_new[:,instance.jmin[b]:instance.jmax[b]+1,0:instance.imax[b]+1],axis=1),axis=1)*_lon_B ) /_lon_total

                else:

                  self.output_tfreq[:,n,b,]=np.sum(np.sum( \
                    self.ifhN[n].variables[self.input_var_name][:,instance.jmin[b]:instance.jmax[b]+1,instance.imin[b]:instance.imax[b]+1] * \
                    _area_T_new[:,instance.jmin[b]:instance.jmax[b]+1,instance.imin[b]:instance.imax[b]+1] \
                    ,axis=1),axis=1)
                  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
          else:  
            _new_shape.append(_var_shape[0])
            _new_shape.append(instance.nboxes)
            self.output_tfreq=ma.zeros(_new_shape,dtype=float)
            for b in range(instance.nboxes):
              if(instance.imin[b]>instance.imax[b]): #box wraps over end of longitude range, need to create average in parts.
                print('warning: lon wraps end, taking sum of two parts.')
                _lon_A = self.lon[self.nlon-1] - self.lon[instance.imin[b]]
                _lon_B = self.lon[instance.imax[b]] - self.lon[0]
                _lon_total = _lon_A + _lon_B
                self.output_tfreq[:,b,]= \
                  ( np.sum(np.sum(self.ifhN.variables[self.input_var_name][:,instance.jmin[b]:instance.jmax[b]+1,instance.imin[b]:self.nlon]*_area_T_new[:,instance.jmin[b]:instance.jmax[b]+1,instance.imin[b]:self.nlon],axis=1),axis=1)*_lon_A + \
                  np.sum(np.sum(self.ifhN.variables[self.input_var_name][:,instance.jmin[b]:instance.jmax[b]+1,0:instance.imax[b]+1]*_area_T_new[:,instance.jmin[b]:instance.jmax[b]+1,0:instance.imax[b]+1],axis=1),axis=1)*_lon_B ) /_lon_total
              else:
                self.output_tfreq[:,b,]=np.sum(np.sum(self.ifhN.variables[self.input_var_name][:,instance.jmin[b]:instance.jmax[b]+1,instance.imin[b]:instance.imax[b]+1]*_area_T_new[:,instance.jmin[b]:instance.jmax[b]+1,instance.imin[b]:instance.imax[b]+1],axis=1),axis=1)
            
        elif(value=='z20'):
          if(Diag): print('calculate_quantity: z20 chosen.')
          #print('len(value_split)=',len(value_split))
          #print('self.nlat=',self.nlat)

#          if(len(value_split)==1): #assume 1 or 5 only ATM.
#            print('n_data_funcs.calculate_quantity: Using whole lat/lon region.')
#            self.jmin,self.jmax,self.imin,self.imax=0,self.nlat,0,self.nlon #should this be nlat-1,nlon-1 ?
#          else:
#            print('n_data_funcs.calculate_quantity: Using sub lat/lon region.')
#            self.jmin,self.jmax,self.imin,self.imax=tuple([int(x) for x in value_split[1::]]) 

          #print(self.nfiles)
          #print('self.ifhN=',self.ifhN)
          #print(self.ifhN.shape)
          #print(self.nfiles)
          #print(self.nfiles_flat)
          #print(len(self.ifhN))

          if(self.nfiles==1):
            _var_shape=self.ifhN.variables[self.input_var_name].shape
          else:
            _var_shape=self.ifhN[0].variables[self.input_var_name].shape
          _new_shape=[]
          if(self.nfiles>1): #ensembles
            if(type(_input)==type(None)):
              _new_shape.append(_var_shape[0])
            else:
              _new_shape.append(_input.shape[0])
            _new_shape.append(self.nfiles)
            _new_shape.append(instance.nboxes)
            self.output_tfreq=ma.zeros(_new_shape,dtype=float)
            for n in range(self.nfiles):
              #for b in range(instance.nboxes):
              for b in range(instance.nboxes):
                #print('n,b=',n,b)
                #print('jmin,jmax,imin,imax=',instance.jmin[b],instance.jmax[b],instance.imin[b],instance.imax[b])

                if(instance.imin[b]>instance.imax[b]): #box wraps over end of longitude range, need to create average in parts. Note that this is only approx. as really need to take into account the width of the cell edges...
                  print('warning: lon wraps end, taking average of two parts.')
                  #print(self.lon[instance.imin[b]:self.nlon])
                  #print(self.lon[0:instance.imax[b]+1])
                  _lon_A = self.lon[self.nlon-1] - self.lon[instance.imin[b]]
                  _lon_B = self.lon[instance.imax[b]] - self.lon[0]
                  _lon_total = _lon_A + _lon_B
                  #print('_lon_total=',_lon_total)

                  if(type(_input)==type(None)):
                    self.output_tfreq[:,n,b,]= \
                      ( np.average(np.average(self.ifhN[n].variables[self.input_var_name][:,instance.jmin[b]:instance.jmax[b]+1,instance.imin[b]:self.nlon],axis=1,weights=self.clat[instance.jmin[b]:instance.jmax[b]+1]),axis=1)*_lon_A + \
                       np.average(np.average(self.ifhN[n].variables[self.input_var_name][:,instance.jmin[b]:instance.jmax[b]+1,0:instance.imax[b]+1],axis=1,weights=self.clat[instance.jmin[b]:instance.jmax[b]+1]),axis=1)*_lon_B ) /_lon_total
                  else:
                    self.output_tfreq[:,n,b,]= \
                      ( np.average(np.average(_input[:,n,instance.jmin[b]:instance.jmax[b]+1,instance.imin[b]:self.nlon],axis=1,weights=self.clat[instance.jmin[b]:instance.jmax[b]+1]),axis=1)*_lon_A + \
                       np.average(np.average(_input[:,n,instance.jmin[b]:instance.jmax[b]+1,0:instance.imax[b]+1],axis=1,weights=self.clat[instance.jmin[b]:instance.jmax[b]+1]),axis=1)*_lon_B ) /_lon_total

                else:
                  if(type(_input)==type(None)):
                    self.output_tfreq[:,n,b,]=np.average(np.average(self.ifhN[n].variables[self.input_var_name][:,instance.jmin[b]:instance.jmax[b]+1,instance.imin[b]:instance.imax[b]+1],axis=1,weights=self.clat[instance.jmin[b]:instance.jmax[b]+1]),axis=1)
                  else:
                    self.output_tfreq[:,n,b,]=np.average(np.average(_input[:,n,instance.jmin[b]:instance.jmax[b]+1,instance.imin[b]:instance.imax[b]+1],axis=1,weights=self.clat[instance.jmin[b]:instance.jmax[b]+1]),axis=1)
                #print('self.nlon=',self.nlon)
                #j=self.ifhN[n].variables[self.input_var_name][0,instance.jmin[b]:instance.jmin[b]+1,instance.imin[b]:instance.imax[b]+1]
                #print(j.shape)
                #print(j)
                #raise SystemExit('STOP!:'+__file__+' line number: '+str(inspect.stack()[0][2]))
          else: #non ensembles case
            #print('xxx,hello')
            #print('_input.shape=',_input.shape)

            if(type(_input)==type(None)):
              _new_shape.append(_var_shape[0])
            else:
              _new_shape.append(_input.shape[0])
            _new_shape.append(instance.nboxes)
            self.output_tfreq=ma.zeros(_new_shape,dtype=float)

            for b in range(instance.nboxes):
              if(instance.imin[b]>instance.imax[b]): #box wraps over end of longitude range, need to create average in parts.
                print('warning: lon wraps end, taking average of two parts.')
                _lon_A = self.lon[self.nlon-1] - self.lon[instance.imin[b]]
                _lon_B = self.lon[instance.imax[b]] - self.lon[0]
                _lon_total = _lon_A + _lon_B

                if(type(_input)==type(None)):
                  self.output_tfreq[:,b,]= \
                    ( np.average(np.average(self.ifhN.variables[self.input_var_name][:,instance.jmin[b]:instance.jmax[b]+1,instance.imin[b]:self.nlon],axis=1,weights=self.clat[instance.jmin[b]:instance.jmax[b]+1]),axis=1)*_lon_A + \
                    np.average(np.average(self.ifhN.variables[self.input_var_name][:,instance.jmin[b]:instance.jmax[b]+1,0:instance.imax[b]+1],axis=1,weights=self.clat[instance.jmin[b]:instance.jmax[b]+1]),axis=1)*_lon_B ) /_lon_total
                else:
                  self.output_tfreq[:,b,]= \
                    ( np.average(np.average(_input[:,instance.jmin[b]:instance.jmax[b]+1,instance.imin[b]:self.nlon],axis=1,weights=self.clat[instance.jmin[b]:instance.jmax[b]+1]),axis=1)*_lon_A + \
                    np.average(np.average(_input[:,instance.jmin[b]:instance.jmax[b]+1,0:instance.imax[b]+1],axis=1,weights=self.clat[instance.jmin[b]:instance.jmax[b]+1]),axis=1)*_lon_B ) /_lon_total

              else:

                #print(self.output_tfreq.shape)
                #print('xxx',self.clat,instance.jmin,instance.jmax)
                #j=self.ifhN.variables[self.input_var_name][:]
                #print(j.shape)
                #k=np.squeeze(self.ifhN.variables[self.input_var_name][:])
                #print(k.shape)
                #print(_var_shape)

                if(type(_input)==type(None)):
                  if(len(_var_shape)==4): #normally z20 works on time,lat,lon but sometimes some 2d vars have extra "height dimension".
                    self.output_tfreq[:,b,]=np.average(np.average(self.ifhN.variables[self.input_var_name][:,0,instance.jmin[b]:instance.jmax[b]+1,instance.imin[b]:instance.imax[b]+1],axis=1,weights=self.clat[instance.jmin[b]:instance.jmax[b]+1]),axis=1)
                  else:
                    self.output_tfreq[:,b,]=np.average(np.average(self.ifhN.variables[self.input_var_name][:,instance.jmin[b]:instance.jmax[b]+1,instance.imin[b]:instance.imax[b]+1],axis=1,weights=self.clat[instance.jmin[b]:instance.jmax[b]+1]),axis=1)
                else:
                  if(len(_var_shape)==4): #normally z20 works on time,lat,lon but sometimes some 2d vars have extra "height dimension".
                    self.output_tfreq[:,b,]=np.average(np.average(_input[:,instance.jmin[b]:instance.jmax[b]+1,instance.imin[b]:instance.imax[b]+1],axis=1,weights=self.clat[instance.jmin[b]:instance.jmax[b]+1]),axis=1)
                  else:
                    self.output_tfreq[:,b,]=np.average(np.average(_input[:,instance.jmin[b]:instance.jmax[b]+1,instance.imin[b]:instance.imax[b]+1],axis=1,weights=self.clat[instance.jmin[b]:instance.jmax[b]+1]),axis=1)
              #raise SystemExit('STOP!:'+__file__+' line number: '+str(inspect.stack()[0][2]))
            
        elif(value_split[0]=='equatorial'): #test/dummy case.
          if(Diag): print('calculate_quantity: equatorial chosen.')
          if(len(value_split)==1): #assume 1 or 3 only ATM.
            print('n_data_funcs.calculate_quantity: Using whole lat/lon region.')
            self.imin,self.imax=0,self.nlon
          else:
            self.imin,self.imax=tuple([int(x) for x in value_split[1::]]) 
          if(self.nfiles>1): #ensembles
            _var_shape=self.ifhN[0].variables[self.input_var_name].shape
            _new_shape=[]
            _new_shape.append(_var_shape[0])
            _new_shape.append(self.nfiles)
            for shape in _var_shape[2::]:
              _new_shape.append(shape)
            self.output_tfreq=ma.zeros(_new_shape,dtype=float) #e.g. ntimes, nensembles, nlats, nlons
            if(Diag): print('equatorial: self.output_tfreq.shape=',self.output_tfreq.shape)
            for n in range(self.nfiles):
              self.output_tfreq[:,n,]=np.average(self.ifhN[n].variables[self.input_var_name][:,46:47+1,self.imin:self.imax+1],axis=1)
          else:
            self.output_tfreq=np.average(self.ifhN.variables[self.input_var_name][:,46:47+1,self.imin:self.imax+1],axis=1)

        elif(value=='equatorial_cross_section'):
          if(Diag): print('calculate_quantity: equatorial_cross_section chosen.')
          if(len(value_split)==1): #assume 1 or 7 only ATM.
            print('n_data_funcs.calculate_quantity: Using whole lat/lon region.')
            self.jmin,self.jmax,self.imin,self.imax,self.kmin,self.kmax=0,self.nlat,0,self.nlon,0,self.ndep
          else:
            self.jmin,self.jmax,self.imin,self.imax,self.kmin,self.kmax=tuple([int(x) for x in value_split[1::]])           
          if(self.nfiles>1): #ensembles
            _var_shape=self.ifhN[0].variables[self.input_var_name].shape
            _new_shape=[]
            _new_shape.append(_var_shape[0])
            _new_shape.append(self.nfiles)
            _new_shape.append(_var_shape[1])
            for shape in _var_shape[3::]:
              _new_shape.append(shape)
            self.output_tfreq=ma.zeros(_new_shape,dtype=float) #e.g. ntimes, nensembles, nlats, nlons
            for n in range(self.nfiles):
              self.output_tfreq[:,n,]=np.average(self.ifhN[n].variables[self.input_var_name][:,:,136:137+1,:],axis=2)
          else:
            self.output_tfreq=np.average(self.ifhN.variables[self.input_var_name][:,:,136:137+1,:],axis=2)

        else:
          raise SystemExit('Index type '+value+' not known:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    return(self.output_tfreq)
          
  def modify_timeseries_4testing(self,**kwargs):
    import netCDF4
    import math
    import numpy as np
    import numpy.ma as ma
    import inspect
    import itertools
    '''
    This is for testing the implications of removing a day (month etc.) at begin/end or both or none of a time-series. But as tfreq is focusing on daily revision might be required for other frequencies.
    '''
    Diag=False
    
    for key, value in kwargs.items():
      if(key=='Diag'):
        Diag=bool(value)
      elif(key=='what_to_keep'):
        if(value=='all_times'):
          self.year_fraction_tfreq=self.year_fraction_tfreq
          self.date_time_stamp_tfreq=self.date_time_stamp_tfreq
          self.output_tfreq=self.output_tfreq
        elif(value=='all_but_first'):
          self.year_fraction_tfreq=self.year_fraction_tfreq[1::]
          self.date_time_stamp_tfreq=self.date_time_stamp_tfreq[1::]
          self.output_tfreq=self.output_tfreq[:,1::]
        elif(value=='all_but_last'):
          self.year_fraction_tfreq=self.year_fraction_tfreq[0:-1]
          self.date_time_stamp_tfreq=self.date_time_stamp_tfreq[0:-1]
          self.output_tfreq=self.output_tfreq[:,0:-1]
        elif(value=='all_but_first_and_last'):
          self.year_fraction_tfreq=self.year_fraction_tfreq[1:-1]
          self.date_time_stamp_tfreq=self.date_time_stamp_tfreq[1:-1]
          self.output_tfreq=self.output_tfreq[:,1:-1]
      else:
        raise SystemExit('Dont know that key.'+__file__+' line number: '+str(inspect.stack()[0][2]))
    #return year_fraction_tfreq,date_time_stamp_tfreq,nino_tfreq
    
  def daily_monthly_indices_info(self,**kwargs):
    import netCDF4
    import math
    import numpy as np
    import numpy.ma as ma
    import inspect
    import itertools
    from decadal_diag import generate_daily_month_indices
    timesep_check=Diag=False
    for key, value in kwargs.items():
      if(key=='timesep'):
        timesep=value
        timesep_check=True  
      elif(key=='Diag'):
        Diag=bool(value)
      else:
        raise SystemExit('Dont know that key.'+__file__+' line number: '+str(inspect.stack()[0][2]))
        
    if(not timesep_check):
      print('daily_monthly_indices_info: Setting to default timesep: 1')
      timesep=1
      
    #print('timesep=',timesep)
    
    #if(self.nfiles>1 and self.nfiles_flat==self.nfiles):       
    if(self.nfiles>1): #ensembles
    #assume all the same...
      self.daily_month_indice_beg,self.daily_month_indice_end, \
        self.daily_year_beg,self.daily_year_end, \
        self.daily_month_beg,self.daily_month_end, \
        self.daily_day_beg,self.daily_day_end, \
        self.beg_month_partial,self.end_month_partial = \
        generate_daily_month_indices(self.date_time_stamp_tfreq[0],self.time_tfreq_units,self.time_tfreq_calendar,timesep)
    else: 
      self.daily_month_indice_beg,self.daily_month_indice_end, \
        self.daily_year_beg,self.daily_year_end, \
        self.daily_month_beg,self.daily_month_end, \
        self.daily_day_beg,self.daily_day_end, \
        self.beg_month_partial,self.end_month_partial = \
        generate_daily_month_indices(self.date_time_stamp_tfreq,self.time_tfreq_units,self.time_tfreq_calendar,timesep)      
    #print('self.daily_month_indice_beg=',self.daily_month_indice_beg)
    #print('self.daily_month_indice_end=',self.daily_month_indice_end)
    #print('self.date_time_stamp_tfreq[0]=',self.date_time_stamp_tfreq[0])
      
  def daily_to_monthly(self,**kwargs):
    import netCDF4
    import math
    import numpy as np
    import numpy.ma as ma
    import inspect
    import itertools
    EndOption_check=Diag=False

    for key, value in kwargs.items():
      if(key=='EndOption'):
        EndOption=value
        EndOption_check=True
      elif(key=='input'):
        input=value
      elif(key=='Diag'):
        Diag=bool(value) 
      else:
        raise SystemExit('Dont know that key.'+__file__+' line number: '+str(inspect.stack()[0][2]))
        
    if(not EndOption_check):
      print('daily_to_monthly: Setting to default EndOption: 1')
      EndOption=1

    #print('input=',input)
    #print('input.shape=',input.shape)
    #print('input.ndim=',input.ndim)

    output_shape=[len(self.daily_month_indice_beg)]                     
    if(input.ndim>1):
      for sss in input.shape[1::]:
        output_shape.append(sss)
             
    #print('output_shape=',output_shape)

    self.output=ma.zeros(output_shape,dtype=float)
            
    #print('self.output.shape=',self.output.shape)

    for month in range(0,len(self.daily_month_indice_beg)):
      self.output[month,:]=np.average(input[self.daily_month_indice_beg[month]:self.daily_month_indice_end[month]+1,],axis=0)

    self.year_fraction_monthly=ma.zeros(len(self.daily_month_indice_beg))
    for month in range(0,len(self.daily_month_indice_beg)):
      self.year_fraction_monthly[month]=np.average(self.year_fraction_tfreq[self.daily_month_indice_beg[month]:self.daily_month_indice_end[month]+1])

    if(self.nfiles>1): #ensembles
      self.num_stamp=netCDF4.date2num(self.date_time_stamp_tfreq[0],self.time_tfreq_units,self.time_tfreq_calendar)
    else:
      self.num_stamp=netCDF4.date2num(self.date_time_stamp_tfreq,self.time_tfreq_units,self.time_tfreq_calendar)
      
    self.num_stamp_monthly=np.zeros(len(self.daily_month_indice_beg))
    #print('num_stamp_monthly.shape=',num_stamp_monthly.shape)

    for month in range(0,len(self.daily_month_indice_beg)):
      self.num_stamp_monthly[month]=np.average(self.num_stamp[self.daily_month_indice_beg[month]:self.daily_month_indice_end[month]+1])
      
    #print('self.num_stamp_monthly=',self.num_stamp_monthly)
    
    self.date_time_stamp_monthly=netCDF4.num2date(self.num_stamp_monthly,self.time_tfreq_units,self.time_tfreq_calendar)

    #print('self.date_time_stamp_monthly=',self.date_time_stamp_monthly)
    
    #print('beg,end_month_partial=',self.beg_month_partial,self.end_month_partial)

    if(EndOption==1):
      print('daily_to_monthly: Discarding beg&/end month if they exist.')
      if(self.beg_month_partial or self.end_month_partial):
        if(self.beg_month_partial and self.end_month_partial):
          print('daily_to_monthly: type#1')
          self.output=self.output[:,1:-1]
          self.year_fraction_monthly=self.year_fraction_monthly[1:-1]
          self.date_time_stamp_monthly=self.date_time_stamp_monthly[1:-1]
      
        elif(not self.beg_month_partial and self.end_month_partial):
          print('daily_to_monthly: type#2')
          self.output=self.output[:,0:-1]
          self.year_fraction_monthly=self.year_fraction_monthly[0:-1]
          self.date_time_stamp_monthly=self.date_time_stamp_monthly[0:-1]

        elif(self.beg_month_partial and not self.end_month_partial):
          print('daily_to_monthly: type#3')
          self.output=self.output[:,1::]
          self.year_fraction_monthly=self.year_fraction_monthly[1::]
          self.date_time_stamp_monthly=self.date_time_stamp_monthly[1::]

        else:
          raise SystemExit('daily_to_monthly: Shouldnt get here:'+__file__+' line number: '+str(inspect.stack()[0][2]))
      else:
        print('daily_to_monthly: type#4')
        self.output=self.output
        self.year_fraction_monthly=self.year_fraction_monthly
        self.date_time_stamp_monthly=self.date_time_stamp_monthly
    
    elif(EndOption==2):
      print('daily_to_monthly: Keeping beg/end month or both.')
      self.output=self.output
      self.year_fraction_monthly=self.year_fraction_monthly
      self.date_time_stamp_monthly=self.date_time_stamp_monthly
  
    else:
      raise SystemExit('daily_to_monthly: EndOption can be only 1 or 2:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    self.daily_to_monthly_test=True 
    return(self.output)

  def monthly_clim_anom(self,**kwargs):
    import netCDF4
    import math
    import numpy as np
    import numpy.ma as ma
    import inspect
    import itertools
    from decadal_diag import \
      fractional_year_from_num2date, get_timestamp_number
    '''
    cbeg: beginning year for climatology calculation (default begin valid year).
    cend: ending year for climatology calculation (default begin valid year).
    
    abeg: beginning year for anomaly output (default begin valid year).
    aend: ending year for anomaly output (default begin valid year).
    
    if cbeg/cend/abeg/aend are not set, for e.g., then, all years used/generated.
    
    ClimOnly: calculate climatology only and return.
    AnomOnly: calculate anomaly onlyl and return.
    
    AnnOut: generate annual outputs rather than monthly ones. Note that assume for now that
    all years have months of equal lengths - not quite true but reasonably accurate.
    
    clim: pass climatology, this way it doesn't need to be calculated for anomaly generation.
    
    Todo: need to create timestamp values representative of spatial averages so that these can be used
    in generating plot titles, for example.
    
    '''
    ClimOnly=AnomOnly=AnnOut=ZeroClim=Diag=False
    monthly_climatology=None
    cbeg=cend=abeg=aend=None
    for key, value in kwargs.items():
      if(key=='Diag'):
        Diag=bool(value)
        print('Diag=',Diag)
        if(Diag): print('monthly_clim_anom: Diagnostics turned on.')
      elif(key=='input'):
        input=value
      elif(key=='cbeg'):
        cbeg=int(value)
      elif(key=='cend'):
        cend=int(value)
      elif(key=='abeg'):
        abeg=int(value)
      elif(key=='aend'):
        aend=int(value)
      elif(key=='ClimOnly'):
        ClimOnly=bool(value)
        if(Diag and ClimOnly): print('monthly_clim_anom: Climatologies only.')
      elif(key=='AnomOnly'):
        AnomOnly=bool(value)
        if(Diag and AnomOnly): print('monthly_clim_anom: Anomalies only.')
      elif(key=='AnnOut'):
        AnnOut=bool(value)
        if(Diag and AnnOut): print('monthly_clim_anom: Produce annual output rather than monthly.')
      elif(key=='clim'):
        monthly_climatology=self.monthly_climatology=value
        #self.monthly_climatology=value
        AnomOnly=True
        print('monthly_clim_anom: Reading in climatology rather than calculating it.')
      elif(key=='ZeroClim'):
        ZeroClim=bool(value)
        if(ZeroClim):
          if(Diag): print('monthly_clim_anom: Zeroing climatlogy in anomaly calculation.')
        else:
          if(Diag): print('monthly_clim_anom: Not zeroing climatlogy in anomaly calculation.')
      else:
        raise SystemExit('option '+key+' not known:'+__file__+' line number: '+str(inspect.stack()[0][2]))

      if(ClimOnly and AnomOnly):
        raise SystemExit('monthly_clim_anom: Either ClimOnly or AnomOnly or neither (i.e. both Clim & Anom):'+__file__+' line number: '+str(inspect.stack()[0][2]))   
      
    #print('monthly_climatology=',monthly_climatology)
    #print('len(self.date_time_stamp_tfreq)=',len(self.date_time_stamp_tfreq))
    #print(self.date_time_stamp_monthly)
    #print(self.date_time_stamp_monthly[0][0].year)
    #print(self.date_time_stamp_monthly[0][-1].year)

    #print('monthly_clim_anom: self.date_time_stamp_monthly=',self.date_time_stamp_monthly)

    if(Diag): print('monthly_clim_anom: self.daily_to_monthly_test=',self.daily_to_monthly_test)

    #print('xxx',self.date_time_stamp_monthly,self.daily_to_monthly_test)
    #print('xxx',self.date_time_stamp_tfreq,self.daily_to_monthly_test)

    try:
      if(not self.daily_to_monthly_test and self.nfiles>1): #ensembles
        ybeg=self.date_time_stamp_monthly[0][0].year
        if(Diag): print('monthly_clim_anom: aaa')
      else:
        ybeg=self.date_time_stamp_monthly[0].year
        if(Diag): print('monthly_clim_anom: bbb')
    except AttributeError:
      #ybeg=self.date_time_stamp_tfreq[0].year
      if(self.dummy_mode):
        try:
          ybeg=self.date_time_stamp_tfreq[0].year
        except AttributeError:
          ybeg=self.date_time_stamp_tfreq[0][0].year
      elif(not self.daily_to_monthly_test and self.nfiles>1): #ensembles
        ybeg=self.date_time_stamp_tfreq[0][0].year
        if(Diag): print('monthly_clim_anom: ccc')
      else:
        ybeg=self.date_time_stamp_tfreq[0].year
        if(Diag): print('monthly_clim_anom: ddd')
      
    try:
      if(not self.daily_to_monthly_test and self.nfiles>1): #ensembles
        yend=self.date_time_stamp_monthly[0][-1].year
      else:
        yend=self.date_time_stamp_monthly[-1].year
    except AttributeError:
      #yend=self.date_time_stamp_tfreq[-1].year

      if(self.dummy_mode):
        try:
          yend=self.date_time_stamp_tfreq[-1].year
        except AttributeError:
          yend=self.date_time_stamp_tfreq[0][-1].year
      elif(not self.daily_to_monthly_test and self.nfiles>1): #ensembles
        yend=self.date_time_stamp_tfreq[0][-1].year
      else:
        yend=self.date_time_stamp_tfreq[-1].year

    ydiff_monthly=yend-ybeg+1

    #raise SystemExit('STOP!:'+__file__+' line number: '+str(inspect.stack()[0][2]))

    MissingMonths=False

    try:
      if(not self.daily_to_monthly_test and self.nfiles>1): #ensembles
        first_month=self.date_time_stamp_monthly[0][0].month
      else:
        first_month=self.date_time_stamp_monthly[0].month
    except AttributeError:
      #first_month=self.date_time_stamp_tfreq[0].month
      if(self.dummy_mode):
        try:
          first_month=self.date_time_stamp_tfreq[0].month
        except AttributeError:
          first_month=self.date_time_stamp_tfreq[0][0].month
      elif(not self.daily_to_monthly_test and self.nfiles>1): #ensembles
        first_month=self.date_time_stamp_tfreq[0][0].month
      else:
        first_month=self.date_time_stamp_tfreq[0].month
      
    try:
      if(not self.daily_to_monthly_test and self.nfiles>1): #ensembles
        last_month=self.date_time_stamp_monthly[0][-1].month
      else:
        last_month=self.date_time_stamp_monthly[-1].month
    except AttributeError:
      #last_month=self.date_time_stamp_tfreq[-1].month
      if(self.dummy_mode):
        try:
          last_month=self.date_time_stamp_tfreq[-1].month
        except AttributeError:
          last_month=self.date_time_stamp_tfreq[0][-1].month
      elif(not self.daily_to_monthly_test and self.nfiles>1): #ensembles
        last_month=self.date_time_stamp_tfreq[0][-1].month
      else:
        last_month=self.date_time_stamp_tfreq[-1].month
      
    #first_month=self.date_time_stamp_monthly[0].month
    #last_month=self.date_time_stamp_monthly[-1].month

    if(Diag): print('monthly_clim_anom: ybeg,yend=',ybeg,yend)
    if(Diag): print('monthly_clim_anom: first,last_month=',first_month,last_month)

    missing_months_beg,missing_months_end=0,0

    cyear_beg_skip,cyear_end_skip=0,1

    if(first_month!=1):
      #missing_months_beg=12-first_month
      missing_months_beg=first_month-1
      cyear_beg_skip=1
      MissingMonths=True

    if(last_month!=12):
      missing_months_end=12-last_month
      cyear_end_skip=2
      MissingMonths=True

    self.PaddedYears=False
  
    if(MissingMonths):
      self.PaddedYears=True
      print('monthly_clim_anom: There are missing months in the set. '+str(missing_months_beg)+' at beginning and '+str(missing_months_end)+' at end.')
      print('monthly_clim_anom: Currently years with missing months are not used in generating long term monthly climatology.')
      print('monthly_clim_anom: And missing months will be set to missing in the final time-series.')
      self.ts_beg,self.ts_end,self.ts_avg,self.dt_beg,self.dt_end,self.dt_avg = \
        get_timestamp_number(ybeg,yend,1,12,self.time_tfreq_units,self.time_tfreq_calendar)
      year_fraction_monthly_full=fractional_year_from_num2date(self.ts_avg,self.time_tfreq_calendar) 
  
      if(Diag): print('input.shape=',input.shape[1::])
      input_full_shape=[ydiff_monthly*self.nmy]
      for sss in input.shape[1::]:
        input_full_shape.append(sss)
      if(Diag): print('monthly_clim_anom: input_full_shape=',input_full_shape)
      input_full=ma.masked_all(input_full_shape,dtype=float)

      if(Diag): print('monthly_clim_anom: input_full.shape=',input_full.shape)

      #if('cbeg' not in locals()): #assign to full series.
      if(type(cbeg)==type(None)):
        cbeg=ybeg
      #if('cend' not in locals()): #assign to full series.
      if(type(cend)==type(None)):
        cend=yend

      #if('abeg' not in locals()): #assign to full series.
      if(type(abeg)==type(None)):
        abeg=ybeg
      #if('aend' not in locals()): #assign to full series.
      if(type(aend)==type(None)):
        aend=yend
        
      if(missing_months_beg!=0 and cbeg==ybeg):
        print('monthly_clim_anom: Warning: missing months in first year and cbeg set to first year.')
      if(missing_months_beg!=0 and abeg==ybeg):
        print('monthly_clim_anom: Warning: missing months in first year and abeg set to first year.')
        
      if(missing_months_end!=0 and cend==yend):
        print('monthly_clim_anom: Warning: missing months in last year and cbeg set to last year.')
      if(missing_months_end!=0 and aend==yend):
        print('monthly_clim_anom: Warning: missing months in last year and abeg set to last year.')
        
      last_month_index=(ydiff_monthly*self.nmy)-(12-last_month)
      print('monthly_clim_anom: ydiff_monthly,missing_months_beg,last_month_index=',ydiff_monthly,missing_months_beg,last_month_index)
      
      input_full[missing_months_beg:last_month_index,]=input #assigning data to larger array, with missing values in unassigned cells.

      self.PaddedYears_missing_months_beg=missing_months_beg
      self.PaddedYears_missing_months_end=missing_months_end
      self.PaddedYears_last_month_index=last_month_index

      #print('self.dt_avg=',self.dt_avg) #this is the one, need
      #print('self.dt_avg.shape=',self.dt_avg.shape)
      #print('self.ts_avg=',self.ts_avg)
      #print('year_fraction_monthly_full=',year_fraction_monthly_full)
      #print('self.time_tfreq[0][:]=',self.time_tfreq[0][:])
      #print('self.time_tfreq[0].shape=',self.time_tfreq[0].shape)
      #print('len(self.time_tfreq)=',len(self.time_tfreq))
      #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

      self.time_tfreq_full=self.dt_avg #all years 12 months.
      
    else:
      print('monthly_clim_anom: All years have 12 months.')

      #print('type(self.time_tfreq)=',type(self.time_tfreq)) 
      #print('len(self.time_tfreq)=',len(self.time_tfreq)) 

      #print('xxx',self.daily_to_monthly_test)

      #self.num_stamp_monthly

      try:
        self.time_tfreq_full=self.time_tfreq #.copy()
      except AttributeError:
        self.time_freq_full=self.num_stamp_monthly

      input_full=input.copy()
      
      if(self.daily_to_monthly_test):
        year_fraction_monthly_full=self.date_time_stamp_monthly.copy()
      else:
        if(self.dummy_mode):

        #self.time_tfreq_units = _dummy_time_units
        #self.time_tfreq_calendar = _dummy_calendar
        #self.dummy_mode = True
        #if(self.daily_to_monthly_test):
        #  self.date_time_stamp_monthly = _dummy_time_stamp
        #  self.num_stamp_monthly = _dummy_num_stamp #this comes from daily_to_monthly function
        #  #self.nfiles=None
        #else:
        #  self.date_time_stamp_tfreq =_dummy_time_stamp
        #  self.time_tfreq = _dummy_num_stamp

          self.year_fraction_tfreq=fractional_year_from_num2date(self.date_time_stamp_tfreq[0],self.time_tfreq_calendar)

          year_fraction_monthly_full=self.year_fraction_tfreq.copy()

        elif(self.nfiles>1): #ensembles
          year_fraction_monthly_full=self.year_fraction_tfreq[0].copy()
        else:
          year_fraction_monthly_full=self.year_fraction_tfreq.copy()

        
    #if('cbeg' not in locals()): #assign to full series.
    if(type(cbeg)==type(None)):
      cbeg=ybeg
    #if('cend' not in locals()): #assign to full series.
    if(type(cend)==type(None)):
      cend=yend

    #if('abeg' not in locals()): #assign to full series.
    if(type(abeg)==type(None)):
      abeg=ybeg
    #if('aend' not in locals()): #assign to full series.
    if(type(aend)==type(None)):
      aend=yend

    if(Diag): print('monthly_clim_anom: input.shape=',input.shape)

    if(Diag): print('monthly_clim_anom: cbeg,cend=',cbeg,cend)
    if(Diag): print('monthly_clim_anom: ybeg,yend=',ybeg,yend)

    if(cend<cbeg):
      raise SystemExit('monthly_clim_anom: cend<cbeg:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    if(cbeg<ybeg):
      raise SystemExit('monthly_clim_anom: cbeg<ybeg:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    if(cend>yend):
      raise SystemExit('monthly_clim_anom: cend>yend:'+__file__+' line number: '+str(inspect.stack()[0][2]))
      
    if(aend<abeg):
      raise SystemExit('monthly_clim_anom: aend<abeg:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    if(abeg<ybeg):
      raise SystemExit('monthly_clim_anom: abeg<ybeg:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    if(aend>yend):
      raise SystemExit('monthly_clim_anom: aend>yend:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    
    if(Diag): print('monthly_clim_anom: Input data over years '+str(ybeg)+'-'+str(yend))
    if(Diag): print('monthly_clim_anom: Climatology years '+str(cbeg)+'-'+str(cend))
    if(Diag): print('monthly_clim_anom: Anomaly years '+str(abeg)+'-'+str(aend))
    
    #print('cbeg,ybeg=',cbeg,ybeg)
    
    icbeg=(cbeg-ybeg)*12
    icend=icbeg+(cend-cbeg+1)*12-1
    if(Diag): print('monthly_clim_anom: icbeg,icend=',icbeg,icend)

    iabeg=(abeg-ybeg)*12
    iaend=iabeg+(aend-abeg+1)*12-1
    if(Diag): print('monthly_clim_anom: iabeg,iaend=',iabeg,iaend)
    
    output_shape_climatology=[self.nmy]
    if(input.ndim>1):
      for sss in input.shape[1::]:
        output_shape_climatology.append(sss)
    if(Diag): print('monthly_clim_anom: output_shape_climatology=',output_shape_climatology)
    
    output_shape_anomaly=[ydiff_monthly*self.nmy]
    if(input.ndim>1):
      for sss in input.shape[1::]:
        output_shape_anomaly.append(sss)
    if(Diag): print('monthly_clim_anom: output_shape_anomaly=',output_shape_anomaly)

    if(Diag): print('monthly_clim_anom: input_full.shape=',input_full.shape)
    
    to_shape_monthly=[cend-cbeg+1,self.nmy]
    if(input.ndim>1):
      for sss in output_shape_anomaly[1::]:
        to_shape_monthly.append(sss)
        
    if(Diag): print('monthly_clim_anom: to_shape_monthly=',to_shape_monthly)
    
#    if('monthly_climatology' not in locals()):
    if(type(monthly_climatology)==type(None)):
      monthly_data_reshaped=np.reshape(input_full[icbeg:icend+1,],to_shape_monthly)
      self.monthly_climatology = np.average(monthly_data_reshaped,axis=0)
      #if(Diag): print('monthly_clim_anom: self.monthly_climatology=',self.monthly_climatology)

    #print('xxx',icbeg,icend,cbeg,cend)

    if(self.daily_to_monthly_test):
      self.num_stamp_climatology = np.average(np.reshape(self.num_stamp_monthly[icbeg:icend+1],[cend-cbeg+1,self.nmy]),axis=0) #gone through daily to monthly function.
    else:
      if(self.dummy_mode):
        self.num_stamp_climatology = np.average(np.reshape(self.time_tfreq_full[icbeg:icend+1],[cend-cbeg+1,self.nmy]),axis=0) #original monthly inputs.
      elif(self.nfiles>1): #ensembles
        #j=self.time_tfreq_full[icbeg:icend+1]
        #print('j.shape=',j.shape)
        #print('self.time_tfreq_full.shape=',self.time_tfreq_full.shape)
        #print('input_full.shape=',input_full.shape)
        self.num_stamp_climatology = np.average(np.reshape(self.time_tfreq_full[icbeg:icend+1],[cend-cbeg+1,self.nmy]),axis=0) #original monthly inputs. fuck
      else:
        self.num_stamp_climatology = np.average(np.reshape(self.time_tfreq_full[icbeg:icend+1],[cend-cbeg+1,self.nmy]),axis=0) #original monthly inputs.

    if(AnnOut):
      self.num_stamp_climatology = np.average(self.num_stamp_climatology,weights=self.days_in_month)
    self.date_time_stamp_climatology=netCDF4.num2date(self.num_stamp_climatology,self.time_tfreq_units,self.time_tfreq_calendar)

    #if(Diag): print('self.date_time_stamp_climatology=',self.date_time_stamp_climatology)

    self.year_fraction_climatology=fractional_year_from_num2date(self.date_time_stamp_climatology,self.time_tfreq_calendar) #fuck
    
    if(Diag): print('monthly_clim_anom: self.monthly_climatology.shape=',self.monthly_climatology.shape)
    
    if(Diag): print('monthly_clim_anom: self.days_in_month=',self.days_in_month)
    
    #raise SystemExit('STOP!:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    
    if(ClimOnly):
      if(AnnOut):
        return(np.average(self.monthly_climatology,axis=0,weights=self.days_in_month))
      else:
        return(self.monthly_climatology)
    
    monthly_climatology_repeat1 = np.expand_dims(self.monthly_climatology,-1)
    monthly_climatology_repeat2 = np.tile(monthly_climatology_repeat1,(aend-abeg+1))
    monthly_climatology_repeat = np.moveaxis(monthly_climatology_repeat2,-1,0)

    to_shape_climatology=[(aend-abeg+1)*self.nmy]
    if(input.ndim>1):
      for sss in output_shape_climatology[1::]:
        to_shape_climatology.append(sss)
        
    if(Diag): print('monthly_clim_anom: to_shape_climatology=',to_shape_climatology)

    if(ZeroClim):
      monthly_climatology_flat=0.0
    else:
      monthly_climatology_flat=np.reshape(monthly_climatology_repeat,to_shape_climatology)

    self.monthly_anomaly = input_full[iabeg:iaend+1,] - monthly_climatology_flat

    if(Diag): print('monthly_clim_anom: self.monthly_anomaly.shape=',self.monthly_anomaly.shape)
      
    if(self.daily_to_monthly_test):
      self.num_stamp_anomaly = self.num_stamp_monthly[iabeg:iaend+1] #gone through daily to monthly function.      
    else:
      if(self.dummy_mode):
        self.num_stamp_anomaly = self.time_tfreq_full[iabeg:iaend+1] #original monthly inputs.
      elif(self.nfiles>1): #ensembles
        self.num_stamp_anomaly = self.time_tfreq_full[iabeg:iaend+1] #original monthly inputs. fuck
      else:
        self.num_stamp_anomaly = self.time_tfreq_full[iabeg:iaend+1] #original monthly inputs.
      
    if(AnnOut):
      self.num_stamp_anomaly = np.average(np.reshape(self.num_stamp_anomaly,[aend-abeg+1,self.nmy]), axis=1,weights=self.days_in_month)
    self.date_time_stamp_anomaly=netCDF4.num2date(self.num_stamp_anomaly,self.time_tfreq_units,self.time_tfreq_calendar)

    #print('xxx self.date_time_stamp_anomaly=',self.date_time_stamp_anomaly)

    #print('self.dummy_mode,self.nfiles,self.daily_to_monthly_test=',self.dummy_mode,self.nfiles,self.daily_to_monthly_test)
    if(self.dummy_mode):
      self.year_fraction_anomaly=fractional_year_from_num2date(self.date_time_stamp_anomaly,self.time_tfreq_calendar) #fuck
    elif(self.nfiles>1): #ensembles

      if(self.daily_to_monthly_test):
        self.year_fraction_anomaly=fractional_year_from_num2date(self.date_time_stamp_anomaly,self.time_tfreq_calendar) #fuck
      else:
        self.year_fraction_anomaly=fractional_year_from_num2date(self.date_time_stamp_anomaly[0],self.time_tfreq_calendar) #fuck

    else:
      self.year_fraction_anomaly=fractional_year_from_num2date(self.date_time_stamp_anomaly,self.time_tfreq_calendar) #fuck

    if(Diag): print('monthly_clim_anom: self.num_stamp_anomaly.shape=',self.num_stamp_anomaly.shape)
    
    if(AnnOut):
      to_shape_anomaly=[aend-abeg+1,self.nmy]
      if(input.ndim>1):
        for sss in input_full.shape[1::]:
          to_shape_anomaly.append(sss)
        
      self.monthly_anomaly=np.average(np.reshape(self.monthly_anomaly,to_shape_anomaly), axis=1,weights=self.days_in_month) #actually annual.

    if(AnomOnly):
        return(self.monthly_anomaly)

    if(AnnOut):
        return(np.average(self.monthly_climatology,axis=0,weights=self.days_in_month),self.monthly_anomaly)
    else:
      return(self.monthly_climatology,self.monthly_anomaly)
    
#end of class n_data_funcs
