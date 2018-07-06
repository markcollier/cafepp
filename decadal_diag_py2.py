def shade_2d_polar(data,**kwargs):
  '''
  plot a 2d array.
  '''
    
  import matplotlib.pyplot as plt
  import cartopy.crs as ccrs

  Diag = add_contours = title_check = units_check = extend_check = reverse_xaxis = reverse_yaxis = clevs_check = \
    xyvals_check = xlim_check = ylim_check = grid = xtik_check = ytik_check = cmap_check = coast = NPS = SPS = False
  xsize,ysize=6.0,4.0
  for key, value in kwargs.items():
    if(Diag): print('key,value=',key,value)
    if(key=='Diag'):
      Diag=bool(value)
    elif(key=='xysize'):
      xsize,ysize=value
    elif(key=='clevs'):
      clevs=value
      clevs_check=True
    elif(key=='output'):
      output=value
    elif(key=='add_contours'):
      add_contours=bool(value)
    elif(key=='title'):
      title=value
      title_check=True
    elif(key=='units'):
      units=value
      units_check=True
    elif(key=='extend'):
      extend=value
      extend_check=True
#     elif(key=='reverse_xaxis'):
#       reverse_xaxis=bool(value)
#     elif(key=='reverse_yaxis'):
#       reverse_yaxis=bool(value)
    elif(key=='xyvals'):
      xvals,yvals=value
      xyvals_check=True
    elif(key=='xlim'):
      xlim=value
      xlim_check=True
    elif(key=='ylim'):
      ylim=value
      ylim_check=True
    elif(key=='xlab'):
      xlab=value
      xlab_check=True
    elif(key=='ylab'):
      ylab=value
      ylab_check=True
#     elif(key=='xtik'):
#       xtik=value
#       xtik_check=True
#     elif(key=='ytik'):
#       ytik=value
#       ytik_check=True
    elif(key=='grid'):
      grid=bool(value)
    elif(key=='coast'):
      coast=bool(value)
    elif(key=='cmap'):
      cmap=value
      cmap_check=True
    else:
      raise SystemExit('Dont know that key.'+__file__+' line number: '+str(inspect.stack()[0][2]))
      
  if(not title_check): title='data'
  if(not units_check): units='units'  
  if(not extend_check): extend='both'
  if(not cmap_check): cmap='jet'
  if(not xlim_check): xlim=(0,360)
  if(not ylim_check): ylim=(-90,0)
    
#   print('xlim=',xlim)
#   print('ylim=',ylim)
  
  if(ylim[0]<0 and ylim[1]>0):
    raise SystemExit('ylim[0]<0 and ylim[1]>0.'+__file__+' line number: '+str(inspect.stack()[0][2]))
    
  if(ylim[0]>0 and ylim[1]<0):
    raise SystemExit('ylim[0]>0 and ylim[1]<0.'+__file__+' line number: '+str(inspect.stack()[0][2]))  
    
  if(ylim[0]<0): SPS=True
  if(ylim[1]>0): NPS=True
    
  if(SPS and NPS or not SPS and not NPS):
    raise SystemExit('Could not determine SPS/NPS.'+__file__+' line number: '+str(inspect.stack()[0][2])) 
    
  fig = plt.gcf()
  fig.set_size_inches(xsize, ysize) #default 6.0,4.0
  
  if(NPS):
#     print('generating NPS...')
    ax = plt.axes(projection=ccrs.NorthPolarStereo())
  else:
#     print('generating SPS...')
    ax = plt.axes(projection=ccrs.SouthPolarStereo())    
  
#python3 syntax:
#  lonlat_extent=[*xlim,*ylim]
#python2 syntax: todo

#   print('lonlat_extent=',lonlat_extent)

  #print(len(clevs))
  print('clevs=',clevs)
  #if('clevs' in locals()):
  
  if(not clevs_check or type(clevs)==type(None)):
    cs=ax.contourf(xvals, yvals, data, transform=ccrs.PlateCarree(), extend=extend, cmap=cmap)
  else:
    cs=ax.contourf(xvals, yvals, data, clevs, transform=ccrs.PlateCarree(), extend=extend, cmap=cmap)
    
  # without the set_global, currently, the plot is tiny because the limits
  # are being erroneously being set (opened issue for that)
  #ax.set_global()
  
  ax.set_extent(lonlat_extent, crs=ccrs.PlateCarree())
  #ax.set_extent([0, 360, 45, 90], crs=ccrs.PlateCarree())
      
  if(add_contours): plt.contour(data,colors='black')
  cb=plt.colorbar(cs)
  cb.set_label(units)
  
  if(type(units)==type(None)):
    plt.title(title, fontsize=16)
  else:
    plt.title(title+' ('+units+')', fontsize=16)

#   if(xlim_check): plt.xlim(xlim)
      
#   if(ylim_check): plt.ylim(ylim)
          
#   if(reverse_xaxis): plt.gca().invert_xaxis()
      
#   if(reverse_yaxis): plt.gca().invert_yaxis()
    
  if('xlab' in locals()): plt.xlabel(xlab)
  if('ylab' in locals()): plt.ylabel(ylab)
    
  if(grid): plt.grid(True,linestyle='-')
  if(coast): ax.coastlines()
  #ax.stock_img()
  
  locs, labels = plt.xticks()
  
  #plt.xticks(range(-90, 90, 30), fontsize=14)
  if('xtik' in locals()): plt.xticks(xtik)  
  if('ytik' in locals()): plt.yticks(ytik) 

  #print('locs=',locs)
  #print('labels=',labels[:])
  
  if('output' in locals()):
    plt.savefig(output+'.png')
    print('Image saved to ',output+'.png')
  else:
    plt.show()

  return()
