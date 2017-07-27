#!/bin/bash
##!/bin/csh
#PBS -P r67
##PBS -q normal
#PBS -q express
##PBS -q copyq 
##PBS -l walltime=10:00:00
##PBS -l walltime=00:05:00
##PBS -l walltime=01:00:00
##PBS -l walltime=03:00:00
##PBS -l walltime=00:20:00
#PBS -l walltime=24:00:00
##PBS -l mem=1800MB
##PBS -l mem=30000MB
#PBS -l mem=7000MB
##PBS -l mem=10000MB
##PBS -l mem=15000MB
#PBS -l ncpus=1
#PBS -M mark.collier@csiro.au
#PBS -N analysis
##PBS -wd

cd /home/599/mac599/decadal

echo "hello"

#module rm ncl
#module add ncl/6.4.0
#ncl ~/decadal/plot_wwv_panel.ncl
#ncl ~/decadal/plot_wwv_clim.ncl
#ncl ~/decadal/plot_iso_ts.ncl
#ncl ~/decadal/plot_eof_iso20.ncl
#ncl ~/decadal/plot_sst_1sd_enso.ncl
#ncl ~/decadal/plot_subT_xy.ncl

. ./setup.bash
#./diag_spinup_monthly.bash
#./diag_forecast_daily.bash
#./diag_spinup_monthly_vN.bash 
#./cafepp.bash
#./enso_pred.bash 
#./isoN_obs.py 
./cafepp_daily.bash

echo "there"

exit
