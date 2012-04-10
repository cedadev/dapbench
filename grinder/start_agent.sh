#!/bin/sh
#
# usage: ./start_agent.sh $GRINDERPROPERTIES $JAVA_OPT1 $JAVA_OPT2 ...
cd `dirname $0`
LIBDIR=$PWD/../lib
CLASSPATH=`ls $LIBDIR/*.jar | tr '\n' ':'`

GRINDERPROPERTIES=$1 ; shift
JAVA_OPTS=$@

java -cp $CLASSPATH $JAVA_OPTS net.grinder.Grinder $GRINDERPROPERTIES