#!/bin/sh
#
# subset_2d_cdo.sh
#
#
# Scripts implementing this test should subset a dataset to a given
# bounding box.  Scripts can assume the given variable is a 2D field.
#
#  usage: %prog dataset variable bbox outputfile
#
# where bbox = 'lon0,lon1,lat0,lat1'

TEMP1=subset_2d_tmp

dataset=$1
variable=$2
bbox=$3
outfile=$4

# Extract bbox over all variables then split on variable
cdo sellonlatbox,$bbox $dataset $TEMP1.nc
cdo selname,$variable $TEMP1.nc $outfile

rm $TEMP1.nc