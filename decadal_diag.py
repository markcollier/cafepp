from __future__ import print_function #this is to allow print(,file=xxx) feature

def finish(file_name,odir,ofil,ofil_modified,season,fh_printfile):
  '''
  Do final processing, reporting and tidying up.
  '''
  import os

  print('Output: ',file_name,file=fh_printfile)
  print('Will need to put in "importance flag", perhaps it can go in another standard metadata tag?',file=fh_printfile)
  if(season!='ANN' or season!='MON'):
    print('Will need to move this CMIP6 file to slightly different name to clearly specify that it is a special season where the time axis is not continguous.',file=fh_printfile)
  #o.close()
  #if(tdir != odir):
  #  os.rename(tdir+'/'+ofil,odir+'/'+ofil)
  #print('Output file: '+odir+'/'+ofil,file=fh_printfile)

  if(os.path.exists(odir+'/'+ofil) and season != 'MON'):
    print('Output frequency not standard moving', odir+'/'+ofil,' to ',odir+'/'+ofil_modified,file=fh_printfile)
    print('Output frequency not standard moving', odir+'/'+ofil,' to ',odir+'/'+ofil_modified) #print to screen too...
    os.rename(odir+'/'+ofil,odir+'/'+ofil_modified)
  elif(season=='MON'):
    print('Output: ',file_name)
    pass
  else:
    print('xxx',odir+'/'+ofil,file=fh_printfile)
    print('xxx',odir+'/'+ofil) #print to screen too...
    raise SystemExit('Something wrong, expected output file doesn\'t exist.')

  #raise SystemExit('Finished O.K.')
  return

#begin
def filemonth_index(season,ybeg,yend,mbeg,mend,fh_printfile):
  '''
  System for generating array of indices to select months used in temporal averaging from each input file.
  Current thinking is to have it dimensioned nyears,12 even if all months are not there for first and/or last year.

  Want to be able to create arbitrary seasonal outputs. For example, rather than just ANN, might want have a set of annuall defined seasons, all written out in one go. This could be DJF, MAM, JJA, SON, DJF, ... MAM, JJA, DJF. These might be easier and use less disk than utilising each in a seperate file. They might not be continous, e.g. could be just DJF, JJA. These could be DjFMaMJjASoN  DjFJjA for the two examples. But likely not have overlap, so that the seasons describe unique input data.

  '''
  import numpy as np

  nmy=12
  
  tindex_select_maxyears_by_nmy=np.zeros((yend-ybeg+1,12))
  
  print(tindex_select_maxyears_by_nmy.shape,file=fh_printfile)

  ybeg_now=0
  yend_now=yend-ybeg

  #mbeg=4 #temporary
  #mend=2 #temporary
  #mbeg=1 #temporary
  #mend=12 #temporary

  #season='MAM' #tempoarary
  #season='DJF' #tempoarary

  print('ybeg_now=',ybeg_now,' yend_now=',yend_now,file=fh_printfile) 
  print('mbeg=',mbeg,' mend=',mend,file=fh_printfile) 
  
  if ( season=='MON' ):
    sstr=''
    times_in_season=12
    times_in_season=1
    tindex_select_maxyears_by_nmy[:]=1

    if(mbeg!=1):
      tindex_select_maxyears_by_nmy[0,0:mbeg-1]=0
    if(mend!=12):
      tindex_select_maxyears_by_nmy[yend_now-ybeg_now,mend::]=0

    #if(mbeg>1):
    #  tindex_select_maxyears_by_nmy[0,0:mbeg]=0
    #if(mend<12):
    #  tindex_select_maxyears_by_nmy[-1,-(nmy-mend)]=0
    #print(tindex_select_maxyears_by_nmy,file=fh_printfile)
    #raise SystemExit('Forced exit.')

  elif ( season=='DJF' ):

    times_in_season=3
    sstr='_'+season
    #index_start=11 #base 0
    #index_end=index_start+2
    #for y in range(ybeg_now,yend_now+1):
    for y in range(ybeg_now,yend_now+1):
      print('y=',y,file=fh_printfile)
      if(y==ybeg_now):
        if(mbeg<=12): #check, in the least, the first year must have december defined, even if a short year. This may not be true for an odd season definition like NDJF.
          tindex_select_maxyears_by_nmy[y-ybeg_now,11]=1
          #tindex_select_maxyears_by_nmy[y-ybeg_now+1,0:0+times_in_season-1]=1

      elif(y==yend_now):
        if(mend>1): #check
          tindex_select_maxyears_by_nmy[y-ybeg_now,0:0+times_in_season-1]=1
        else:
          tindex_select_maxyears_by_nmy[y-ybeg_now-1,11]=0 #have to unassign previous year december as a consequence.
      else:
        tindex_select_maxyears_by_nmy[y-ybeg_now,0:0+times_in_season-1]=1
        tindex_select_maxyears_by_nmy[y-ybeg_now,11]=1

    #print(tindex_select_maxyears_by_nmy,file=fh_printfile)
    #raise SystemExit('Forced exit.')

  elif ( season=='MAM' ):
    times_in_season=3
    sstr='_'+season
    for y in range(ybeg_now,yend_now+1):
      print('y=',y,file=fh_printfile)
      if(y==ybeg_now):
        if(mbeg<=3): #check
          tindex_select_maxyears_by_nmy[y-ybeg_now,2:2+times_in_season]=1
      elif(y==yend_now):
        if(mend>=5): #check
          tindex_select_maxyears_by_nmy[y-ybeg_now,2:2+times_in_season]=1
      else:
        tindex_select_maxyears_by_nmy[y-ybeg_now,2:2+times_in_season]=1

    #index_start=5 #base 0
    #index_end=(yend-ybeg)*nmy+index_start
    #for y in range(ybeg_now,yend_now+1):
    #for y in range(ybeg_now-ybeg_now,yend_now+1-ybeg_now):
    #for y in range(ybeg_now,yend_now+1):
    #  tindex_select_maxyears_by_nmy[y-1,2:2+3]=1
    #print(tindex_select_maxyears_by_nmy,file=fh_printfile)
    #raise SystemExit('Forced exit.')

  elif ( season=='JJA' ):
    times_in_season=3
    sstr='_'+season
    for y in range(ybeg_now,yend_now+1):
      print('y=',y,file=fh_printfile)
      if(y==ybeg_now):
        if(mbeg<=6): #check
          tindex_select_maxyears_by_nmy[y-ybeg_now,5:5+times_in_season]=1
      elif(y==yend_now):
        if(mend>=8): #check
          tindex_select_maxyears_by_nmy[y-ybeg_now,5:5+times_in_season]=1
      else:
        tindex_select_maxyears_by_nmy[y-ybeg_now,5:5+times_in_season]=1

    #index_start=5 #base 0
    #index_end=(yend-ybeg)*nmy+index_start
    #for y in range(ybeg_now-ybeg_now,yend_now-ybeg_now+1):
    #for y in range(ybeg_now-ybeg_now,yend_now+1-ybeg_now):

    #for y in range(ybeg_now,yend_now+1):
    #  tindex_select_maxyears_by_nmy[y-1,5:5+3]=1

  elif ( season=='SON' ):
    times_in_season=3
    sstr='_'+season
    for y in range(ybeg_now,yend_now+1):
      print('y=',y,file=fh_printfile)
      if(y==ybeg_now):
        if(mbeg<=9): #check
          tindex_select_maxyears_by_nmy[y-ybeg_now,8:8+times_in_season]=1
      elif(y==yend_now):
        if(mend>=11): #check
          tindex_select_maxyears_by_nmy[y-ybeg_now,8:8+times_in_season]=1
      else:
        tindex_select_maxyears_by_nmy[y-ybeg_now,8:8+times_in_season]=1
    #index_start=5 #base 0
    #index_end=(yend-ybeg)*nmy+index_start
    #for y in range(ybeg_now,yend_now+1):
    #for y in range(ybeg_now-ybeg_now,yend_now+1-ybeg_now):
    #for y in range(ybeg_now,yend_now+1):
    #  tindex_select_maxyears_by_nmy[y-1,8:8+3]=1

  elif ( season=='SO' ):
    times_in_season=2
    sstr='_'+season
    #index_start=5 #base 0
    #index_end=(yend-ybeg)*nmy+index_start
    #for y in range(ybeg_now-ybeg_now,yend_now+1-ybeg_now):
    for y in range(ybeg_now,yend_now+1):
      tindex_select_maxyears_by_nmy[y-1,8:8+2]=1
  elif ( season=='DecJan' ):
  #use better season name when months (2 in this case)  may be ambiguous
    times_in_season=2
    sstr='_'+season
    #index_start=5 #base 0
    #index_end=(yend-ybeg)*nmy+index_start
    #for y in range(ybeg_now-ybeg_now,yend_now+1-ybeg_now):
    for y in range(ybeg_now,yend_now+1):
      tindex_select_maxyears_by_nmy[y-1,0]=1
      tindex_select_maxyears_by_nmy[y-1,11]=1

  elif ( season=='ANN' ):
    times_in_season=12
    sstr='_'+season
    for y in range(ybeg_now,yend_now+1):
      print('y=',y,file=fh_printfile)
      if(y==ybeg_now):
        tindex_select_maxyears_by_nmy[y-ybeg_now,mbeg-1:12]=1
        #if(mbeg<=1): #check
        #  tindex_select_maxyears_by_nmy[y-ybeg_now,0:0+times_in_season]=1
      elif(y==yend_now):
        tindex_select_maxyears_by_nmy[y-ybeg_now,0:mend]=1
        #if(mend>=0): #check
        #  tindex_select_maxyears_by_nmy[y-ybeg_now,0:0+times_in_season]=1
      else:
        tindex_select_maxyears_by_nmy[y-ybeg_now,0:0+times_in_season]=1

    #tindex_select_maxyears_by_nmy[:]=1

  else:
    raise SystemExit('That season not established yet.')
  #raise SystemExit('Forced exit.')
  return sstr,times_in_season,tindex_select_maxyears_by_nmy

def time_avg(var,input_fhs,file_index,month_index,weights_values,ibeg,iend,season):
  import numpy as np
  '''
  '''
  #print('ibeg,iend=',ibeg,iend)
  unique_fhs=np.unique(file_index[ibeg:iend+1])
  #print('unique_fhs=',unique_fhs)
  jjj=file_index[ibeg:iend+1]
  #kkk=jjj-file_index[ibeg]
  #print('jjj=',jjj)
  fhs_break=99
  for test in list(range(0,len(jjj))):
    #print('test=',test)
    if(jjj[test]!=jjj[test-1]):
      fhs_break=test
      break

  #print('fhs_break=',fhs_break)

  #print('ibeg,ibeg+fhs_break=',ibeg,ibeg+fhs_break)
  #print('ibeg+fhs_break+1,iend=',ibeg+fhs_break+1,iend)

  #print('len(unique_fhs)=',len(unique_fhs))
  if(len(unique_fhs)==1):
    time=input_fhs[file_index[ibeg]].variables['time'][month_index[ibeg:iend+1]]
    #print('time=',time) 
  else:
    #timeA=input_fhs[file_index[ibeg]].variables['time'][month_index[ibeg:ibeg+fhs_break+1]]
    #timeB=input_fhs[file_index[ibeg+fhs_break+1]].variables['time'][month_index[ibeg+fhs_break+1:iend+1]]
    time=np.concatenate(( input_fhs[file_index[ibeg]].variables['time'][month_index[ibeg:ibeg+fhs_break+1]],input_fhs[file_index[ibeg+fhs_break+1]].variables['time'][month_index[ibeg+fhs_break+1:iend+1]]), axis=0)
  #print('timeA=',timeA) 
  #print('timeB=',timeB) 
  #print('iend-ibeg+1=',iend-ibeg+1)
  if(season!='MON'):
    for xxx in range(iend-ibeg+1):
      #print('xxx=',xxx)
      time[xxx]=time[xxx]*weights_values[ibeg+xxx]
    time=np.sum(time,axis=0)/sum(weights_values[ibeg:iend+1])
  #print(time)
  #print('time.shape=',time.shape)
  #raise SystemExit('Forced exit.')
  return(time)

#def data_wavg(ivarSnow,input_fhs,file_index,month_index,weights_values,levels,nlev,ibeg,iend,season,Forecast,icnt,month_in_file,fh_printfile):
def data_wavg(ivarSnow,input_fhs,locate_file_index_Ntimes_b1_flat_nominus1s,ind_beg,ind_end,month_in_file_total_months_beg_to_end,levels,nlev,MonthlyWeights,month_index_ntims,fh_printfile,var_size):
  #from __future__ import print_function
  '''
  '''

  import numpy as np
  import numpy.ma as ma
  nmy=12
  days_in_month=[31,28,31,30,31,30,31,31,30,31,30,31] #approx (ignoring leap years).

  print('data_wavg: locate_file_index_Ntimes_b1_flat_nominus1s=',locate_file_index_Ntimes_b1_flat_nominus1s,file=fh_printfile)

  locate_file_index_Ntimes_b1_flat_nominus1s=locate_file_index_Ntimes_b1_flat_nominus1s-1 #values are b1, need to subtract 1 to make b0

  print('data_wavg: ivarSnow=',ivarSnow,file=fh_printfile)
  #print('data_wavg: input_fhs=',input_fhs,file=fh_printfile)
  print('data_wavg: locate_file_index_Ntimes_b1_flat_nominus1s=',locate_file_index_Ntimes_b1_flat_nominus1s,file=fh_printfile)
  print('data_wavg: ind_beg,ind_end=',ind_beg,ind_end,file=fh_printfile)
  print('data_wavg: month_in_file_total_months_beg_to_end=',month_in_file_total_months_beg_to_end,file=fh_printfile)
  print('data wavg: month_in_file_total_months_beg_to_end.shape=',month_in_file_total_months_beg_to_end.shape,file=fh_printfile)
  print('data_wavg: levels=',levels,file=fh_printfile)
  print('data_wavg: nlev=',nlev,file=fh_printfile)
  print('data_wavg: MonthlyWeights=',MonthlyWeights,file=fh_printfile)
  print('data_wavg: month_index_ntims=',month_index_ntims,file=fh_printfile)
  print('data_wavg: month_index_ntims.shape=',month_index_ntims.shape,file=fh_printfile)
  print('data_wavg: var_size=',var_size,file=fh_printfile)

#testing out on MONTHLY case. Some of this code needs to be taken up into main routine as it doesn't need to be here.

  weights=[]
  for month in list(range(ind_beg,ind_end+1)):
    print('month=',month,file=fh_printfile)

    print('month_in_file_total_months_beg_to_end[locate_file_index_Ntimes_b1_flat_nominus1s[month]]=',month_in_file_total_months_beg_to_end[locate_file_index_Ntimes_b1_flat_nominus1s[month]],file=fh_printfile)
    weights.append(days_in_month[month_index_ntims[month]]) 

    if(month==ind_beg):
      print('month==ind_beg',file=fh_printfile)
      if(len(var_size)==3 and ( var_size[0]==1 or var_size[0]==12 )):
        data=input_fhs[locate_file_index_Ntimes_b1_flat_nominus1s[month]].variables[ivarSnow][[month_in_file_total_months_beg_to_end[locate_file_index_Ntimes_b1_flat_nominus1s[month]]-1]]
      else:
        print('here xxx',file=fh_printfile)
        data=input_fhs[locate_file_index_Ntimes_b1_flat_nominus1s[month]].variables[ivarSnow][[month_in_file_total_months_beg_to_end[locate_file_index_Ntimes_b1_flat_nominus1s[month]]-1],levels,]
    else:
      print('month!=ind_beg')
      if(len(var_size)==3 and ( var_size[0]==1 or var_size[0]==12 )):
        data=np.vstack((data, input_fhs[locate_file_index_Ntimes_b1_flat_nominus1s[month]].variables[ivarSnow][[month_in_file_total_months_beg_to_end[locate_file_index_Ntimes_b1_flat_nominus1s[month]]-1]]))
      else:
        data=np.vstack((data, input_fhs[locate_file_index_Ntimes_b1_flat_nominus1s[month]].variables[ivarSnow][[month_in_file_total_months_beg_to_end[locate_file_index_Ntimes_b1_flat_nominus1s[month]]-1],levels,]))
    print('data.shape=',data.shape,file=fh_printfile)

  print('weights=',weights,file=fh_printfile)

  if(MonthlyWeights):
    avgdata=np.average(data,axis=0,weights=weights) #note that np.average has weights option. Use None if equal.
  else:
    avgdata=np.average(data,axis=0) #note that np.average has weights option.

  print('avgdata.shape=',avgdata.shape,file=fh_printfile)
  tdata=np.expand_dims(avgdata,axis=0) #add time-dimension when averaging to form season.
  print('tdata.shape=',tdata.shape,file=fh_printfile)
  #raise SystemExit('Forced exit.')
  return(tdata)

#def diag_nhblocking_index(data,lat,lon):
def diag_nhblocking_index(data,*argv):
  '''
  http://www.cpc.ncep.noaa.gov/products/precip/CWlink/blocking/index/index.nh.shtml

  To write out GHGS/GHGN would need to have a new dimension based on size of deltas vector.
  http://www.met.rdg.ac.uk/phdtheses/The%20predictability%20of%20atmospheric%20blocking.pdf
  '''
  import numpy as np
  import inspect

  lat,lon,fh_printfile=argv

  print('blocking data.shape=',data.shape,file=fh_printfile)
  #np.set_printoptions(threshold='nan')
  #print('lat=',lat[:],file=fh_printfile)
  #deltas=np.array([-5.,0.,5.])
  deltas=np.array([-5.,5.,0.])
  blocked=np.zeros((1,len(lon[:])))
#  if(len(data.shape) == 3):
#    blocked=np.zeros((12,len(lon[:])))
#  else:
#    blocked=np.zeros(len(lon[:]))
  #print('lat60d=',lat60d,file=fh_printfile)
  #print('lat40d=',lat40d,file=fh_printfile)

  for delta in range(0,len(deltas)):
    lat40d=np.abs(lat[:] - 40.+deltas[delta]).argmin()
    lat60d=np.abs(lat[:] - 60.+deltas[delta]).argmin()
    lat80d=np.abs(lat[:] - 80.+deltas[delta]).argmin()
    #if(len(data.shape) == 3):
    GHGS=(data[:,lat60d,:]-data[:,lat40d,:])/(lat[lat60d]-lat[lat40d])
    GHGN=(data[:,lat80d,:]-data[:,lat60d,:])/(lat[lat80d]-lat[lat60d])
      #print('GHGS=',GHGS[30],file=fh_printfile)
      #print('GHGN=',GHGN[30],file=fh_printfile)
    blocked=blocked+(np.select([GHGS>0.],[1])+np.select([GHGN<-10.],[1])/2)
    kkk=np.where(blocked>0)
      #jjj=np.where(GHGS.any()>0. and GHGN.any()<-10.)
      #jjj=np.logical_and(GHGS>0.,GHGN<-10.)
      #print(blocked[:],file=fh_printfile)
      #print(kkk[:],file=fh_printfile)
    #else:
    #  GHGS=(data[lat60d,:]-data[lat40d,:])/(lat[lat60d]-lat[lat40d])
    #  GHGN=(data[lat80d,:]-data[lat60d,:])/(lat[lat80d]-lat[lat60d])
    #  #print('GHGS=',GHGS[30],file=fh_printfile)
    #  #print('GHGN=',GHGN[30],file=fh_printfile)
    #  blocked=blocked+(np.select([GHGS>0.],[1])+np.select([GHGN<-10.],[1])/2)
    #  kkk=np.where(blocked>0)
  #print('GHGS.shape=',GHGS.shape,file=fh_printfile)
  #print(blocked.shape)
  #print(blocked)
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  return(blocked,GHGS,GHGN)
  #return(blocked,GHGS,GHGN) #note only delta=0 value kept here.

def init_data(ivarSnow,input_fhs,file_index,month_index,times_in_season_cnt,ntims_out,levels,nlev,weights):
  import numpy as np
#days_in_month=[31,28,31,30,31,30,31,31,30,31,30,31]
#[0 0 0 1 1 1 2 2 2 3 3 3 4 4 4]
#[5 6 7 5 6 7 5 6 7 5 6 7 5 6 7]
  #print('nlev=',nlev,' levels=',levels)
  #print(locals())
  if(len(str(weights))==1):
    www=1.0
  else:
    www=weights[month_index[times_in_season_cnt]]
  if 'nlev' in locals() and nlev>0:
    #print('nlev=',nlev)
    #print('hello2')
    #data=input_fhs[file_index[times_in_season_cnt]].variables[ivarSnow][month_index[times_in_season_cnt],levels,:,:]*www
    print('month_index=',month_index)
    print('times_in_season_cnt=',times_in_season_cnt)
    data=input_fhs[file_index[times_in_season_cnt]].variables[ivarSnow][month_index[times_in_season_cnt:times_in_season_cnt+ntims_out],levels,:,:]*www
    #print(data[:,:])
    print('data.shape=',data.shape)
    print('weights=',weights)
    print('www=',www)
    print('www.shape=',www.shape)
    #print(np.amin(data))
    #print(np.amax(data))
    #print(np.nanmax(data))
    #print(month_index)
    #print(times_in_season_cnt)
    #print(month_index[times_in_season_cnt])
    #raise SystemExit('Forced exit.')
  else:
    #data=input_fhs[file_index[times_in_season_cnt]].variables[ivarSnow][month_index[times_in_season_cnt],:,:]
    print('hhh')
    #print(weights)
    #print(len(range(weights)))
    #raise SystemExit('Forced exit.')
    #print('lll',len("1"))
    #print(len(str(weights)))
    data=input_fhs[file_index[times_in_season_cnt]].variables[ivarSnow][month_index[times_in_season_cnt:times_in_season_cnt+ntims_out],]*www
    print(data.shape)
    #print(data)
    #raise SystemExit('Forced exit.')
  return data

def sum_data(data,ivarSnow,input_fhs,file_index,month_index,times_in_season_cnt,levels,nlev,weights):

  #print('nlev=',nlev,' levels=',levels)
  if(len(str(weights))==1):
    www=1.0
  else:
    www=weights[month_index[times_in_season_cnt]]
  if 'nlev' in locals() and nlev>0:
    data=data+input_fhs[file_index[times_in_season_cnt]].variables[ivarSnow][month_index[times_in_season_cnt],levels,:,:]*www
    #print('3dsum')
  else:
    data=data+input_fhs[file_index[times_in_season_cnt]].variables[ivarSnow][month_index[times_in_season_cnt],]*www
    #print('1dsum')
  return data

def avg_data(data,weight):
  #this can be removed later. As I init/sum the data, I can apply the fraction of the weight (e.g. 1/ total_weight/numseasons)
  #days_in_month=[31,28,31,30,31,30,31,31,30,31,30,31]
  data=data/weight
  return data

def standard(diag,ivarS,data,area_t,lat,lon):

  if(diag and ivarS=='acc_drake'):
    data=diag_acc_drake(data,area_t,lat,lon)
  elif(diag and ivarS=='acc_africa'):
    data=diag_acc_africa(data,area_t,lat,lon)
  elif(diag and ivarS=='mozmbq'):
    data=diag_mozmbq(data,area_t,lat,lon)
  elif(diag and ivarS=='aabw'):
    data=diag_aabw(data,area_t,lat,lon)
  elif(diag and ivarS=='nadw'):
    data=diag_nadw(data,area_t,lat,lon)
  elif(diag and ivarS=='pp'):
    #print(data.shape)
    #raise SystemExit('Forced exit.')
    data=diag_pp(data,depth_edges,area_t,lat,lon)
  elif(diag and ivarS=='ssh'):
    data=diag_ssh(data1,data2,depth_edges,area_t,lat,lon)
  elif(diag and ivarS=='moc'):
    data=diag_moc(data1,data2,depth_edges,area_t,lat,lon)
  elif(diag and ivarS=='moc_atlantic'):
    data=diag_moc_atlantic(data1,data2,depth_edges,area_t,lat,lon)
  elif(diag and ivarS=='moc_pacific'):
    data=diag_moc_pacific(data1,data2,depth_edges,area_t,lat,lon)
  elif(diag and ivarS=='moc_indian'):
    data=diag_moc_indian(data1,data2,depth_edges,area_t,lat,lon)
  elif(diag and ivarS=='shice_cover'):
    data=diag_shice_cover(data,area_t,lat,lon)
  elif(diag and ivarS=='nhice_cover'):
    data=diag_nhice_cover(data,area_t,lat,lon)
  elif(diag and ivarS=='nino34'):
    #print(data.shape)
    data=diag_nino34(data,area_t,lat,lon)
  elif(diag):
    raise SystemExit('Diagnostic variable unknown.')
  return

def diag_acc_drake(data,area_t,lat,lon):
  '''
  '''
  import numpy as np
  #print(data.shape)
  #raise SystemExit('Forced exit.')
  lon=np.add(lon,360.0)
  lon=np.where(lon<360.,lon,lon-360.)
  lat=np.squeeze(lat)
  acc_drake_lat_min=np.abs(lat - -70.).argmin()
  acc_drake_lat_max=np.abs(lat - -54.).argmin()
  acc_drake_lon=np.abs(lon - 292.).argmin()
  #print('lon,latmin,latmax=',acc_drake_lon,acc_drake_lat_min,acc_drake_lat_max)
  ivara=data[acc_drake_lat_min:acc_drake_lat_max,acc_drake_lon]
  ydis=np.zeros(ivara.shape,dtype=np.float)+1.0#assume all distances are same for now.
  data=np.sum(ivara*ydis,axis=0)

def diag_acc_africa(data,area_t,lat,lon):
  '''
  '''
  import numpy as np
  lon=np.add(lon,360.0)
  lon=np.where(lon<360.,lon,lon-360.)
  lat=np.squeeze(lat)
  acc_africa_lat_min=np.abs(lat - -72.).argmin()
  acc_africa_lat_max=np.abs(lat - -33.).argmin()
  acc_africa_lon=np.abs(lon - 20.).argmin()
  ivara=data[acc_africa_lat_min:acc_africa_lat_max,acc_africa_lon]
  ydis=np.zeros(ivara.shape,dtype=np.float)+1.0#assume all distances are same for now.
  data=np.sum(ivara*ydis,axis=0)
  return data

def diag_mozmbq(data,area_t,lat,lon):
  '''
  '''
  import numpy as np
  lon=np.add(lon,360.0)
  lon=np.where(lon<360.,lon,lon-360.)
  lat=np.squeeze(lat)
  mozmbq_lon_min=np.abs(lon - 34.).argmin()
  mozmbq_lon_max=np.abs(lon - 46.).argmin() #min or max
  mozmbq_lat=np.abs(lat - 18.).argmin()
  ivara=data[mozmbq_lat,mozmbq_lon_min:mozmbq_lon_max]
  xdis=np.zeros(ivara.shape,dtype=np.float)+1.0#assume all distances are same for now.
  data=np.sum(ivara*xdis,axis=0)
  return data

def diag_aabw(data,area_t,lat,lon):
  '''
  '''
  import numpy as np
  lon=np.add(lon,360.0)
  lon=np.where(lon<360.,lon,lon-360.)
  lat=np.squeeze(lat)
  aabw_lat_min=np.abs(lat - -90.).argmin()
  aabw_lat_max=np.abs(lat - -60.).argmin()
  #print('aabw_latmin,aabw_latmax=',aabw_lat_min,aabw_lat_max)
  step1=np.cumsum(np.sum(fa.variables['ty_trans'],axis=3),axis=1)+np.sum(fa.variables['ty_trans_gm'],axis=3)
  data=np.amax(np.amax(step1[:,aabw_lat_min:aabw_lat_max],axis=0),axis=0) *-1
  return data

def diag_nadw(data,area_t,lat,lon):
  '''
  '''
  import numpy as np
  lon=np.add(lon,360.0)
  lon=np.where(lon<360.,lon,lon-360.)
  lat=np.squeeze(lat)
  nadw_lat_min=np.abs(lat - 30.).argmin()
  nadw_lat_max=np.abs(lat - 50.).argmin()
  #print('nadw_latmin,nadw_latmax=',nadw_lat_min,nadw_lat_max)
  step1=np.cumsum(np.sum(fa.variables['ty_trans'],axis=3),axis=1)+np.sum(fa.variables['ty_trans_gm'],axis=3)
  #print(step1)
  data=np.amax(np.amax(step1[:,nadw_lat_min:nadw_lat_max],axis=0),axis=0)
  return data

def diag_pp(data,depth_edges,area_t,lat,lon):
  '''
  /short/v19/mtc599/ao_am2/feb17a/plot01/preprocess_bgc.jnl
  '''
  import numpy as np
  nmy=12
  #print(data.shape)
  fac1 = 3.1536e7*12e-15*1e-3    # convert mmol(CO2)/sec to Pg(C)/year
  #depth_edges=fa.variables['st_edges_ocean']
  deplevel=np.abs(np.squeeze(depth_edges) - 200.).argmin()
  depdiffs=np.diff(depth_edges)
  step1=data[0:deplevel,:,:]
  #must be quicker way to form weights:
  #try https://docs.scipy.org/doc/numpy/reference/generated/numpy.broadcast_to.html#numpy.broadcast_to
  #print(step1.shape)
  #print(depdiffs.shape)
  #j=np.broadcast_to(depdiffs[0:deplevel],step1.shape)
  #print(j.shape)
  #raise SystemExit('Forced exit.')
  depwgts=np.ones(step1.shape,dtype=np.float)
  for j in range(0,len(lat)):
    for i in range(0,len(lon)):
      depwgts[:,j,i]=depdiffs[0:deplevel]
  step2=step1*depwgts
  step3=np.sum(step2,axis=0)*106/16.*fac1*area_t
  data=np.sum(np.sum(step3,axis=0),axis=0)
  print('data.shape=',data.shape)
  return data

def diag_nflux(data,depth_edges,area_t,lat,lon):
  '''
  /short/v19/mtc599/ao_am2/feb17a/plot01/preprocess_bgc.jnl
  '''
  import numpy as np
  fac1 = 3.1536e7*12e-15*1e-3    # convert mmol(CO2)/sec to Pg(C)/year
  data=np.sum(np.sum(data*area_t,axis=-1),axis=-1)*fac1
  #print('data.shape=',data.shape)
  #data=np.array(0.0)
  return data

def diag_ep(data,depth_edges,area_t,lat,lon):
  '''
  /short/v19/mtc599/ao_am2/feb17a/plot01/preprocess_bgc.jnl
  '''
  import numpy as np
  fac1 = 3.1536e7*12e-15*1e-3    # convert mmol(CO2)/sec to Pg(C)/year
  #data=np.array(0.0)
  deplevel=np.abs(np.squeeze(depth_edges) - 100.).argmin()
  step1=data[deplevel,]*5/86400*106/16.*fac1*area_t # g(C)/(area_bin)/year units
  data=np.sum(np.sum(step1,axis=-1),axis=-1) #Export production (wdet=5m/s at 100m)"/units="Pg(C)/yr
  #print('deplevel=',deplevel)
  #print('data.shape=',data.shape)
  #raise SystemExit('Forced exit.')
  return data

def diag_ssh(data1,data2,depth_edges,area_t,lat,lon):
  '''
  '''
  import numpy as np
  import seawater
        #http://www.pmel.noaa.gov/maillists/tmap/ferret_users/fu_2000/msg00447.html
  #depth_edges=fa.variables['st_edges_ocean']
  deplevel=np.abs(np.squeeze(depth_edges) - 200.).argmin()
  depdiffs=np.diff(depth_edges)

  temp=data1[0:deplevel,:,:]
  salt=data2[0:deplevel,:,:]
  depwgts=np.ones(salt.shape,dtype=np.float)
  #raise SystemExit('Forced exit.')
  for j in range(0,salt.shape[1]):
    for i in range(0,salt.shape[2]):
      depwgts[:,j,i]=depdiffs[0:deplevel]
  dens=seawater.dens(salt,temp,0)
  dens0=seawater.dens(salt*0.+35.,temp*0.,0)
  ddens = (dens0-dens)/dens0

  data = np.sum(ddens * depwgts,axis=0) - 1.9
  return data

def make_mask3D(data,nbasins,nzb,nlats):
  '''
  '''
  import numpy as np
  import numpy.ma as ma
  import cdms2
  import inspect

  #print('msftyyz data.shape=',data.shape)
  #print(np.shape(data))
  #if(len(np.shape(data))==3):
  #  t0=1
  #else:
  #  t0=np.shape(data)[0]
  tmpdata=np.ma.zeros((1,nbasins,nzb,nlats),dtype='f')
  #print('tmpdata.shape=',tmpdata.shape)
  landMask=np.where( np.array(data,dtype=bool) ,0,1)
  mask_vals=cdms2.open('/home/599/mac599/decadal/CMIP5/ancillary_files/lsmask_20110618.nc','r').variables['mask_ttcell'][:,:,:]

  mask=np.zeros(np.shape(data),dtype=float)

  #print('mask_vals.shape=',mask_vals.shape)
  #print('data.shape=',data.shape)
  #print('mask.shape=',mask.shape)

  mask=mask+np.where(np.expand_dims(mask_vals,axis=0)==2,1,0)
  mask=mask+np.where(np.expand_dims(mask_vals,axis=0)==4,1,0)
  atlantic_arctic_mask=ma.masked_equal(mask,0)

  mask=np.zeros(np.shape(data),dtype=float)
  mask=mask+np.where(np.expand_dims(mask_vals,axis=0)==3,1,0)
  mask=mask+np.where(np.expand_dims(mask_vals,axis=0)==5,1,0)
  indoPac_mask=ma.masked_equal(mask,0)

  mask=np.zeros(np.shape(data),dtype=float)
  mask=mask+np.where(np.expand_dims(mask_vals,axis=0)/np.expand_dims(mask_vals,axis=0)==1,1,0)
  global_mask=ma.masked_equal(mask,0)
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  return atlantic_arctic_mask,indoPac_mask,global_mask

#def diag_msftyyz(data1,data2,atlantic_arctic_mask,indoPac_mask,global_mask,nbasins,nzb,nlats):
def diag_msftyyz(data1,data2,*argv):
  '''
  '''
  import numpy as np
  import numpy.ma as ma
  import cdms2
  import inspect
  atlantic_arctic_mask,indoPac_mask,global_mask,nbasins,nzb,nlats=argv
#  if(len(np.shape(data))==3):
#    t0=1
#  else:
#    t0=np.shape(data)[0]
  #print('t0=',t0)
  data=data1+data2
  tmpdata=np.ma.zeros((1,nbasins,nzb,nlats),dtype='f')
  tmpdata[:,0,:,:]=np.cumsum( np.sum( data*np.where(atlantic_arctic_mask==1,1,1e20) ,axis=-1) ,axis=-2)
  tmpdata[:,1,:,:]=np.cumsum( np.sum( data*np.where(indoPac_mask==1,1,1e20) ,axis=-1) ,axis=-2)
  tmpdata[:,2,:,:]=np.cumsum( np.sum( data*np.where(global_mask==1,1,1e20) ,axis=-1) ,axis=-2)
  data=tmpdata*1e9

  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

    #sss=np.array()
    #print('sss=',sss)
    #raise SystemExit('Forced exit.')
    #print('mask.shape=',mask.shape)
    #landMask=np.array(data,dtype=bool)
    #landMask=np.invert(data,dtype=bool)
    #landMask=np.array(~data,dtype=bool)
    #landMask=np.zeros((50,300,360),dtype=bool)
    #j=np.where(data==np.NA,0,np.NA)
    #print('j=',j)
    #print('data=',data)
    #raise SystemExit('Forced exit.')
    #landMask=np.zeros(data,dtype=bool)
    #print('landMask=',landMask[:])
    #print('landMask.shape=',landMask.shape)
    #data=data*10**9
    #print('hello')
    #data.mask=False
    #print('data=',data)
    #newmask=np.where(mask)
    #mask.mask=np.where(mask_vals==0,0,1)
    #print('mask=',mask)
    #atlantic_arctic_mask_tmp=np.ma.mask_or(np.where(mask==2,1,0),np.where(mask==4,1,0) )
    #indoPac_mask_tmp=np.ma.mask_or(np.where(mask==3,1,0),np.where(mask==5,1,0) )
    #atlantic_arctic_mask=np.ma.mask_or(atlantic_arctic_mask_tmp,landMask)
    #indoPac_mask=np.ma.mask_or(indoPac_mask_tmp,landMask)
    #atlantic_arctic_mask=np.ma.make_mask(np.logical_and(mask!=2.0,mask!=4.0))
    #atlantic_arctic_mask_3D=np.tile(np.expand_dims(atlantic_arctic_mask,0), (nzb,1,1))
    #print('area.shape=',area.shape)
    #indoPac_mask=np.ma.make_mask(np.logical_and(mask!=3.0,mask!=5.0))
    #indoPac_mask_3D=np.tile(np.expand_dims(indoPac_mask,0), (nzb,1,1))
    #for zzz in range(nzb):
    #  #data[zzz,:,:].mask=ma.masked_where(atlantic_arctic_mask,data[zzz,:,:].mask)
    #  #data[zzz,:,:].mask=ma.mask_or(atlantic_arctic_mask,atlantic_arctic_mask)
    #  data[zzz,:,:].mask=atlantic_arctic_mask
    #data.mask=atlantic_arctic_mask_3D
    #if os.path.isfile(odir+'/'+ofil):
    #  os.remove('j.nc')
    #o=netCDF4.Dataset('j.nc','w',format=netcdf)
    #o.createDimension('lat',nlat)
    #o.createDimension('lon',nlon)
    #o.createDimension('lev',nzb)
    #latV=o.createVariable('lat','f8','lat')
    #lonV=o.createVariable('lon','f8','lon')
    #depV=o.createVariable('lev','f8','lev')
    #d1=o.createVariable('data','f4',['lev','lat','lon'],fill_value=1e20)
#    d2=o.createVariable('mask','f4',['lat','lon'],fill_value=1e20)
    #mmm=landMask
    #o.variables['lat'][:] = lat_vals[:]
    #o.variables['lon'][:] = lon_vals_360[:]
    #o.variables['lev'][:] = zt[:]
    #o.variables['data'][:]=mmm[:]
    #o.variables['data'][:]=atlantic_arctic_mask[:]
    #o.variables['data'][:]=landMask[:]
    #o.variables['data'][:]=newmask[:]
    #o.variables['data'][:]=atlantic_arctic_mask[:]
    #o.variables['data'][:]=indoPac_mask[:]
    #o.variables['mask'][:]=mask[:]
    #o.variables['mask'][:]=mask[:]
    #o.close()
    #raise SystemExit('Forced exit.')
    #data0=ma.copy(data)
    #data1=ma.copy(data)
    #data2=ma.copy(data)
    #data1=data
    #data0.mask=np.where(atlantic_arctic_mask==1,1,0)
    #data0.mask=np.ma.mask_or(atlantic_arctic_mask,landMask)
    #data0=data*np.where(atlantic_arctic_mask==1,1,1e20)
    #data1.mask=landMask
    #data1=data*np.where(indoPac_mask==1,1,1e20)
    #data1.mask=np.where(indoPac_mask==1,1,0)
    #data1.mask=indoPac_mask+landMask
    #data1.mask=np.ma.mask_or(indoPac_mask,landMask)
    #data1.mask=np.ma.mask_and(indoPac_mask,landMask)
    #data1.mask=np.ma.mask_or(atlantic_arctic_mask,landMask)
    #data2.mask=landMask
    #data2=data*np.where(global_mask==1,1,1e20)
    #j=np.sum(data,axis=-1)
    #k=np.cumsum(j,axis=-1)
    #print('j.shape=',j.shape)
    #print('k.shape=',k.shape)
    #print('mask=',mask)
    #print('mask.shape=',mask.shape)
    #print('atlantic_arctic_mask=',atlantic_arctic_mask)
    #print('atlantic_arctic_mask.shape=',atlantic_arctic_mask.shape)
    #raise SystemExit('Forced exit.')
    #newdata=np.zeros((1,3,50,300),dtype='f')
  return data

def transPort(var,i_start,i_end,j_start,j_end):
  '''
  transPort
  '''
  import numpy as np
  trans=np.sum( np.sum( np.sum(var[:,j_start:j_end+1,i_start:i_end+1],axis=-1),axis=-1),axis=-1)
  #print('trans=',trans)
  return trans

#def diag_rws500(u,v,lat,lon,fh_printfile):
def diag_rws500(u,v,*argv):
  '''
  rws500
  '''
  import numpy as np
  from windspharm.standard import VectorWind
  from windspharm.tools import prep_data, recover_data, order_latdim
  import spharm

  lat,lon,fh_printfile=argv

  #print('lat=',lat)

  print('u.shape=',u.shape,file=fh_printfile)
  print('v.shape=',v.shape,file=fh_printfile)

  u, u_info = prep_data(u, 'tyx')
  v, v_info = prep_data(v, 'tyx')
  lat, u, v = order_latdim(lat, u, v)

  w = VectorWind(u, v)
  eta = w.absolutevorticity()
  div = w.divergence()
  uchi, vchi = w.irrotationalcomponent()
  etax, etay = w.gradient(eta)

  #eta = recover_data(eta, u_info)
  #div = np.squeeze(w.divergence())
  #uchi, vchi = np.squeeze(w.irrotationalcomponent())

  print('uchi.shape=',uchi.shape,file=fh_printfile)
  print('vchi.shape=',vchi.shape,file=fh_printfile)
  print('eta.shape=',eta.shape,file=fh_printfile)

  S1 = -eta * div
  S2 = -(uchi * etax + vchi * etay)
  S = S1 + S2
  S = recover_data(S,u_info)

  print('S.shape=',S.shape,file=fh_printfile)
  return S 

#def diag_mfo(tx_trans,ty_trans,nlines):
def diag_mfo(tx_trans,ty_trans,*argv):
  '''
  transAcrossLine from app_funcs.py
  '''
  import numpy as np
  import numpy.ma as ma
  import cdms2
  #from app_funcs import *

  nlines,fh_printfile=argv

  #if(len(np.shape(tx_trans))==3):
  t0=1
  #else:
  #  t0=np.shape(data)[0]
  print('tx_trans.shape=',tx_trans.shape)
  #transports= np.zeros([len(tx_trans[:,0,0,0]),len(getTransportLines())],dtype=np.float32)
  transports=np.zeros((t0,nlines),dtype='f')
  print('transports.shape=',transports.shape)
#0 barents opening
  #j=transPort(ty_trans,292,300,271,271)
  #j=transAcrossLine(ty_trans,292,300,271,271)
  #print('j.shape=',j.shape)
  #raise SystemExit('Forced exit.')
  transports[:,0]=transPort(ty_trans,292,300,271,271)
  transports[:,0]+=transPort(tx_trans,300,300,260,271)
  #1 bering strait
  transports[:,1]=transPort(ty_trans,110,111,246,246)
  #2 canadian archipelago
  transports[:,2]=transPort(ty_trans,206,212,285,285)
  transports[:,2]+=transPort(tx_trans,235,235,287,288)
  #3 denmark strait
  transports[:,3]=transPort(tx_trans,249,249,248,251)
  transports[:,3]+=transPort(ty_trans,250,255,247,247)
  #4 drake passage
  transports[:,4]=transPort(tx_trans,212,212,32,49)
  #5 english channel is unresolved by the access model
  #6 pacific equatorial undercurrent
  #specified down to 350m not the whole depth
  transports[:,6]=transPort(np.ma.masked_where( tx_trans[:,0:25,:]<0,tx_trans[:,0:25,:]),124,124,128,145)
  #7 faroe scotland channel    
  transports[:,7]=transPort(ty_trans,273,274,238,238)
  transports[:,7]+=transPort(tx_trans,274,274,232,238)
  #8 florida bahamas strait
  transports[:,8]=transPort(ty_trans,200,205,192,192)
  #9 fram strait
  transports[:,9]=transPort(tx_trans,267,267,279,279)
  transports[:,9]+=transPort(ty_trans,268,284,278,278)
  #10 iceland faroe channel
  transports[:,10]=transPort(ty_trans,266,268,243,243)
  transports[:,10]+=transPort(tx_trans,268,268,240,243)
  transports[:,10]+=transPort(ty_trans,269,272,239,239)
  transports[:,10]+=transPort(tx_trans,272,272,239,239)
  #11 indonesian throughflow
  transports[:,11]=transPort(tx_trans,31,31,117,127)
  transports[:,11]+=transPort(ty_trans,35,36,110,110)
  transports[:,11]+=transPort(ty_trans,43,44,110,110)
  transports[:,11]+=transPort(tx_trans,46,46,111,112)
  transports[:,11]+=transPort(ty_trans,47,57,113,113)
  #12 mozambique channel    
  transports[:,12]=transPort(ty_trans,320,323,91,91)
  #13 taiwan luzon straits
  transports[:,13]=transPort(ty_trans,38,39,190,190)
  transports[:,13]+=transPort(tx_trans,40,40,184,188)
  #14 windward passage
  transports[:,14]=transPort(ty_trans,205,206,185,185)
  return transports

def diag_moc(data1,data2,depth_edges,area_t,lat,lon):
  '''
  want to return depwgts etc. so that they can be used in subsequent passes.
  '''
  import numpy as np
  #http://www.pmel.noaa.gov/maillists/tmap/ferret_users/fu_2000/msg00447.html
  ##depth_edges=fa.variables['st_edges_ocean']
  ##deplevel=np.abs(np.squeeze(depth_edges) - 200.).argmin()
  ##depdiffs=np.diff(depth_edges)
  #print('depdiffs=',depdiffs)
  #print('data.shape=',data.shape)
  #print('depdiffs.shape=',depdiffs.shape)
  ##depwgts=np.resize(depdiffs,data.shape)
  ##xyz=np.resize(depdiffs,(50,12,300,360))
  ##xyz=np.reshape(depdiffs,(50,12,300,360))
  ##xyz=np.tile(depdiffs,(12,50,300))

  #depwgts=np.ones(data.shape,dtype=np.float)
  #if(len(data.shape)==4):
  #  for t in range(0,data.shape[0]):
  #    for j in range(0,len(lat)):
  #      for i in range(0,len(lon)):
  #        depwgts[t,:,j,i]=depdiffs
  #else:
  #  for j in range(0,len(lat)):
  #    for i in range(0,len(lon)):
  #      depwgts[:,j,i]=depdiffs
  #print('depwgts.shape=',depwgts.shape)
  #print('depwgts=',depwgts[:,0,0])
#
#  areawgts=np.ones(data.shape,dtype=np.float)
#  if(len(data.shape)==4):
#    for t in range(0,data.shape[0]):
#      for z in range(0,data.shape[1]):
#        print('t,z=',t,z)
#        areawgts[t,z,:,:]=area_t
#  else:
#    for z in range((data.shape[0])):
#      #print('z=',z)
#      areawgts[z,:,:]=area_t
#  print('areawgts.shape=',areawgts.shape)
#  #raise SystemExit('Forced exit.')

#  #depwgts=np.swapaxes(xyz,1,0)
#  #print('depwgts.shape=',depwgts.shape)
#  #print('ddd=',depwgts[0,:,0,0])
#  #step1=data[:,:,:]
#  #step1=data[:,:,:]
#  #print(step1.shape)
#  #depwgts=np.ones(step1.shape,dtype=np.float)
#  #for j in range(0,len(lat)):
#  #  for i in range(0,len(lon)):
#  #    depwgts[:,j,i]=depdiffs
#  #step2=step1*depwgts

#  step2=data*depwgts*areawgts
#  #print('step2.shape=',step2.shape)
#  step3=np.sum(step2,axis=-1)
#  data=np.cumsum(step3,axis=-1)

  step1=np.sum((data1+data2),axis=-1)
  #print(step1[0,:,50])
  #jjj=step1[0,:,50]
  #print('jjj.shape=',jjj.shape)
  #print(np.cumsum(jjj))
  #print('step1.shape=',step1.shape)
  #data=np.nancumsum(step1,axis=-2) #why does this fail?
  data=np.cumsum(step1,axis=-2)
  #print('data.shape=',data.shape)
  #print(data[0,:,50])
  #raise SystemExit('Forced exit.')
  return data

def diag_moc_atlantic(data1,data2,depth_edges,area_t,lat,lon):
  '''
  '''
  import numpy as np
  lon=np.add(lon,360.0)
  lon=np.where(lon<360.,lon,lon-360.)
  lat=np.squeeze(lat)
  ##depth_edges=fa.variables['st_edges_ocean']
  #depdiffs=np.diff(depth_edges)
  moc_lon_min=np.abs(lon - 280.).argmin()
  moc_lon_max=np.abs(lon - 360.).argmin() #actually needs to be 20 but will need to cycle data...
  step1=data1[:,:,moc_lon_min:moc_lon_max]+data2[:,:,moc_lon_min:moc_lon_max]
  #depwgts=np.ones(step1.shape,dtype=np.float)
  #for j in range(0,len(lat)):
  #  for i in range(0,len(lon[moc_lon_min:moc_lon_max])):
  #    depwgts[:,j,i]=depdiffs
  #step2=step1*depwgts
  #step3=np.sum(step2,axis=2)
  #data=np.cumsum(step3,axis=0)
  step2=np.sum(step1,axis=-1)
  data=np.cumsum(step2,axis=-2)
  return data

def diag_moc_pacific(data1,data2,depth_edges,area_t,lat,lon):
  '''
  '''
  import numpy as np
  lon=np.add(lon,360.0)
  lon=np.where(lon<360.,lon,lon-360.)
  lat=np.squeeze(lat)
  #depth_edges=fa.variables['st_edges_ocean']
  depdiffs=np.diff(depth_edges)
  moc_lon_min=np.abs(lon - 120.).argmin()
  moc_lon_max=np.abs(lon - 280.).argmin()
  step1=data1[:,:,moc_lon_min:moc_lon_max]+data2[:,:,moc_lon_min:moc_lon_max]
  #depwgts=np.ones(step1.shape,dtype=np.float)
  #for j in range(0,len(lat)):
  #  for i in range(0,len(lon[moc_lon_min:moc_lon_max])):
  #    depwgts[:,j,i]=depdiffs
  #step2=step1*depwgts
  step2=np.sum(step1,axis=-1)
  data=np.cumsum(step2,axis=-2)
  return data

def diag_moc_indian(data1,data2,depth_edges,area_t,lat,lon):
  '''
  '''
  import numpy as np
  lon=np.add(lon,360.0)
  lon=np.where(lon<360.,lon,lon-360.)
  lat=np.squeeze(lat)
  #depth_edges=fa.variables['st_edges_ocean']
  depdiffs=np.diff(depth_edges)
  moc_lon_min=np.abs(lon - 30.).argmin()
  moc_lon_max=np.abs(lon - 120.).argmin()
#salso limit lat range to -70,30.
  step1=data1[:,:,moc_lon_min:moc_lon_max]+data2[:,:,moc_lon_min:moc_lon_max]
  #depwgts=np.ones(step1.shape,dtype=np.float)
  #for j in range(0,len(lat)):
  #  for i in range(0,len(lon[moc_lon_min:moc_lon_max])):
  #    depwgts[:,j,i]=depdiffs
  #step2=step1*depwgts
  step2=np.sum(step1,axis=-1)
  data=np.cumsum(step2,axis=-2)
  return data

def diag_shice_cover(data,area_t,lat,lon):
  '''
  '''
  import numpy as np
  import numpy.ma as ma
  step1=ma.masked_values(data[:,0:100,:],-1e20)
  step2=np.sum(step1,axis=0)
  data=np.sum(np.sum(step2*area_t[0:100,:],axis=0),axis=0)*1e-12
  return data
def diag_nhice_cover(data,area_t,lat,lon):
  '''
  '''
  import numpy as np
  import numpy.ma as ma
  step1=ma.masked_values(data[:,200:300,:],-1e20)
  step2=np.sum(step1,axis=0)
  data=np.sum(np.sum(step2*area_t[200:300,:],axis=0),axis=0)*1e-12
  return data

#def diag_rws(data1,data2,lats,lons,outputs_string):
def diag_rws5(data1,data2,*argv):
  '''
    pfull = 3.65029282220392, 19.0883974368005, 52.3401931985815, 
    99.1299239257332, 157.381018593963, 224.749226564636, 298.944381749781, 
    378.086570479306, 458.325137866391, 533.786395581918, 601.717232306161, 
    662.593165914118, 716.859286879887, 764.944402046312, 807.267727191908, 
    844.24236698194, 876.277191904271, 903.778279009585, 927.14956118501, 
    946.793479415368, 963.111301427177, 976.503336402698, 987.369305525111, 
    996.108392737186
  '''
  import numpy as np
  import numpy.ma as ma
  from windspharm.standard import VectorWind
  from windspharm.tools import prep_data, recover_data, order_latdim

  lats,lons,outputs_string,fh_printfile=argv

  #print('data1.shape=',data1.shape)
  #print('data2.shape=',data2.shape)
  #print('uwnd.shape=',uwnd.shape)
  #print('vwnd.shape=',vwnd.shape)
  #print('lats=',lats[:])
  #print('lons=',lons[:])
  #raise SystemExit('Forced exit.')

  #lats=lats_tmp[:]

  uwnd,uwnd_info = prep_data(data1,'zyx')
  vwnd,vwnd_info = prep_data(data2,'zyx')

  lats, uwnd, vwnd = order_latdim(lats, uwnd, vwnd)

  #print('lats=',lats[:])

  w5 = VectorWind(uwnd, vwnd)
  eta5 = w5.absolutevorticity()
  div5 = w5.divergence()
  uchi5, vchi5 = w5.irrotationalcomponent()
  etax5, etay5 = w5.gradient(eta5)
  rws5 = -eta5 * div5 - uchi5 * etax5 + vchi5 * etay5

  #print(eta.shape)
  #eta = recover_data(eta, uwnd_info)
  #S1 = -eta * div
  #S2 = -(uchi * etax + vchi * etay)
  #S = S1 + S2
  #S = -eta * div - (uchi * etax + vchi * etay)

  print('rws5.shape=',rws5.shape)

  if "rws5" in outputs_string:
    rws5 = recover_data(rws5, uwnd_info)
  if "div5" in outputs_string:
    div5 = recover_data(div5, uwnd_info)
  if "eta5" in outputs_string:
    eta5 = recover_data(eta5, uwnd_info)
  if "uchi5" in outputs_string:
    uchi5 = recover_data(uchi5, uwnd_info)
  if "vchi5" in outputs_string:
    vchi5 = recover_data(vchi5, uwnd_info)

  print('rws5.shape=',rws5.shape)
  #Sx=np.flip(S,1)
  #Sx=S[:,::-1,::]
  #Sx=np.rollaxis(S,2)
  #('data.shape=', (90, 144, 24))
  #print('Sx.shape=',Sx.shape)
  #return Sx
  #return S
  #return recover_data(uwnd, uwnd_info)
  #return recover_data(vwnd, uwnd_info)

  s=",";return_what=s.join(outputs_string)
  #return_what="rws,div,eta,uchi,vchi"
  print("return_what=",return_what)

  #if "rws" in outputs_string:
  #  print("yes")
  #else:
  #  print("no")
  #raise SystemExit('Forced exit.')

  #return(rws,div,eta,uchi,vchi)
  return(eval(return_what))

def diag_north_salt_trans(salt,vvel,*argv):
  '''
  note that salinity and northward velocity are on different grids, may need to interpolate to another grid. for now assume same grid.
  '''

  import numpy as np
  import numpy.ma as ma
  import inspect

  north_cell_width,area,nlats,nlons,zt,z0,zb,depth=argv

  z=zb-z0 #zt is level mid-point, z0 is upper bound, zb is lower bound, z is level delta (thickness).

  find_z=np.abs(zb - depth).argmin() #find depth for which to sum over. Might need to add vertical interpolation to find exact depth.

  salt=ma.masked_equal(salt,-1e20)
  vvel=ma.masked_equal(salt,-1e20)

  north_cell_width=np.expand_dims(np.expand_dims(area,0),0)
  north_cell_width=np.tile(north_cell_width ,(1,find_z+1,1,1))

  north_cell_width = north_cell_width*salt/salt

  thickness=np.expand_dims(np.expand_dims(np.expand_dims(z[0:find_z+1],1),2),0)

  thickness=np.tile( thickness ,(1,1,nlats,nlons))

  thickness = thickness*salt/salt

  print(salt.shape)
  print(north_cell_width.shape)

  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  result = np.sum(vvel * north_cell_width * thickness * (salt[:,0:find_z+1,:,:]), axis=1)

  print('total salt transport of ocean=',np.sum(np.sum(np.sum(result))))

  return(result)

#def diag_so5l(data,*argv):
#  '''
#  build up new level by level a new set of so taking into account bounds of input and output. Will need to think about how to deal with missing data especially ocean bottom.
#  '''
#
#  import numpy as np
#  import numpy.ma as ma
#  import inspect
#
#  nlats,nlons,nzt,zt,z0,zb,nzt_new,zt_new,z0_new,zb_new=argv
#
#  #data=ma.masked_equal(data,-1e20)
#
#  #print(data.shape)
#
#  nzt=zt_new.size
#
#  #interpolated_data=np.zeros((1,5,nlats,nlons),dtype=float)
#  interpolated_data=np.zeros((1,nzt_new,nlats,nlons),dtype=float)
#
#  zbounds_new=np.column_stack((z0_new,zb_new))
#
#  for lll in range(0,nzt_new):
#    #print(lll)
#    #print(zbounds_new[lll,:])
#    interpolated_data[:,lll,:,:]=ocean_vertical_interpolate(data,nlats,nlons,zt,zb,z0,zbounds_new[lll,:])
#
#  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
#
#  return interpolated_data

def diag_dTbydz(data,*argv):
  '''
need to think of clever way to export new vertical coordinate and have it defined before the cmor dimension definitions are performed.
  '''

  import numpy as np
  import numpy.ma as ma
  import inspect

  nlats,nlons,nzt,zt,z0,zb=argv

  data=ma.masked_equal(data,-1e20)

  data_new=np.zeros((1,nzt,nlats,nlons),dtype=float)

  zt_new=np.zeros(nzt-1,dtype=float)
  dz=zb-z0

  #print(data.shape)
  #nzt=zt.size
  #print('zt: mid level depth value.')
  #print('z0: top level depth value.')
  #print('zb: bottom level depth value.')
  #print('dz: level thickness .')
  #print('data: data value at depth zt.')

  #print("     zt    z0    zb    dz  data")
  #print("     zt    z0    zb    dz")
  for zzz in range(1,nzt):
    #print("%5.2f"% zt[zzz], "%5.2f"% z0[zzz], "%5.2f"% zb[zzz], "%5.2f"% dz[zzz], "%5.2f"% data[zzz])
    #print("%2.0f"% zzz, "%5.2f"% zt[zzz], "%5.2f"% z0[zzz], "%5.2f"% zb[zzz], "%5.2f"% dz[zzz])

    for lll in range(1,nzt-1):
      data_new[:,lll,:,:]=(data[:,lll+1,:,:]-data[:,lll,:,:]) / (zt[lll+1]-zt[lll])
      zt_new[lll]=(zt[lll+1]+zt[lll])/2.
  #output=np.amax(data_new,axis=1)

  #print(data_new.shape)

  #print(zt_new)
  #print(output.shape)
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  return data_new

def diag_maxdTbydz(data,*argv):
  '''
  '''

  import numpy as np
  import numpy.ma as ma
  import inspect

  nlats,nlons,nzt,zt,z0,zb=argv

  data=ma.masked_equal(data,-1e20)

  data_new=np.zeros((1,nzt-1,nlats,nlons),dtype=float)
  zt_new=np.zeros(nzt-1,dtype=float)
  dz=zb-z0

  #print(data.shape)
  #nzt=zt.size
  #print('zt: mid level depth value.')
  #print('z0: top level depth value.')
  #print('zb: bottom level depth value.')
  #print('dz: level thickness .')
  #print('data: data value at depth zt.')

  #print("     zt    z0    zb    dz  data")
  #print("     zt    z0    zb    dz")
  for zzz in range(0,nzt):
    #print("%5.2f"% zt[zzz], "%5.2f"% z0[zzz], "%5.2f"% zb[zzz], "%5.2f"% dz[zzz], "%5.2f"% data[zzz])
    #print("%2.0f"% zzz, "%5.2f"% zt[zzz], "%5.2f"% z0[zzz], "%5.2f"% zb[zzz], "%5.2f"% dz[zzz])

    for lll in range(0,nzt-1):
      data_new[:,lll,:,:]=(data[:,lll+1,:,:]-data[:,lll,:,:]) / (zt[lll+1]-zt[lll])
      zt_new[lll]=(zt[lll+1]+zt[lll])/2.
  output=np.amax(data_new,axis=1)

  #print(zt_new)
  #print(output.shape)
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  return output

def diag_depmaxdTbydz(data,*argv):
  '''
  '''

  import numpy as np
  import numpy.ma as ma
  import inspect

  nlats,nlons,nzt,zt,z0,zb=argv

  data=ma.masked_equal(data,-1e20)

  data_new=np.zeros((1,nzt-1,nlats,nlons),dtype=float)
  output=np.zeros((1,nlats,nlons),dtype=float)
  zt_new=np.zeros(nzt-1,dtype=float)
  dz=zb-z0

  #print(data.shape)
  #nzt=zt.size
  #print('zt: mid level depth value.')
  #print('z0: top level depth value.')
  #print('zb: bottom level depth value.')
  #print('dz: level thickness .')
  #print('data: data value at depth zt.')
  #print("     zt    z0    zb    dz  data")
  #print("     zt    z0    zb    dz")
  #for zzz in range(0,nzt):
    #print("%5.2f"% zt[zzz], "%5.2f"% z0[zzz], "%5.2f"% zb[zzz], "%5.2f"% dz[zzz], "%5.2f"% data[zzz])
    #print("%2.0f"% zzz, "%5.2f"% zt[zzz], "%5.2f"% z0[zzz], "%5.2f"% zb[zzz], "%5.2f"% dz[zzz])

  for lll in range(0,nzt-1):
    data_new[:,lll,:,:]=(data[:,lll+1,:,:]-data[:,lll,:,:]) / (zt[lll+1]-zt[lll])
    zt_new[lll]=(zt[lll+1]+zt[lll])/2.
  zindex_where_max=np.argmax(data_new,axis=1) #note only first occurence of maximum value is obtained, usually OK.

  #print(zt_new)
  #print(zt_new.shape)
  #zt_new3d=np.expand_dims(np.expand_dims(np.expand_dims(zt_new,0),2),3)
  #zt_new3d=np.tile( zt_new3d,(1,1,nlats,nlons))
  #print(zt_new3d.shape)
  #jjj=data_new[output]
  #print(jjj.shape)
#* data[:,0,:,:]/data[:,0,:,:]
  #print('zindex_where_max.shape=',zindex_where_max.shape)
  #print('data_new.shape=',data_new.shape)
  #print('zt_new3d.shape=',zt_new3d.shape)

  for jj in range(0,nlats):
    for ii in range(0,nlons):
      output[:,jj,ii]=zt_new[zindex_where_max[:,jj,ii]]
  output=output * data[:,0,:,:]/data[:,0,:,:]

  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  return output

def diag_varNl(data,*argv):
  '''
  build up new level by level a new set of thetao taking into account bounds of input and output. Will need to think about how to deal with missing data especially ocean bottom.
  '''

  import numpy as np
  import numpy.ma as ma
  import inspect

  nlats,nlons,nzt,zt,z0,zb,nzt_new,zt_new,z0_new,zb_new=argv

  #data=ma.masked_equal(data,-1e20)

  #print(data.shape)

  nzt=zt_new.size
  #zbounds_new=np.column_stack((z0_new,zb_new)).flatten()
  zbounds_new=np.column_stack((z0_new,zb_new))

  #interpolated_data=np.zeros((1,5,nlats,nlons),dtype=float)
  if(nzt==1):
    interpolated_data=np.zeros((1,nlats,nlons),dtype=float)

    #print(zt,zb,z0,zbounds_new)
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

    #jjj=ocean_vertical_interpolate(data,nlats,nlons,zt,zb,z0,zbounds_new[:,])
    #print(jjj.shape)
    interpolated_data[:,:,:]=ocean_vertical_interpolate(data,nlats,nlons,zt,zb,z0,zbounds_new[:,])
  else:
    interpolated_data=np.zeros((1,nzt_new,nlats,nlons),dtype=float)
    print(zt,zb,z0,zbounds_new)
    for lll in range(0,nzt_new):
      interpolated_data[:,lll,:,:]=ocean_vertical_interpolate(data,nlats,nlons,zt,zb,z0,zbounds_new[lll,:])

  #np.set_printoptions(threshold='nan') #will print out whole array
  #print(interpolated_data[:])
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  return interpolated_data

#def diag_thetao10l(data,*argv):
#  '''
#  build up new level by level a new set of thetao taking into account bounds of input and output. Will need to think about how to deal with missing data especially ocean bottom.
#  '''
#
#  import numpy as np
#  import numpy.ma as ma
#  import inspect
#
#  nlats,nlons,nzt,zt,z0,zb,nzt_new,zt_new,z0_new,zb_new=argv
#
#  #data=ma.masked_equal(data,-1e20)
#
#  #print(data.shape)
#
#  interpolated_data=np.zeros((1,nzt_new,nlats,nlons),dtype=float)
#
#  zbounds_new=np.column_stack((z0_new,zb_new))
#
#  for lll in range(0,nzt_new):
#    #print(lll)
#    #print(zbounds_new[lll,:])
#    interpolated_data[:,lll,:,:]=ocean_vertical_interpolate(data,nlats,nlons,zt,zb,z0,zbounds_new[lll,:])
#  print(interpolated_data.shape)
#
#  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
#
#  return interpolated_data

def diag_thetao0to80m(data,*argv):
  '''
  '''

  import numpy as np
  import numpy.ma as ma
  import inspect

  nlats,nlons,zt,z0,zb=argv

  data=ma.masked_equal(data,-1e20)

  print(data.shape)

  lev_top_bot=np.array([0.0, 80.0])
  lev_top_bot=np.array([5.0, 80.0])
  lev_top_bot=np.array([5.0, 85.0])

  result=ocean_vertical_interpolate(data,nlats,nlons,zt,zb,z0,lev_top_bot)

  #print(result.shape)

  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  return(result)

def diag_salt_content(data,*argv):
  '''
  '''

  import numpy as np
  import numpy.ma as ma
  import inspect

  area,nlats,nlons,zt,z0,zb,depth=argv

  data=ma.masked_equal(data,-1e20)

  #print(data.shape)

  z=zb-z0 #zt is level mid-point, z0 is upper bound, zb is lower bound, z is level delta (thickness).

  find_z=np.abs(zb - depth).argmin() #find depth for which to sum over. Might need to add vertical interpolation to find exact depth.

  print('total area of earth=',np.sum(np.sum(area)))

  area=np.expand_dims(np.expand_dims(area,0),0)
  area=np.tile(area ,(1,find_z+1,1,1))

  area = area*data/data

  print(area.shape)

  print('total area of ocean=',np.sum(np.sum(area[0,0,:])))

  thickness=np.expand_dims(np.expand_dims(np.expand_dims(z[0:find_z+1],1),2),0)

  thickness=np.tile( thickness ,(1,1,nlats,nlons))

  thickness = thickness*data/data

  mass = thickness * area * 1020.0 #of ocean

  volume = thickness * area

  print('total mass of water=',np.sum(np.sum(np.sum(mass))))

  print('total volume of ocean=',np.sum(np.sum(np.sum(volume))))

#salt in psu not g/kg or kg/kg

  result = np.sum(thickness * area * (data[:,0:find_z+1,:,:]*1.), axis=1)

  print('total salt of ocean=',np.sum(np.sum(np.sum(result))))

#total salt/volume agrees with: https://www.quora.com/How-much-total-NaCl-is-dissolved-in-all-of-the-oceans-and-seas-on-Earth-accounting-for-differences-in-salinity-and-how-would-we-estimate-this-figure

#total area of ocean agrees with:

  return(result)

def diag_north_heat_trans(temp,vvel,*argv):
  '''
  note that temperature and northward velocity are on different grids, may need to interpolate to another grid. for now assume same grid.
  '''

  import numpy as np
  import numpy.ma as ma
  import inspect

  north_cell_width,area,nlats,nlons,zt,z0,zb,depth=argv

  z=zb-z0 #zt is level mid-point, z0 is upper bound, zb is lower bound, z is level delta (thickness).

  find_z=np.abs(zb - depth).argmin() #find depth for which to sum over. Might need to add vertical interpolation to find exact depth.

  temp=ma.masked_equal(temp,-1e20)
  vvel=ma.masked_equal(temp,-1e20)

  north_cell_width=np.expand_dims(np.expand_dims(area,0),0)
  north_cell_width=np.tile(north_cell_width ,(1,find_z+1,1,1))

  north_cell_width = north_cell_width*temp/temp

  thickness=np.expand_dims(np.expand_dims(np.expand_dims(z[0:find_z+1],1),2),0)

  thickness=np.tile( thickness ,(1,1,nlats,nlons))

  thickness = thickness*temp/temp

  print(temp.shape)
  print(north_cell_width.shape)

  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  result = np.sum(vvel * north_cell_width * thickness * (temp[:,0:find_z+1,:,:]+273.15) * 1020.0 * 4184.0, axis=1)

  print('total heat transport of ocean=',np.sum(np.sum(np.sum(result))))

  return(result)

#def diag_heat_content(data,lev,value):
def diag_heat_content(data,*argv):

  '''
  http://www.geo.utexas.edu/courses/387H/Lectures/term_Chris.pdf
  https://www.sciencedaily.com/terms/seawater.htm
  http://pordlabs.ucsd.edu/ltalley/sio210/transports/index.html
  http://pordlabs.ucsd.edu/jen/sio210/lecture_heat_salt_transports_US.ppt
  http://sam.ucsd.edu/sio210/lect_2/lecture_2.html

  Q = CpmT (J)
  dQ = CpmdT

  Q = Cp p T (J/m^3), where p is density

  Q is total heat content (J)
  Cp is the specific heat capacity at constant pressure (J kg-1 K-1), Cp=4184.
  m is the mass of the material (kg)
  T is temperature (K)

  or J/m^2 if integrate over depth only

  '''

  import numpy as np
  import numpy.ma as ma
  import inspect

  data=ma.masked_equal(data,-1e20)

  #print(data)
  #print(data.filled())
  #print(data.fill_value)
  #data
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  area,nlats,nlons,zt,z0,zb,depth=argv

  #depth=200.#temporary
  #depth=10000.#temporary
  z=zb-z0 #zt is level mid-point, z0 is upper bound, zb is lower bound, z is level delta (thickness).

  find_z=np.abs(zb - depth).argmin() #find depth for which to sum over. Might need to add vertical interpolation to find exact depth.

  #print(zt,z0,zb,z)

  #print(data.shape)

  #print('zb=',zb)

  #print(area.shape)

  #print('find_z=',find_z)

  #print('total_area=',np.sum(np.sum(area)))

  print('integrating from surface to depth ',zb[find_z])

  #j=np.reshape(z,(50,300,360))
  #j=np.tile(z,(50,300,360))
  #print(j.shape)

  print('total area of earth=',np.sum(np.sum(area)))

  area=np.expand_dims(np.expand_dims(area,0),0)
  area=np.tile(area ,(1,find_z+1,1,1))

  area = area*data/data

  print('total area of ocean=',np.sum(np.sum(area[0,0,:])))

  #print(area.shape)

  thickness=np.expand_dims(np.expand_dims(np.expand_dims(z[0:find_z+1],1),2),0)

  thickness=np.tile( thickness ,(1,1,nlats,nlons))

  thickness = thickness*data/data

  mass = thickness * area * 1020.0 #of ocean

  volume = thickness * area

  print('total mass of water=',np.sum(np.sum(np.sum(mass))))

  print('total volume of ocean=',np.sum(np.sum(np.sum(volume))))

  #print('thickness.shape=',thickness.shape)

  #print('thickness.shape=',thickness.shape)

  #print('area',area[0,:,30,30])
  #print('thickness',thickness[0,:,30,30])
  #print('data',data[0,:,50,50])
  #print(data[0,0,50:60,100:120][:])

  #print(depth)

  #could calculate dependent density and heat capacity using seawater package.

  result = np.sum(thickness * area * (data[:,0:find_z+1,:,:]+273.15) * 1020.0 * 4184.0, axis=1)

  print('total heat content of ocean *10^22=',np.sum(np.sum(np.sum(result)))/10**22)

  #result = np.sum(thickness * (data[:,0:find_z+1,:,:]+273.15) * 1020.0 * 4184.0, axis=1)
  #result = np.sum(thickness * (data[:,0:find_z+1,:,:]+0.) * 1020.0 * 4184.0, axis=1)

#/ np.sum(thickness,axis=1)

  #print(result.shape)

  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  return(result)

def diag_isothetaoNc(data,lev,value):
  '''
  '''
  import numpy as np
  import numpy.ma as ma
  #from decadal_diag import calc_iso_surface
  #from decadal_diag import calc_isoN 

  nmy=12

#generate a mask based on where isosurface is not defined so that it can applied on output data.

#  isomask=np.zeros((300,360),dtype='f')

#  for j in range(0,300):
#    for i in range(0,360):

#      depwgts[:,j,i]=depdiffs

  #print('data=',data)
  #print('diag_isothetaoNc data.shape=',data.shape)

  data=ma.getdata(data)

  #data=ma.masked_invalid(ma.getdata(data))
  #data=np.nan_to_num(ma.getdata(data))

  data_shape=data.shape
  data_size=len(data.shape)

  #print('data=',data[:,0,180])
  #raise SystemExit('Forced exit.')

  lmax=25 #hard-wired for CAFE (approx. 500m)
  ymin=59 #hard-wired for CAFE (approx. 45S)
  ymax=209 #hard-wired for CAFE (approx. 45N)

  if(data_size==3): #this doesn't exist anymore, all arrays must have leading time dimension.
  #single time data e.g. ANN
    #('data.shape=', (50, 300, 360))
    #data=np.swapaxes(data,0,2)
    #data=np.swapaxes(data,0,1)
    #data=calc_iso_surface(data, my_value=value, zs=lev, interp_order=6)
    #data=np.nan_to_num(data)
    #newdata=np.where(data==0,1e20,data)
    newdata=calc_isoN(data, value=value, levs=lev, lmax=lmax, ymin=ymin, ymax=ymax, diag=False)
  else:
  #monthly time data MON
    #newdata=np.zeros((nmy,data_shape[2],data_shape[3])) #monthly
    newdata=np.zeros((data_shape[0],data_shape[2],data_shape[3]))
    #for mnow in range(0,nmy): #monthly
    for tnow in range(0,data_shape[0]):
      #print('tnow=',tnow)
      newdata[tnow,]=calc_isoN(data[tnow,], value=value, levs=lev, lmax=lmax, ymin=ymin, ymax=ymax, diag=False)

    #raise SystemExit('Forced exit.')

      #data_tmp=data[mnow,] 
      #data_tmp=np.swapaxes(data_tmp,0,2)
      #data_tmp=np.swapaxes(data_tmp,0,1)
      #newdata[mnow,]=calc_iso_surface(data_tmp, my_value=value, zs=lev, interp_order=6)
  return newdata

    #('data.shape=', (12, 50, 300, 360))
    #('data.shape=', (12, 360, 300, 50))
    #('data.shape=', (12, 300, 360, 50))
  #print('data.shape=',data.shape)
  #lon=np.where(lon<360.,lon,lon-360.)
  #data=np.ma.masked_less_equal(data,0)
  #print('data=',data)
  #print('data.shape=',data.shape)
  #print('data=',data[:,180])

  #raise SystemExit('Forced exit.')
  return data

#def diag_nino34(data,area_t,lat,lon,fh_printfile):
def diag_nino34(data,*argv):
  '''
  #5s-5n,170-120W
  Comput the Nino34 index from upper level (temporarly averaged in seasonal average case) SST.
  Parameters
  ----------
  data : data object usually SST(lat,lon)
  area_t : corresponding object of area weights
  lat : raw lats
  lon : raw lons

  Returns
  -------

  data : Nino34 index (scalar or vector depending on inputs)
  '''
  import numpy as np
  #print('data.shape=',data.shape)
  #print('argv0=',argv[0])
  #print('argv1=',argv[1])
  #print('argv2=',argv[2])
  #lon=argv[0]
  area_t,lat,lon,fh_printfile=argv
  #for arg in argv:
  #  print('another arg through *argv :',arg)
  #raise SystemExit('Forced exit.')
  #lon=np.add(lon,360.0)
  #lon=np.where(lon<360.,lon,lon-360.)

  lon=np.add(lon,360.0)
  lon=np.where(lon<360.,lon,lon-360.)
  lon=np.roll(lon,80)

  #print('lat=',lat,file=fh_printfile)

  lat=np.squeeze(lat)
  area_t=np.roll(area_t,80,axis=-1)
  data=np.roll(data,80,axis=-1)

  #print('data.shape=',data.shape)

  #print('lat=',lat,file=fh_printfile)
  #print('lon=',lon,file=fh_printfile)

  #print('lat.shape=',lat.shape,file=fh_printfile)
  #print('lon.shape=',lon.shape,file=fh_printfile)

  nino34_lat_min=np.abs(lat - -5.).argmin()
  nino34_lat_max=np.abs(lat - 5.).argmin()
  nino34_lon_min=np.abs(lon - 190.).argmin()
  nino34_lon_max=np.abs(lon - 240.).argmin()

  #nino34_lat_min=50
  #nino34_lat_max=55
  #nino34_lon_min=50
  #nino34_lon_max=55
  #print('diag_nino34: nino34_lat,lon,(min,max)=',nino34_lat_min,nino34_lat_max,nino34_lon_min,nino34_lon_max,file=fh_printfile)
  #raise SystemExit('Forced exit.')
  #print('data.shape=',data.shape,file=fh_printfile)
  #print('area_t.shape',area_t.shape,file=fh_printfile)
  #j=np.vstack((area_t,area_t))
  #j=np.resize(area_t,data.shape)
  data_shape=data.shape
  data_size=len(data_shape)
  #print('data_shape=',data_shape)
  #print('data_size=',data_size)

  ntims=data_shape[0]
  #nlevs=s[1]
  nlats=data_shape[-2]
  nlons=data_shape[-1]

  newdata=np.zeros(ntims,dtype=float)

  if(data_size==3):
    nlevs=1
  else:
    nlevs=data_shape[1]

  if(data_size==3): #sst
    for t in range(ntims):
      newdata[t]=xtra_nino34(data[t,],nino34_lat_min,nino34_lat_max,nino34_lon_min,nino34_lon_max,area_t,fh_printfile)
  else: #temp
    for t in range(ntims):
      newdata[t]=xtra_nino34(data[t,0,],nino34_lat_min,nino34_lat_max,nino34_lon_min,nino34_lon_max,area_t,fh_printfile)
  #print(newdata)
  #raise SystemExit('Forced exit.')

  #  for t in range(ntims):
  #    data=xtra_nino34(data,nino34_lat_min,nino34_lat_max,nino34_lon_min,nino34_lon_max,area_t,fh_printfile)

##in future all data will have time dimension.
#  if(len(s)==3):
#    #has time dimension in it.
#    newdata=np.zeros(s[0])
#    #print('newdata.shape=',newdata.shape,file=fh_printfile)
#    #print('tmpdata.shape=',tmpdata.shape,file=fh_printfile)
#    for q in range(s[0]):
#      tmpdata=data[q,]
#      #print('q=',q,file=fh_printfile)
#      #print('tmpdata.shape=',tmpdata.shape,file=fh_printfile)
#      newdata[q]=xtra_nino34(tmpdata,nino34_lat_min,nino34_lat_max,nino34_lon_min,nino34_lon_max,area_t,fh_printfile)
#    data=newdata 
#      #print('newdata=',newdata,file=fh_printfile)
#  else:
#    data=xtra_nino34(data,nino34_lat_min,nino34_lat_max,nino34_lon_min,nino34_lon_max,area_t,fh_printfile)
#    #print('xxdata=',data,file=fh_printfile)
#    #raise SystemExit('Forced exit.')
  return(newdata)

#    Vshape=salt.shape
#    ntims=Vshape[0]
#    nlevs=Vshape[1]
#
#    #print('Vshape=',Vshape)
#    if(nlats!=Vshape[-2]): raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
#    if(nlons!=Vshape[-1]): raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

def xtra_nino34(data,nino34_lat_min,nino34_lat_max,nino34_lon_min,nino34_lon_max,area_t,fh_printfile):
  '''
  As diag_nino34 needs to cope with arrays with and without a time dimension, it is more compact to define a function that can work in both cases.
  '''
  import numpy as np
  #print('xtra_nino34: nino34_lat,lon,(min,max)=',nino34_lat_min,nino34_lat_max,nino34_lon_min,nino34_lon_max,file=fh_printfile)
  data=np.sum(np.sum(data[nino34_lat_min:nino34_lat_max,nino34_lon_min:nino34_lon_max]*area_t[nino34_lat_min:nino34_lat_max,nino34_lon_min:nino34_lon_max],axis=0),axis=0) / np.sum(np.sum(area_t[nino34_lat_min:nino34_lat_max,nino34_lon_min:nino34_lon_max],axis=0),axis=0)
  return data

def MustHaveAllLevs(TestIt):
  if(TestIt):
    raise SystemExit('Need all depth levels for this diagnostic.')
  return

#see seawater/extras.py dist
#http://stackoverflow.com/questions/15736995/how-can-i-quickly-estimate-the-distance-between-two-latitude-longitude-points
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km
#end

def create_odirs(ovars,institution_id,source_id,experiment_id,ripf,table,grid_label,version):
    """
    Text
    """
    odir=[]
    for o in range(0,len(ovars)):
      odir.append('CMIP6/CMIP/'+institution_id+'/'+source_id+'/'+experiment_id+'/'+ripf+'/'+table+'/'+ovars[o]+'/'+grid_label+'/'+version)
    return odir

def create_ofils(season,table,ovars,experiment_id,source_id,ripf,grid_label,ybeg,yend,mbeg,mend,dbeg,dend):
    """
    Text
    """
    ofil=[]
    ofil_modified=[]
    #mbeg=1 #temporary
    #mend=12 #temporary

    for o in range(0,len(ovars)):
      #if(dbeg>0 or dend>0): print('hello')
      #print(table)
      #raise SystemExit('Forced exit.')

      if(season == 'DJF' or season == 'DecJan'):
        ybeg_here=ybeg+1
      else:
        ybeg_here=ybeg

      if(table=='Oday' or table=='day'):
        ofil.append(ovars[o]+'_'+table+'_'+experiment_id+'_'+source_id+'_'+ripf+'_'+grid_label+'_'+str('{0:04d}'.format(ybeg))+str('{0:02d}'.format(mbeg))+str('{0:02d}'.format(dbeg))+'-'+str('{0:04d}'.format(yend))+str('{0:02d}'.format(mend))+str('{0:02d}'.format(dend))+'.nc')
        ofil_modified.append(ovars[o]+'_'+table+'_'+experiment_id+'_'+source_id+'_'+ripf+'_'+grid_label+'_'+str('{0:04d}'.format(ybeg))+str('{0:02d}'.format(mbeg))+str('{0:02d}'.format(dbeg))+'-'+str('{0:04d}'.format(yend))+str('{0:02d}'.format(mend))+str('{0:02d}'.format(dend))+'.nc')

      elif(table=='fx' or table=='Ofx'):
        ofil.append(ovars[o]+'_'+table+'_'+experiment_id+'_'+source_id+'_'+ripf+'_'+grid_label+'.nc')
        ofil_modified.append(ovars[o]+'_'+table+'_'+experiment_id+'_'+source_id+'_'+ripf+'_'+grid_label+'.nc')
        #ofil_modified.append(ofil)

      else:
        if(season=='MON'):
          ofil.append(ovars[o]+'_'+table+'_'+experiment_id+'_'+source_id+'_'+ripf+'_'+grid_label+'_'+str('{0:04d}'.format(ybeg_here))+str('{0:02d}'.format(mbeg))+'-'+str('{0:04d}'.format(yend))+str('{0:02d}'.format(mend))+'.nc')
        else:
          ofil.append(ovars[o]+'_'+table+'_'+experiment_id+'_'+source_id+'_'+ripf+'_'+grid_label+'_'+str('{0:04d}'.format(ybeg_here))+'-'+str('{0:04d}'.format(yend))+'.nc')
    
        if(season=='MON' or season=='None'):
          #ofil_modified.append(ofil)
          ofil_modified.append(ovars[o]+'_'+table+'_'+experiment_id+'_'+source_id+'_'+ripf+'_'+grid_label+'_'+str('{0:04d}'.format(ybeg_here))+str('{0:02d}'.format(mbeg))+'-'+str('{0:04d}'.format(yend))+str('{0:02d}'.format(mend))+'.nc')
        else:
          ofil_modified.append(ovars[o]+'_'+table+'_'+experiment_id+'_'+source_id+'_'+ripf+'_'+grid_label+'_'+str('{0:04d}'.format(ybeg_here))+'-'+str('{0:04d}'.format(yend))+'_'+season+'.nc')

    return ofil,ofil_modified

#def diag_iod(data,area_t,lat,lon):
def diag_iod(data,*argv):
  '''
  #5s-5n,170-120W
  Comput the IOD index from upper level (temporarly averaged in seasonal average case) SST.
  Parameters
  ----------
  data : data object usually SST(lat,lon)
  area_t : corresponding object of area weights
  lat : raw lats
  lon : raw lons

  Returns
  -------

  data : iod index (scalar or vector depending on inputs)
  '''

  import numpy as np
  area_t,lat,lon,fh_printfile=argv
  lon=np.add(lon,360.0)
  lon=np.where(lon<360.,lon,lon-360.)
  lon=np.roll(lon,80)
  lat=np.squeeze(lat)
  area_t=np.roll(area_t,80,axis=-1)
  data=np.roll(data,80,axis=-1)

  iodW_lat_min=np.abs(lat - -10.).argmin()
  iodW_lat_max=np.abs(lat - 10.).argmin()
  iodW_lon_min=np.abs(lon - 60.).argmin() #check
  iodW_lon_max=np.abs(lon - 180.).argmin() #check

  iodE_lat_min=np.abs(lat - -10.).argmin()
  iodE_lat_max=np.abs(lat - 0.).argmin()
  iodE_lon_min=np.abs(lon - 90.).argmin()
  iodE_lon_max=np.abs(lon - 110.).argmin()
  #print('data.shape=',data.shape,file=fh_printfile)
  #print('area_t.shape',area_t.shape,file=fh_printfile)
  #j=np.vstack((area_t,area_t))
  #j=np.resize(area_t,data.shape)
  s=data.shape
  #print('s=',s,file=fh_printfile)
  #print('iodW_lat_min=',iodW_lat_min,file=fh_printfile)
  #print('iodW_lat_max=',iodW_lat_max,file=fh_printfile)
  #print('iodW_lon_min=',iodW_lon_min,file=fh_printfile)
  #print('iodW_lon_max=',iodW_lon_max,file=fh_printfile)
  #print('',file=fh_printfile)
  #print('iodE_lat_min=',iodE_lat_min,file=fh_printfile)
  #print('iodE_lat_max=',iodE_lat_max,file=fh_printfile)
  #print('iodE_lon_min=',iodE_lon_min,file=fh_printfile)
  #print('iodE_lon_max=',iodE_lon_max,file=fh_printfile)
  #raise SystemExit('Forced exit.')

  if(len(s)==3):
    #has time dimension in it.
    newdata=np.zeros(s[0])
    #print('newdata.shape=',newdata.shape)
    #print('tmpdata.shape=',tmpdata.shape)
    for q in range(s[0]):
      tmpdata=data[q,]
      #print('tmpdata.shape=',tmpdata.shape)
      #print('q=',q)
      newdata[q]=xtra_iod(tmpdata,iodW_lat_min,iodW_lat_max,iodW_lon_min,iodW_lon_max,iodE_lat_min,iodE_lat_max,iodE_lon_min,iodE_lon_max,area_t)
    data=newdata 
      #print('newdata=',newdata)
  else:
    data=xtra_iod(data,iodW_lat_min,iodW_lat_max,iodW_lon_min,iodW_lon_max,iodE_lat_min,iodE_lat_max,iodE_lon_min,iodE_lon_max,area_t)
    #print('xxdata=',data)
  return data

def xtra_iod(data,iodW_lat_min,iodW_lat_max,iodW_lon_min,iodW_lon_max,iodE_lat_min,iodE_lat_max,iodE_lon_min,iodE_lon_max,area_t):
  '''
  As diag_iod needs to cope with arrays with and without a time dimension, it is more compact to define a function that can work in both cases.
  '''
  import numpy as np
  data=np.sum(np.sum(data[iodW_lat_min:iodW_lat_max,iodW_lon_min:iodW_lon_max]*area_t[iodW_lat_min:iodW_lat_max,iodW_lon_min:iodW_lon_max],axis=0),axis=0) / np.sum(np.sum(area_t[iodW_lat_min:iodW_lat_max,iodW_lon_min:iodW_lon_max],axis=0),axis=0) - np.sum(np.sum(data[iodE_lat_min:iodE_lat_max,iodE_lon_min:iodE_lon_max]*area_t[iodE_lat_min:iodE_lat_max,iodE_lon_min:iodE_lon_max],axis=0),axis=0) / np.sum(np.sum(area_t[iodE_lat_min:iodE_lat_max,iodE_lon_min:iodE_lon_max],axis=0),axis=0)
  return data

def ocean_vertical_interpolate(data,nlats,nlons,zt,zb,z0,lev_top_bot):
  '''
  see raijin:~mac599/decadal/ocean_vertical_interpolate.py (test/development script).
  need to think about when mising values b/c part of weighting. For example, could try
  to enforce same total quantity content by rescaling profile.
  '''
  import numpy as np
  import numpy.ma as ma
  import inspect

  MissVal=1e20

  #print(lev_top_bot)
  lev_top_bot=np.squeeze(lev_top_bot)
  #print(lev_top_bot)
  #raise SystemExit('Forced exit.')

  data=ma.masked_equal(data,-1e20)
  data.set_fill_value(MissVal)

  ilat,jlat=199,300 #at this point the data has only valid values in top 5 levels here.
  #print(data[:,:,ilat,jlat]) #199,300:top 5 levels only.
  mask=ma.getmaskarray(data[0,]) #only need surface
  #print(mask)

  dz=zb-z0
  nzt=zt.size

  #dz3d=data*dz

  dz3d=np.expand_dims(np.expand_dims(np.expand_dims(dz[:],0),2),3)
  #print(dz3d.shape)
  dz3d=np.tile( dz3d,(1,1,nlats,nlons)) * data/data

  #print(dz3d.shape)

  #print(dz3d[:,:,ilat,jlat])

  diag=True
  diag=False

  total_thickness=0.0
  interpolated_data=np.zeros((1,nlats,nlons),dtype=float)

  total_thickness2d=np.zeros((1,nlats,nlons),dtype=float)
  #total_thickness_lower2d=np.zeros((1,nlats,nlons),dtype=float)
  #total_thickness_upper2d=np.zeros((1,nlats,nlons),dtype=float)

  if(diag):
    print('zt: mid level depth value.')
    print('z0: top level depth value.')
    print('zb: bottom level depth value.')
    print('dz: level thickness .')
    print('data: data value at depth zt.')

    #print("     zt    z0    zb    dz  data")
    #print("     zt    z0    zb    dz")
    #for zzz in range(0,nzt):
      #print("%5.2f"% zt[zzz], "%5.2f"% z0[zzz], "%5.2f"% zb[zzz], "%5.2f"% dz[zzz], "%5.2f"% data[zzz])
      #print("%2.0f"% zzz, "%5.2f"% zt[zzz], "%5.2f"% z0[zzz], "%5.2f"% zb[zzz], "%5.2f"% dz[zzz])

  lev_midway=np.average(lev_top_bot)

  #print('lev_top_bot,lev_midway=',lev_top_bot,',',lev_midway)
  #lev_top_bot=np.array([0.,6000.]) #temporary for testing

  #print('lev_top_bot[0]=',lev_top_bot[0,])

  if(lev_top_bot[0]<z0[0]):
    raise SystemExit('Bad upper value.')

  if(lev_top_bot[1]>zb[-1]):
    raise SystemExit('Bad lower value.')

  Upper=True #means shallower part of ocean.
  Lower=True #means deeper part of ocean.
  Between=False #if between 2 levels and use level value.

  for lll in range(0,nzt):
    #print(z0[lll],zb[lll])
    if(lev_top_bot[0]>=z0[lll] and lev_top_bot[1]<=zb[lll]):
      #print('Requested vertical slab between existing levels, data will simply take value at zt[lll].')
      Upper=False
      Lower=False
      Between=True
      upper=lll
      lower=lll
      break
  #if(Upper and Lower): print('Requested vertical slab not between any existing levels.')

  if(Upper):
    upper=0
    for lll in range(0,nzt):
      if(z0[lll]==lev_top_bot[0]):
        #print('no upper partial cell contribution')
        Upper=False
        upper=lll
        break
      elif(zt[lll]>lev_top_bot[0]):
        upper=lll
        #print('a upper',upper,zt[upper])
        break

  if(Lower):
    lower=0
    for lll in range(0,nzt):
      if(zb[lll]>lev_top_bot[1]):
        lower=lll
        #print('a lower',lower,zb[lower])
        break
      elif(zb[lll]==lev_top_bot[1]):
        #print('no lower partial cell contribution')
        Lower=False
        #lower=lll+1
        lower=lll #made this change to cope with full depth integration...
        break

  if(diag):
    print('Levels for which full input data is used (based 0)=',upper,' to ',lower,' out of ',nzt-1,' (base 0) levels.')
    #if(Upper):
    #  print('Contributions from upper partial level (base 0)=',upper-1)

    #if(Lower):
    #  print('Contributions from lower partial level (base 0)=',lower)

  if(Upper):
    #print('Contributions from upper partial level ',upper-1,'.')
    #print('b upper',data[upper],dz[upper],zb[upper],lev_top_bot[0])

    total_thickness_upper=z0[upper]-lev_top_bot[0]
    total_thickness_upper2d=data[0,upper-1,:,:]/data[0,upper-1,:,:]*total_thickness_upper
    total_thickness_upper2d=ma.masked_equal( np.expand_dims(total_thickness_upper2d,0), MissVal)
    total_thickness2d[0,:,:]=total_thickness2d[0,:,:]+total_thickness_upper2d[0,:,:].filled(0.)
    #print('total_thickness_upper=',total_thickness_upper)

    #total_thickness=total_thickness+total_thickness_upper
    interpolated_data=interpolated_data+data[:,upper,:,:]*total_thickness_upper

    #print('total_thickness_upper=',total_thickness_upper,'data=',data[0,upper,ilat,jlat])

  #print('Contributions from middle levels.')
  #for mmm in range(upper,lower+1):
  for mmm in range(upper,lower+0):
    #print('mmm',mmm)
    #print('mmm=',mmm,'data=',data[0,mmm,ilat,jlat])
    #interpolated_data=interpolated_data+data[:,mmm,:,:]*dz[mmm]
    interpolated_data=interpolated_data+data[:,mmm,:,:].filled(0.)*dz3d[0,mmm,:,:].filled(0.)

    total_thickness=total_thickness+dz[mmm]
    total_thickness2d[0,:,:]=total_thickness2d[0,:,:] + dz3d[0,mmm,:,:] #.filled(0.)

  if(Lower):
    #print('Contributions from lower partial level ',lower,'.')
    #print('b lower',data[lower],dz[lower],zb[lower-1],lev_top_bot[1])

    total_thickness_lower=lev_top_bot[1]-z0[lower]
    total_thickness_lower2d=data[0,lower,:,:]/data[0,lower,:,:]*total_thickness_lower
    total_thickness_lower2d=ma.masked_equal( np.expand_dims(total_thickness_lower2d,0), MissVal)
    total_thickness2d[0,:,:]=total_thickness2d[0,:,:]+total_thickness_lower2d[0,:,:].filled(0.)

    #total_thickness_lower2d=total_thickness_lower * data[0,lower,:,:]/data[0,lower,:,:]
    #np.set_printoptions(threshold='nan') #will print out whole array
    #print(total_thickness_lower2d.shape)
    #print(total_thickness_lower2d[:,:,:])
    #raise SystemExit('Forced exit.')
    #print('total_thickness_lower=',total_thickness_lower,'data=',data[0,lower,ilat,jlat])
    #total_thickness=total_thickness+total_thickness_lower #temp del
    #interpolated_data=interpolated_data+data[:,lower,:,:]*total_thickness_lower #temp del
    #interpolated_data=interpolated_data+data[:,lower,:,:].filled(0.)*total_thickness_lower2d[0,lower,:,:]
  #print('total_thickness2d=',total_thickness2d[0,ilat,jlat])
  #print('interpolated_data=',interpolated_data[:,ilat,jlat])
  #raise SystemExit('Forced exit.')
  #interpolated_data=(interpolated_data/total_thickness)*data[:,0,:,:]/data[:,0,:,:]
  #interpolated_data=(interpolated_data/total_thickness)
  #interpolated_data=ma.masked_equal(interpolated_data/total_thickness2d, NaN)
  #interpolated_data=ma.masked_equal( np.where(total_thickness2d>0,interpolated_data/total_thickness2d,-1e20), -1e20)

  #if(not Upper and not Lower):
  if(Between):
    interpolated_data=data[:,lower,:,:]
  else:
    interpolated_data=np.where(total_thickness2d>0,interpolated_data/total_thickness2d,MissVal)

  #interpolated_data.set_fill_value(MissVal)
  #print(interpolated_data)
  #print(interpolated_data.filled())
  #print(interpolated_data.fill_value)
  #print(data.type)
  #print(interpolated_data.type)
  #print(interpolated_data.shape)
  #print('total_thickness=',total_thickness)
  #print('interpolated_data=',interpolated_data[:,ilat,jlat])
  #print(interpolated_data)
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  return(interpolated_data)
  #return(interpolated_data.filled())

def atmos_vertical_interpolate(data,zt,newlevs,ps,type):
  '''
  '''
  import numpy as np

  #consider extrapolation down (beyond lowest model pressure level) and up (above highest model pressure level).

  #put this vertical interpolation stuff in a function later...
  #print('zt=',zt[:])
  #print('newlevs=',newlevs[:])

  ps_shape=ps.shape

  #print('aaa ps.shape=',ps.shape)
  #print('aaa data.shape=',data.shape)

  #var_dims=f.variables[dvar].dimensions
  #var_size=f.variables[dvar].shape

  #nlat=90 #later get from input automatically.
  #nlon=144 #later get from input automatically.
  nlat=ps_shape[len(ps_shape)-2]
  nlon=ps_shape[len(ps_shape)-1]
  #print(nlat,nlon)
  #raise SystemExit('Forced exit.')

  nzt=len(zt)
  nnewlevs=len(newlevs)

  interpolated_data=np.zeros((1,nnewlevs,nlat,nlon),dtype=float)

  index_hi=np.zeros(nnewlevs,dtype=int)
  index_lo=np.zeros(nnewlevs,dtype=int)

  for lll in range(0,nnewlevs):
    found=False
    #print(lll,newlevs[lll])
    for mmm in range(0,nzt):
      #print(mmm,zt[mmm])
      if(zt[mmm]>newlevs[lll]):
        #index_hi[lll]=zt[mmm]
        #index_lo[lll]=zt[mmm-1]
        index_lo[lll]=mmm
        index_hi[lll]=mmm-1
        found=True
        break
    #print(found,newlevs[lll],index_hi[lll],index_lo[lll])
    if not found:
      #extrapolation, does the following work?
      #index_hi[lll]=zt[23]
      #index_lo[lll]=zt[22]
      index_lo[lll]=nzt-2
      index_hi[lll]=nzt-1

  print('index_hi,index_lo=',index_hi,index_lo)
  #raise SystemExit('Forced exit.')

  if(type=='linear'):
    #print('linear interpolation chosen.')
    for lll in range(0,nnewlevs):
      #print('level=',lll,' value=',newlevs[lll],' hi=',zt[index_hi[lll]],' lo=',zt[index_lo[lll]])
      dx = zt[index_hi[lll]] - zt[index_lo[lll]]
      dy = data[0,index_hi[lll],:,:] - data[0,index_lo[lll],:,:]
      dp = newlevs[lll] - zt[index_lo[lll]]
      interpolated_data[0,lll,:,:] = data[0,index_lo[lll],:,:] + dp * dy/dx
      #interpolated_data[0,lll,:,:] = data[0,index_lo[lll],:,:]

      #lon=np.where(lon<360.,lon,lon-360.)
      interpolated_data[0,lll,:,:]=np.where(newlevs[lll]<ps,interpolated_data[0,lll,:,:],1e20)
      #print('j.shape=',j.shape)
      #print(j)
      #raise SystemExit('Forced exit.')

      #print('dx.shape=',dx.shape)
      #print('dy.shape=',dy.shape)
      #print('dp.shape=',dp.shape)
      #print('interpolated_data.shape=',interpolated_data.shape)
  elif(type=='log_linear'):
    #print('log_linear interpolation chosen (not ready).')
    #raise SystemExit('Forced exit.')
    for lll in range(0,nnewlevs):
      #print('level=',lll)
      dx = np.log(zt[index_hi[lll]]) - np.log(zt[index_lo[lll]])
      dy = data[0,index_hi[lll],:,:] - data[0,index_lo[lll],:,:]
      dp = np.log(newlevs[lll]) - np.log(zt[index_lo[lll]])
      interpolated_data[0,lll,:,:] = data[0,index_lo[lll],:,:] + dp * dy/dx
      interpolated_data[0,lll,:,:]=np.where(newlevs[lll]<ps,interpolated_data[0,lll,:,:],1e20)
  elif(type=='log_log'):
    #print('log_log interpolation chosen (not ready).')
    #raise SystemExit('Forced exit.')
    for lll in range(0,nnewlevs):
      #print('level=',lll)
      dx = np.log(zt[index_hi[lll]]) - np.log(zt[index_lo[lll]])
      dy = np.log(data[0,index_hi[lll],:,:]) - np.log(data[0,index_lo[lll],:,:])
      dp = np.log(newlevs[lll]) - np.log(zt[index_lo[lll]])
      interpolated_data[0,lll,:,:] = np.exp( np.log(data[0,index_lo[lll],:,:]) + dp * dy/dx )
      interpolated_data[0,lll,:,:]=np.where(newlevs[lll]<ps,interpolated_data[0,lll,:,:],1e20)
  elif(type=='pressure_cubed'):
    #print('pressure_cubed  interpolation chosen (not ready).')
    #raise SystemExit('Forced exit.')
    for lll in range(0,nnewlevs):
      #print('level=',lll)
      dx = np.power(zt[index_hi[lll]],3.) - np.power(zt[index_lo[lll]],3.)
      dy = data[0,index_hi[lll],:,:] - data[0,index_lo[lll],:,:]
      dp = np.power(newlevs[lll],3.) - np.power(zt[index_lo[lll]],3.)
      interpolated_data[0,lll,:,:] = data[0,index_lo[lll],:,:] + dp * dy/dx
      interpolated_data[0,lll,:,:]=np.where(newlevs[lll]<ps,interpolated_data[0,lll,:,:],1e20)
  else:
    raise SystemExit('Other interpolation types not implemented yet.')
  return interpolated_data

def calc_iso_surface(my_array, my_value, zs, interp_order=6, power_parameter=0.5):
#http://stackoverflow.com/questions/13627104/using-numpy-scipy-to-calculate-iso-surface-from-3d-array
    if interp_order < 1: interp_order = 1
    from numpy import argsort, take, clip, zeros
    dist = (my_array - my_value)**2
    arg = argsort(dist,axis=2)
    dist.sort(axis=2)
    w_total = 0.
    z = zeros(my_array.shape[:2], dtype=float)
    for i in xrange(int(interp_order)):
        zi = take(zs, arg[:,:,i])
        valuei = dist[:,:,i]
        wi = 1/valuei
        clip(wi, 0, 1.e6, out=wi) # avoiding overflows
        w_total += wi**power_parameter
        z += zi*wi**power_parameter
    z /= w_total
    return z

def calc_isoN(data, value, levs, lmax, ymin, ymax, diag):
  '''
   calc_isoN
   inputs:

   data(depth,lat,lon): note only 1 time is processed each
     call and therefore dimension is stripped away prior to
     calling this routine.
   value: critical value of isosurface (e.g. 20degC)
   levs: depth levels (vector)
   lmax: truncate number of levels to search (minimum of lmax, size(levs))
   ymin: start processing at this latitude index (starting 0)
   ymax: finish processing at this latitude index
   diag: turn on/off diagnostics

   output:

   data(lat,lon), units are in units of depth.

   wrote this as found the one off web  (calc_iso_surface) was
   not working for our data with missing values.
   quite inefficient, could speed up by creating 2d array of
   above and below, and performing depth interpolation as array
   rather than individually.

   only 4 profiles (and of course missing data over land).
   could be critical value at surface (or at any exact level) too.

   if want to speed up comment # out if(diag) statements...

                       less    <T>    more
-----------------------------------------------------------------------
            -       -                  -                         -
           -        -                   -                        -
 ^         -         -                    -                      -
 z       -           -                     -                     -
 v      -             -                      -                   -
       -              -                       -                  -
      -               -                        -                 -
     -                -                         -                -
-------|-----------------|-----------------|------------------|--------
       20                20                20                 20

iso    defined           not-defined       defined            not-defined
  '''
  import numpy as np
  import numpy.ma as ma
  import inspect

  nlev=data.shape[0]
  nlat=data.shape[1]
  nlon=data.shape[2]

  #if(diag):
  #print('data.shape=',data.shape)
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  #  print('value=',value)
  #  print('levs=',levs)
  #  print('nlev,nlat,nlon=',nlev,nlat,nlon)

  newdata=np.zeros((nlat,nlon))

  #labove=np.zeros((nlat,nlon))
  #lbelow=np.zeros((nlat,nlon))
  #dabove=np.zeros((nlat,nlon))
  #dbelow=np.zeros((nlat,nlon))

  if(ymin<0): raise SystemExit('ymin<0.')
  if(ymax>nlat): raise SystemExit('ymax>nlat.')

  xabove=np.zeros((nlat,nlon),dtype=int)
  xbelow=np.zeros((nlat,nlon),dtype=int)

  newdata=newdata+1e20 #assign default value, missing.

  nlev_now=min(nlev,lmax)

  ymin=max(0,ymin)
  ymax=min(nlat,ymax)

  #print(ymin,ymax)
  #raise SystemExit('Forced exit.')

  #xspot=50
  #yspot=50

  #xspot=0
  #yspot=0

  #fillvalue=data.get_fill_value()
  #print('fillvalue=',fillvalue)
  #print('data=',data[0,yspot,xspot].mask)
  #if(data[0,yspot,xspot]==fillvalue):
  #if(mask[0,yspot,xspot]):
  #  print('hello')
  #else:
  #  print('there')
  #j=np.equal(data[0,yspot,xspot], fillvalue)
  #print(j)
  #if(data[0,yspot,xspot]==nan):
  #raise SystemExit('Forced exit.')

  #mask=ma.getmask(data)
  mask=ma.getmaskarray(data[0,]) #only need surface
  #print('mask.shape=',mask.shape)

  mask2=ma.zeros(mask.shape,dtype=float)
  mask2.mask=True
  #print('mask2=',mask2)
  #raise SystemExit('Forced exit.')

  #if(diag): ifound1=ifound2=ifound3=ifound4=ifound5=0

  for y in range(ymin,ymax):
    for x in range(0,nlon):
      #if(diag): found1=found2=found3=found4=found5=False #if not found, then assign point missing as either temperature always greater or less than critical value.

      #if(not (found1 and found2)):
      #  raise SystemExit('XXXced exit.')
      #raise SystemExit('abc')

      #print('mask,y,x=',mask[0,y,x],y,x)
      if(not mask[y,x]): #skip over points where missing (land) at surface.
        mask2[y,x]=False #these False (ocean) points will be used in final calculation.
        #print(data[0,y,x])
        #raise SystemExit('Forced exit.')
        if(data[0,y,x]==value): #if surface equals critical, then assign and start on new y,x
          #if(diag):
          #  found1=True
          #  ifound1+=1
          mask2[y,x]=True
          #print('1 yes')
          #print(data[:,y,x])
          newdata[y,x]=levs[0]
          #raise SystemExit('Forced exit.')
        else:
          #print(data[:,y,x])
          #print(data[0,y,x])
          for l in range(1,nlev_now):
            #print('l=',l)
            if(data[l,y,x]<value and data[l-1,y,x]>value):
              #if(diag):
              #  found2=True
              #  ifound2+=1
              #print('5 yes')
              #warm at top, cooler at depth
              #print(data[:,y,x])
              xabove[y,x]=l-1
              xbelow[y,x]=l
              #labove[y,x]=levs[l-1]
              #lbelow[y,x]=levs[l]
              #dabove[y,x]=data[l-1,y,x]
              #dbelow[y,x]=data[l,y,x]
              #print('labove,lbelow,dabove,dbelow=',labove[y,x],lbelow[y,x],dabove[y,x],dbelow[y,x])
              #newdata[y,x] = (dabove[y,x] - value) / (dabove[y,x] - dbelow[y,x]) * (lbelow[y,x] - labove[y,x]) + labove[y,x]
              #print(newdata[y,x])
              #raise SystemExit('Forced exit.')
              break #found a case, get out of depth scan, star on new y,x
            elif(data[l,y,x]==value):
              #if(diag):
              #  found3=True
              #  ifound3+=1
              mask2[y,x]=True
              #found a level with exact critical value
              #print('2 yes')
              #print(data[:,y,x])
              newdata[y,x] = levs[l]
              #print(newdata[y,x])
              #raise SystemExit('Forced exit.')
              break #found a case, get out of depth scan, start on new y,x
            elif(data[l,y,x]>value and data[l-1,y,x]<value):
              #if(diag):
              #  found4=True
              #  ifound4+=1
              #print('4 yes')
              #cool at top, warmer at depth
              #print(data[:,y,x])
              xabove[y,x]=l-1
              xbelow[y,x]=l
              #labove[y,x]=levs[l-1]
              #lbelow[y,x]=levs[l]
              #dabove[y,x]=data[l-1,y,x]
              #dbelow[y,x]=data[l,y,x]
              #print('labove,lbelow,dabove,dbelow=',labove[y,x],lbelow[y,x],dabove[y,x],dbelow[y,x])
              #newdata[y,x] = (dabove[y,x] - value) / (dabove[y,x] - dbelow[y,x]) * (lbelow[y,x] - labove[y,x]) + labove[y,x]
              #print(newdata[y,x])
              #raise SystemExit('Forced exit.')
              break #found a case, get out of depth scan, start on new y,x
            elif(data[l-1,y,x]==value):
              #if(diag):
              #  found5=True
              #  ifound5+=1
              mask2[y,x]=True
              #found a level with exact critical value (note this block should not be executed as caught above when looking at surface value).
              #print('3 yes')
              newdata[y,x] = levs[l-1]
              #print(newdata[y,x])
              #raise SystemExit('Forced exit.')
              break #found a case, get out of depth scan, start on new y,x
          #raise SystemExit('Forced exit.')
      #if(diag): print('found1,2,3,4,5,y,x=',found1,found2,found3,found4,found5,y,x)
      #if(not (found1 and found2 and found3 and found4 and found5)):
        #newdata[y,x]=1e20
        #raise SystemExit('Forced exit.')
  #print('mask2=',mask2)
  for y in range(ymin,ymax):
    for x in range(0,nlon):
      #print('x,y=',x,y)
      if(not mask2[y,x]): #skip over points where missing (combination of land and values alread set) at surface.
        newdata[y,x] = (data[xabove[y,x],y,x] - value) / (data[xabove[y,x],y,x] - data[xbelow[y,x],y,x]) * (levs[xbelow[y,x]] - levs[xabove[y,x]]) + levs[xabove[y,x]]
  #if(diag): print('ifound1,2,3,4,5=',ifound1,ifound2,ifound3,ifound4,ifound5)
  newdata=np.where(np.isnan(newdata),1e20,newdata) #for model output need this.
  return newdata

def grab_var_meta(dvar,frequency):
  '''
  documentation
  '''
  #defaults:
  area_t=False
  area_u=False
  #frequency='month'
  grid_label='gn'
  grid='native grid'
  varStructure='time_lat_lon'
  if not 'vertical_interpolation_method' in locals(): vertical_interpolation_method='log_linear'

  if(dvar=='thetao'):
    #diag=True
    realm='ocean'
    diag_dims=['time','st_ocean','yt_ocean','xt_ocean']
    #inputs=dvar
    table='Omon'
    inputs=['temp']
    units='degC'
    ovars=[dvar]
    varStructure='time_depth_lat_lon'

  elif(dvar=='thetao100m'):
    #not sure if I need this, as could have just specified levels=0...10 and it would do the rest, as olevel is arbitrary. Would need to specify a different grid/grid_label
    #diag=True
    realm='ocean'
    diag_dims=['time','st_ocean','yt_ocean','xt_ocean']
    #inputs=dvar
    table='Omon'
    inputs=['temp']
    units='degC'
    ovars=[dvar]
    grid_label='gn100m'
    grid='Upper 100m of ocean only'
    varStructure='time_depth_lat_lon'

  elif(dvar=='so100m'):
    #diag=True
    realm='ocean'
    diag_dims=['time','st_ocean','yt_ocean','xt_ocean']
    #inputs=dvar
    table='Omon'
    inputs=['temp']
    units='0.001'
    ovars=[dvar]
    grid_label='gn100m'
    grid='Upper 100m of ocean only'
    varStructure='time_depth_lat_lon'

  elif(dvar=='uo'):
    #diag=True
    realm='ocean'
    diag_dims=['time','st_ocean','yt_ocean','xt_ocean']
    #inputs=dvar
    table='Omon'
    inputs=['u']
    units='m s-1'
    ovars=[dvar]
    #grid_label='gn100m'
    #grid='Upper 100m of ocean only'
    varStructure='time_depth_lat_lon'

  elif(dvar=='uo100m'):
    #diag=True
    realm='ocean'
    diag_dims=['time','st_ocean','yt_ocean','xt_ocean']
    #inputs=dvar
    table='Omon'
    inputs=['u']
    units='m s-1'
    ovars=[dvar]
    grid_label='gn100m'
    grid='Upper 100m of ocean only'
    varStructure='time_depth_lat_lon'

  elif(dvar=='vo'):
    #diag=True
    realm='ocean'
    diag_dims=['time','st_ocean','yt_ocean','xt_ocean']
    #inputs=dvar
    table='Omon'
    inputs=['v']
    units='m s-1'
    ovars=[dvar]
    grid_label='gn100m'
    grid='Upper 100m of ocean only'
    varStructure='time_depth_lat_lon'

  elif(dvar=='vo100m'):
    #diag=True
    realm='ocean'
    diag_dims=['time','st_ocean','yt_ocean','xt_ocean']
    #inputs=dvar
    table='Omon'
    inputs=['v']
    units='m s-1'
    ovars=[dvar]
    grid_label='gn100m'
    grid='Upper 100m of ocean only'
    varStructure='time_depth_lat_lon'

  elif(dvar=='eta_t' or dvar=='tx_trans_int_z'):
    #diag=True
    realm='ocean'
    inputs=dvar
    table='Omon'
    ovars=[dvar]
  
  elif(dvar=='pr'):
    #diag=False
    area_t=False
    inputs=['precip']
    realm='atmos'
    diag_dims=['time','lat','lon']
    units='kg m-2 s-1'
    if(frequency == 'month'): table='Amon'
    else: table='day'
    ovars=[dvar]
    varStructure='time_lat_lon'

  elif(dvar=='tas'):
    #diag=False
    area_t=False
    inputs=['t_ref']
    realm='atmos'
    diag_dims=['time','lat','lon']
    units='K'
    if(frequency == 'month'): table='Amon'
    else: table='day'
    ovars=[dvar]
    varStructure='time_lat_lon'

  elif(dvar=='hfls'):
    #diag=False
    area_t=False
    inputs=['evap']
    realm='atmos'
    diag_dims=['time','lat','lon']
    units='W m-2'
    if(frequency == 'month'): table='Amon'
    else: table='day'
    ovars=[dvar]
    varStructure='time_lat_lon'

  elif(dvar=='uas'):
    #diag=False
    area_t=False
    inputs=['uas']
    realm='atmos'
    diag_dims=['time','lat','lon']
    units='m s-1'
    if(frequency == 'month'): table='Amon'
    else: table='day'
    ovars=[dvar]
    varStructure='time_lat_lon'

  elif(dvar=='vas'):
    #diag=False
    area_t=False
    inputs=['vas']
    realm='atmos'
    diag_dims=['time','lat','lon']
    units='m s-1'
    if(frequency == 'month'): table='Amon'
    else: table='day'
    ovars=[dvar]
    varStructure='time_lat_lon'

  elif(dvar=='hfss'):
    #diag=False
    area_t=False
    inputs=['shflx']
    realm='atmos'
    diag_dims=['time','lat','lon']
    units='W m-2'
    if(frequency == 'month'): table='Amon'
    else: table='day'
    ovars=[dvar]
    varStructure='time_lat_lon'

  elif(dvar=='huss'):
    #diag=False
    area_t=False
    inputs=['q_ref']
    realm='atmos'
    diag_dims=['time','lat','lon']
    units='1.0'
    if(frequency == 'month'): table='Amon'
    else: table='day'
    ovars=[dvar]
    varStructure='time_lat_lon'
  
  elif(dvar=='rlut'):
    #diag=False
    area_t=False
    inputs=['olr']
    realm='atmos'
    diag_dims=['time','lat','lon']
    units='W m-2'
    if(frequency == 'month'): table='Amon'
    else: table='day'
    ovars=[dvar]
    varStructure='time_lat_lon'

  elif(dvar=='sfcWind'):
    #diag=False
    area_t=False
    inputs=['wind']
    realm='atmos'
    diag_dims=['time','lat','lon']
    units='m s-1'
    if(frequency == 'month'): table='Amon'
    else: table='day'
    ovars=[dvar]
    varStructure='time_lat_lon'

  elif(dvar=='tslsi'):
    #diag=False
    area_t=False
    inputs=['t_ref']
    realm='atmos'
    diag_dims=['time','lat','lon']
    units='K'
    if(frequency == 'month'): table='Amon'
    else: table='day'
    ovars=[dvar]
    varStructure='time_lat_lon'
  
  elif(dvar=='o2'):
    #diag=False
    realm='ocean_bgc'
    ovars=[dvar]
  
  elif(dvar=='acc_drake' or dvar=='acc_africa'):
    #diag=True
    inputs=['tx_trans_int_z']
    realm='ocean'
    diag_dims=['time']
    dvar='tx_trans_int_z'
    levels=0
    ovars=[dvar]
  
  elif(dvar=='mozmbq'):
    #diag=True
    inputs=['ty_trans_int_z']
    realm='ocean'
    diag_dims=['time']
    ovars=[dvar]
  
  elif(dvar=='aabw'):
    #diag=True
    inputs=['ty_trans','ty_trans_gm']
    realm='ocean'
    diag_dims=['time']
    ovars=[dvar]
  
  elif(dvar=='nadw'):
    #diag=True
    inputs=['ty_trans','ty_trans_gm']
    realm='ocean'
    diag_dims=['time']
    ovars=[dvar]
  
  elif(dvar=='pp'):
    #diag=True
    area_t=True
    inputs=['pprod_gross']
    realm='ocean_bgc'
    diag_dims=['time']
    units='Pg(C)/yr'
    table='Omon'
    ovars=[dvar]
    #frequency='month'
  
  elif(dvar=='nflux'):
    #diag=True
    area_t=True
    inputs=['stf07']
    realm='ocean_bgc'
    diag_dims=['time']
    units='Pg(C)/yr'
    table='Omon'
    ovars=[dvar]
    #frequency='month'
  
  elif(dvar=='ep'):
    #diag=True
    area_t=True
    inputs=['det']
    realm='ocean_bgc'
    diag_dims=['time']
    units='Pg(C)/yr'
    table='Omon'
    ovars=[dvar]
    #frequency='month'
  
  elif(dvar=='ssh'):
    #diag=True
    area_t=True
    inputs=['temp','salt']
    realm='ocean'
    diag_dims=['time','yt_ocean','xt_ocean']
    dvar='ssh'
    ovars=[dvar]
    varStructure='time_lat_lon'
  
  elif(dvar=='moc' or dvar=='moc_atlantic' or dvar=='moc_pacific' or dvar=='moc_indian'):
    #diag=True
    #inputs=['v']
    inputs=['tx_trans','tx_trans_gm']
    realm='ocean'
    #diag_dims=['time','st_ocean','yu_ocean']
    diag_dims=['time','st_ocean','yt_ocean']
    area_t=True
    area_u=True
    dvar='tx_trans'
    ovars=[dvar]
  
  elif(dvar=='shice_cover' or dvar=='nhice_cover'):
    #diag=True
    inputs=['CN']
    realm='ice'
    diag_dims=['time']
    area_t=True
    dvar='CN'
    ovars=[dvar]
  
  elif(dvar=='nhbi'):
    #diag=True
    inputs=['h500']
    realm='atmos'
    diag_dims=['time','lon']
    area_t=True
    #dvar='h500'
    levels=0
    nlev=0
    table='Amon'
    units='1.0'
    ovars=[dvar,'GHGS','GHGN']
  
  elif(dvar=='rws'):
    #diag=True
    inputs=['ucomp','vcomp']
    realm='atmos'
    diag_dims=['time','pfull','lat','lon']
    #area_t=True
    #dvar='ucomp'
    units='s-2'
    table='Amon'
    #levels=8,9
    #nlev=2
    ovars=[dvar]
    varStructure='time_height_lat_lon'
  
  elif(dvar=='tos'):
    varStructure='lat_lon'
    #diag=True
    area_t=True
    inputs=['temp']
    realm='ocean'
    diag_dims=['time','yt_ocean','xt_ocean']
    units='degC'
    if(frequency == 'month'): table='Omon'
    else: table='Oday'
    ovars=[dvar]
    varStructure='time_lat_lon'
  
  elif(dvar=='sos'):
    #diag=True
    area_t=True
    inputs=['salt']
    realm='ocean'
    diag_dims=['time','yt_ocean','xt_ocean']
    units='psu'
    units='0.001'
    table='Omon'
    ovars=[dvar]
    varStructure='time_lat_lon'
  
  elif(dvar=='zg500'):
    #diag=True
    area_t=False
    inputs=['h500']
    realm='atmos'
    diag_dims=['time','lat','lon']
    units='m'
    if(frequency == 'month'): table='Amon'
    else: table='day'
    ovars=[dvar]
    varStructure='time_lat_lon'

  elif(dvar=='zg5'):
    #diag=True
    area_t=False
    inputs=['hght','ps']
    realm='atmos'
    diag_dims=['time','phalf','lat','lon']
    units='m'
    if(frequency == 'month'): table='Amon'
    else: table='day'
    ovars=[dvar]
    varStructure='time_height_lat_lon'
    if not 'vertical_interpolation_method' in locals(): vertical_interpolation_method='log_linear'

  elif(dvar=='zg700'):
    #diag=True
    area_t=False
    inputs=['h500','ps']
    realm='atmos'
    diag_dims=['time','lat','lon']
    units='m'
    if(frequency == 'month'): table='Amon'
    else: table='day'
    ovars=[dvar]
    varStructure='time_height_lat_lon'
    if not 'vertical_interpolation_method' in locals(): vertical_interpolation_method='log_linear'
  
  elif(dvar=='ps'):
    #diag=True
    area_t=False
    inputs=['ps']
    realm='atmos'
    diag_dims=['time','lat','lon']
    units='Pa'
    table='Amon'
    ovars=[dvar]
    varStructure='time_lat_lon'
  
  elif(dvar=='psl'):
    #diag=True
    area_t=False
    inputs=['slp']
    realm='atmos'
    diag_dims=['time','lat','lon']
    units='Pa'
    if(frequency == 'month'): table='Amon'
    else: table='day'
    ovars=[dvar]
    varStructure='time_lat_lon'
  
  elif(dvar=='zg'):
    #diag=True
    area_t=False
    inputs=['hght']
    realm='atmos'
    diag_dims=['time','phalf','lat','lon']
    units='m'
    if(frequency == 'month'): table='Amon'
    else: table='day'
    ovars=[dvar]
    varStructure='time_height_lat_lon'
  
  elif(dvar=='temptotal'):
    #diag=True
    area_t=False
    inputs=['temp_total']
    realm='ocean'
    #frequency='scalar'
    diag_dims=['time']
    units='Joule/1e25'
    table='Omon'
    ovars=[dvar]
    varStructure='time'
  
  elif(dvar=='salttotal'):
    #diag=True
    area_t=False
    inputs=['salt_total']
    realm='ocean'
    #frequency='scalar'
    diag_dims=['time']
    units='kg/1e18'
    table='Omon'
    ovars=[dvar]
    varStructure='time'
  
  elif(dvar=='nino34'):
    #diag=True
    area_t=True
    inputs=['temp']
    realm='ocean'
    diag_dims=['time']
    units='degC'
    if(frequency == 'month'): table='Omon'
    else: table='Oday'
    ovars=[dvar]
    levels=0
    nlev=0
    varStructure='time'
  
  elif(dvar=='iod'):
    #diag=True
    area_t=True
    inputs=['temp']
    realm='ocean'
    diag_dims=['time']
    units='degC'
    table='Omon'
    ovars=[dvar]
    #frequency='month'
    levels=0
    nlev=0
    #print('len(ovars)=',len(ovars),file=fh_printfile)
    #raise SystemExit('Forced exit.')
    varStructure='time'
  
  elif(dvar=='ua' or dvar=='ua5' or dvar=='ua10' or dvar=='ua17'):
    #diag=True
    area_t=False
    if(dvar=='ua'):
      inputs=['ucomp']
    else:
      inputs=['ucomp','ps']
    realm='atmos'
    diag_dims=['time','pfull','lat','lon']
    units='m/sec'
    if(frequency == 'month'): table='Amon'
    else: table='day'
    #frequency='month'
    ovars=[dvar]
    varStructure='time_height_lat_lon'
    if not 'vertical_interpolation_method' in locals(): vertical_interpolation_method='log_linear'
  
  elif(dvar=='va' or dvar=='va5' or dvar=='va10' or dvar=='va17'):
    #diag=True
    area_t=False
    if(dvar=='va'):
      inputs=['vcomp']
    else:
      inputs=['vcomp','ps']
    realm='atmos'
    diag_dims=['time','pfull','lat','lon']
    units='m/sec'
    table='Amon'
    #frequency='month'
    ovars=[dvar]
    varStructure='time_height_lat_lon'
    if not 'vertical_interpolation_method' in locals(): vertical_interpolation_method='log_linear'
  
  elif(dvar=='pv' or dvar=='pv5' or dvar=='pv10' or dvar=='pv17'):
    #diag=True
    area_t=False
    if(dvar=='pv'):
      inputs=['pv']
    else:
      inputs=['pv','ps']
    realm='atmos'
    diag_dims=['time','phalf','lat','lon']
    units='1/s'
    table='Amon'
    ovars=[dvar]
    varStructure='time_height_lat_lon'
    if not 'vertical_interpolation_method' in locals(): vertical_interpolation_method='log_linear'
  
  elif(dvar=='divg' or dvar=='divg5' or dvar=='divg10' or dvar=='divg17'):
    #diag=True
    area_t=False
    if(dvar=='divg'):
      inputs=['divg']
    else:
      inputs=['divg','ps']
    realm='atmos'
    diag_dims=['time','phalf','lat','lon']
    units='1/s'
    table='Amon'
    ovars=[dvar]
    varStructure='time_height_lat_lon'
    if not 'vertical_interpolation_method' in locals(): vertical_interpolation_method='log_linear'
  
  elif(dvar=='vort' or dvar=='vort5' or dvar=='vort10' or dvar=='vort17'):
    #diag=True
    area_t=False
    if(dvar=='vort'):
      inputs=['vort']
    else:
      inputs=['vort','ps']
    realm='atmos'
    diag_dims=['time','phalf','lat','lon']
    units='1/s'
    table='Amon'
    ovars=[dvar]
    varStructure='time_height_lat_lon'
    if not 'vertical_interpolation_method' in locals(): vertical_interpolation_method='log_linear'
  
  elif(dvar=='mlotst'):
    #diag=True
    area_t=True
    inputs=['mld']
    realm='ocean'
    diag_dims=['time','yt_ocean','xt_ocean']
    units='m'
    table='Omon'
    ovars=[dvar]
    varStructure='time_lat_lon'
  
  elif(dvar=='mlotstsq'):
    #diag=True
    area_t=True
    inputs=['mld_sq']
    realm='ocean'
    diag_dims=['time','yt_ocean','xt_ocean']
    units='m'
    table='Omon'
    ovars=[dvar]
    varStructure='time_lat_lon'
  
  elif(dvar=='umo'):
    #diag=True
    area_t=False
    inputs=['tx_trans']
    realm='ocean'
    diag_dims=['time','yt_ocean','xu_ocean']
    units='kg s-1'
    table='Omon'
    #frequency='month'
    ovars=[dvar]
    varStructure='time_depth_lat_lon'
  
  elif(dvar=='vmo'):
    #diag=True
    area_t=False
    inputs=['ty_trans']
    realm='ocean'
    diag_dims=['time','yu_ocean','xt_ocean']
    units='kg s-1'
    table='Omon'
    #frequency='month'
    ovars=[dvar]
    varStructure='time_depth_lat_lon'
  
  elif(dvar=='volcello'):
    #diag=True
    area_t=False
    inputs=['temp']
    realm='ocean'
    diag_dims=['time','yu_ocean','xt_ocean']
    units='m3'
    table='fx'
    #frequency='month'
    ovars=[dvar]
    varStructure='time_depth_lat_lon'
  
  elif(dvar=='areacello'):
    area_t=False
    inputs=['temp']
    realm='ocean'
    diag_dims=['time','yu_ocean','xt_ocean']
    units='m2'
    table='Ofx'
    #frequency='month'
    ovars=[dvar]
    varStructure='time_depth_lat_lon'
  
  elif(dvar=='cl'):
    #diag=True
    area_t=False
    inputs=['cld_amt']
    realm='atmos'
    diag_dims=['time','phalf','lat','lon']
    units='%'
    table='Amon'
    ovars=[dvar]
    varStructure='time_height_lat_lon'
  
  elif(dvar=='sftof'):
    inputs=['temp']
    realm='ocean'
    diag_dims=['yu_ocean','xt_ocean']
    units='%'
    table='fx'
    #frequency='month'
    ovars=[dvar]
    varStructure='time_lat_lon'
  
  elif(dvar=='thkcello'):
    inputs=['temp']
    realm='ocean'
    diag_dims=['st_ocean','yu_ocean','xt_ocean']
    units='m'
    table='fx'
    #frequency='month'
    ovars=[dvar]
    varStructure='time_depth_lat_lon'
  
  elif(dvar=='deptho'):
    inputs=['temp']
    realm='ocean'
    diag_dims=['st_ocean','yu_ocean','xt_ocean']
    units='m'
    table='Ofx'
    #frequency='month'
    ovars=[dvar]
    varStructure='time_depth_lat_lon'
  
  elif(dvar=='msftyyz'):
    inputs=['ty_trans','ty_trans_gm']
    diag_dims=['time', 'basin', 'st_ocean','yu_ocean']
    realm='ocean'
    units='10^-9 kg s-1'
    units='kg s-1'
    table='Omon'
    #frequency='month'
    ovars=[dvar]
    varStructure='time_basin_depth_lat'
  
  elif(dvar=='mfo'):
    inputs=['tx_trans','ty_trans']
    realm='ocean'
    diag_dims=['time', 'oline']
    units='kg s-1'
    table='Omon'
    #frequency='month'
    ovars=[dvar]
    varStructure='time_oline'
  
  elif(dvar=='so'):
    #diag=True
    realm='ocean'
    #inputs=dvar
    table='Omon'
    #area_t=True
    inputs=['salt']
    #realm='ocean'
    diag_dims=['time','st_ocean','yt_ocean','xt_ocean']
    units='psu'
    units='0.001'
    table='Omon'
    ovars=[dvar]
    varStructure='time_depth_lat_lon'
  
  elif(dvar=='rws500'):
    #diag=True
    area_t=False
    inputs=['ucomp','vcomp']
    realm='atmos'
    diag_dims=['time','lat','lon']
    units='s-2'
    if(frequency == 'month'): table='Amon'
    else: table='day'
    ovars=[dvar]
    varStructure='time_lat_lon'

  elif(dvar=='rws5'):
    area_t=False
    inputs=['ucomp','vcomp','ps']
    realm='atmos'
    diag_dims=['time','pfull','lat','lon']
    units=['s-2','s-1','s-1','ms-1','ms-1']
    if(frequency == 'month'): table='Amon'
    else: table='day'
    #ovars=[dvar]
    ovars=['rws5','div5','eta5','uchi5','vchi5']
    grid_label='gn5'
    grid='3D vars use plev5, 300, 500, 700 and 850hPa'
    varStructure='time_height_lat_lon'
    if not 'vertical_interpolation_method' in locals(): vertical_interpolation_method='linear'
  
  elif(dvar=='ta' or dvar=='ta5' or dvar=='ta10' or dvar=='ta17'):
    #diag=True
    area_t=False
    if(dvar=='ta'):
      inputs=['temp']
    else:
      inputs=['temp','ps']
    realm='atmos'
    diag_dims=['time','pfull','lat','lon']
    units='K'
    if(frequency == 'month'): table='Amon'
    else: table='day'
    #frequency='month'
    ovars=[dvar]
    varStructure='time_height_lat_lon'
    if not 'vertical_interpolation_method' in locals(): vertical_interpolation_method='log_linear'
  
  elif(dvar=='zg' or dvar=='zg5' or dvar=='zg10' or dvar=='zg17'):
    #diag=True
    area_t=False
    if(dvar=='zg'):
      inputs=['hght']
    else:
      inputs=['hght','ps']
    realm='atmos'
    diag_dims=['time','phalf','lat','lon']
    units='m'
    table='Amon'
    #frequency='month'
    ovars=[dvar]
    varStructure='time_height_lat_lon'
    if not 'vertical_interpolation_method' in locals(): vertical_interpolation_method='log_linear'
  
  elif(dvar=='hur' or dvar=='hur5' or dvar=='hur10' or dvar=='hur17'):
    #diag=True
    area_t=False
    if(dvar=='hur'):
      inputs=['rhum']
    else:
      inputs=['rhum','ps']
    realm='atmos'
    diag_dims=['time','pfull','lat','lon']
    units='%'
    table='Amon'
    #frequency='month'
    ovars=[dvar]
    varStructure='time_height_lat_lon'
    if not 'vertical_interpolation_method' in locals(): vertical_interpolation_method='log_linear'
  
  elif(dvar=='hus' or dvar=='hus5' or dvar=='hus10' or dvar=='hus17'):
    #diag=True
    area_t=False
    if(dvar=='hus'):
      inputs=['sphum']
    else:
      inputs=['sphum','ps']
    realm='atmos'
    diag_dims=['time','pfull','lat','lon']
    units='1.0'
    if(frequency == 'month'): table='Amon'
    else: table='day'
    ovars=[dvar]
    varStructure='time_height_lat_lon'
    if not 'vertical_interpolation_method' in locals(): vertical_interpolation_method='log_linear'
  
  elif(dvar=='isothetao16c' or dvar=='isothetao20c' or dvar=='isothetao22c'):
    #diag=True
    area_t=True
    inputs=['temp']
    realm='ocean'
    diag_dims=['time','yt_ocean','xt_ocean']
    units='m'
    table='Omon'
    varStructure='time_lat_lon'
    ovars=[dvar]
  
  elif(dvar=='tauu'):
    #diag=True
    area_t=False
    inputs=['tau_x']
    realm='atmos'
    diag_dims=['time','lat','lon']
    units='Pa'
    if(frequency == 'month'): table='Amon'
    else: table='day'
    ovars=[dvar]
    varStructure='time_lat_lon'
  
  elif(dvar=='tauv'):
    #diag=True
    area_t=False
    inputs=['tau_y']
    realm='atmos'
    diag_dims=['time','lat','lon']
    units='Pa'
    table='Amon'
    ovars=[dvar]
    varStructure='time_lat_lon'
  
  else:
    #diag=False
    inputs=['']
    #inputs=dvar
    dvarnow=[dvar]
    #exit
  return realm,table,inputs,units,ovars,area_t,area_u,diag_dims,grid_label,grid,vertical_interpolation_method,varStructure

def diag_psl(data,*argv):
  '''
  '''
  import numpy as np
  onehundred,fh_printfile=argv
  return data*onehundred

def diag_hfls(data):
  '''
  '''
  import numpy as np
  return data/28.9

def diag_volcello(data,*argv):
  '''
  '''
  import numpy as np
  import inspect
  area_t,zt,z,nlats,nlons,fh_printfile=argv
  area=np.tile(np.expand_dims(area_t,0), (len(zt),1,1))
  thickness=np.expand_dims(np.expand_dims(z[:],1),2)
  thickness=np.tile( thickness ,(1,nlats,nlons))
  data=np.ma.array(data/data) * thickness*area
  #print('area.shape=',area.shape)
  #print('thickness.shape=',thickness.shape)
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  return data

def diag_cl(data,*argv):
  '''
  '''
  import numpy as np
#  import inspect
  return np.where(data<0.,0.,data*100.0) 

def curvilinear_to_rectilinear(cube, target_grid_cube=None):
    """Regrid curvilinear data to a rectilinear grid if necessary."""

    coord_names = [coord.name() for coord in cube.dim_coords]
    aux_coord_names = [coord.name() for coord in cube.aux_coords]

    if 'time' in aux_coord_names:
        aux_coord_names.remove('time')
    if 'depth' in aux_coord_names:
        aux_coord_names.remove('depth')

    if aux_coord_names == ['latitude', 'longitude']:

        if not target_grid_cube:
            grid_res = get_grid_res(cube.coord('latitude').shape)
            lats = numpy.arange(-90, 90.01, grid_res)
            lons = numpy.arange(0, 360, grid_res)
            target_grid_cube = _make_grid(lats, lons)

        # Interate over slices (experimental regridder only works on 2D slices)
        cube, coord_names = _check_coord_names(cube, coord_names)
        slice_dims = coord_names

        if 'time' in slice_dims:
            slice_dims.remove('time')
        if 'depth' in slice_dims:
            slice_dims.remove('depth')
    
        cube_list = []
        for i, cube_slice in enumerate(cube.slices(slice_dims)):
            weights = numpy.ones(cube_slice.shape)
            cube_slice.coord(axis='x').coord_system = iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)
            cube_slice.coord(axis='y').coord_system = iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)
            regridded_cube = regrid_weighted_curvilinear_to_rectilinear(cube_slice, weights, target_grid_cube)
            cube_list.append(regridded_cube)

        new_cube = iris.cube.CubeList(cube_list)
        new_cube = new_cube.merge_cube()
        coord_names = [coord.name() for coord in new_cube.dim_coords]

        regrid_status = True

    else:

        new_cube = cube
        regrid_status = False
    
    return new_cube, coord_names, regrid_status

#@numba.jit
def apply_weights(src, dest_shape, n_s, n_b, row, col, s):
    """
    Apply ESMF regirdding weights.
    """

    dest = np.ndarray(dest_shape).flatten()
    dest[:] = 0.0
    src = src.flatten()

    for i in range(n_s):
        dest[row[i]-1] = dest[row[i]-1] + s[i]*src[col[i]-1]

    return dest.reshape(dest_shape)

def shade_2d_simple(data):
  '''
  plot a 2d array and save to a file.
  '''
  import matplotlib.pyplot as plt

  fn='test.png'
  cs=plt.contourf(data)
  plt.contour(data,colors='black')
  cb=plt.colorbar(cs)
  cb.set_label('units')
  plt.savefig('test.png')
  print('Image saved to ',fn)
  #pylab.show()
  #plt.show()

  return()

def shade_2d_latlon(data,lats,lons,clevs):
    """
    """
    import cartopy.crs as ccrs
    from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
    from cartopy.util import add_cyclic_point
    import matplotlib as mpl
    mpl.rcParams['mathtext.default'] = 'regular'
    import matplotlib.pyplot as plt

    ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=180))
    #clevs = [0,50,100,150,200,250,300,10000]
    #clevs = [0,50,100,150,200,250,300]
    if('clevs' in locals()):
      fill = ax.contourf(lons, lats, data , clevs, cmap=plt.cm.RdBu_r, transform=ccrs.PlateCarree(), extend='both')
    else:
      fill = ax.contourf(lons, lats, data, cmap=plt.cm.RdBu_r, transform=ccrs.PlateCarree(), extend='both')
    ax.coastlines()
    ax.gridlines()
    ax.set_xticks([0, 60, 120, 180, 240, 300, 359.99], crs=ccrs.PlateCarree())
    ax.set_yticks([-90, -60, -30, 0, 30, 60, 90], crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True, number_format='.0f')
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    plt.colorbar(fill, orientation='horizontal')
    plt.title('data($units$)', fontsize=16)
    plt.savefig('test.png')
    #plt.show()

def diag_zmld_boyer(temp,salt,*argv):
    """
    depth in metres (m) is approximately equal to pressure in decibars (db).
    http://www.seabird.com/document/an69-conversion-pressure-depth
    Update: seem to get an IndexError in zmld_boyer, not sure why a.t.m.
    """
    import numpy as np
    import inspect
    import seawater as sw
    import numpy.ma as ma

    p,nlats,nlons,fh_printfile=argv
    temp=ma.masked_equal(temp,-1e20)
    salt=ma.masked_equal(salt,-1e20)

    #print(temp.shape)

    Vshape=temp.shape
    ntims=Vshape[0]
    #print('Vshape=',Vshape)
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    if(nlats!=Vshape[-2]): raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    if(nlons!=Vshape[-1]): raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

    data=np.ones((ntims,nlats,nlons),float)*-1e20

    for t in range(0,ntims):
      #for y in range(50,nlats):
      #  for x in range(50,nlons):
      for y in range(0,nlats):
        for x in range(0,nlons):
          print('y,x=',y,x)
          kval_tmp=np.array(np.nonzero(~temp[0,:,y,x].mask)).flatten() #assume salt has some number of non-missing points above ocean bottom.
        #print('kval_tmp=',kval_tmp)
        #print(kval_tmp.size)
          if(kval_tmp.size>0):
            kval=kval_tmp[-1]
            print('kval=',kval)
            print('temp=',temp[0,0:kval,y,x])
            print('salt=',salt[0,0:kval,y,x])
            print('p=',p[0:kval])
            data[t,y,x],dummy=zmld_boyer(salt[t,0:kval,y,x],temp[t,0:kval,y,x],p[0:kval]) #dummy is mld based on temperature threshold, ignore for now.
          #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    return(data)

def zmld_boyer(s,t,p):
    """
    Computes mixed layer depth, based on de Boyer Montegut et al., 2004.

    Parameters
    ----------
    s : array_like
        salinity [psu (PSS-78)]
    t : array_like
        temperature [?~D~C (ITS-90)]
    p : array_like
        pressure [db].

    Notes
    -----
    Based on density with fixed threshold criteria
    de Boyer Montegut et al., 2004. Mixed layer depth over the global ocean:
        An examination of profile data and a profile-based climatology.
        doi:10.1029/2004JC002378

    dataset for test and more explanation can be found at:
    http://www.ifremer.fr/cerweb/deboyer/mld/Surface_Mixed_Layer_Depth.php

    Codes based on : http://mixedlayer.ucsd.edu/
    taken from python-oceans//oceans/sw_extras/sw_extras.py
    """
    import numpy as np
    import inspect
    import seawater as sw

    #p,fh_printfile=argv

#    print(t.shape)
#    print(s.shape)
#    print(p.shape)

    m = len(s)
    # starti = min(find((pres-10).^2==min((pres-10).^2)));
    starti = np.min(np.where(((p - 10.)**2 == np.min((p - 10.)**2)))[0])
    pres = p[starti:m]
    sal = s[starti:m]
    temp = t[starti:m]
    starti = 0
    m = len(sal)
    pden = sw.dens0(sal, temp)-1000

    mldepthdens_mldindex = m
    for i, pp in enumerate(pden):
        if np.abs(pden[starti] - pp) > .03:
            mldepthdens_mldindex = i
            break

    # Interpolate to exactly match the potential density threshold.
    presseg = [pres[mldepthdens_mldindex-1], pres[mldepthdens_mldindex]]
    pdenseg = [pden[starti] - pden[mldepthdens_mldindex-1], pden[starti] -
               pden[mldepthdens_mldindex]]
    P = np.polyfit(presseg, pdenseg, 1)
    presinterp = np.linspace(presseg[0], presseg[1], 3)
    pdenthreshold = np.polyval(P, presinterp)

    # The potential density threshold MLD value:
    ix = np.max(np.where(np.abs(pdenthreshold) < 0.03)[0])
    mldepthdens_mldindex = presinterp[ix]

    # Search for the first level that exceeds the temperature threshold.
    mldepthptmp_mldindex = m
    for i, tt in enumerate(temp):
        if np.abs(temp[starti] - tt) > 0.2:
            mldepthptmp_mldindex = i
            break

    # Interpolate to exactly match the temperature threshold.
    presseg = [pres[mldepthptmp_mldindex-1], pres[mldepthptmp_mldindex]]
    tempseg = [temp[starti] - temp[mldepthptmp_mldindex-1],
               temp[starti] - temp[mldepthptmp_mldindex]]
    P = np.polyfit(presseg, tempseg, 1)
    presinterp = np.linspace(presseg[0], presseg[1], 3)
    tempthreshold = np.polyval(P, presinterp)

    # The temperature threshold MLD value:
    ix = np.max(np.where(np.abs(tempthreshold) < 0.2)[0])
    mldepthptemp_mldindex = presinterp[ix]

    return mldepthdens_mldindex, mldepthptemp_mldindex
    #return data

def sigmatheta(s, t, p, pr=0):
    """
    :math:`\\sigma_{\\theta}` is a measure of the density of ocean water
    where the quantity :math:`\\sigma_{t}` is calculated using the potential
    temperature (:math:`\\theta`) rather than the in situ temperature and
    potential density of water mass relative to the specified reference
    pressure.

    Parameters
    ----------
    s(p) : array_like
           salinity [psu (PSS-78)]
    t(p) : array_like
           temperature [:math:`^\\circ` C (ITS-90)]
    p : array_like
        pressure [db]
    pr : number
         reference pressure [db], default = 0

    Returns
    -------
    sgmte : array_like
           density  [kg m :sup:`3`]

    Examples
    --------
    >>> # Data from UNESCO Tech. Paper in Marine Sci. No. 44, p22.
    >>> from seawater.library import T90conv
    >>> from oceans import sw_extras as swe
    >>> s = [0, 0, 0, 0, 35, 35, 35, 35]
    >>> t = T90conv([0, 0, 30, 30, 0, 0, 30, 30])
    >>> p = [0, 10000, 0, 10000, 0, 10000, 0, 10000]
    >>> swe.sigmatheta(s, t, p)
    array([ -0.157406  ,  -0.20476006,  -4.34886626,  -3.63884068,
            28.10633141,  28.15738545,  21.72863949,  22.59634627])

    References
    ----------
    .. [1] Fofonoff, P. and Millard, R.C. Jr UNESCO 1983. Algorithms for
    computation of fundamental properties of seawater. UNESCO Tech. Pap. in
    Mar. Sci., No. 44, 53 pp.  Eqn.(31) p.39.
    http://www.scor-int.org/Publications.htm

    .. [2] Millero, F.J., Chen, C.T., Bradshaw, A., and Schleicher, K. A new
    high pressure equation of state for seawater. Deap-Sea Research., 1980,
    Vol27A, pp255-264. doi:10.1016/0198-0149(80)90016-3

    """
    import numpy as np
    import inspect
    import seawater as sw
    import numpy.ma as ma
    s, t, p, pr = list(map(np.asanyarray, (s, t, p, pr)))
    return sw.pden(s, t, p, pr) - 1000.0

def diag_zmld_so(temp,salt,*argv):
    """
    depth in metres (m) is approximately equal to pressure in decibars (db).
    http://www.seabird.com/document/an69-conversion-pressure-depth
    Update:
    """
    import numpy as np
    import inspect
    #import seawater as sw
    import numpy.ma as ma

    p,nlats,nlons,fh_printfile=argv
    temp=ma.masked_equal(temp,-1e20)
    salt=ma.masked_equal(salt,-1e20)

    #print(temp.shape)

    Vshape=temp.shape

    ntims=Vshape[0]
    #print('Vshape=',Vshape)
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    if(nlats!=Vshape[-2]): raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    if(nlons!=Vshape[-1]): raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

    data=np.ones((ntims,nlats,nlons),float)*-1e20

    for t in range(0,ntims):
      #for y in range(50,nlats):
      #  for x in range(50,nlons):
      for y in range(0,nlats):
        for x in range(0,nlons):
          #print('y,x=',y,x)
          kval_tmp=np.array(np.nonzero(~temp[0,:,y,x].mask)).flatten() #assume salt has some number of non-missing points above ocean bottom.
        #print('kval_tmp=',kval_tmp)
        #print(kval_tmp.size)
          if(kval_tmp.size>0):
            kval=kval_tmp[-1]#kval is the deepest point.
            #print('kval=',kval)
            #print('temp=',temp[0,0:kval,y,x])
            #print('salt=',salt[0,0:kval,y,x])
            #print('p=',p[0:kval])
            value=zmld_so(salt[t,0:kval,y,x], temp[t,0:kval,y,x],p[0:kval], threshold=0.05, smooth=None)
            if(value.size==1):
              #print('value=',value)
              data[t,y,x]=zmld_so(salt[t,0:kval,y,x], temp[t,0:kval,y,x],p[0:kval], threshold=0.05, smooth=None) #do I have to set to 0 otherwise? sometimes I got 2 values for return value...
          #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    return(data)

def zmld_so(s, t, p, threshold=0.05, smooth=None):
    """
    Computes mixed layer depth of Southern Ocean waters.

    Parameters
    ----------
    s : array_like
        salinity [psu (PSS-78)]
    t : array_like
        temperature [?~D~C (ITS-90)]
    p : array_like
        pressure [db].
    smooth : int
        size of running mean window, to smooth data.

    References
    ----------
    Mitchell B. G., Holm-Hansen, O., 1991. Observations of modeling of the
        Antartic phytoplankton crop in relation to mixing depth. Deep Sea
        Research, 38(89):981-1007. doi:10.1016/0198-0149(91)90093-U

    """
    from pandas import rolling_mean
    import numpy as np
    import inspect
    sigma_t = sigmatheta(s, t, p)
    depth = p
    if smooth is not None:
        sigma_t = rolling_mean(sigma_t, smooth, min_periods=1)

    sublayer = np.where(depth[(depth >= 5) & (depth <= 10)])[0]
    sigma_x = np.nanmean(sigma_t[sublayer])
    nan_sigma = np.where(sigma_t < sigma_x + threshold)[0]
    sigma_t[nan_sigma] = np.nan
    der = np.divide(np.diff(sigma_t), np.diff(depth))
    mld = np.where(der == np.nanmax(der))[0]
    zmld = depth[mld]

    return zmld

def diag_spice(temp,salt,*argv):
    """
    depth in metres (m) is approximately equal to pressure in decibars (db).
    http://www.seabird.com/document/an69-conversion-pressure-depth
    Update:
    """
    import numpy as np
    import inspect
    #import seawater as sw
    import numpy.ma as ma

    p,nlats,nlons,fh_printfile=argv
    temp=ma.masked_equal(temp,-1e20)
    salt=ma.masked_equal(salt,-1e20)

    Vshape=temp.shape
    ntims=Vshape[0]
    nlevs=Vshape[1]
    #print('Vshape=',Vshape)
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    if(nlats!=Vshape[-2]): raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    if(nlons!=Vshape[-1]): raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

    data=np.ones((ntims,nlevs,nlats,nlons),float)*-1e20

    for t in range(0,ntims):
      temp_flat=temp[t,].reshape(nlevs*nlats*nlons) #units of degC
      salt_flat=salt[t,].reshape(nlevs*nlats*nlons) #units of psu (1.0) e.g. 35
      data=spice(salt_flat,temp_flat,p).reshape(nlevs,nlats,nlons) #p passed as dummy, not needed as no potential temperature calculation needed..

      #print(data_flat.shape)
      #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

#    for t in range(0,ntims):
#      #for y in range(50,nlats):
#      #  for x in range(50,nlons):
#      for y in range(0,nlats):
#        for x in range(0,nlons):
#          #print('y,x=',y,x)
#          kval_tmp=np.array(np.nonzero(~temp[0,:,y,x].mask)).flatten() #assume salt has some number of non-missing points above ocean bottom.
#        #print('kval_tmp=',kval_tmp)
#        #print(kval_tmp.size)
#          if(kval_tmp.size>0):
#            kval=kval_tmp[-1]#kval is the deepest point.
#            #print('kval=',kval)
#            #print('temp=',temp[0,0:kval,y,x])
#            #print('salt=',salt[0,0:kval,y,x])
#            #print('p=',p[0:kval])
#            data[t,0:kval,y,x]=spice(salt[t,0:kval,y,x], temp[t,0:kval,y,x],p[0:kval])
#            #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    return(data)

#def spice(s, t, p):
def spice(s, pt, p): #already potential temperature
    """
    Compute sea spiciness as defined by Flament (2002).

    .. math:: \pi(\theta,s) = \sum^5_{i=0} \sum^4_{j=0} b_{ij}\theta^i(s-35)^i

    Parameters
    ----------
    s(p) : array_like
           salinity [psu (PSS-78)]
    t(p) : array_like
           temperature [:math:`^\\circ` C (ITS-90)]
    p : array_like
        pressure [db]

    Returns
    -------
    sp : array_like
         :math:`\pi` [kg m :sup:`3`]

    See Also
    --------
    pressure is not used... should the input be theta instead of t?
    Go read the paper!

    Notes
    -----
    Spiciness, just like potential density, is only useful over limited
    vertical excursions near the pressure to which they are referenced; for
    large vertical ranges, the slope of the isopycnals and spiciness isopleths
    vary significantly with pressure, and generalization of the polynomial
    expansion to include a reference pressure dependence is needed.

    Examples
    --------
    >>> from oceans import sw_extras as swe
    >>> swe.spice(33, 15, 0)
    array(0.5445864137500002)

    References
    ----------
    .. [1] A state variable for characterizing water masses and their
    diffusive stability: spiciness. Prog. in Oceanography Volume 54, 2002,
    Pages 493-501.

    http://www.satlab.hawaii.edu/spice/spice.m

    """
    import numpy as np
    import inspect
    #import seawater as sw
    #import numpy.ma as ma
    #s, t, p = list(map(np.asanyarray, (s, t, p))) #not needed

    #print('s.shape=',s.shape)
    # FIXME: I'm not sure about this next step.
    #pt = sw.ptmp(s, t, p) #not neeed

    B = np.zeros((6, 5))
    B[0, 0] = 0.
    B[0, 1] = 7.7442e-001
    B[0, 2] = -5.85e-003
    B[0, 3] = -9.84e-004
    B[0, 4] = -2.06e-004

    B[1, 0] = 5.1655e-002
    B[1, 1] = 2.034e-003
    B[1, 2] = -2.742e-004
    B[1, 3] = -8.5e-006
    B[1, 4] = 1.36e-005

    B[2, 0] = 6.64783e-003
    B[2, 1] = -2.4681e-004
    B[2, 2] = -1.428e-005
    B[2, 3] = 3.337e-005
    B[2, 4] = 7.894e-006

    B[3, 0] = -5.4023e-005
    B[3, 1] = 7.326e-006
    B[3, 2] = 7.0036e-006
    B[3, 3] = -3.0412e-006
    B[3, 4] = -1.0853e-006

    B[4, 0] = 3.949e-007
    B[4, 1] = -3.029e-008
    B[4, 2] = -3.8209e-007
    B[4, 3] = 1.0012e-007
    B[4, 4] = 4.7133e-008

    B[5, 0] = -6.36e-010
    B[5, 1] = -1.309e-009
    B[5, 2] = 6.048e-009
    B[5, 3] = -1.1409e-009
    B[5, 4] = -6.676e-010

    sp = np.zeros_like(pt)
    T = np.ones_like(pt)
    s = s - 35
    r, c = B.shape
    for i in range(r):
        S = np.ones_like(pt)
        for j in range(c):
            sp += B[i, j] * T * S
            S *= s
        T *= pt

    #print('sp=',sp.shape)
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    return(sp)

def diag_bigthetao(temp,salt,*argv):
    """
    depth in metres (m) is approximately equal to pressure in decibars (db).
    http://www.seabird.com/document/an69-conversion-pressure-depth
    Update:
    """
    import numpy as np
    import inspect
    import gsw as gsw
    import numpy.ma as ma

    depths,lat_vals,lon_vals_360,nlats,nlons,fh_printfile=argv

    depths3d=np.expand_dims(np.expand_dims(depths,1),2)
    depths3d=np.tile( depths3d ,(1,nlats,nlons)) # 1m same as pressure in db.

    #print('depths3d.shape=',depths3d.shape)

    temp=ma.masked_equal(temp,-1e20)
    salt=ma.masked_equal(salt,-1e20)
    #print(depths3d.shape)
    #print('salt.shape=',salt.shape)
    #print('type(salt)=',type(salt))
    #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    #print('salt=',salt[0,:50,50])
    #print('temp=',temp[0,:50,50])

    Vshape=temp.shape
    ntims=Vshape[0]
    nlevs=Vshape[1]

    #print('Vshape=',Vshape)
    if(nlats!=Vshape[-2]): raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    if(nlons!=Vshape[-1]): raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

    data=np.zeros((ntims,nlevs,nlats,nlons),float)

    #SP = [34.5487, 34.7275, 34.8605, 34.6810, 34.5680, 34.5600]
    #p = [10, 50, 125, 250, 600, 1000]
    #lon = 188
    #lat = 4
    #print(gsw.SA_from_SP(SP, p, lon, lat))

    #print(lon_vals_360[:])
    #p=depths[:]-10.1325
    #p=depths[:]
    #print(p)

    #print(lon_vals_360)
    #print('type(lon_vals_360=',type(lon_vals_360))

    for t in range(0,ntims):
      #s=salt[t,:,:,:]
      #print('s.shape=',s.shape)
      #print('depths3d.shape=',depths3d.shape)
      #print('lon_vals_360.shape=',lon_vals_360.shape)
      #print('lat_vals.shape=',lat_vals.shape)
      abs_salt=gsw.SA_from_SP(salt[t,:,:,:], depths3d-10.1325, lon_vals_360[:], lat_vals[:])
      #abs_salt=gsw.SA_from_SP(salt[t,:,:,:], depths3d-10.1325, lon_vals_360, lat_vals)
      #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
      #print(abs_salt.shape)
      data[t,:,:,:]=gsw.CT_from_pt(abs_salt, temp[t,:,:,:])
      data=ma.masked_where(temp==-1e20,data)
      #print('data.shape=',data.shape)
      #print('type(data)=',type(data))
      #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    return(data)

def diag_soabs(salt,*argv):
    """
    depth in metres (m) is approximately equal to pressure in decibars (db).
    http://www.seabird.com/document/an69-conversion-pressure-depth
    Update:
    """
    import numpy as np
    import inspect
    import gsw as gsw
    import numpy.ma as ma

    depths,lat_vals,lon_vals_360,nlats,nlons,fh_printfile=argv

    depths3d=np.expand_dims(np.expand_dims(depths,1),2)
    depths3d=np.tile( depths3d ,(1,nlats,nlons)) # 1m same as pressure in db.

    salt=ma.masked_equal(salt,-1e20)

    Vshape=salt.shape
    ntims=Vshape[0]
    nlevs=Vshape[1]

    #print('Vshape=',Vshape)
    if(nlats!=Vshape[-2]): raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    if(nlons!=Vshape[-1]): raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

    data=np.zeros((ntims,nlevs,nlats,nlons),float)

    for t in range(0,ntims):
      data[t,:,:,:]=gsw.SA_from_SP(salt[t,:,:,:], depths3d-10.1325, lon_vals_360[:], lat_vals[:])
      data=ma.masked_where(salt==-1e20,data)
    return(data)

def diag_spiciness(temp,salt,*argv):
    """
    depth in metres (m) is approximately equal to pressure in decibars (db).
    http://www.seabird.com/document/an69-conversion-pressure-depth
    Update:
    """
    import numpy as np
    import inspect
    import gsw as gsw
    import numpy.ma as ma

    depths,lat_vals,lon_vals_360,nlats,nlons,fh_printfile=argv

    depths3d=np.expand_dims(np.expand_dims(depths,1),2)
    depths3d=np.tile( depths3d ,(1,nlats,nlons)) # 1m same as pressure in db.

    temp=ma.masked_equal(temp,-1e20)
    salt=ma.masked_equal(salt,-1e20)

    Vshape=temp.shape
    ntims=Vshape[0]
    nlevs=Vshape[1]

    if(nlats!=Vshape[-2]): raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    if(nlons!=Vshape[-1]): raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

    data=np.zeros((ntims,nlevs,nlats,nlons),float)

    for t in range(0,ntims):
      abs_salt=gsw.SA_from_SP(salt[t,:,:,:], depths3d-10.1325, lon_vals_360[:], lat_vals[:])
      con_temp=gsw.CT_from_pt(abs_salt, temp[t,:,:,:])
      data[t,:,:,:]=gsw.spiciness0(abs_salt, con_temp)
      data=ma.masked_where(temp==-1e20,data)
    return(data)

def diag_potrho(temp,salt,*argv):
    """
    depth in metres (m) is approximately equal to pressure in decibars (db).
    http://www.seabird.com/document/an69-conversion-pressure-depth
    Update:
    """
    import numpy as np
    import inspect
    import gsw as gsw
    import numpy.ma as ma

    depths,lat_vals,lon_vals_360,nlats,nlons,fh_printfile=argv

    depths3d=np.expand_dims(np.expand_dims(depths,1),2)
    depths3d=np.tile( depths3d ,(1,nlats,nlons)) # 1m same as pressure in db.

    temp=ma.masked_equal(temp,-1e20)
    salt=ma.masked_equal(salt,-1e20)

    Vshape=temp.shape
    ntims=Vshape[0]
    nlevs=Vshape[1]

    if(nlats!=Vshape[-2]): raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
    if(nlons!=Vshape[-1]): raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))

    data=np.zeros((ntims,nlevs,nlats,nlons),float)
    offset=10.1325
    offset=0.

    for t in range(0,ntims):
      abs_salt=gsw.SA_from_SP(salt[t,:,:,:], depths3d-offset, lon_vals_360[:], lat_vals[:])
      con_temp=gsw.CT_from_pt(abs_salt, temp[t,:,:,:])
      data[t,:,:,:]=gsw.rho(abs_salt, con_temp, depths3d-offset)
      data=ma.masked_where(temp==-1e20,data)
    return(data)

def uncomment_json(input,output,clobber):
  '''
  To remove comments from input file and write to output file observing clobber setting.
  '''
  import os
  import inspect

  ifh=open(input)

  if(os.path.exists(output) and not clobber):
    raise SystemExit('Output exists and clobber=False:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  else:
    if(os.path.exists(output)):
      os.remove(output)
    ofh=open(output,'w')

  for i,line in enumerate(ifh):
    fields=line.strip().split('#')

    if(fields[0]!=''):
      print(fields[0],file=ofh)
    else:
      None

  ifh.close()
  ofh.close()

  return()

def process_json(input,output,REALISATION,YBEG_MIN,YEND_MAX,MBEG_MIN,MEND_MAX,DBEG_MIN,DEND_MAX,clobber):
  '''
  To process keyword strings input file and write to output file observing clobber setting.
  '''
  import os
  import inspect

  ifh=open(input)

  if(os.path.exists(output) and not clobber):
    raise SystemExit('Output exists and clobber=False:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  else:
    if(os.path.exists(output)):
      os.remove(output)
    ofh=open(output,'w')

  #print(type(REALISATION))
  if(REALISATION<10):
    PPREALISATION="00"+str(REALISATION)
  elif ( REALISATION<100 ):
    PPREALISATION="0"+str(REALISATION)
  else:
    PPREALISATION=str(REALISATION)

  if ( REALISATION<10 ):
    PREALISATION="0"+str(REALISATION)
  elif ( REALISATION<100 ):
    PREALISATION=str(REALISATION)
  else:
    PREALISATION=str(REALISATION)

  #print(PPREALISATION)

  for i,line in enumerate(ifh):

    line=line.replace('YBEG_MIN',str(YBEG_MIN))
    line=line.replace('YEND_MAX',str(YEND_MAX))
    line=line.replace('MBEG_MIN',str(MBEG_MIN))
    line=line.replace('MEND_MAX',str(MEND_MAX))
    line=line.replace('DBEG_MIN',str(DBEG_MIN))
    line=line.replace('DEND_MAX',str(DEND_MAX))
    line=line.replace('PPREALISATION',str(PPREALISATION))
    line=line.replace('PREALISATION',str(PREALISATION))
    line=line.replace('REALISATION',str(REALISATION))

    #print(line,end='')
    print(line,file=ofh,end='')
  #raise SystemExit('Forced exit file:'+__file__+' line number: '+str(inspect.stack()[0][2]))
  ifh.close()
  ofh.close()

  return()

def fractional_year_from_num2date(stamps,calendar):
  '''
  Calculate fractional year YYYY.XXXX for generating time-axis suitable for plotting.
  Can cope with different calendar systems. Ignores time-frequencies less than hours (e.g. minutes, seconds)
  although they could be included if required.
  First written 02 March 2018 by Mark Collier
  Last modified 02 March 2018 by Mark Collier
  '''
  import datetime
  import netCDF4
  import numpy as np
    
  fraction_year_size=len(stamps)
  #print('fraction_year_size=',fraction_year_size)
  fraction_year=np.zeros(fraction_year_size,dtype=float)

  for i,stamp in enumerate(stamps):
    #print(i,stamp)
    this_year=(stamp.year)
    this_month=(stamp.month)
    this_day=(stamp.day)
    this_hour=(stamp.hour)
    #print('this_hour=',this_hour)
    time_string='days since '+str(this_year)+'-01-01'
    
    time_stamp_beg=datetime.datetime(this_year,1,1) + datetime.timedelta(hours=0.0)
    time_beg=netCDF4.date2num(time_stamp_beg,time_string,calendar)
    
    time_stamp_now=datetime.datetime(this_year,this_month,this_day) + datetime.timedelta(hours=this_hour)
    time_now=netCDF4.date2num(time_stamp_now,time_string,calendar)
    
    time_stamp_end=datetime.datetime(this_year,12,31) + datetime.timedelta(hours=24.0)
    time_end=netCDF4.date2num(time_stamp_end,time_string,calendar)

    fraction_of_the_year=(time_now-time_beg)/(time_end+1.0)
    fraction_year[i]=this_year+fraction_of_the_year

  return(fraction_year)

def get_daily_indices_for_monthlyave(time,stamp,calendar):
  '''
  Calculate the indices of time that correspond to the month, allowing monthly averages of some quantity to be calculated.
  Might need to consider other kinds of calendars e.g. 365_day etc.
  '''
  import datetime
  import netCDF4
  import calendar

  ybeg=stamp[0].year
  yend=stamp[-1].year
  
  indices=[]
  for ynow in range(ybeg,yend+1):
    if(not calendar.isleap(ynow) or calendar=='noleap'):
      days_in_month=[31,28,31,30,31,30,31,31,30,31,30,31]
    else:
      days_in_month=[31,29,31,30,31,30,31,31,30,31,30,31]
    for mnow in range(0,12):
      #print('ynow,mnow=',ynow,mnow)
      dates=[datetime.datetime(ynow,mnow+1,1,12)+n*datetime.timedelta(hours=24) for n in range(days_in_month[mnow])]
      #print('dates=',dates)
      indices.append(netCDF4.date2index(dates,time,select='exact'))
  return(indices)

def new_monthly_array_shape(data_shape,a,b):
  '''
  Determine vector describing how to reshape array so that monthly climatologies can be formed.
  a typically equals number of years
  b typically equals 12, number of months in a year
  '''
  import numpy as np
  in_shape=np.asarray(data_shape)
  in_size=in_shape.size
  value=np.zeros((2+in_size-1),dtype=int)
  value[0]=a
  value[1]=b
  if(len(in_shape)>1):
    for i,d in enumerate(in_size):
      if(i>0):
        #print('i,d=',i,d)
        value[i+1]=d
  return(value)
