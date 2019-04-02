#!/bin/bash

# with commando "clean" all containers with name prefix skyport2_ will be killed

if [ "${1}x" == "cleanx" ] ; then
  docker rm -f $(docker ps -a -f name=skyport2_ -q)
  sleep 2
fi

set -x
set -e


./init.sh
exec docker-compose up