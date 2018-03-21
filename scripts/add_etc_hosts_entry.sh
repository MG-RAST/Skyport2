#!/bin/bash


if [ $(cat /etc/hosts | grep "skyport" | wc -l) -eq 0 ] ; then
  echo "127.0.0.1	skyport" >> /etc/hosts 
fi
