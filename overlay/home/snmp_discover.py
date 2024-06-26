import argparse
import os
import ipaddress
import nmap
from pysnmp.hlapi import SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity, getCmd

parser = argparse.ArgumentParser(description='SNMP Discovery script.')
parser.add_argument('--silent', action='store_true', help='If set, the script will not print anything.')
args = parser.parse_args()

def delete_existing_configs(output_dir):
    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
    commands_cfg_path = "/opt/nagios/etc/objects/dynamicCommands.cfg"
    with open(commands_cfg_path, "w") as cfg_file:
        cfg_file.write("")
def append_commands_to_cfg(output):
    commands_cfg_path = "/opt/nagios/etc/objects/dynamicCommands.cfg"


    with open(commands_cfg_path, "a") as cfg_file:
        for line in output:
            if line.strip():
                value = line.strip()
                command_name = f"check_netsnmp2_{value.replace(' ', '_')}"
                command_definition = f"""
                define command {{
                    command_name {command_name}
                    command_line $USER2$/check_snmp_printer2 -H $HOSTADDRESS$ -C public -t "CONSUMX {value}"
                }}
                """
                cfg_file.write(command_definition)

def discover_hosts():
    output_dir = "/opt/nagios/etc/discovered_printers/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        delete_existing_configs(output_dir)

    network = os.getenv('NETWORK')
    if not network:
        print("NETWORK environment variable is not set")
        gtfo(2, 'NETWORK environment variable is not set')

    try:
        network = ipaddress.ip_network(network)
    except ValueError as e:
        raise ValueError(f"Invalid network format: {e}")

    nm = nmap.PortScanner()
    if not args.silent:
        print("Scanning network for active hosts (ICMP)...")
    nm.scan(hosts=str(network), arguments='-sn --unprivileged')

    active_hosts = [host for host in nm.all_hosts() if nm[host].state() == 'up']

    if not args.silent:
        print(f"Active hosts found: {active_hosts}")

    if not active_hosts:
        print("No active hosts found.")
        return

    host_names = {}

    hostgroup_defined = False

    for ip in active_hosts:
        community = 'public'
        snmp_timeout = 0.05

        error_indication, error_status, error_index, var_binds = next(
            getCmd(SnmpEngine(),
                   CommunityData(community),
                   UdpTransportTarget((ip, 161), timeout=snmp_timeout, retries=0),
                   ContextData(),
                   ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)))
        )

        if error_indication:
            if not args.silent:
                print(f"No SNMP: {error_indication}, ip: {ip}")
        elif error_status:
            if not args.silent:
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


                            command = f"/opt/custom-plugins/check_snmp_printer2 -H {ip} -C public -t 'CONSUM TEST'"
                            stream = os.popen(command)
                            output = stream.read().strip().split('\n')
                            if not args.silent:
                                print(f"SNMP! Saved config file for ip: {ip}")
                                print(output)

                            if output:
                                output = output[1:]

                            append_commands_to_cfg(output)

                            with open(f"{output_dir}{unique_name}.cfg", "w") as f:
                                f.write(f"""
                                define host {{
                                    use                     generic-printer         ; Inherit default values from a template
                                    host_name               {unique_name}           ; The name we're giving to this printer
                                    alias                   {full_name} printer     ; A longer name associated with the printer
                                    address                 {ip}                    ; IP address of the printer
                                }}



                                define service {{
                                    use                     generic-service
                                    host_name               {unique_name}
                                    service_description     PING
                                    check_command           check_ping!3000.0,80%!5000.0,100%
                                    check_interval          2
                                    contacts                admin
                                    retry_interval          1
				    notification_options    c,w
                                }}
                                """)
                                for param in output:
                                    if param.strip():
                                        service_description = param.strip()
                                        service_command = service_description.replace(" ", "_")
                                        f.write(f"""
                                define service {{
                                    use                     generic-service
                                    host_name               {unique_name}
                                    service_description     {service_description}
                                    check_command           check_netsnmp2_{service_command}! -H {ip}
                                    notification_options    c,w
                                    contacts          admin
                                    check_interval          1
                                }}
                                                """)           


def gtfo(exitcode, message=''):
    if message:
        print(message)
    exit(exitcode)
if __name__ == "__main__":

    discover_hosts()
    gtfo(0, 'Network discovery done.')
