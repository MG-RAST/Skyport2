#! /bin/bash

############################
# set environment variables for the Skyport2 client
############################



if [[ $_ == $0 ]]; then 
  echo "Error: please use command \"source ./init-client.sh\""
  exit 1
fi
  

# setting this to this machines local IP address; for production use, set this to the IP address of your SKYPORT server
export SKYPORT_HOST=$(/sbin/ip -o -4 addr list eth0 | awk '{print $4}' | cut -d/ -f1)`

export SKYPORT_TMPDIR=`pwd`/tmp
mkdir -p ${SKYPORT_TMPDIR}


