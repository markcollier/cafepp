from __future__ import print_function #this is to allow print(,file=xxx) feature

def finish(file_name,odir,ofil,ofil_modified,season,fh_printfile):
  '''
  finish
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

def diag_nhblocking_index(data,lat,lon):
  '''
  To write out GHGS/GHGN would need to have a new dimension based on size of deltas vector.
  http://www.met.rdg.ac.uk/phdtheses/The%20predictability%20of%20atmospheric%20blocking.pdf
  '''
  import numpy as np
  print('data.shape=',data.shape)
  #np.set_printoptions(threshold='nan')
  #print('lat=',lat[:])
  #deltas=np.array([-5.,0.,5.])
  deltas=np.array([-5.,5.,0.])
  if(len(data.shape) == 3):
    blocked=np.zeros((12,len(lon[:])))
  else:
    blocked=np.zeros(len(lon[:]))
  #print('lat60d=',lat60d)
  #print('lat40d=',lat40d)
  for delta in range(0,len(deltas)):
    lat40d=np.abs(lat[:] - 40.+deltas[delta]).argmin()
    lat60d=np.abs(lat[:] - 60.+deltas[delta]).argmin()
    lat80d=np.abs(lat[:] - 80.+deltas[delta]).argmin()
    if(len(data.shape) == 3):
      GHGS=(data[:,lat60d,:]-data[:,lat40d,:])/(lat[lat60d]-lat[lat40d])
      GHGN=(data[:,lat80d,:]-data[:,lat60d,:])/(lat[lat80d]-lat[lat60d])
      #print('GHGS=',GHGS[30])
      #print('GHGN=',GHGN[30])
      blocked=blocked+(np.select([GHGS>0.],[1])+np.select([GHGN<-10.],[1])/2)
      kkk=np.where(blocked>0)
      #jjj=np.where(GHGS.any()>0. and GHGN.any()<-10.)
      #jjj=np.logical_and(GHGS>0.,GHGN<-10.)
      #print(blocked[:])
      #print(kkk[:])
    else:
      GHGS=(data[lat60d,:]-data[lat40d,:])/(lat[lat60d]-lat[lat40d])
      GHGN=(data[lat80d,:]-data[lat60d,:])/(lat[lat80d]-lat[lat60d])
      #print('GHGS=',GHGS[30])
      #print('GHGN=',GHGN[30])
      blocked=blocked+(np.select([GHGS>0.],[1])+np.select([GHGN<-10.],[1])/2)
      kkk=np.where(blocked>0)
  #raise SystemExit('Forced exit.')
      print('GHGS.shape=',GHGS.shape)
  return(blocked,GHGS,GHGN) #note only delta=0 value kept here.

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

  print('msftyyz data.shape=',data.shape)
  #print(np.shape(data))
  if(len(np.shape(data))==3):
    t0=1
  else:
    t0=np.shape(data)[0]
  #print('t0=',t0)
  tmpdata=np.ma.zeros((t0,nbasins,nzb,nlats),dtype='f')
  landMask=np.where( np.array(data,dtype=bool) ,0,1)
  mask_vals=cdms2.open('/g/data/p66/mac599/CMIP5/ancillary_files/lsmask_20110618.nc','r').variables['mask_ttcell'][:,:,:]

  mask=np.zeros(np.shape(data),dtype=float)
  if(t0==1):
    mask=mask+np.where(mask_vals==2,1,0)
    mask=mask+np.where(mask_vals==4,1,0)
  else:
    for txx in range(t0):
      mask[txx,]=mask[txx,]+np.where(mask_vals==2,1,0)
      mask[txx,]=mask[txx,]+np.where(mask_vals==4,1,0)
  atlantic_arctic_mask=ma.masked_equal(mask,0)

  mask=np.zeros(np.shape(data),dtype=float)
  if(t0==1):
    mask=mask+np.where(mask_vals==3,1,0)
    mask=mask+np.where(mask_vals==5,1,0)
  else:
    for txx in range(t0):
      mask[txx,]=mask[txx,]+np.where(mask_vals==3,1,0)
      mask[txx,]=mask[txx,]+np.where(mask_vals==5,1,0)
  indoPac_mask=ma.masked_equal(mask,0)

  mask=np.zeros(np.shape(data),dtype=float)
  if(t0==1):
    mask=mask+np.where(mask_vals/mask_vals==1,1,0)
  else:
    for txx in range(t0):
      mask[txx,]=mask[txx,]+np.where(mask_vals/mask_vals==1,1,0)
  global_mask=ma.masked_equal(mask,0)
  return atlantic_arctic_mask,indoPac_mask,global_mask

def diag_msftyyz(data,atlantic_arctic_mask,indoPac_mask,global_mask,nbasins,nzb,nlats):
  '''
  '''
  import numpy as np
  import numpy.ma as ma
  import cdms2
  if(len(np.shape(data))==3):
    t0=1
  else:
    t0=np.shape(data)[0]
  #print('t0=',t0)
  tmpdata=np.ma.zeros((t0,nbasins,nzb,nlats),dtype='f')
  tmpdata[:,0,:,:]=np.cumsum( np.sum( data*np.where(atlantic_arctic_mask==1,1,1e20) ,axis=-1) ,axis=-2)
  tmpdata[:,1,:,:]=np.cumsum( np.sum( data*np.where(indoPac_mask==1,1,1e20) ,axis=-1) ,axis=-2)
  tmpdata[:,2,:,:]=np.cumsum( np.sum( data*np.where(global_mask==1,1,1e20) ,axis=-1) ,axis=-2)
  data=tmpdata*1e9

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

def diag_rws500(u,v,lat,lon,fh_printfile):
  '''
  rws500
  '''
  import numpy as np
  from windspharm.standard import VectorWind
  from windspharm.tools import prep_data, recover_data, order_latdim
  import spharm

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

def diag_mfo(tx_trans,ty_trans,nlines):
  '''
  transAcrossLine from app_funcs.py
  '''
  import numpy as np
  import numpy.ma as ma
  import cdms2
  #from app_funcs import *
  if(len(np.shape(tx_trans))==3):
    t0=1
  else:
    t0=np.shape(data)[0]
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

def diag_rws(data1,data2,lats,lons,rws_string):
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

  if "rws5" in rws_string:
    rws5 = recover_data(rws5, uwnd_info)
  if "div5" in rws_string:
    div5 = recover_data(div5, uwnd_info)
  if "eta5" in rws_string:
    eta5 = recover_data(eta5, uwnd_info)
  if "uchi5" in rws_string:
    uchi5 = recover_data(uchi5, uwnd_info)
  if "vchi5" in rws_string:
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

  s=",";return_what=s.join(rws_string)
  #return_what="rws,div,eta,uchi,vchi"
  print("return_what=",return_what)

  #if "rws" in rws_string:
  #  print("yes")
  #else:
  #  print("no")
  #raise SystemExit('Forced exit.')

  #return(rws,div,eta,uchi,vchi)
  return(eval(return_what))

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
  #print('data.shape=',data.shape)

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
      print('tnow=',tnow)
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
  print('data=',data)
  print('data.shape=',data.shape)

  #print('data=',data[:,180])

  #raise SystemExit('Forced exit.')
  return data

def diag_nino34(data,area_t,lat,lon,fh_printfile):
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
  #lon=np.add(lon,360.0)
  #lon=np.where(lon<360.,lon,lon-360.)

  lon=np.add(lon,360.0)
  lon=np.where(lon<360.,lon,lon-360.)
  lon=np.roll(lon,80)

  #print('lat=',lat,file=fh_printfile)

  lat=np.squeeze(lat)
  area_t=np.roll(area_t,80,axis=-1)
  data=np.roll(data,80,axis=-1)

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
  s=data.shape
  #print('s=',s,file=fh_printfile)

#in future all data will have time dimension.
  if(len(s)==3):
    #has time dimension in it.
    newdata=np.zeros(s[0])
    #print('newdata.shape=',newdata.shape,file=fh_printfile)
    #print('tmpdata.shape=',tmpdata.shape,file=fh_printfile)
    for q in range(s[0]):
      tmpdata=data[q,]
      #print('q=',q,file=fh_printfile)
      #print('tmpdata.shape=',tmpdata.shape,file=fh_printfile)
      newdata[q]=xtra_nino34(tmpdata,nino34_lat_min,nino34_lat_max,nino34_lon_min,nino34_lon_max,area_t,fh_printfile)
    data=newdata 
      #print('newdata=',newdata,file=fh_printfile)
  else:
    data=xtra_nino34(data,nino34_lat_min,nino34_lat_max,nino34_lon_min,nino34_lon_max,area_t,fh_printfile)
    #print('xxdata=',data,file=fh_printfile)
    #raise SystemExit('Forced exit.')
  return data

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
        ofil_modified.append(ofil)

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

def diag_iod(data,area_t,lat,lon):
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
  #print('data.shape=',data.shape)
  #print('area_t.shape',area_t.shape)
  #j=np.vstack((area_t,area_t))
  #j=np.resize(area_t,data.shape)
  s=data.shape
  #print('s=',s)
  #print('iodW_lat_min=',iodW_lat_min)
  #print('iodW_lat_max=',iodW_lat_max)
  #print('iodW_lon_min=',iodW_lon_min)
  #print('iodW_lon_max=',iodW_lon_max)
  #print('')
  #print('iodE_lat_min=',iodE_lat_min)
  #print('iodE_lat_max=',iodE_lat_max)
  #print('iodE_lon_min=',iodE_lon_min)
  #print('iodE_lon_max=',iodE_lon_max)
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

def vertical_interpolate(data,zt,newlevs,ps,type):
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

  index_hi=np.zeros(nnewlevs,float)
  index_lo=np.zeros(nnewlevs,float)

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

  #print('index_hi,index_lo=',index_hi,index_lo)
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

  nlev=data.shape[0]
  nlat=data.shape[1]
  nlon=data.shape[2]

  #if(diag):
  #  print('data.shape=',data.shape)
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

  xabove=np.zeros((nlat,nlon))
  xbelow=np.zeros((nlat,nlon))

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
    inputs=['tx_trans']
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
