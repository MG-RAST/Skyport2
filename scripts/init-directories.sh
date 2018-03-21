#! /bin/bash

if [[ $_ == $0 ]]; then
  echo "Error: this script has to be sourced"
  exit 1
fi



# Top level data dir
export DATADIR=${REPO_DIR}/live-data
mkdir -p $DATADIR

# Path to config dir with service specific subdirs. Contains config for demo case
export CONFIGDIR=${REPO_DIR}/Config/
export DOCSDIR=${REPO_DIR}/Documents/
export CWL_DIR=${REPO_DIR}/CWL


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
export LOGDIR=${DATADIR}/log/

# Create log dirs for Shock , nginx
mkdir -p ${LOGDIR}
mkdir -p ${LOGDIR}/shock
mkdir -p ${LOGDIR}/nginx
mkdir -p ${LOGDIR}/awe
mkdir -p ${LOGDIR}/awe-worker


