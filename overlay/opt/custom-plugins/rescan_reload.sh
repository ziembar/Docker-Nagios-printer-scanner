#!/bin/bash
exit_code=$?
python3 /home/snmp_discover.py --silent
./etc/rc.d/init.d/nagios reload
exit exit_code