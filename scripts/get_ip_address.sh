#/bin/bash


# this script trys to detect the IP address under Linux and OSX


if [[ $_ == $0 ]]; then 
  echo "Error: please use command \"source ./get_ip_address.sh\""
  exit 1
fi

if [ ! -z ${USE_SKYPORT_HOST} ] ; then
  SKYPORT_HOST=${USE_SKYPORT_HOST}
  echo "Variable USE_SKYPORT_HOST has been set."
  echo "SKYPORT_HOST=${SKYPORT_HOST}"
  return 0
fi




MY_IP=$(for i in $(ifconfig -a | cut -d ' ' -f 1 | cut -d $'\t' -f 1 | grep -Ev "^$" | grep -v "^veth\|^lo\|^docker\|^br" | cut -d : -f 1) ; do ifconfig $i ; done | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p')  

echo "MY_IP: ${MY_IP}"


COUNT=$(echo "${MY_IP}" | wc -l | tr -d ' ')

echo "COUNT: ${COUNT}"

if [ ${COUNT} -gt 1 ] || [ ${COUNT} -eq 0 ] ; then
  echo ""
  echo "detected: ${MY_IP}"
  echo ""
  echo "Auto-detection of IP address failed: Please specify one manually:"
  echo "> export USE_SKYPORT_HOST=<your IP address>"
  echo "Then execute \"source ./init.sh\""
  return 1
fi 

export SKYPORT_HOST=${MY_IP}
echo "SKYPORT_HOST=${SKYPORT_HOST}"



