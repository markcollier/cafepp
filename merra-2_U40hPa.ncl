begin

if(fileexists("newdata_U40hPa.nc"))then
  system("rm newdata_U40hPa.nc")
end if

ifh=addfile("data_U40hPa.nc","r")
ofh=addfile("newdata_U40hPa.nc","c")

U40hPa=ifh->U40hPa
time=ifh->time
lat=ifh->lat
lon=ifh->lon

printVarSummary(U40hPa)

neof = 3

wgt = sqrt(cos(lat*0.01745329)) 

U40hPaW = U40hPa*conform(U40hPa, wgt, 1)

optEof = True
eof    = eofunc_n_Wrap(U40hPaW, neof, optEof, 0)
eof_ts = eofunc_ts_n_Wrap(U40hPaW, eof, False, 0)

printVarSummary(eof)
printVarSummary(eof_ts)

eof!0="eof number"
eof!1="lat"
eof!2="lon"

eof&lat=lat
eof&lon=lon

eof_ts!0="eof number"
eof_ts!1="time"

eof_ts&time=time

ofh->eof=eof
ofh->eof_ts=eof_ts

end
