#!/bin/bash
#PBS -P v14
#PBS -q express
##PBS -l walltime=24:00:00
##PBS -l walltime=00:10:00
#PBS -l mem=15000MB
#PBS -l ncpus=1
#PBS -M mark.collier@csiro.au
#PBS -N analysis

cd RUNDIR

echo "hello"

CONDA_SOURCE

CONDA_ACTIVATE

CAFEPP_SCRIPT

echo "there"

exit
