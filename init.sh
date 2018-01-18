#! /bin/bash

############################
# set environment variables
############################

# Top level data dir
export DATADIR=`pwd`/data
mkdir -p $DATADIR

export SKYPORT_TMPDIR=$DATADIR/tmp
mkdir -p ${SKYPORT_TMPDIR}


# Path to shock data and log dir
export SHOCKDIR=${DATADIR}/shock/
mkdir -p ${SHOCKDIR}/data
mkdir -p ${SHOCKDIR}/log

# Path to AWE
export AWEDIR=${DATADIR}/awe
mkdir -p ${DATADIR}/awe
mkdir -p ${DATADIR}/awe/db
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



DOCKER_VERSION=$(docker --version | grep -o "[0-9]*\.[0-9]*\.[0-9a-z\.-]*")
export DOCKER_BINARY=${DATADIR}/docker-${DOCKER_VERSION}


if [ ! -e ${DOCKER_BINARY} ] ; then
  curl -fsSL -o ${SKYPORT_TMPDIR}/docker-${DOCKER_VERSION}.tgz https://download.docker.com/linux/static/stable/x86_64/docker-${DOCKER_VERSION}.tgz 
  if [ ! -e ${SKYPORT_TMPDIR}/docker-${DOCKER_VERSION}.tgz ] ; then
    echo "download.docker.com did not work, try old location get.docker.com..."
    curl -fsSL -o ${SKYPORT_TMPDIR}/docker-${DOCKER_VERSION}.tgz  https://get.docker.com/builds/Linux/x86_64/docker-${DOCKER_VERSION}.tgz
  fi
  
  if [ ! -e ${SKYPORT_TMPDIR}/docker-${DOCKER_VERSION}.tgz ] ; then
    echo "docker binary not found"
    exit 1
  fi
  
  tar -xvzf ${SKYPORT_TMPDIR}/docker-${DOCKER_VERSION}.tgz -C ${SKYPORT_TMPDIR} docker/docker 
  mv ${SKYPORT_TMPDIR}/docker/docker ${DATADIR}/docker-${DOCKER_VERSION}
  
  
fi


echo Set config to:
echo TAG=$TAG 
echo CONFIGDIR=$CONFIGDIR
echo SHOCKDIR=${SHOCKDIR}
echo DATADIR=${DATADIR}
echo LOGDIR=${LOGDIR}
echo "DOCKER_VERSION=${DOCKER_VERSION}"