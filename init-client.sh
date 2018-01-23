#! /bin/bash

############################
# set environment variables for the Skyport2 client
############################


if [[ $_ == $0 ]]; then 
  echo "Error: please use command \"source ./init-client.sh\""
  exit 1
fi
  
OS=`uname -s`

# setting this to this machines local IP address; for production use, set this to the IP address of your SKYPORT server
# 
if [ ${OS} == "Darwin" ]
then
  MYIP=$(ifconfig | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p')
else
  # draft of a smarter ip detection method:
  # for i in $(ifconfig -a | cut -d ' ' -f 1 | grep -Ev "^$" | grep -v "^veth\|^lo\|^docker\|^br" | cut -d : -f 1) ; do ifconfig $i ; done | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p'
  MYIP=$(/sbin/ip -o -4 addr list eth0 | awk '{print $4}' | cut -d/ -f1)
fi


export SKYPORT_HOST=${MYIP}

export SKYPORT_TMPDIR=`pwd`/tmp
mkdir -p ${SKYPORT_TMPDIR}


# now set some variables for the building blocks

export AWE_SERVER=http://${SKYPORT_HOST}:8001/awe/api/
export SHOCK_SERVER=http://${SKYPORT_HOST}:8001/shock/api/


