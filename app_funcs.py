import datetime
import numpy as np
import re
import os,sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import calendar

#get outpath
outpath= os.environ.get('APP_OUTPATH')
if not outpath:
	raise Exception('Please set environment variable "APP_OUTPATH" as the output folder')

#get cdat_location from evironment variable and load cdms2
try:
	sys.path.append(os.environ['CDAT_LOCATION'])
except:
	print "you have not specified the environment variable: 'CDAT_LOCATION' , trying to import cdms2 anyway"
import cdms2


#function to give a sample plot of a variable
def plotVar(outpath,file_name,cmip_table,vcmip,local_experiment):
	f=cdms2.open(outpath+'/'+file_name,'r')
	var=f.variables[vcmip]
	dims=var.shape
	units=var.units
	plt.figure()
	print 'plotting...'
	#3D field: 
	#plot lat-lon plots at different levels, 
	#for first time step only
	if len(dims)==4:
		#3D- plot contour at first z level, 
		plt.subplot(221)
		plt.title('first level')
		plt.imshow(var[0,0,:,:],origin='lower')
		plt.colorbar()
		#last level
		plt.subplot(222)
		plt.title('last level')
		plt.imshow(var[0,-1,:,:],origin='lower')
		plt.colorbar()
		#middle level
		plt.subplot(223)
		plt.title('middle level')
		lev=int(np.floor(dims[1]/2))
		plt.imshow(var[0,lev,:,:],origin='lower')
		plt.colorbar()
		#average
		plt.subplot(224)
		plt.title('ave over z')
		print 'calculating ave over z...'
		plt.imshow(np.ma.average(var[0,:],axis=0),origin='lower')
		print 'done'		
		plt.colorbar()
	elif len(dims)==3: 
	#
	#2D field:
	#plot lat-lon contour at first time
		plt.imshow(var[0,:,:],origin='lower')
		#plt.contourf(lon[:],lat[:],var[0,:,:],100)
		plt.colorbar()
	elif len(dims)==2:
	#2D field:(fixed time variables)
	#plot lat-lon contours 
		plt.imshow(var[:,:],origin='lower')
		#plt.contourf(lon[:],lat[:],var[0,:,:],100)
		plt.colorbar()
	else: 
	#assume scalar
	#plot line plot, variable vs. time
		plt.plot(np.array(var[:]))

	#Set a super title for whole image
	plt.suptitle('Plot of '+vcmip +' ('+units+')')	

	#
	#make output directory and save figure:
	#
	folder=outpath+'/CMIP5/plots/'+local_experiment+'/'+cmip_table
	if not os.path.isdir(folder):
		os.makedirs(folder)
	plt.savefig(folder+'/'+vcmip+'.png')
	print 'saved figure for variable ', vcmip
	
	#cleanup
	plt.clf()
	f.close()

def calcRefDate(time):
	ref= re.search('\d{4}-\d{2}-\d{2}', time.units).group(0).split('-')
	return datetime.date(int(ref[0]), int(ref[1]), int(ref[2]))

#function to call the calculation defined in the 'calculation' string in the database
def calculateVals(access_file,varNames,calculation):
	
	#Set array for coordinates if used by calculation
	if calculation.find('times')!=-1:
		times=access_file[0].variables[varNames[0]].getTime()
	if calculation.find('depth')!=-1:
		depth=access_file[0].variables[varNames[0]].getAxis(1)
	if calculation.find('lat')!=-1:
		lat=access_file[0].variables[varNames[0]].getLatitude()
	if calculation.find('lon')!=-1:
		lon=access_file[0].variables[varNames[0]].getLatitude()

	var=[]
	for v in varNames:
		try: #extract variable out of file
			var.append(access_file[0].variables[v][:])
		except: #try to find variable in extra files instead
			var.append(access_file[1].variables[v][:])
	try:
		return eval(calculation)
	except Exception , e:
		print "error evaluating calculation:", calculation
		raise

#Calculate the y_overturning mass streamfunction
#For three basins: 
#0 Atlantic-Arctic
#1 Indian-Pacific basin
#2 Global Basin
def meridionalOverturning(transList,typ):
#TODO remove masks once satified with these calculations
	ty_trans=transList[0]
	#print type(ty_trans), np.shape(ty_trans) ,np.shape(ty_trans.mask)
	
	#initialise array
	dims=list(np.shape(ty_trans[:,:,:,0])) +[3] #remove x, add dim for 3 basins
	transports= np.ma.zeros(dims,dtype=np.float32)
	
	#first calculate for global basin
	#2: global basin
	transports[:,:,:,2]=calcOverturning(transList,typ)
	#plt.figure()
	#cs=plt.contourf(transports[0,:,:,2],20)
	#plt.savefig('plots/over_circ.ps')
	#plt.clf()
	try:
		if ty_trans.mask==False: 
		#if there is no mask: set masks to arrays of zeros
			for trans in transList:
				trans.mask=np.zeros(np.shape(trans),dtype=bool)
	except: pass
	#grab land mask out of ty_trans file (assuming the only masked values are land)
	landMask=np.array(ty_trans.mask[0,:,:,:],dtype=bool)

	#cs=plt.contourf(landMask[0,:,:],20)
	#plt.colorbar()
	#plt.savefig('plots/landMask.ps')
	#plt.clf()	

	#plot ty_trans
	#cs=plt.contourf(ty_trans[0,5,:,:])
	#plt.savefig('plots/ty_trans.ps')
	#plt.clf()
	
	#Get basin masks
	mask=getBasinMask()
	
	#0: atlantic arctic basin
	#set masks
	#atlantic and arctic basin are given by mask values 2 and 4 #TODO double check this
	atlantic_arctic_mask=np.ma.make_mask(np.logical_and(mask!=2.0,mask!=4.0))
	#print ty_trans.hardmask
	for t in range(np.shape(ty_trans)[0]):
		for z in range(np.shape(ty_trans)[1]):
			for trans in transList:
				trans.mask[t,z,:,:]=np.ma.mask_or(atlantic_arctic_mask,landMask[z,:,:])
	#plot ty_trans for atlantic basin
	#cs=plt.contourf(ty_trans[0,5,:,:],20)
	#plt.colorbar()
	#plt.savefig('plots/ty_trans_atlantic.ps')
	#plt.clf()

	#calculate MOC with atlantic basin mask
	transports[:,:,:,0]=calcOverturning(transList,typ)
	
	#1: indoPacific basin:
	#set masks
	#Indian and Pacific basin are given by mask values 3 and 5 #TODO double check this
	indoPac_mask=np.ma.make_mask(np.logical_and(mask!=3.0,mask!=5.0))
	for t in range(np.shape(ty_trans)[0]):
		for z in range(np.shape(ty_trans)[1]):
			for trans in transList:
				trans.mask[t,z,:,:]=np.ma.mask_or(indoPac_mask,landMask[z,:,:])
	#plot ty_trans for indoPacific basin
	#cs=plt.contourf(ty_trans[0,5,:,:],20)
	#plt.colorbar()
	#plt.savefig('plots/ty_trans_indoPac.ps')
	#plt.clf()	

	#calculate MOC with indoPacific basin mask:
	transports[:,:,:,1]=calcOverturning(transList,typ)

	return transports

#calculate overturning circulation depending on what inputs are given	
def calcOverturning(transList,typ):
	#assumes transList is a list of variables:
	#ty_trans, ty_trans_gm, ty_trans_submeso
	#where the gm and submeso quantities may or may not exist
	#gm = bolus
	#

	#Calculation is:
	#sum over the longditudes and 
	#for ty_trans run a cumalative sum over depths (not for gm or submeso)
	#The result for each variable in transList are added together
	typ=typ.split('_')
	n=len(transList)
	if len(typ)==1:
		#normal case for cmip5, need to convert units
		# gm and submeso quantities are output in Sv so need to be multiplied by 10**9
		typ=typ[0]
		if n==1:
			if typ=='bolus':
				#should be bolus transport for rho levels 
				return transList[0].sum(3)*10**9
		elif n==2:
			if typ=='bolus':
				#bolus advection is sum of gm and submeso
				return ( transList[0].sum(3)+transList[1].sum(3) ) *10**9
			elif typ=='full':
				#full y overturning on rho levels, where trans and trans_gm are present (no submeso)
				tmp= transList[0].sum(3).cumsum(1)+transList[1].sum(3) *10**9
				s=transList[0].sum(3).sum(1)
				for i in range(tmp.shape[1]):
					tmp[:,i,:]=tmp[:,i,:]-s
				return tmp
		elif n==3:
			#assume full y overturning:
			#trans + trans_gm +trans_submeso
			if typ=='full':
				tmp= transList[0].sum(3).cumsum(1)+transList[1].sum(3)*10**9+transList[2].sum(3)*10**9
				s=transList[0].sum(3).sum(1)
				for i in range(tmp.shape[1]):
					tmp[:,i,:]=tmp[:,i,:]-s
				return tmp
	elif typ[1]=='Sv':
		#case from old diagnostics, units all in sieverts 
		typ=typ[0]
		if n==1:
			if typ=='bolus':
				#should be bolus transport for rho levels 
				return transList[0].sum(3)
		elif n==2:
			if typ=='bolus':
				#bolus advection is sum of gm and submeso
				return transList[0].sum(3)+transList[1].sum(3)
			elif typ=='full':
				#full y overturning on rho levels, where trans and trans_gm are present (no submeso)
				tmp= transList[0].sum(3).cumsum(1)+transList[1].sum(3)
				s=transList[0].sum(3).sum(1)
				for i in range(tmp.shape[1]):
					tmp[:,i,:]=tmp[:,i,:]-s
				return tmp
		elif n==3:
			#assume full y overturning:
			#trans + trans_gm +trans_submeso
			if typ=='full':
				tmp=transList[0].sum(3).cumsum(1)+transList[1].sum(3)+transList[2].sum(3)
				s=transList[0].sum(3).sum(1)
				for i in range(tmp.shape[1]):
					tmp[:,i,:]=tmp[:,i,:]-s
				return tmp

#Compute monthly average of daily values (for 2D variables)
def monthAve(var,time):
	datelist=time.asComponentTime()
	monthave=[]
	#get month, value of first date
	month=datelist[0].month
	val_sum=var[0,:,:]
	count=1
	#loop over all dates
	for index, d in enumerate(datelist[1:]):
		if d.month==month: #same month 
			count+=1
			val_sum+=var[index+1,:,:] #add value to sum
		else: #new month
			monthave.append(val_sum/count) #calculate average for previous month and add to list
			val_sum=var[index+1,:,:] #get first value for the new month
			count=1
			month=d.month
	#append last month to list 
	monthave.append(val_sum/count)
	print 'monthly ave has shape:',np.shape(np.array(monthave))
	print np.array(monthave)[0,50,50]
	return np.array(monthave)

#calculate a climatology of monthly means
def monthClim(var,time,vals_wsum,clim_days):
	datelist=time.asComponentTime()
	print 'calculating climatology...'
	#loop over all dates,
	try:
		for index, d in enumerate(datelist):
			m=d.month #month
			#add the number of days for this month
			dummy,days=calendar.monthrange(d.year,m)
#			print index,d,m,days
			clim_days[m-1]+=days
			#add values weighted by the number of days in this month
			vals_wsum[m-1,:]+=(var[index,:]*days)
	except Exception,e:
		print e
		raise

	return vals_wsum,clim_days

#calculate a average monthly means (average is vals_wsum/clim_days)
def ave_months(var,time,vals_wsum,clim_days):
	datelist=time.asComponentTime()
	print 'calculating climatology...'
	#loop over all dates,
	try:
		for index, d in enumerate(datelist):
			m=d.month #month
			#add the number of days for this month
			dummy,days=calendar.monthrange(d.year,m)
#			print index,d,m,days
			clim_days+=days
			#add values weighted by the number of days in this month
			vals_wsum[:]+=(var[index,:]*days)
	except Exception,e:
		print e
		raise

	return vals_wsum,clim_days


#def daysInMonth(time):
#	tvals=time[:]
#		
#	days=np.zeros([len(tvals)])
#	for i,t in enumerate(tvals):	
#		d=datetime.timedelta(int(t))+refdate
#		dummy,days[i]=calendar.monthrange(d.year,d.month)
#	print days
#	return days[0]

# returns days in month for time variable
def daysInMonth(time):
	tvals=time[:]
	refdate=calcRefDate(time)
	if len(tvals)==1:
		d=datetime.timedelta(int(tvals[0]))+refdate
		dummy,days=calendar.monthrange(d.year,d.month)
	else:
		days=[]
		for t in tvals:
			d=datetime.timedelta(int(t))+refdate
			dummy,d=calendar.monthrange(d.year,d.month)
			days.append(d)
	return days		

#convert daily time values to monthly
#returns time values, 
#and the min and max time for each month (bounds)
#assumes time is in the gregorian calandar, relative to date 0001-01-01
def day2mon(tvals):
	datelist=[]
	for t in tvals: 
		datelist.append(datetime.datetime(1,1,1)+ datetime.timedelta(t))
	#get month, value of first date
	month=datelist[0].month
	val_sum=tvals[0]
	count=1
	tmonth=[] #List of average time value for each month
	tmin=[] #list of start of month bounds
	tmax=[] #list of end of month bounds
	tmin.append(np.floor(tvals[0]))
	print month
	#loop over all dates
	for index, d in enumerate(datelist[1:]):
		#print index , count ,d.month
		if d.month==month: #same month 
			count+=1
			val_sum+=tvals[index+1] #add value to sum
		else: #new month
			tmonth.append(val_sum/count)#calculate average for previous month and add to list
			val_sum=tvals[index+1] #get first value for the new month
			count=1
			month=d.month
			tmin.append(np.floor(tvals[index+1]))
			tmax.append(np.floor(tvals[index+1]))
	#append last month to list 
	tmonth.append(val_sum/count)
	print tmonth
	tmax.append(np.floor(tvals[index+1])+1)
	return np.array(tmonth), tmin,tmax

#List of strings giving the names of the straits used in the mass transports across lines
def getTransportLines():
	return ['barents_opening','bering_strait','canadian_archipelago','denmark_strait',\
		'drake_passage','english_channel','pacific_equatorial_undercurrent',\
		'faroe_scotland_channel','florida_bahamas_strait','fram_strait','iceland_faroe_channel',\
		'indonesian_throughflow','mozambique_channel','taiwan_luzon_straits','windward_passage']
	
#Calculates the mass transports across lines
#for each line requested in cmip5
#
def lineTransports(tx_trans,ty_trans):
	#print tx_trans[0,:,34,64], tx_trans[0,:,34,64].sum()
	#initialise array
	transports= np.zeros([len(tx_trans[:,0,0,0]),len(getTransportLines())],dtype=np.float32)
	#0 barents opening
	transports[:,0]=transAcrossLine(ty_trans,292,300,271,271)
	transports[:,0]+=transAcrossLine(tx_trans,300,300,260,271)
	#1 bering strait
	transports[:,1]=transAcrossLine(ty_trans,110,111,246,246)
	#2 canadian archipelago
	transports[:,2]=transAcrossLine(ty_trans,206,212,285,285)
	transports[:,2]+=transAcrossLine(tx_trans,235,235,287,288)
	#3 denmark strait
	transports[:,3]=transAcrossLine(tx_trans,249,249,248,251)
	transports[:,3]+=transAcrossLine(ty_trans,250,255,247,247)
	#4 drake passage
	transports[:,4]=transAcrossLine(tx_trans,212,212,32,49)
	#5 english channel is unresolved by the access model
	#6 pacific equatorial undercurrent
	#specified down to 350m not the whole depth
	transports[:,6]=transAcrossLine(np.ma.masked_where(\
		tx_trans[:,0:25,:]<0,tx_trans[:,0:25,:]),124,124,128,145)
	#7 faroe scotland channel    
	transports[:,7]=transAcrossLine(ty_trans,273,274,238,238)
	transports[:,7]+=transAcrossLine(tx_trans,274,274,232,238)
	#8 florida bahamas strait
	transports[:,8]=transAcrossLine(ty_trans,200,205,192,192)
	#9 fram strait
	transports[:,9]=transAcrossLine(tx_trans,267,267,279,279)
	transports[:,9]+=transAcrossLine(ty_trans,268,284,278,278)
	#10 iceland faroe channel
	transports[:,10]=transAcrossLine(ty_trans,266,268,243,243)
	transports[:,10]+=transAcrossLine(tx_trans,268,268,240,243)
	transports[:,10]+=transAcrossLine(ty_trans,269,272,239,239)
	transports[:,10]+=transAcrossLine(tx_trans,272,272,239,239)
	#11 indonesian throughflow
	transports[:,11]=transAcrossLine(tx_trans,31,31,117,127)
	transports[:,11]+=transAcrossLine(ty_trans,35,36,110,110)
	transports[:,11]+=transAcrossLine(ty_trans,43,44,110,110)
	transports[:,11]+=transAcrossLine(tx_trans,46,46,111,112)
	transports[:,11]+=transAcrossLine(ty_trans,47,57,113,113)
	#12 mozambique channel    
	transports[:,12]=transAcrossLine(ty_trans,320,323,91,91)
	#13 taiwan luzon straits
	transports[:,13]=transAcrossLine(ty_trans,38,39,190,190)
	transports[:,13]+=transAcrossLine(tx_trans,40,40,184,188)
	#14 windward passage
	transports[:,14]=transAcrossLine(ty_trans,205,206,185,185)
	return transports

#
#Calculate the heights of each atmospheric level at any lat and lon
#uses the model orography and level a and b coefficients to calculate this
def calcHeights(zgrid):
	a_vals,b_vals,dummy1,dummy2=getHybridLevels(zgrid)
	orog=getOrog()
	z=len(a_vals)
	[y,x]=np.shape(orog)
	height=np.zeros([z,y,x],dtype=np.float32)
	for i, a in enumerate(a_vals):
		height[i,:]=a+b_vals[i]*orog[:]
	#f=Scientific.IO.NetCDF.NetCDFFile('/home/599/pfu599/app/trunk/heights.nc','w')
	#f.createDimension('z',z)
	#f.createDimension('y',y)
	#f.createDimension('x',x)
	#f.createVariable('height','f',('z','y','x',))
	#f.variables['height'][:]=height[:]
	#f.close()
	return height

def calcBurden_fromConc(conc):
	t_num,z,y,x=np.shape(conc)
	orog=getOrog()
	#Get level heights and the difference between levels
	a_vals,b_vals,bounds,b_bounds=getHybridLevels('theta')
	dz=np.zeros([z,y,x],dtype=np.float32)
	for i in range(z):
		dz[i]=bounds[i,1]-bounds[i,0]+ orog*(b_bounds[i,1]-b_bounds[i,0])
	
	#calculate burden
	burden=np.zeros([t_num,y,x],dtype=np.float32)
	#for z in range(z):
	#sum up over heights
	#weight concentration by level height 
	burden[:,:,:]=(conc[:]*dz[:]).sum(1)
	return burden
        
#Calculate aerosol burdens from mixing ratio
def calcBurden(theta,pressure,var):
        #first calculate concentration
        conc=calcConcentration(theta,pressure,var)
        return calcBurden_fromConc(conc)

#Calculate aerosol burdens from mixing ratio
def calcBurden_temp(temp,pressure,var):
        #first calculate concentration
        conc=calcConcentration_temp(temp,pressure,var)
        return calcBurden_fromConc(conc)


#Calculate gas/aerosol concentration from mixing ratio
# Concentration is mass mixing ratio* density
# Density = P*rd/temp
def calcConcentration(theta,pressure,var):
	rd=287.0
	cp=1003.5
	p_0=100000.0
	fac1=pressure/rd
	#convert theta (potential temp) to absolute temp
	fac2=(1.0/theta)*((p_0/pressure)**(rd/cp)) 
	return var*fac1*fac2
	

#Calculate gas/aerosol concentration from mixing ratio
# Concentration is mass mixing ratio* density
# Density = pressure*rd/temp
def calcConcentration_temp(temp,pressure,var):
	rd=287.0
	return var*pressure/rd/temp

#idea use to reduce memory usage (doesn't seem to make a difference)
def calcBurdens(variables):
	theta=variables[0]
	pressure=variables[1]
	burden=calcBurden(theta,pressure,variables[2])
	for i in range(3,len(variables)):
		burden+=calcBurden(theta,pressure,variables[i])
	return burden
		
	
#Calculate the mass trasport across a line
#either i_start=i_end and the line goes from j_start to j_end 
#or j_start=j_end and the line goes from i_start to i_end
#var is either the x or y mass transport depending on the line
#
def transAcrossLine(var,i_start,i_end,j_start,j_end):
	if i_start==i_end or j_start==j_end:
		try:
			trans= var[:,:,j_start:j_end+1,i_start:i_end+1].sum(1).sum(1).sum(1) #sum each axis apart from time (3d)
		except:
			trans= var[:,j_start:j_end+1,i_start:i_end+1].sum(1).sum(1) #sum each axis apart from time (2d)
		#print var[0,0,j_start:j_end+1,i_start:i_end+1]
		return trans
	else: raise Exception('ERROR: Transport across a line needs to be calculated for a single value of i or j')

def msftbarot(psiu,tx_trans):
	drake_trans=transAcrossLine(tx_trans,212,212,32,49)
	#loop over times
	for i,trans in enumerate(drake_trans):
#offset psiu by the drake passage transport at that time
		psiu[i,:]=psiu[i,:]+trans
	return psiu


#returns a and b coefficients of the hybrid height levels
#zgrid is either theta or rho, specifying which levels to use
def getHybridLevels(zgrid):
	a_theta=[2.00003376e+01, 8.00013504e+01 ,  1.79999115e+02 ,  3.20001465e+02,
	   5.00000580e+02 ,  7.20000366e+02 ,  9.80000854e+02  , 1.27999805e+03,
	   1.61999988e+03 ,  1.99999841e+03 ,  2.42000171e+03  , 2.88000146e+03,
	   3.37999829e+03 , 3.91999951e+03  , 4.50000146e+03   ,5.12000000e+03,
	   5.77999951e+03 ,  6.47999951e+03 ,  7.22000000e+03  , 8.00000146e+03,
	   8.82000000e+03 ,  9.67999902e+03 ,  1.05799980e+04  , 1.15199980e+04,
	   1.24999990e+04 ,  1.35200010e+04 ,  1.45807998e+04  , 1.56946396e+04,
	   1.68753105e+04 ,  1.81386270e+04 ,  1.95030098e+04  , 2.09901875e+04,
	   2.26260820e+04 ,  2.44582852e+04 ,  2.65836406e+04  , 2.92190801e+04,
	   3.29086914e+04 ,  3.92548320e+04]
	b_theta=[ 0.99771649 , 0.9908815 ,  0.97954255 , 0.96377707 , 0.94369549 , 0.91943836,
	  0.89117801 , 0.85911834 , 0.82349348 , 0.78457052 , 0.74264622 , 0.6980502,
	  0.65114272 , 0.60231441 , 0.55198872 , 0.50061995 , 0.44869339 , 0.39672577,
	  0.34526527 , 0.29489139 , 0.24621508 , 0.19987822 , 0.15655422 , 0.11694787,
	  0.08179524 , 0.05186372 , 0.02793682 , 0.01071648 , 0.00130179  ,0.     ,     0.,
	  0.         , 0.         , 0.         , 0.         , 0.         , 0.      ,    0.    ]
	a_rho= [  9.99820614e+00,   4.99988823e+01 ,  1.30000229e+02,   2.49998337e+02,
	   4.10001038e+02 ,  6.10000488e+02  , 8.50000610e+02,   1.13000146e+03,
	   1.44999902e+03 ,  1.81000110e+03  , 2.21000000e+03,   2.64999951e+03,
	   3.12999976e+03 ,  3.65000073e+03  , 4.20999854e+03,   4.81000098e+03,
	   5.45000000e+03 ,  6.12999951e+03  , 6.85000000e+03,   7.61000098e+03,
	   8.40999902e+03  , 9.25000098e+03  , 1.01300000e+04,   1.10500000e+04,
	   1.20100010e+04  , 1.30100020e+04  , 1.40504004e+04,   1.51377197e+04,
	   1.62849736e+04  , 1.75069688e+04  , 1.88208203e+04,   2.02465996e+04,
	   2.18081367e+04  , 2.35421836e+04  , 2.55209609e+04,   2.79013574e+04,
	   3.10638887e+04  , 3.60817617e+04]
	b_rho= [ 0.99885815,  0.99429625,  0.98520386,  0.97164404,  0.95370984,  0.93152744,
	  0.90525305 , 0.87507457 , 0.84121162  ,0.80391401 , 0.76346451 , 0.7201758,
	  0.67439252 , 0.62649053 , 0.57687736  ,0.52599078 , 0.47430137 , 0.42230991,
	  0.37054887 , 0.31958207 , 0.27000487  ,0.22244327 , 0.17755543 , 0.13603023,
	  0.09858811 , 0.06598078 , 0.03898239  ,0.01831469 , 0.00487211 , 0.  ,        0.,
	  0.         , 0. ,         0.          ,0.         , 0.         , 0. ,         0.        ]
	if zgrid=='theta':
		a_vals=a_theta
		b_vals=b_theta
		min_vals=[0]+a_rho[1:]
		max_vals=a_rho[1:]+[42427.90234375 ]
		min_b=[1.0]+b_rho[1:]
		max_b=b_rho[1:]+[0.0]
	if zgrid=='rho':
		a_vals=a_rho
		b_vals=b_rho
		min_vals=[0]+a_theta[:-1]
		max_vals=a_theta
		min_b=[1.0]+b_theta[:-1]
		max_b=b_theta
	return a_vals,b_vals,np.column_stack((min_vals, max_vals)),np.column_stack((min_b,max_b))

#gets the ACCESS model orography from a file and returns it
def getOrog():
	orog_fName=outpath+'/CMIP5/ancillary_files/Base-09Ipj.astart-00011001_short.nc' #use this for time being
	orog_file=cdms2.open(orog_fName, 'r')
	orog_vals=np.float32(orog_file.variables['orog'][0,0,:,:])
	orog_file.close()
	return orog_vals

def areacella():
	fName=outpath+'/CMIP5/ancillary_files/Base-09Ipj.astart-00011001_short.nc' #use this for time being
	f=cdms2.open(fName, 'r')
	vals=np.float32(f.variables['areacella'][:,:])
	f.close()
	return vals

def landFrac():
	fName=outpath+'/CMIP5/ancillary_files/Base-09Ipj.astart-00011001_short.nc' #use this for time being
	f=cdms2.open(fName, 'r')
	vals=np.float32(f.variables['sftlf'][0,0,:,:]).filled(0)
	f.close()
	return vals

#list of the names of the land tiles in moses
def mosesTiles():
	return ['Broadleaf' ,'Needleleaf','C3 grass','C4 grass','Shrubs','Urban','Water','Bare ground','Ice']
#list of the names of the land tiles in cable
def cableTiles():
	return ['Evergreen_Needleleaf','Evergreen_Broadleaf','Deciduous_Needleleaf','Deciduous_Broadleaf','Shrub',\
		'C3_grass','C4_grass','Tundra','C3_crop','C4_crop', 'Wetland','','','Barren','Urban','Lakes','Ice'] 

#level values and bounds for soil depths in moses
def mosesSoilLevels():
	levels=np.array([0.05, 0.225 ,0.675, 2.000])
	boundmin=np.array([0.0,0.10, 0.350 ,1.0])
	boundmax=np.array([0.10, 0.350 ,1.0, 3.0])
	bounds=np.column_stack((boundmin,boundmax))
	return levels,bounds

#level values and bounds for soil depths in cable
def cableSoilLevels():
	levels=np.array([ 0.011 ,  0.051 ,  0.157 ,  0.4385,  1.1855,  3.164 ],dtype=np.float32)
	boundmin=np.array([0,0.022,  0.08 ,  0.234,  0.643,  1.728],dtype=np.float32)
	boundmax=np.array([ 0.022,  0.08 ,  0.234,  0.643,  1.728,  4.6  ],dtype=np.float32)
	bounds=np.column_stack((boundmin,boundmax))
	return levels,bounds

#Calculate ice_mass transport. assumes only one time value
def iceTransport(ice_thickness,snow_thickness,vel,xy):
	gridfile=outpath+'/CMIP5/ancillary_files/cice_grid_20101208.nc' #file with grids specifications
	f=cdms2.open(gridfile,'r')
	if xy=='y':
		#for y_vel use length dx
		L=np.float32(f.variables['hun'][:]/100) #grid cell length in m (from cm)
	elif xy=='x':
		#for x_vel use length dy
		L=np.float32(f.variables['hue'][:]/100) #grid cell length in m (from cm)
	else: raise Exception('need to supply value either \'x\' or \'y\' for ice Transports')
	ice_density=900 #kg/m3
	snow_density=300 #kg/m3
	f.close()
	return ((ice_density*ice_thickness+snow_density*snow_thickness)*vel*L).filled(0)

def iceFramTransport(ice_thickness,snow_thickness,velx,vely):
	#ice mass transport across fram strait
	tx_trans=iceTransport(ice_thickness,snow_thickness,velx,'x')
	ty_trans=iceTransport(ice_thickness,snow_thickness,vely,'y')
	transport=transAcrossLine(tx_trans,267,267,279,279)
	transport+=transAcrossLine(ty_trans,268,284,278,278)
	return transport

#Calculate values for mrfso
#using values in var (field8230) and soil level thicknesses for cable or moses
def calc_mrfso(var,model):
	if model=='cable':
		lev,bounds=cableSoilLevels()
	elif model=='moses':
		lev,bounds=mosesSoilLevels()
	else: raise Exception('model passed must be cable or moses for calculation of mrfso')
	thickness=bounds[:,1]-bounds[:,0]
	#compute weighted sum of var*thickness along z-axis of var
	[tn,zn,yn,xn]=np.shape(var)
	out=np.ma.zeros([tn,yn,xn],dtype=np.float32)
	#Note using density of water not ice (1000kg/m^3)
	for z in range(len(thickness)):
		out+= var[:,z,:,:]*thickness[z]*1000
	return out

#calculate weighted average using tile fractions
#sum of variable for each tile 
# multiplied by tile fraction
def tileAve(var,tileFrac):
	t,z,y,x=np.shape(var)
	vout=np.ma.zeros([t,y,x],dtype=np.float32)
	#loop over pft tiles and sum
	for i in range(z):
		vout+=var[:,i,:,:]*tileFrac[:,i,:,:]
	return vout

#temp for land or sea ice
def calc_tslsi(var):
	#total temp,open sea temp,seaIce area fraction
	ts,ts_sea,sic=var
	#land area Fraction
	A_l=landFrac()
	#land or sea ice fraction
	A_lsi=A_l+(1-A_l)*sic
	#open ocean fraction
	A_o=(1-A_l)*(1-sic)
	return (ts-ts_sea*A_o)/A_lsi

#hfbasin is output as the heat transport hfy, integrated over depth and longitude,
# calculated for each of three ocean basins
#hfy is given as the linear sum of the variables in transList
def hfbasin(transList):
	dims=list(np.shape(transList[0][:,:,0])) +[3] #remove x add dim for 3 basins
	output= np.ma.zeros(dims,dtype=np.float32)

	#grab land mask from first var (assuming the only masked values are land)
	landMask=np.array(transList[0].mask[0,:,:],dtype=bool)
	#Get basin masks
	basin=getBasinMask()

	#2 global basin
	for trans in transList:
		output[:,:,2]+=trans.sum(2)
		
	#0: atlantic arctic basin
	#atlantic and arctic basin are given by mask values 2 and 4 #TODO double check this
	atlantic_arctic_mask=np.ma.make_mask(np.logical_and(basin!=2.0,basin!=4.0))

	for trans in transList:
		for t in range(np.shape(trans)[0]):
				trans.mask[t,:,:]=np.ma.mask_or(atlantic_arctic_mask,landMask)	
		output[:,:,0]+=trans.sum(2)
	
	#1: indoPacific basin:
	#Indian and Pacific basin are given by mask values 3 and 5 #TODO double check this
	indoPac_mask=np.ma.make_mask(np.logical_and(basin!=3.0,basin!=5.0))
	for trans in transList:
		for t in range(np.shape(trans)[0]):
				trans.mask[t,:,:]=np.ma.mask_or(indoPac_mask,landMask)	
		output[:,:,1]+=trans.sum(2)
				
	return output
	
#calculates the northward meridional fluxes for each basin
#assumes that the x -coordinate has already been averaged over
def basinMeridFlux(var):
	glob,atlantic,arctic,pacific,indian=var
	dims=list(np.shape(glob[:,:,0])) +[3] #remove x, add dim for 3 basins
	output= np.ma.zeros(dims,dtype=np.float32)
	#atlantic,arctic
	output[:,:,0]=atlantic[:,:,0]+arctic[:,:,0]
	#indo-pacific
	output[:,:,1]=indian[:,:,0]+pacific[:,:,0]
	#global
	output[:,:,2]=glob[:,:,0]
	return output

def oceanFrac():
	fname=outpath+'/CMIP5/ancillary_files/grid_spec.auscom.20110618.nc' #file with grids specifications
	f=cdms2.open(fname,'r')
	return np.float32(f.variables['wet'][:,:])

def getBasinMask():
	mask_file=outpath+'/CMIP5/ancillary_files/lsmask_20110618.nc'
	return cdms2.open(mask_file,'r').variables['mask_ttcell'][0,:,:]

def calc_rsds(sw_heat,swflx):
	sw_heat[:,0,:,:]=swflx+sw_heat[:,0,:,:] #correct surface level
	return sw_heat

def maskSeaIce(var,sic):
	#return np.ma.masked_where((np.array(var[1])==0).__and__(landFrac()==0),var[0])
	return np.ma.masked_where(sic==0,var)

#take name of grid and find corresponding vertex positions from ancillary file
def get_vertices(name):
	#dictionary to map grid names to names of vertex variables
	dictionary={'geolon_t':'x_vert_T','geolat_t':'y_vert_T','geolon_c':'x_vert_C','geolat_c':'y_vert_C',\
	'TLON':'lont_bonds','TLAT':'latt_bonds','ULON':'lonu_bonds','ULAT':'latu_bonds'}
	try:
		vertexname=dictionary[name]
	except:
		raise Exception('app_funcs.get_vertices: ocean grid specification unknown, '+name)
	try: #ocean grid
		fname=outpath+'/CMIP5/ancillary_files/grid_spec.auscom.20110618.nc' 
		f=cdms2.open(fname,'r')
		vert=np.array(f.variables[vertexname][:],dtype='float32').transpose((1,2,0))
	except: #cice grid (convert from rad to degrees)
		fname=outpath+'/CMIP5/ancillary_files/cice_grid_20101208.nc'
		f=cdms2.open(fname,'r')
		vert=np.array(f.variables[vertexname][:],dtype='float32').transpose((1,2,0))*57.2957795
	#restrict longditudes to the range0-360
	return vert[:]

#first variable is dummy tsoil (on soil levels)
#second variable is tile frac
#the rest of the variables are the soil temp for one level, for each tile
def calc_tsl(var):
	vout=var[0]*0
	#loop over soil levels, calculate tile average for each.
	for i in range(6):
		vout[:,i,:,:]=tileAve(var[i+2],var[1])
	return vout

def calc_areacello(area,mask_v):
	area.mask=mask_v.mask
	return area.filled(0)

def calc_volcello(area,dht):
	return area.filled(0)

#calculate clwvi by integrating over water collumn
#assumes only one time step
def calc_clwvi(var):
	press=var[0]
	print press.shape
	out=np.ma.zeros([1]+list(press.shape[2:]),dtype=np.float32)
	for z in range(press.shape[1]-1):
		mix=np.ma.zeros(press.shape[2:],dtype=np.float32)		
		for v in var[1:]:
			mix[:,:]+=v[0,z,:,:]
		out[:,:]+=mix*(press[0,z,:]-press[0,z+1,:])
	return out*0.101972

#calculates zostga from T and pressure
def calc_zostoga(var,depth,lat):
	#extract variables
	[T,dz,areacello]=var
	[nt,nz,ny,nx]=T.shape #dimension lengths
	zostoga=np.zeros([nt],dtype=np.float32)
	#calculate pressure field
	press=np.ma.array(sw_press(depth,lat))
	press.mask=T[0,:].mask
	#do calculation for each time step
	for t in range(nt):
		tmp=((1. - rho_from_theta(T[t,:],35.00,press)/rho_from_theta(4.00,35.00,press))*dz[t,:]).sum(0)
		areacello.mask=T[0,0,:].mask
		zostoga[t]=(tmp*areacello).sum(0).sum(0)/areacello.sum()
	return zostoga
	
#calculates zostga from T and pressure
def calc_zostoga2(var,depth,lat):
	#extract variables
	[T,dz,areacello]=var
	[nt,nz,ny,nx]=T.shape #dimension lengths
	zostoga=np.zeros([nt],dtype=np.float32)
	#calculate pressure field
	press=np.ma.array(sw_press(depth,lat))
	press.mask=T[0,:].mask
	
	#initialize volcello
	volcello=dz[0,:]
	#do calculation for each time step
	for t in range(nt):
		#set volcello
		for z in range(nz):		
			volcello[z]=dz[t,z,:]*areacello[:]
		tmp=((1. - rho_from_theta(T[t,:],35.00,press)/rho_from_theta(4.00,35.00,press))*volcello).sum()
		zostoga[t]=tmp/volcello.sum()
	return zostoga
	
#calculates zossga from T,S and pressure
def calc_zossga(var,depth,lat):
	#extract variables
	[T,S,dz,areacello]=var
	[nt,nz,ny,nx]=T.shape
	zossga=np.zeros([nt],dtype=np.float32)
	#calculate pressure field
	press=np.ma.array(sw_press(depth,lat))
	press.mask=T[0,:].mask
	#do calculation for each time step
	for t in range(nt):
		tmp=((1. - rho_from_theta(T[t,:],S[t,:],press)/rho_from_theta(4.00,35.00,press))*dz[t,:]).sum(0)
		areacello.mask=T[0,0,:].mask
		zossga[t]=(tmp*areacello).sum(0).sum(0)/areacello.sum()
	return zossga

#function to calculate density from temp, salinity and pressure
def rho_from_theta(th,s,p):
	th2 = th*th
	sqrts = np.ma.sqrt(s)
	anum =          9.9984085444849347e+02 +    \
		       th*( 7.3471625860981584e+00 +    \
		       th*(-5.3211231792841769e-02 +    \
		       th*  3.6492439109814549e-04)) +  \
		        s*( 2.5880571023991390e+00 -    \
		       th*  6.7168282786692355e-03 +    \
		        s*  1.9203202055760151e-03)
	aden =          1.0000000000000000e+00 +    \
		       th*( 7.2815210113327091e-03 +    \
		       th*(-4.4787265461983921e-05 +    \
		       th*( 3.3851002965802430e-07 +    \
		       th*  1.3651202389758572e-10))) + \
		        s*( 1.7632126669040377e-03 -    \
		       th*( 8.8066583251206474e-06 +    \
		      th2*  1.8832689434804897e-10) +   \
		    sqrts*( 5.7463776745432097e-06 +    \
		      th2*  1.4716275472242334e-09))
	pmask=(p!=0.0)
	pth = p*th
	anum = anum +   pmask*(     p*( 1.1798263740430364e-02 +   \
	                   th2*  9.8920219266399117e-08 +   \
	                     s*  4.6996642771754730e-06 -   \
	                     p*( 2.5862187075154352e-08 +   \
	                   th2*  3.2921414007960662e-12)) )
	aden = aden +   pmask*(     p*( 6.7103246285651894e-06 -   \
	              pth*(th2*  2.4461698007024582e-17 +   \
	                     p*  9.1534417604289062e-18)) )
#	print 'rho',np.min(anum/aden),np.max(anum/aden)
	return anum/aden

#deprecated funtion, do not use. Use rho_from_theta instead
def rf_eos(S,T,P):
	t1 = [ 9.99843699e+2, 7.35212840e+0, -5.45928211e-2, 3.98476704e-4 ]
	s1 = [ 2.96938239e+0, -7.23268813e-3, 2.12382341e-3 ]
	p1 = [ 1.04004591e-2, 1.03970529e-7, 5.18761880e-6, -3.24041825e-8, -1.23869360e-11 ]

	t2 = [ 1.0, 7.28606739e-3, -4.60835542e-5, 3.68390573e-7, 1.80809186e-10 ]
	s2 = [ 2.14691708e-3, -9.27062484e-6, -1.78343643e-10, 4.76534122e-6, 1.63410736e-9 ]
	p2 = [ 5.30848875e-6, -3.03175128e-16, -1.27934137e-17 ]

	Pn = t1[0] + t1[1]*T + t1[2]*T**2 + t1[3]*T**3 + s1[0]*S + s1[1]*S*T + s1[2]*S**2 \
	  + p1[0]*P + p1[1]*P*T**2 + p1[2]*P*S + p1[3]*P**2 + p1[4]*P**2*T**2

	Pd = t2[0] + t2[1]*T + t2[2]*T**2 + t2[3]*T**3 + t2[4]*T**4 \
	  + s2[0]*S + s2[1]*S*T + s2[2]*S*T**3 + s2[3]*np.sqrt(S**3) + s2[4]*np.sqrt(S**3)*T**2 \
	  + p2[0]*P + p2[1]*P**2*T**3 + p2[2]*P**3*T
	return Pn/Pd

#Calculates the pressure field from depth and latitude
def sw_press(dpth,lat):
#return array on depth,lat,lon	
	pi = 4*np.arctan(1.)
	deg2rad = pi/180
	x = np.sin(abs(lat[:])*deg2rad)  # convert to radians
	c1 = 5.92e-3+x**2*5.25e-3
	#expand arrays into 3 dimensions
        print('dpth.shape=',dpth.shape)
	nd,=dpth.shape
	nlat,nlon=lat.shape
	dpth=np.expand_dims(np.expand_dims(dpth[:],1),2)
        print('dpth.shape=',dpth.shape)
	dpth=np.tile(dpth,(1,nlat,nlon))
        print('dpth.shape=',dpth.shape)
	c1=np.expand_dims(c1,0)
	c1=np.tile(c1,(nd,1,1))
	return ((1-c1)-np.sqrt(((1-c1)**2)-(8.84e-6*dpth)))/4.42e-6
	
#calculates an average over southern or northern hemisphere
#assumes 4D (3D+ time) variable
#def hemi_ga(var,vol,southern):
#	dims=var.shape
#	mid=150
#	if southern:
#		total_vol=vol[:,:mid,:],.sum()
#		v_ga=v[:,:mid,:]*vol[:,:mid,:]).sum()/total_vol
#	else:
#		total_vol=vol[:,mid:,:],.sum()
#		v_ga=v[:,mid:,:]*vol[:,mid:,:]).sum()/total_vol
#	return v_ga
		
		

def getSource(model):
	if model=='ACCESS1-0'or model=='ACCESS1.0':
		return 'ACCESS1-0 2011. '+\
		'Atmosphere: AGCM v1.0 (N96 grid-point, 1.875 degrees EW x approx 1.25 degree NS, 38 levels); '+\
		'ocean: NOAA/GFDL MOM4p1 (nominal 1.0 degree EW x 1.0 degrees NS, tripolar north of 65N, '+\
		 'equatorial refinement to 1/3 degree from 10S to 10 N, cosine dependent NS south of 25S, 50 levels); '+\
		'sea ice: CICE4.1 (nominal 1.0 degree EW x 1.0 degrees NS, tripolar north of 65N, '+\
		'equatorial refinement to 1/3 degree from 10S to 10 N, cosine dependent NS south of 25S); '+\
		'land: MOSES2 (1.875 degree EW x 1.25 degree NS, 4 levels'
	elif model=='ACCESS1.3'or model=='ACCESS1-3':
		return 'ACCESS1.3 2011. '+\
		'Atmosphere: AGCM v1.0 (N96 grid-point, 1.875 degrees EW x approx 1.25 degree NS, 38 levels); '+\
		'ocean: NOAA/GFDL MOM4p1 (nominal 1.0 degree EW x 1.0 degrees NS, tripolar north of 65N, '+\
		 'equatorial refinement to 1/3 degree from 10S to 10 N, cosine dependent NS south of 25S, 50 levels); '+\
		'sea ice: CICE4.1 (nominal 1.0 degree EW x 1.0 degrees NS, tripolar north of 65N, '+\
		'equatorial refinement to 1/3 degree from 10S to 10 N, cosine dependent NS south of 25S); '+\
		'land: CABLE1.0 (1.875 degree EW x 1.25 degree NS, 6 levels'
	else: return model +': unknown source'


