module use ~access/modules

module rm python/2.6.6
module rm python/2.6.6-matplotlib

#module rm python/2.7.3
#module rm python/2.7.3-matplotlib

#module rm python/2.7.6
#module rm python/2.7.6-matplotlib

module add python/2.7.6
module add python/2.7.6-matplotlib
module load pythonlib/netCDF4
module load pythonlib/windspharm
module load pythonlib/pyspharm  
module load pythonlib/cartopy

module load pythonlib/cdat-lite/6.0rc2-fixed
module load pythonlib/ScientificPython/2.8

module add cdo

# added by Anaconda2 4.3.0 installer
#export PATH="/g/data/v14/mac599/anaconda2/bin:$PATH"

#PYTHONPATH=/home/599/mac599/decadal/seawater-3.3:$PYTHONPATH:/home/599/mac599/decadal/eofs

export PYTHONPATH=/home/599/mac599/decadal/xarray/lib/python2.7/site-packages:/home/599/mac599/decadal/cdo/lib/python2.7/site-packages:/home/599/mac599/decadal/esmf/lib/python2.7/site-packages:/home/599/mac599/decadal/XlsxWriter/lib/python2.7/site-packages:/home/599/mac599/decadal/dreqPy/lib/python2.7/site-packages:/home/599/mac599/CMIP5/analysis/leon2014/mmNmods/scripts/2014/AEROSOL/TRADE/APP1-0:/home/599/mac599/decadal/cmor/lib/python2.7/site-packages:/home/599/mac599/decadal/eofs/python/2.7.6/lib/python2.7/site-packages/lib/python2.7/site-packages:/home/599/mac599/decadal/seawater-3.3:$PYTHONPATH

export LD_LIBRARY_PATH=/home/599/mac599/decadal/cmor/lib:$LD_LIBRARY_PATH
export APP_OUTPATH=/g/data/p66/mac599
export CDAT_LOCATION=. #set to a dummy location for now (otherwise APP gives message).
