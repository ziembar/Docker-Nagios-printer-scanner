#!/bin/bash
python3 /home/snmp_discover.py --silent
./etc/rc.d/init.d/nagios reload
exit 0