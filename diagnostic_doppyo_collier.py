def potential_temperature(p, t, lat_name=None, lon_name=None):
  """
      Returns the potential temperature
      Author: Mark Collier
      Date: 26/11/2018
      
      Parameters
      ----------
      p : pressure level
      
      t : xarray DataArray
          Array containing fields of temperature (Kelvin) with at least coordinates latitude, longitude and
          level (following standard naming - see Limitations)

      Returns
      -------
      potential_temperature : xarray DataArray
        Array containing potential temperature (Kelvin)
        
      Examples
      --------
      
      temperature = xr.DataArray(np.random.normal(size=(6,4)), \
        coords=[('lat', np.arange(-75,76,30)), ('lon', np.arange(45,316,90))])

      potential_temperature = potential_temperature(300, temperature)

      Limitations
      -----------

      All input array coordinates must follow standard naming (see doppyo.utils.get_lat_name(), 
      doppyo.utils.get_lon_name(), etc)
        
      To Do
      -----
      
  """

  p0 = 1000
  pt = pow(t * (p0 /p ), 0.286)
  pt.attrs['units'] = 'kelvin'
  pt.attrs['long_name'] = 'Potential temperature'
  return pt

def Phillips_criterion(u300, u700, pt300, pt700, lat_name=None, lon_name=None):
  """
      Returns the Phillips criterion
      Author: Mark Collier
      Date: 26/11/2018
      
      Parameters
      ----------
      u300 : xarray DataArray
          Array containing fields of zonal velocity @300hPa with at least coordinates latitude, longitude and
          level (following standard naming - see Limitations)

      u700 : xarray DataArray
          Array containing fields of zonal velocity @700hPa with at least coordinates latitude, longitude and
          level (following standard naming - see Limitations)
          
      pt300 : xarray DataArray
          Array containing fields of potential temperature @300hPa (Kelvin) with at least coordinates latitude, longitude and
          level (following standard naming - see Limitations)

      pt700 : xarray DataArray
          Array containing fields of potential temperature @700hPa (Kelvin) with at least coordinates latitude, longitude and
          level (following standard naming - see Limitations)

      Returns
      -------
      Pcr : xarray DataArray
        Array containing the Phillips Criterion (m/s). Normally look at values >=0, ill defined near equator.
        
      Examples
      --------
      
      u = xr.DataArray(np.random.normal(size=(24,5,6,4)), \
        coords=[('time', pd.date_range('2000-01-01',periods=24,freq='M')), \
                ('level', [100,300,700,900,1000]), \
                ('lat', np.arange(-75,76,30)), \
                ('lon', np.arange(45,316,90)), \
                ])

      t = xr.DataArray(np.random.normal(size=(24,5,6,4))+273.15, \
        coords=[('time', pd.date_range('2000-01-01',periods=24,freq='M')), \
                ('level', [100,300,700,900,1000]), \
                ('lat', np.arange(-75,76,30)), \
                ('lon', np.arange(45,316,90)), \
                ])

      Pcr = Phillips_criterion(u.sel(level=300), u.sel(level=700), potential_temperature(300, t.sel(level=300)), potential_temperature(700, t.sel(level=700)))

      Limitations
      -----------

      All input array coordinates must follow standard naming (see doppyo.utils.get_lat_name(), 
      doppyo.utils.get_lon_name(), etc)

      see pages 88+: https://books.google.com.au/books?id=WweaWERxDGMC&pg=PA92&lpg=PA92&dq=Phillips+criterion&source=bl&ots=IVdKSChaNQ&sig=LdAHb6PhWJEau1qYYeQiXgm7BG4&hl=en&sa=X&ved=2ahUKEwi44bSCuPHeAhUBfCsKHYdpDwI4ChDoATADegQIBhAB#v=onepage&q=Phillips%20criterion&f=false
      
      To Do
      -----
      
  """
  degtorad = utils.constants().pi / 180
  
  if lat_name is None:
    lat_name = utils.get_lat_name(u300)
  if lon_name is None:
    lon_name = utils.get_lon_name(u300)

  bk = 0.124 #dimensionless constant
  Cp = 1004 #J deg-1 kg-1
  sigma_bar = 1/(2*(pt300 - pt700)) #pt in C or K.
  earth_radius = 6.371e6 #m utils.constants().R_earth
  gamma = 7.292e-5 #rad s-1
  
  # critical_vertical_wind_shear_for_instability:
  critical = \
    ((bk * Cp * sigma_bar) / (earth_radius * gamma)) * \
    ((xr.ufuncs.cos(u300[lat_name] * degtorad))) / xr.ufuncs.square(xr.ufuncs.sin(u300[lat_name] * degtorad)) \

  Pcr = u300 - u700 - critical #defined for values >= 0.0
  
  Pcr.attrs['units'] = 'm s^-1'
  Pcr.attrs['long_name'] = 'Philips criterion'
  return Pcr
