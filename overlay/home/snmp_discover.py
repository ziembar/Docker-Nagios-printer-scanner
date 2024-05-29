import os
import ipaddress
import nmap
from pysnmp.hlapi import SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity, getCmd

def delete_existing_configs(output_dir):
    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)

def discover_hosts():
    output_dir = "/opt/nagios/etc/discovered_printers/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        delete_existing_configs(output_dir)

    # Retrieve the network from the environment variable
    network = os.getenv('NETWORK')
    if not network:
        raise ValueError("NETWORK environment variable is not set")

    try:
        network = ipaddress.ip_network(network)
    except ValueError as e:
        raise ValueError(f"Invalid network format: {e}")

    # Initialize the nmap scanner
    nm = nmap.PortScanner()
    print("Scanning network for active hosts (ICMP)...")
    nm.scan(hosts=str(network), arguments='-sn --unprivileged')

    active_hosts = [host for host in nm.all_hosts() if nm[host].state() == 'up']

    print(f"Active hosts found: {active_hosts}")

    if not active_hosts:
        print("No active hosts found.")
        return

    host_names = {}

    for ip in active_hosts:
        community = 'public'    # Change this to your SNMP community string
        snmp_timeout = 0.05     # Timeout in seconds

        error_indication, error_status, error_index, var_binds = next(
            getCmd(SnmpEngine(),
                   CommunityData(community),
                   UdpTransportTarget((ip, 161), timeout=snmp_timeout, retries=0),
                   ContextData(),
                   ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)))
        )

        if error_indication:
            print(f"No SNMP: {error_indication}, ip: {ip}")
        elif error_status:
            print(f"No SNMP: {error_status.prettyPrint()}, ip: {ip}")
        else:
            for var_bind in var_binds:
                full_name = var_bind[1].prettyPrint()
                first_word = full_name.split()[0]

                if first_word in host_names:
                    host_names[first_word] += 1
                    unique_name = f"{first_word}{host_names[first_word]}"
                else:
                    host_names[first_word] = 1
                    unique_name = first_word

                print(f"SNMP! Saved config file for ip: {ip}")
                with open(f"{output_dir}{unique_name}.cfg", "w") as f:
                    f.write(f"""
define host {{
    use                     generic-printer         ; Inherit default values from a template
    host_name               {unique_name}           ; The name we're giving to this printer
    alias                   {full_name} printer     ; A longer name associated with the printer
    address                 {ip}                    ; IP address of the printer
    hostgroups              network-printers        ; Host groups this printer is associated with
}}



define service {{

    use                     generic-service         ; Inherit values from a template
    host_name               {unique_name}              ; The name of the host the service is associated with
    service_description     Printer Status          ; The service description
    check_command           check_hpjd!-C public    ; The command used to monitor the service
    check_interval          10                      ; Check the service every 10 minutes under normal conditions
    retry_interval          1                       ; Re-check the service every minute until its final/hard state is determined
}}

define service {{

    use                     generic-service
    host_name               {unique_name}
    service_description     PING
    check_command           check_ping!3000.0,80%!5000.0,100%
    check_interval          10
    retry_interval          1
}}


define service{{
       use                             generic-service
       host_name                       {unique_name}
       hostgroup_name                  network-printers
       servicegroup_name               snmpServices
       service_description             printer status
       check_command                   check_netsnmp2! -H {ip}
       notification_options            c,u,r
       check_interval          1

       }}
                    """)

if __name__ == "__main__":
    discover_hosts()
