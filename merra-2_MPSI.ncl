begin

if(fileexists("newdata_mpsi.nc"))then
  system("rm newdata_mpsi.nc")
end if

ifh=addfile("data_mpsi.nc","r")
ofh=addfile("newdata_mpsi.nc","c")

data_eastward_V=ifh->data_eastward_V
data_westward_V=ifh->data_westward_V
data_both_V=ifh->data_both_V
data_eastward_PS=ifh->data_eastward_PS
data_westward_PS=ifh->data_westward_PS
data_both_PS=ifh->data_both_PS

lev=ifh->lev
lat=ifh->lat
lon=ifh->lon

eastward_mpsi=zonal_mpsi(data_eastward_V, lat, lev*100, data_westward_PS)
westward_mpsi=zonal_mpsi(data_westward_V, lat, lev*100, data_westward_PS)
both_mpsi=zonal_mpsi(data_both_V, lat, lev*100, data_both_PS)

printVarSummary(eastward_mpsi)

eastward_mpsi!0="lev"
eastward_mpsi!1="lat"
eastward_mpsi&lev = lev
eastward_mpsi&lat = lat

westward_mpsi!0="lev"
westward_mpsi!1="lat"
westward_mpsi&lev = lev
westward_mpsi&lat = lat

both_mpsi!0="lev"
both_mpsi!1="lat"
both_mpsi&lev = lev
both_mpsi&lat = lat

ofh->eastward_mpsi=eastward_mpsi
ofh->westward_mpsi=westward_mpsi
ofh->both_mpsi=both_mpsi

end
