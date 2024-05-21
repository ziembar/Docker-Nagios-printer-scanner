from pysnmp.hlapi import *
import os

def discover_hosts():
    for i in range(1, 256):
        ip = f'192.168.1.{i}'  # Modify this according to your network
        community = 'public'    # Change this to your SNMP community string
        snmp_timeout = 0.5       # Timeout in seconds

        error_indication, error_status, error_index, var_binds = next(
            getCmd(SnmpEngine(),
                   CommunityData(community),
                   UdpTransportTarget((ip, 161), timeout=snmp_timeout),
                   ContextData(),
                   ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)))
        )

        if error_indication:
            print(f"Error: {error_indication}")
        elif error_status:
            print(f"Error: {error_status.prettyPrint()}")
        else:
            for var_bind in var_binds:
                host_name = var_bind[1].prettyPrint()
                with open(f"/opt/nagios/discovered_printers/{host_name}.cfg", "w") as f:
                    f.write(f"""
define host {{
    use                     generic-printer         ; Inherit default values from a template
    host_name               {host_name}             ; The name we're giving to this printer
    alias                   {host_name}             ; A longer name associated with the printer
    address                 {ip}                    ; IP address of the printer
    hostgroups              network-printers        ; Host groups this printer is associated with
}}
                    """)

if __name__ == "__main__":
    discover_hosts()
