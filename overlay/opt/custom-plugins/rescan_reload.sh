#!/bin/bash
python3 /home/snmp_discover.py --silent
exit_code=$?
/etc/rc.d/init.d/nagios reload
exit exit_code