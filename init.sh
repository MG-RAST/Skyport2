#! /bin/bash

############################
# set environment variables
############################

# Top level data dir
export DATADIR=`pwd`/data
mkdir -p $DATADIR

# Path to shock data and log dir
export SHOCKDIR=${DATADIR}/shock/
mkdir -p ${SHOCKDIR}/data
mkdir -p ${SHOCKDIR}/log

# Path to AWE
export AWEDIR=${DATADIR}/awe
mkdir -p ${DATADIR}/awe
mkdir -p ${DATADIR}/awe-worker/work


# Path to primary log dir
export LOGDIR=`pwd`/data/log/

# Create log dirs for Shock , nginx
mkdir -p ${LOGDIR}
mkdir -p ${LOGDIR}/shock
mkdir -p ${LOGDIR}/nginx
mkdir -p ${LOGDIR}/awe
mkdir -p ${LOGDIR}/awe-worker

# Path to config dir with service specific subdirs. Contains config for demo case
export CONFIGDIR=`pwd`/Config/

# Docker image tag , used by Dockerfiles and Compose file 
export TAG=demo

echo Set config to:
echo TAG=$TAG 
echo CONFIGDIR=$CONFIGDIR
echo SHOCKDIR=${SHOCKDIR}
echo DATADIR=${DATADIR}
echo LOGDIR=${LOGDIR}