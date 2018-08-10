class multi_forc_funcs:
  '''
  create new class for dealing with multi forecast processing. this will take advantage of n_data_funcs classes to populate arrays.
  
  '''

  import netCDF4
  import math
  import numpy as np
  import numpy.ma as ma
  import inspect
  import itertools

  nmy=12
#   rad = 4.0*math.atan(1.0)/180.0
#   days_in_month = [31,28,31,30,31,30,31,31,30,31,30,31]

  def __init__(self, **kwargs):
    '''
    take input_files as tuple, and divide up outputs into many cases to be loaded
    into main data array. As all datasets will be put onto common time axis (padded out to complete years)
    will need to restrict some data to avoid massive array. Once the array is complete, then various operations
    can be performed to form climatologies or anomalies relative to different inputs.
    
    For example, use forecast_v1 as main experiment. Read in assimilation run and ncep observations, and hold these in
    array, and write this out to a file so that it can be utilised quickly.
    '''
    import netCDF4
    import math
    import numpy as np
    import numpy.ma as ma
    import inspect
    import itertools
    
    Diag=False
    input_files=None
    for key, value in kwargs.items():
      #print('key=',key)
      if(key=='Diag'):
        Diag=bool(value)
      elif(key=='input_files'):
        input_files=value
        if(Diag): print('input_files=',input_files)
      else:
        raise SystemExit('multi_forc_funcs.init: Dont know that key.'+__file__+' line number: '+str(inspect.stack()[0][2]))
        
    if(type(input_files)==type(None)):
      raise SystemExit('multi_forc_funcs.init: must supply input files.'+__file__+' line number: '+str(inspect.stack()[0][2]))
    else:
      self.input_files=input_files
      
  def calculate_filedatetime_info_multiforc(self,**kwargs):
    from n_data_funcs import n_data_funcs
    from decadal_diag import cmor_datetime, fractional_year_from_num2date, check_valid_data_plot
    from decadal_diag import nino_indices, file_spec_summary, get_timestamp_number, file_sort_ripf

    import numpy as np
    import netCDF4
    import numpy.ma as ma
    import inspect
    import os
    import pickle
    import bz2

    CRED = '\033[91m'
    CEND = '\033[0m'
    
    Diag=Clobber=False
    for key, value in kwargs.items():
      if(key=='Diag'):
        Diag=bool(value)
      elif(key=='quantity'):
        quantity=value
      elif(key=='ivars'):
        ivars=value
      elif(key=='Clobber'):
        Clobber=bool(value)
      elif(key=='output_pkl'):
        _output_data_name=value
      else:
        raise SystemExit('multi_forc_funcs.calculate_filedatetime_info_multiforc: Dont know that key.'+__file__+' line number: '+str(inspect.stack()[0][2]))

#===============================================================================

    print(CRED+'Processing daily NCEP...'+CEND) #1948-2018

    _cbeg_ncepr2=2001
    _cend_ncepr2=2017
    _abeg_ncepr2=2001
    _aend_ncepr2=2017

    if(quantity=='nino'):
      _ncepr2_nino_indices=nino_indices(Diag=True, grid_label='ncep2', index_selection='ALL')

    _ncepr2_monthly_files=n_data_funcs(Diag=False, input_files=self.input_files[2], input_var_name=ivars[0])

    _ncepr2_monthly_files.calculate_filedatetime_info(Diag=False,calendar='proleptic_gregorian')

    _ncepr2_monthly_files.get_latlon_info(Diag=False)

    if(quantity=='nino'):
      _ncepr2_nino_indices.auto_lat_lon(Diag=False, instance_nino=_ncepr2_nino_indices, instance_data=_ncepr2_monthly_files)

      _ncepr2_monthly_quantity_from_monthly=_ncepr2_monthly_files.calculate_quantity(_ncepr2_nino_indices, Diag=True, quantity=quantity)
    else:
      _ncepr2_monthly_quantity_from_monthly=_ncepr2_monthly_files.calculate_quantity('dummy', Diag=True, quantity=quantity)

    _ncepr2_quantity_monthlyclimatology_from_monthly, _ncepr2_quantity_monthly_from_monthly=_ncepr2_monthly_files.monthly_clim_anom( \
      Diag=False, input=_ncepr2_monthly_quantity_from_monthly, AnnOut=False, ZeroClim=True, cbeg=_cbeg_ncepr2, cend=_cend_ncepr2, abeg=_abeg_ncepr2, aend=_aend_ncepr2)  

    print('_ncepr2_quantity_monthly_from_monthly.shape=',_ncepr2_quantity_monthly_from_monthly.shape)
        
#===============================================================================

    print(CRED+'Processing CAFE assim ...'+CEND)
  
    _cbeg_assim=2002
    _cend_assim=2015
    _abeg_assim=2002
    _aend_assim=2015

    if(quantity=='nino'):
      _cafe_assim_nino_indices=nino_indices(Diag=True,grid_label='gn',index_selection='ALL')

    _cafe_monthly_files_assim=n_data_funcs(input_files=self.input_files[1],input_var_name=ivars[1])

    _cafe_monthly_files_assim.calculate_filedatetime_info(calendar='julian')

    _cafe_monthly_files_assim.get_latlon_info(Diag=False,lat='latitude',lon='longitude')

    if(quantity=='nino'):
      _cafe_assim_nino_indices.auto_lat_lon(Diag=False, instance_nino=_cafe_assim_nino_indices, instance_data=_cafe_monthly_files_assim)

      _cafe_quantity_monthly_assim=_cafe_monthly_files_assim.calculate_quantity(_cafe_assim_nino_indices, quantity=quantity)
    else:
      _cafe_quantity_monthly_assim=_cafe_monthly_files_assim.calculate_quantity('dummy', quantity=quantity)

    _cafe_quantity_monthlyclimatology_from_monthly_assim, _cafe_quantity_monthly_from_monthly_assim=_cafe_monthly_files_assim.monthly_clim_anom( \
      Diag=False, input=_cafe_quantity_monthly_assim, AnnOut=False, ZeroClim=True, \
      cbeg=_cbeg_assim, cend=_cend_assim, abeg=_abeg_assim, aend=_aend_assim)

    print('_cafe_quantity_monthly_from_monthly_assim.shape=',_cafe_quantity_monthly_from_monthly_assim.shape)
    
#===============================================================================

    print(CRED+'Processing CAFE forc v1 ...'+CEND)
  
    self.datetime_all, self.datetime_uniq, self.ripf_all, self.ripf_uniq = file_spec_summary(self.input_files[0],False)

#===============================================================================

    for _ripf in self.ripf_all:
      pass
      
#===============================================================================
    #get one ensemble and determine min/max times so that we can create a time axis that spans all forecasts.
    _one_ensemble_allforcs=[]
    for _cnt_one,_input_file in enumerate(self.input_files[0]):
      if(self.ripf_all[_cnt_one]==self.ripf_uniq[0]):
        _one_ensemble_allforcs.append(_input_file)
        #print('_input_file=',_input_file)
    
    _time_min,_time_max=1e20,-1e20
    for _cnt_one, _one_ensemble_oneforc in enumerate(_one_ensemble_allforcs):
      _ifhs = netCDF4.Dataset(_one_ensemble_oneforc)
      _time =_ifhs.variables['time']
      
      if(_cnt_one==0):
        _time_units=_time.units
        _time_calendar=_time.calendar
      else:
        if(_time_units != _time.units):
          print('Warning: calculate_filedatetime_info_multiforc: time units change.')
        
        if(_time_calendar != _time.calendar):
          print('Warning: calculate_filedatetime_info_multiforc: time calendar change.')
      
      _ntime = _time.size
      _time_compare = np.zeros(_ntime+1,dtype=float)
      _time_compare[0:_ntime] = _time[:]
      _time_compare[_ntime] = _time_min
      _time_min = np.min(_time_compare)
      _time_compare[_ntime] = _time_max
      _time_max = np.max(_time_compare)      
      _ifhs.close()
      
    _year_min=netCDF4.num2date(_time_min,_time_units,_time_calendar)
    _year_max=netCDF4.num2date(_time_max,_time_units,_time_calendar)

    print('calculate_filedatetime_info_multiforc: Forecast start times go from ',_time_min,'to',_time_max,'or',_year_min,'to',_year_max)
    
    self.ybeg_full,self.yend_full=netCDF4.num2date(_time_min,_time_units,_time_calendar).year,netCDF4.num2date(_time_max,_time_units,_time_calendar).year
    self.mbeg_full,self.mend_full=netCDF4.num2date(_time_min,_time_units,_time_calendar).month,netCDF4.num2date(_time_max,_time_units,_time_calendar).month

#===============================================================================
    #calculate beg/end years taking into account other data sources ncep & assim.
  
    _ncepr2_ybeg,_ncepr2_yend=_ncepr2_monthly_files.date_time_stamp_anomaly[0].year,_ncepr2_monthly_files.date_time_stamp_anomaly[-1].year
    _ncepr2_mbeg,_ncepr2_mend=_ncepr2_monthly_files.date_time_stamp_anomaly[0].month,_ncepr2_monthly_files.date_time_stamp_anomaly[-1].month
    
    _assim_ybeg,_assim_yend=_cafe_monthly_files_assim.date_time_stamp_anomaly[0].year,_cafe_monthly_files_assim.date_time_stamp_anomaly[-1].year
    _assim_mbeg,_assim_mend=_cafe_monthly_files_assim.date_time_stamp_anomaly[0].month,_cafe_monthly_files_assim.date_time_stamp_anomaly[-1].month
    
    _ybeg_all_inputs=np.min([self.ybeg_full, _ncepr2_ybeg, _assim_ybeg])
    _yend_all_inputs=np.max([self.yend_full, _ncepr2_yend, _assim_yend])
    
    if(Diag): print('_ybeg,_yend_all_inputs=',_ybeg_all_inputs,_yend_all_inputs)

#===============================================================================
    #make this run over full years ie 12 months every year...
    _j,_k,self.date_full,_m,_n,self.time_full=get_timestamp_number(_ybeg_all_inputs,_yend_all_inputs,1,12,_time_units,_time_calendar)

    self.ntime_full=len(self.time_full)

    self.year_fraction_monthly_full=fractional_year_from_num2date(self.date_full,_time_calendar)
    
    _years_months_full=[]
    for _cnt in range(self.date_full.size):
      _years_months_full.append(self.date_full[_cnt].year*100+self.date_full[_cnt].month)
          
#===============================================================================
    #calculate beg/end indices for ncep & assim.
  
    _year_month1_ncepr2=_ncepr2_monthly_files.date_time_stamp_anomaly[0].year*100+_ncepr2_monthly_files.date_time_stamp_anomaly[0].month
    _year_monthN_ncepr2=_ncepr2_monthly_files.date_time_stamp_anomaly[-1].year*100+_ncepr2_monthly_files.date_time_stamp_anomaly[-1].month
    _time_beg_index_ncepr2=_years_months_full.index(_year_month1_ncepr2)
    _time_end_index_ncepr2=_years_months_full.index(_year_monthN_ncepr2) 
    
    _year_month1_assim=_cafe_monthly_files_assim.date_time_stamp_anomaly[0].year*100+_cafe_monthly_files_assim.date_time_stamp_anomaly[0].month
    _year_monthN_assim=_cafe_monthly_files_assim.date_time_stamp_anomaly[-1].year*100+_cafe_monthly_files_assim.date_time_stamp_anomaly[-1].month
    _time_beg_index_assim=_years_months_full.index(_year_month1_assim)
    _time_end_index_assim=_years_months_full.index(_year_monthN_assim)   
    
#===============================================================================

    _TimesThrough=0
    for _cnt_one, _datetime_uniq in enumerate(self.datetime_uniq):
      #print('_cnt_one=',_cnt_one)

      _year_beg_now,_year_end_now,_month_beg_now,_month_end_now=cmor_datetime(_datetime_uniq)
      
      _one_forecast_allens=[]
      for _cnt_two, _datetime_all in enumerate(self.datetime_all):
        #print('_cnt_one,_cnt_two,_datetime_uniq,_TimesThrough=',_cnt_one,_cnt_two,_datetime_uniq,_TimesThrough)
      
        if(_datetime_all==_datetime_uniq): #match just the first one, but might loop over all cases in future...
          _one_forecast_allens.append([self.input_files[0][_cnt_two]])
    
      _one_forecast_allens_sorted=file_sort_ripf([input_file[0] for input_file in _one_forecast_allens],False)
      _one_forecast_allens_sorted_enslist=[] #need to put into ensemble list form [[,,],[,,],[,,]]
      for input_file in _one_forecast_allens_sorted:
        _one_forecast_allens_sorted_enslist.append([input_file])
      
#       if(_month_beg_now=='01'):
#       if(_month_beg_now=='02'):
      if(_month_beg_now!='XX'): #all forecasts
        _TimesThrough+=1
      
        if(quantity=='nino'):
          _cafe_forc_nino_indices=nino_indices(Diag=True,grid_label='gn',index_selection='ALL')

        _cafe_monthly_files_forc=n_data_funcs(Diag=False,input_files=_one_forecast_allens_sorted_enslist,input_var_name=ivars[2])

        _cafe_monthly_files_forc.calculate_filedatetime_info(calendar='julian')

        _cafe_monthly_files_forc.get_latlon_info(Diag=False,lat='latitude',lon='longitude')

        if(quantity=='nino'):
          _cafe_forc_nino_indices.auto_lat_lon(Diag=False, instance_nino=_cafe_forc_nino_indices, instance_data=_cafe_monthly_files_forc)

          _cafe_quantity_monthly_forc=_cafe_monthly_files_forc.calculate_quantity(_cafe_forc_nino_indices, quantity=quantity)
        else:
          _cafe_quantity_monthly_forc=_cafe_monthly_files_forc.calculate_quantity('dummy', quantity=quantity)

        _cafe_quantity_monthlyclimatology_from_monthly_forc, _cafe_quantity_monthly_from_monthly_forc=_cafe_monthly_files_forc.monthly_clim_anom( \
          Diag=False, input=_cafe_quantity_monthly_forc, AnnOut=False, ZeroClim=True)

        if(_TimesThrough==1): #time, forecast, ensemble, indice, will need to make it a function of dimensions after first 3...
          
          print(CRED+'creating empty arrays...'+CEND)
          _front_dims_ncepr1=[self.ntime_full]
          _front_dims_assim=[self.ntime_full]
          _front_dims_ensemble=[self.ntime_full, len(self.ripf_uniq), len(self.datetime_uniq)]
          _front_dims_all=[self.ntime_full, len(self.datetime_uniq)+2] #forecasts + ncepr1 & assim

          _back_dims_ncepr1=_ncepr2_quantity_monthly_from_monthly.shape[1::]
          _back_dims_assim=_cafe_quantity_monthly_from_monthly_assim.shape[1::]
          _back_dims_ensemble=_cafe_quantity_monthly_from_monthly_forc.shape[2::]
          
          _quantity_monthly_ensemble=ma.masked_equal( np.zeros([*_front_dims_ensemble,*_back_dims_ensemble],dtype=float), 0.0) #forc data
          _quantity_monthly_ncepr1=ma.masked_equal( np.zeros([*_front_dims_ncepr1,*_back_dims_ncepr1],dtype=float), 0.0) #assim & ncep
          _quantity_monthly_assim=ma.masked_equal( np.zeros([*_front_dims_assim,*_back_dims_assim],dtype=float), 0.0) #assim & ncep
          _check_valid_data=np.zeros([*_front_dims_all],dtype=int)

          _time_beg_index_keep=ma.masked_equal( np.zeros([len(self.datetime_uniq)+2],dtype=int), 0) #don't need ensemble dimension, add room obs & assim
          _time_end_index_keep=ma.masked_equal( np.zeros([len(self.datetime_uniq)+2],dtype=int), 0) #don't need ensemble dimension, add room obs & assim
  
        _year_month1_full=self.date_full[0].year*100+self.date_full[0].month
        _year_monthN_full=self.date_full[-1].year*100+self.date_full[-1].month
        
        if(_month_beg_now=='01'): #this shouldn't be needed, need to fix in n_data_funcs (to do with years with incomplete months...)
          _year_month1=_cafe_monthly_files_forc.date_time_stamp_anomaly[0][0].year*100+_cafe_monthly_files_forc.date_time_stamp_anomaly[0][0].month
          _year_monthN=_cafe_monthly_files_forc.date_time_stamp_anomaly[0][-1].year*100+_cafe_monthly_files_forc.date_time_stamp_anomaly[0][-1].month
        else:
          _year_month1=_cafe_monthly_files_forc.date_time_stamp_anomaly[0].year*100+_cafe_monthly_files_forc.date_time_stamp_anomaly[0].month
          _year_monthN=_cafe_monthly_files_forc.date_time_stamp_anomaly[-1].year*100+_cafe_monthly_files_forc.date_time_stamp_anomaly[-1].month

        _time_beg_index=_years_months_full.index(_year_month1)
        _time_end_index=_years_months_full.index(_year_monthN)
        
        if(_cafe_monthly_files_forc.PaddedYears):
          _time_beg_index_modified = _cafe_monthly_files_forc.PaddedYears_missing_months_beg
          _time_end_index_modified = _cafe_monthly_files_forc.PaddedYears_last_month_index-1 #check
          
          _time_beg_index = _time_beg_index + _time_beg_index_modified
          _time_end_index = _time_beg_index + (_time_end_index_modified-_time_beg_index_modified) #+1)
          
        _time_beg_index_keep[_cnt_one] = _time_beg_index
        _time_end_index_keep[_cnt_one] = _time_end_index
        
        if(_cafe_monthly_files_forc.PaddedYears):
          _quantity_monthly_ensemble[_time_beg_index:_time_end_index+1,:,_cnt_one,] = \
            _cafe_quantity_monthly_from_monthly_forc[_time_beg_index_modified:_time_end_index_modified+1,] #cnt_one is equivalent to forecast (one for each set of ensembles.)
        else:
          _quantity_monthly_ensemble[_time_beg_index:_time_end_index+1,:,_cnt_one,] = \
            _cafe_quantity_monthly_from_monthly_forc #cnt_one is equivalent to forecast (one for each set of ensembles.)

        _check_valid_data[_time_beg_index:_time_end_index+1,_cnt_one,] = \
          _check_valid_data[_time_beg_index:_time_end_index+1,_cnt_one,] + 1 #should be either missing or one.

#===============================================================================
    #add in data for ncep & assim.

    print(CRED+'Adding in other data sources & plotting ...'+CEND)

    _cnt_one+=1
    _quantity_monthly_ncepr1[_time_beg_index_ncepr2:_time_end_index_ncepr2+1,] = \
      _ncepr2_quantity_monthly_from_monthly
      
    _time_beg_index_keep[_cnt_one] = _time_beg_index_ncepr2
    _time_end_index_keep[_cnt_one] = _time_end_index_ncepr2
  
    _check_valid_data[_time_beg_index_ncepr2:_time_end_index_ncepr2+1,_cnt_one,] = \
      _check_valid_data[_time_beg_index_ncepr2:_time_end_index_ncepr2+1,_cnt_one,] + 1 #should be either missing or one.
      
    _cnt_one+=1
    _quantity_monthly_assim[_time_beg_index_assim:_time_end_index_assim+1,] = \
      _cafe_quantity_monthly_from_monthly_assim
      
    _time_beg_index_keep[_cnt_one] = _time_beg_index_assim
    _time_end_index_keep[_cnt_one] = _time_end_index_assim
    
    _check_valid_data[_time_beg_index_assim:_time_end_index_assim+1,_cnt_one,] = \
      _check_valid_data[_time_beg_index_assim:_time_end_index_assim+1,_cnt_one,] + 1 #should be either missing or one.
      
    _datetime_uniq=self.datetime_uniq
    _datetime_uniq.append('ncepr2'+str(_year_month1_ncepr2)+'-'+str(_year_monthN_ncepr2))
    _datetime_uniq.append('assim'+str(_year_month1_assim)+'-'+str(_year_monthN_assim))
          
#===============================================================================
    #plot check array.
  
    _check_valid_data=ma.masked_equal(_check_valid_data, 0) #turn any zeros into missing...
    
    check_valid_data_plot(Diag=False, times=self.date_full, forecasts=_datetime_uniq, data=_check_valid_data,  xysize=(15,20))
    
#===============================================================================

    print(CRED+'saving to PKL file '+_output_data_name+'...'+CEND)

    _date_full=self.date_full
    
    _time_full=self.time_full
    
    _year_fraction_monthly_full=self.year_fraction_monthly_full
    
    pkl_objects=( \
      _quantity_monthly_ensemble, _quantity_monthly_ncepr1, _quantity_monthly_assim, _time_beg_index_keep, _time_end_index_keep, \
      _check_valid_data, _date_full, _time_full, _year_fraction_monthly_full, _datetime_uniq, _time_units, _time_calendar, \
      _years_months_full)  
        
    if((os.path.exists(_output_data_name) and Clobber) or (not os.path.exists(_output_data_name))):
      print(CRED+'Pkl file exists and deleting...'+CEND)

      if(os.path.exists(_output_data_name)): os.remove(_output_data_name)

      pickling_out = bz2.BZ2File(_output_data_name, "wb")
      pickle.dump( pkl_objects, pickling_out, protocol=4)
      pickling_out.close()
    
#===============================================================================

    return() #end of multi_forc_funcs: calculate_filedatetime_info_multiforc
