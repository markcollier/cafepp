#!/bin/bash
##!/bin/csh
#PBS -P v14
##PBS -q normal
#PBS -q express
##PBS -q copyq 
##PBS -l walltime=10:00:00
##PBS -l walltime=00:05:00
##PBS -l walltime=01:00:00
#PBS -l walltime=03:00:00
##PBS -l walltime=00:20:00
##PBS -l walltime=24:00:00
##PBS -l mem=1800MB
##PBS -l mem=30000MB
##PBS -l mem=7000MB
##PBS -l mem=10000MB
#PBS -l mem=15000MB
##PBS -l mem=25000MB
#PBS -l ncpus=1
#PBS -M mark.collier@csiro.au
#PBS -N analysis
##PBS -wd

cd /home/599/mac599/decadal/paper_analysis

cd RUNDIR

echo "hello"

#module rm ncl
#module add ncl/6.4.0
#ncl ~/decadal/plot_wwv_panel.ncl
#ncl ~/decadal/plot_wwv_clim.ncl
#ncl ~/decadal/plot_iso_ts.ncl
#ncl ~/decadal/plot_eof_iso20.ncl
#ncl ~/decadal/plot_sst_1sd_enso.ncl
#ncl ~/decadal/plot_subT_xy.ncl
#ncl ~/decadal/paper_analysis/plot_enso.ncl
#ncl ~/decadal/paper_analysis/plot_hov.ncl

#conda activate cafepp_36_cmds

. /short/v14/mac599/anaconda3/etc/profile.d/conda.sh
conda activate cafepp_27_scipy

#. SRCDIR/setup.bash
#. ../setup.bash
#./cafepp_mothly_assimilation.bash
#./cafepp_daily_assimilation.bash
#./cafepp_mothly_forecast.bash
#./cafepp_daily_forecast.bash
#./cafepp_daily_assimilation.bash
#./cafepp_daily_forecast_month.bash
#./cafepp_daily_control.bash
#./cafepp_daily_enkf.bash
#./cafepp_daily_assimilation_year_month.bash

./cafepp_daily_assimilation_year_month.py RUNDIR

echo "there"

exit
