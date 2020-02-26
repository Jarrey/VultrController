#!/bin/sh
# $1: ip or hostname
# $2: api key of Vultr service

ping -c1 $1 > /dev/null
if [ $? -eq 0 ]
  then
    echo Server is Okay
    exit 0
  else
    echo Server is unavailable
    ./VultrCtl.py -k $2 -a r -d -r sy
fi
