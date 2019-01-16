begin

if(fileexists("newdata_Uzon.nc"))then
  system("rm newdata_Uzon.nc")
end if

ifh=addfile("data_Uzon.nc","r")
ofh=addfile("newdata_Uzon.nc","c")

Uzon=ifh->Uzon
time=ifh->time
lat=ifh->lat
lev=ifh->lev

printVarSummary(Uzon)

neof = 6

wgt = sqrt(cos(lat*0.01745329)) 

UzonW = Uzon*conform(Uzon, wgt, 2)

;printVarSummary(UzonW)

;exit

optEof = True
eof    = eofunc_n_Wrap(UzonW, neof, optEof, 0)
eof_ts = eofunc_ts_n_Wrap(UzonW, eof, False, 0)

printVarSummary(eof)
printVarSummary(eof_ts)

eof!0="eof number"
eof!1="lev"
eof!2="lat"

eof&lev=lev
eof&lat=lat

eof_ts!0="eof number"
eof_ts!1="time"

eof_ts&time=time

ofh->eof=eof
ofh->eof_ts=eof_ts

end
