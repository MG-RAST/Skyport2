#/bin/bash


if [[ $_ == $0 ]]; then 
  echo "Error: please use command \"source ./get_ip_address.sh\""
  exit 1
fi

if [ ! -z ${SKYPORT_HOST} ] ; then
  echo "SKYPORT_HOST already configured: SKYPORT_HOST=${SKYPORT_HOST}"
  return 0
fi




MY_IP=$(for i in $(ifconfig -a | cut -d ' ' -f 1 | cut -d $'\t' -f 1 | grep -Ev "^$" | grep -v "^veth\|^lo\|^docker\|^br" | cut -d : -f 1) ; do ifconfig $i ; done | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p')  

COUNT=$(echo ${MYIP} | wc -l )
if [ ${COUNT} -eq 0 ] ; then
  echo "no ip address found"
  return 1
fi 

if [ ${COUNT} -gt 1 ] ; then
  echo ""
  echo ${MYIP}
  echo ""
  echo "Auto-detection of IP address failed: More than one IP address found. Please specify one manually: export SKYPORT_HOST=<your IP address>"
  return 1
fi 

export SKYPORT_HOST=${MY_IP}
echo "SKYPORT_HOST=${SKYPORT_HOST}"



