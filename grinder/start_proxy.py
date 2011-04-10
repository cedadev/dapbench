#!/bin/sh
#
# Start grinder's TCPProxy in a mode suitable for capturing
# OPeNDAP requests.  This script uses TimestampedEchoFilter to
# add timestamps to TCPProxy's basic request filters.  See
# grinder/src/TimestampedEchoFilter.
#

cd `dirname $0`
LIBDIR=$PWD/lib
CLASSPATH=`ls $LIBDIR/*.jar | tr '\n' ':'`

# Add src directory for TimestampedEchoFilter
CLASSPATH=$CLASSPATH:$PWD/src

JAVA_OPTS=

# Invoke with required filters and pass on any further arguments.
java -cp $CLASSPATH $JAVA_OPTS net.grinder.TCPProxy \
    -requestfilter TimestampedEchofilter \
    -responsefilter net.grinder.tools.tcpproxy.NullFilter \
    $@