def year_fraction(ybeg, yend, **kwargs):
  import inspect
  import numpy as np
  #mbeg=mend=None
  mbeg,mend=1,12 #defaults
  for key, value in kwargs.items():
    if(key=='mbeg'):
      mbeg=int(value)
    elif(key=='mend'):
      mend=int(value)
    else:
      raise SystemExit('Dont know that key.'+__file__+' line number: '+str(inspect.stack()[0][2]))
  #months=[1,2,3,4,5,6,7,8,9,10,11,12]

  dim=np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
  day_end=np.cumsum(dim)
  day_beg=day_end-dim+1.0
  day_mid = (day_beg+day_end)/2.0
  day_frac = day_mid/np.sum(dim)
  yvals = range(ybeg,yend+1)
  yfracs = np.zeros((len(yvals)*12),dtype=float)
  for yval in yvals:
    sss=(yval-yvals[0])*12
    eee=sss+12
    yfracs[sss:eee] = yval+day_frac
    #print(sss,eee)

  #print('day_mid=',day_mid)
  #print(months)
  #print('day_end=',day_end)
  #print('day_beg=',day_beg)
  #print('day_frac=',day_frac)
  #print('ybeg,yend=',ybeg,yend)
  #print('yvals=',yvals)
  #print(len(yvals))
  #print(yfracs)
  #return(yfracs[mbeg-1:-1])

  tbeg=mbeg-1
  tend=len(yfracs)-(12-mend)
  return(yfracs[tbeg:tend]) #end of year_fraction

def cmap_hero(clevs, **kwargs):
  '''
  This is a convenient way of creating a new color map based in input contours levels (clevs).
  '''
  import inspect
  import numpy as np
  import matplotlib as mpl  
  import matplotlib.pyplot as plt
  from matplotlib import cm
  
  Diag=False
  middle2white = first_middle2white = last_middle2white = first_flip = last_flip = False
  negative_infinity='.25'
  positive_infinity='.75'
  first_cmap='YlOrRd'
  last_cmap='PuBuGn'
  first_fraction=[0.,1.]
  last_fraction=[0.,1.]
  
  white_test=0
  if(middle2white): white_test+=1
  if(first_middle2white): white_test+=1
  if(last_middle2white): white_test+=1
    
  if(white_test>1): raise SystemExit('Need to have one or none of middle2white,first_middle2white,last_middle2white True.'+__file__+' line number: '+str(inspect.stack()[0][2]))
  
  for key, value in kwargs.items():
    if(key=='Diag'):
      Diag=value
    elif(key=='middle2white'):
      middle2white=bool(value)
    elif(key=='first_middle2white'):
      first_middle2white=bool(value)
    elif(key=='last_middle2white'):
      last_middle2white=bool(value)
    elif(key=='negative_infinity'):
      negative_infinity=value
    elif(key=='positive_infinity'):
      positive_infinity=value
    elif(key=='first_cmap'):
      first_cmap=value
    elif(key=='last_cmap'):
      last_cmap=value
    elif(key=='first_fraction'):
      first_fraction=value
    elif(key=='last_fraction'):
      last_fraction=value
    elif(key=='first_flip'):
      first_flip=bool(value)
    elif(key=='last_flip'):
      last_flip=bool(value)
    else:
      raise SystemExit('Dont know that key.'+__file__+' line number: '+str(inspect.stack()[0][2]))

  if(Diag==0): print('clevs=',clevs)

  positive_cnt=np.sum(np.array(clevs)>0)
  negative_cnt=np.sum(np.array(clevs)<0)
  zero_cnt=np.sum(np.array(clevs)==0)
  
  if(Diag==0): print('positive_cnt,zero_cnt,negative_cnt=',positive_cnt,zero_cnt,negative_cnt)

  #raise SystemExit('STOP!:'+__file__+' line number: '+str(inspect.stack()[0][2]))

  cmap_first = plt.get_cmap(first_cmap)
  cmap_last = plt.get_cmap(last_cmap)

  cmaplist_first = [cmap_first(i) for i in range(cmap_first.N)]
  cmaplist_last = [cmap_last(i) for i in range(cmap_last.N)]

  zero_to_one = np.linspace(0, 1, 256)

  if(Diag>=1): print('zero_to_one.shape=',zero_to_one.shape)
  if(Diag>=1): print('zero_to_one=',zero_to_one)

  zero_to_255 = np.arange(255+1)

  if(Diag>=1): print('zero_to_255.shape=',zero_to_255.shape)
  if(Diag>=1): print('zero_to_255=',zero_to_255)

  if(first_flip): first_fraction=first_fraction[::-1]
  if(last_flip): last_fraction=last_fraction[::-1]

#this length 3 list corresponds to:
#element 0: fractional way through first color map to start (min 0)
#element 1: fractional way through first color map to end (max 1)
#element 2: number of points in
#this allows a segment of the full range of the color map to be linearyly extracted.
  if(middle2white):
    select_first = first_fraction + [negative_cnt-1]
    select_last = last_fraction + [positive_cnt-1]
    
  elif(first_middle2white):
    select_first = first_fraction + [negative_cnt-1]
    select_last = last_fraction + [positive_cnt]
    
  elif(last_middle2white):
    select_first = first_fraction + [negative_cnt]
    select_last = last_fraction + [positive_cnt-1]
    
  else:
    select_first = first_fraction + [negative_cnt]
    select_last = last_fraction + [positive_cnt]
    
  if(Diag==0): print('select_first=',select_first)
  
  #raise SystemExit('STOP!:'+__file__+' line number: '+str(inspect.stack()[0][2]))

#   select_first=[0.2, .8, 2]
#   select_last=[0.2, .8, 2]

  deci_firsts = np.linspace(select_first[0], select_first[1], select_first[2])
  deci_lasts = np.linspace(select_last[0], select_last[1], select_last[2])

  indice_first = []
  for deci_first in deci_firsts:
    if(Diag==0): print('deci_first=',deci_first)
    indice_first.append(np.abs(zero_to_one - deci_first).argmin())

  indice_last = []
  for deci_last in deci_lasts:
    if(Diag==0): print('deci_last=',deci_last)
    indice_last.append(np.abs(zero_to_one - deci_last).argmin())

  if(Diag==0): print('indice_first=',indice_first)
  if(Diag==0): print('indice_last=',indice_last)

  if(middle2white):
    cmaplist = [cmaplist_first[i] for i in indice_first] + [(1.0, 1.0, 1.0, 1.0)] + [(1.0, 1.0, 1.0, 1.0)] + [cmaplist_last[i] for i in indice_last]

  elif(first_middle2white):
    cmaplist = [cmaplist_first[i] for i in indice_first] + [(1.0, 1.0, 1.0, 1.0)] + [cmaplist_last[i] for i in indice_last]

  elif(last_middle2white):
    cmaplist = [cmaplist_first[i] for i in indice_first] + [(1.0, 1.0, 1.0, 1.0)] + [cmaplist_last[i] for i in indice_last]

  else:
    cmaplist = [cmaplist_first[i] for i in indice_first] + [cmaplist_last[i] for i in indice_last]
    
  if(Diag==0): print('cmaplist=',cmaplist)

  cmap = mpl.colors.ListedColormap(cmaplist)
  if(type(positive_infinity)!=type(None)):
    cmap.set_over(positive_infinity)
  if(type(negative_infinity)!=type(None)):
    cmap.set_under(negative_infinity)

  return(cmap) #end of cmap_hero

def leap_year(year, calendar='standard'):
    """Determine if year is a leap year"""
    leap = False
    if ((calendar in ['standard', 'gregorian',
        'proleptic_gregorian', 'julian']) and
        (year % 4 == 0)):
        leap = True
        if ((calendar == 'proleptic_gregorian') and
            (year % 100 == 0) and
            (year % 400 != 0)):
            leap = False
        elif ((calendar in ['standard', 'gregorian']) and
                 (year % 100 == 0) and (year % 400 != 0) and
                 (year < 1583)):
            leap = False
    return leap

def get_dpm(time, calendar='standard'):
    """
    return a array of days per month corresponding to the months provided in `months`
    """
    month_length = np.zeros(len(time), dtype=np.int)

    cal_days = dpm[calendar]

    for i, (month, year) in enumerate(zip(time.month, time.year)):
        month_length[i] = cal_days[month]
        if leap_year(year, calendar=calendar):
            month_length[i] += 1
    return month_length
