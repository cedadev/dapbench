#!/bin/sh

cd `dirname $0`
LIBDIR=$PWD/../lib
CLASSPATH=`ls $LIBDIR/*.jar | tr '\n' ':'`
JAVA_OPTS=$@

java -cp $CLASSPATH $JAVA_OPTS net.grinder.Console