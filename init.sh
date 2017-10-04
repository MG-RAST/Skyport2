#! /bin/bash

############################
# set environment variables
############################

# Path to shock data and log dir
export SHOCKDIR=`pwd`/data/shock/

# Create shock dirs
mkdir -p ${SHOCKDIR}/data
mkdir -p ${SHOCKDIR}/log


# Path to config dir with service specific subdirs. Contains config for demo case
export CONFIGDIR=`pwd`/Config/

# Docker image tag , used by Dockerfiles and Compose file 
export TAG=demo

echo Set config to:
echo TAG=$TAG 
echo CONFIGDIR=$CONFIGDIR
echo SHOCKDIR=${SHOCKDIR}