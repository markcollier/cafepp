begin

statistic=(/1,2,3,4/)
nstatistic=dimsizes(statistic)

if(fileexists("newdata_hadisst_nino.nc"))then
  system("rm newdata_hadisst_nino.nc")
end if

ifh=addfile("data_hadisst_nino.nc","r")
ofh=addfile("newdata_hadisst_nino.nc","c")

data=ifh->data
time=ifh->time

;printVarSummary(data)
;print(data)

indice=ifh->indice
nindice=dimsizes(indice)
print(indice)
print(indice@indice_label)

;exit

d=0; remove mean
sm=3 ;21, 7 good (must be odd)
pct=0.10 ; percent taper, 0.10

do n=0,nindice-1
print("n="+n)

nn=n
  sdof = specx_anal(data(:,nn),d,sm,pct)
  splt = specx_ci(sdof, 0.05, 0.95)

  printVarSummary(sdof)
  printVarSummary(splt)

  splt_shape=dimsizes(splt)
  print(splt_shape)

  if(nn.eq.0)then
    frequency=sdof@frq
    newdata=new((/splt_shape(1),nindice,splt_shape(0)/),float) ; 4 data, 5%, 95%, red noise
  end if

  newdata(:,n,:)=transpose(splt)
end do

frequency!0="frequency"
newdata!0="frequency"
newdata!1="indice"
newdata!2="statistic"

newdata&frequency=frequency
newdata&indice=indice
newdata&statistic=statistic

ofh->newdata=newdata

end
