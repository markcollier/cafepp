begin

plot=True
plot=False

nfrq=232

if(fileexists("newdata.nc"))then
  system("rm newdata.nc")
end if

ifh=addfile("data.nc","r")
ofh=addfile("newdata.nc","c")

data=ifh->data
lev=ifh->lev
time=ifh->time

;printVarSummary(data)
;print(data)

newdata=new((/nfrq,dimsizes(lev),4/),float)

frq=new((nfrq),float)

;exit

d=0; remove mean
sm=7 ;21, 7 good (must be odd)
pct=0.10 ; percent taper, 0.10

do l=0,41
print("l="+l)

ll=l
;ll=41-l

  sdof = specx_anal(data(0:464,ll),d,sm,pct)
  splt = specx_ci(sdof, 0.05, 0.95)

;  printVarSummary(sdof)
;  printVarSummary(splt)

if(l.eq.0)then
  frq=sdof@frq
end if

newdata(:,l,:)=transpose(splt)

;exit

if(plot)then
  wks = gsn_open_wks("x11","spec")
  plot = new(2,graphic)

  r=True
  r@tiMainString = "U"+lev(ll)
  r@tiXAxisString = "Frequency (cyles/month)"
  r@tiYAxisString = "Variance"

  ;r@xyLineColors = (/"foreground","green","blue","red"/)
  r@xyLineColors = (/"black","green","blue","red"/)

  plot(1) = gsn_csm_xy(wks,sdof@frq, splt, r)
  exit
end if

end do

frq!0="frequency"
newdata!0="frequency"
newdata!1="lev"
newdata!2="statistic"
lev!0="lev"

ofh->newdata=newdata
ofh->frq=frq
ofh->lev=lev

end
