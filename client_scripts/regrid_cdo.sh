#!/bin/sh
# regrid_cdo.sh
#
#
# Scripts implementing this test should do simple bilinear interpolation
# regridding on the dataset.  Scripts can assume the dataset contains
# a single variable.
#
#  usage: %prog dataset lons lats outfile
#
# where lons and lats are integers representing number of grid points

dataset=$1
lons=$2
lats=$3
outfile=$4

grid=r${lons}x${lats}

cdo remapbil,$grid $dataset $outfile