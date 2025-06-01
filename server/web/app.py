from flask import Flask, render_template, request, jsonify
import os
import sys
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from server.database.db_manager import DatabaseManager
from server.models.base import CommandTranslator
from server.models.vendors.huawei import HuaweiVendor
from server.models.vendors.cisco import CiscoVendor
from server.models.vendors.juniper import JuniperVendor
from server.models.vendors.nokia import NokiaVendor

app = Flask(__name__)

# Initialize translator and database
db_manager = DatabaseManager()
translator = CommandTranslator()

# Register vendors
vendors = {
    "Huawei": HuaweiVendor(db_manager),
    "Cisco": CiscoVendor(db_manager),
    "Juniper": JuniperVendor(db_manager),
    "Nokia": NokiaVendor(db_manager)
}

for vendor in vendors.values():
    translator.register_vendor(vendor)

# Add example command mappings
def add_example_mappings():
    logger.debug("Adding example mappings to database...")
    try:
        # BGP Commands
        bgp_commands = [
            # Display Commands
            ("Huawei", "Cisco", "display bgp peer", "show ip bgp summary", "BGP", "Display BGP peer information"),
            ("Huawei", "Juniper", "display bgp peer", "show bgp summary", "BGP", "Display BGP peer information"),
            ("Huawei", "Nokia", "display bgp peer", "show router bgp summary", "BGP", "Display BGP peer information"),
            
            ("Cisco", "Huawei", "show ip bgp summary", "display bgp peer", "BGP", "Display BGP peer information"),
            ("Cisco", "Juniper", "show ip bgp summary", "show bgp summary", "BGP", "Display BGP peer information"),
            ("Cisco", "Nokia", "show ip bgp summary", "show router bgp summary", "BGP", "Display BGP peer information"),
            
            ("Juniper", "Huawei", "show bgp summary", "display bgp peer", "BGP", "Display BGP peer information"),
            ("Juniper", "Cisco", "show bgp summary", "show ip bgp summary", "BGP", "Display BGP peer information"),
            ("Juniper", "Nokia", "show bgp summary", "show router bgp summary", "BGP", "Display BGP peer information"),
            
            ("Nokia", "Huawei", "show router bgp summary", "display bgp peer", "BGP", "Display BGP peer information"),
            ("Nokia", "Cisco", "show router bgp summary", "show ip bgp summary", "BGP", "Display BGP peer information"),
            ("Nokia", "Juniper", "show router bgp summary", "show bgp summary", "BGP", "Display BGP peer information"),

            # Configuration Commands
            ("Huawei", "Cisco", "bgp 65000", "router bgp 65000", "BGP", "Enter BGP configuration mode"),
            ("Huawei", "Juniper", "bgp 65000", "set routing-options autonomous-system 65000", "BGP", "Configure BGP AS number"),
            ("Huawei", "Nokia", "bgp 65000", "configure router bgp autonomous-system 65000", "BGP", "Configure BGP AS number"),
            
            ("Huawei", "Cisco", "peer 10.0.0.1 as-number 65001", "neighbor 10.0.0.1 remote-as 65001", "BGP", "Configure BGP peer"),
            ("Huawei", "Juniper", "peer 10.0.0.1 as-number 65001", "set protocols bgp group external peer-as 65001", "BGP", "Configure BGP peer"),
            ("Huawei", "Nokia", "peer 10.0.0.1 as-number 65001", "configure router bgp peer 10.0.0.1", "BGP", "Configure BGP peer"),
            
            ("Huawei", "Cisco", "network 192.168.1.0 255.255.255.0", "network 192.168.1.0 mask 255.255.255.0", "BGP", "Advertise network in BGP"),
            ("Huawei", "Juniper", "network 192.168.1.0 255.255.255.0", "set routing-options static route 192.168.1.0/24", "BGP", "Advertise network in BGP"),
            ("Huawei", "Nokia", "network 192.168.1.0 255.255.255.0", "configure router bgp network 192.168.1.0/24", "BGP", "Advertise network in BGP"),
            
            ("Huawei", "Cisco", "description PEER-ROUTER", "description PEER-ROUTER", "BGP", "Set BGP peer description"),
            ("Huawei", "Juniper", "description PEER-ROUTER", "set protocols bgp group external description PEER-ROUTER", "BGP", "Set BGP peer description"),
            ("Huawei", "Nokia", "description PEER-ROUTER", "configure router bgp description PEER-ROUTER", "BGP", "Set BGP peer description"),
        ]

        # Interface Commands
        interface_commands = [
            # Display Commands
            ("Huawei", "Cisco", "display interface brief", "show ip interface brief", "Interface", "Display interface information"),
            ("Huawei", "Juniper", "display interface brief", "show interfaces terse", "Interface", "Display interface information"),
            ("Huawei", "Nokia", "display interface brief", "show port", "Interface", "Display interface information"),
            
            ("Cisco", "Huawei", "show ip interface brief", "display interface brief", "Interface", "Display interface information"),
            ("Cisco", "Juniper", "show ip interface brief", "show interfaces terse", "Interface", "Display interface information"),
            ("Cisco", "Nokia", "show ip interface brief", "show port", "Interface", "Display interface information"),
            
            ("Juniper", "Huawei", "show interfaces terse", "display interface brief", "Interface", "Display interface information"),
            ("Juniper", "Cisco", "show interfaces terse", "show ip interface brief", "Interface", "Display interface information"),
            ("Juniper", "Nokia", "show interfaces terse", "show port", "Interface", "Display interface information"),
            
            ("Nokia", "Huawei", "show port", "display interface brief", "Interface", "Display interface information"),
            ("Nokia", "Cisco", "show port", "show ip interface brief", "Interface", "Display interface information"),
            ("Nokia", "Juniper", "show port", "show interfaces terse", "Interface", "Display interface information"),

            # Configuration Commands
            ("Huawei", "Cisco", "interface GigabitEthernet0/0/1", "interface GigabitEthernet0/1", "Interface", "Enter interface configuration mode"),
            ("Huawei", "Juniper", "interface GigabitEthernet0/0/1", "set interfaces ge-0/0/1", "Interface", "Configure interface"),
            ("Huawei", "Nokia", "interface GigabitEthernet0/0/1", "configure port 1/1/1", "Interface", "Configure interface"),
            
            ("Huawei", "Cisco", "ip address 10.0.0.1 255.255.255.0", "ip address 10.0.0.1 255.255.255.0", "Interface", "Configure IP address"),
            ("Huawei", "Juniper", "ip address 10.0.0.1 255.255.255.0", "set interfaces ge-0/0/1 unit 0 family inet address 10.0.0.1/24", "Interface", "Configure IP address"),
            ("Huawei", "Nokia", "ip address 10.0.0.1 255.255.255.0", "configure port 1/1/1 ip-address 10.0.0.1/24", "Interface", "Configure IP address"),
            
            ("Huawei", "Cisco", "description UPLINK", "description UPLINK", "Interface", "Set interface description"),
            ("Huawei", "Juniper", "description UPLINK", "set interfaces ge-0/0/1 description UPLINK", "Interface", "Set interface description"),
            ("Huawei", "Nokia", "description UPLINK", "configure port 1/1/1 description UPLINK", "Interface", "Set interface description"),
            
            ("Huawei", "Cisco", "shutdown", "shutdown", "Interface", "Disable interface"),
            ("Huawei", "Juniper", "shutdown", "set interfaces ge-0/0/1 disable", "Interface", "Disable interface"),
            ("Huawei", "Nokia", "shutdown", "configure port 1/1/1 shutdown", "Interface", "Disable interface"),
        ]

        # OSPF Commands
        ospf_commands = [
            # Display Commands
            ("Huawei", "Cisco", "display ospf peer", "show ip ospf neighbor", "OSPF", "Display OSPF neighbor information"),
            ("Huawei", "Juniper", "display ospf peer", "show ospf neighbor", "OSPF", "Display OSPF neighbor information"),
            ("Huawei", "Nokia", "display ospf peer", "show router ospf neighbor", "OSPF", "Display OSPF neighbor information"),
            
            ("Cisco", "Huawei", "show ip ospf neighbor", "display ospf peer", "OSPF", "Display OSPF neighbor information"),
            ("Cisco", "Juniper", "show ip ospf neighbor", "show ospf neighbor", "OSPF", "Display OSPF neighbor information"),
            ("Cisco", "Nokia", "show ip ospf neighbor", "show router ospf neighbor", "OSPF", "Display OSPF neighbor information"),
            
            ("Juniper", "Huawei", "show ospf neighbor", "display ospf peer", "OSPF", "Display OSPF neighbor information"),
            ("Juniper", "Cisco", "show ospf neighbor", "show ip ospf neighbor", "OSPF", "Display OSPF neighbor information"),
            ("Juniper", "Nokia", "show ospf neighbor", "show router ospf neighbor", "OSPF", "Display OSPF neighbor information"),
            
            ("Nokia", "Huawei", "show router ospf neighbor", "display ospf peer", "OSPF", "Display OSPF neighbor information"),
            ("Nokia", "Cisco", "show router ospf neighbor", "show ip ospf neighbor", "OSPF", "Display OSPF neighbor information"),
            ("Nokia", "Juniper", "show router ospf neighbor", "show ospf neighbor", "OSPF", "Display OSPF neighbor information"),

            # Configuration Commands
            ("Huawei", "Cisco", "ospf 1", "router ospf 1", "OSPF", "Enter OSPF configuration mode"),
            ("Huawei", "Juniper", "ospf 1", "set protocols ospf area 0", "OSPF", "Configure OSPF area"),
            ("Huawei", "Nokia", "ospf 1", "configure router ospf area 0", "OSPF", "Configure OSPF area"),
            
            ("Huawei", "Cisco", "network 10.0.0.0 0.0.0.255 area 0", "network 10.0.0.0 0.0.0.255 area 0", "OSPF", "Configure OSPF network"),
            ("Huawei", "Juniper", "network 10.0.0.0 0.0.0.255 area 0", "set protocols ospf area 0 interface ge-0/0/1", "OSPF", "Configure OSPF network"),
            ("Huawei", "Nokia", "network 10.0.0.0 0.0.0.255 area 0", "configure router ospf area 0 interface 1/1/1", "OSPF", "Configure OSPF network"),
            
            ("Huawei", "Cisco", "router-id 1.1.1.1", "router-id 1.1.1.1", "OSPF", "Configure OSPF router ID"),
            ("Huawei", "Juniper", "router-id 1.1.1.1", "set routing-options router-id 1.1.1.1", "OSPF", "Configure OSPF router ID"),
            ("Huawei", "Nokia", "router-id 1.1.1.1", "configure router router-id 1.1.1.1", "OSPF", "Configure OSPF router ID"),
            
            ("Huawei", "Cisco", "passive-interface default", "passive-interface default", "OSPF", "Set all interfaces as passive"),
            ("Huawei", "Juniper", "passive-interface default", "set protocols ospf passive", "OSPF", "Set all interfaces as passive"),
            ("Huawei", "Nokia", "passive-interface default", "configure router ospf passive", "OSPF", "Set all interfaces as passive"),
        ]

        # MPLS Commands
        mpls_commands = [
            # Display Commands
            ("Huawei", "Cisco", "display mpls lsp", "show mpls forwarding-table", "MPLS", "Display MPLS LSP information"),
            ("Huawei", "Juniper", "display mpls lsp", "show mpls lsp", "MPLS", "Display MPLS LSP information"),
            ("Huawei", "Nokia", "display mpls lsp", "show router mpls lsp", "MPLS", "Display MPLS LSP information"),
            
            ("Cisco", "Huawei", "show mpls forwarding-table", "display mpls lsp", "MPLS", "Display MPLS LSP information"),
            ("Cisco", "Juniper", "show mpls forwarding-table", "show mpls lsp", "MPLS", "Display MPLS LSP information"),
            ("Cisco", "Nokia", "show mpls forwarding-table", "show router mpls lsp", "MPLS", "Display MPLS LSP information"),
            
            ("Juniper", "Huawei", "show mpls lsp", "display mpls lsp", "MPLS", "Display MPLS LSP information"),
            ("Juniper", "Cisco", "show mpls lsp", "show mpls forwarding-table", "MPLS", "Display MPLS LSP information"),
            ("Juniper", "Nokia", "show mpls lsp", "show router mpls lsp", "MPLS", "Display MPLS LSP information"),

            # Configuration Commands
            ("Huawei", "Cisco", "mpls ldp", "mpls ldp", "MPLS", "Enter MPLS LDP configuration mode"),
            ("Huawei", "Juniper", "mpls ldp", "set protocols ldp", "MPLS", "Configure MPLS LDP"),
            ("Huawei", "Nokia", "mpls ldp", "configure router ldp", "MPLS", "Configure MPLS LDP"),
            
            ("Huawei", "Cisco", "interface GigabitEthernet0/0/1", "interface GigabitEthernet0/1", "MPLS", "Configure MPLS interface"),
            ("Huawei", "Juniper", "interface GigabitEthernet0/0/1", "set protocols mpls interface ge-0/0/1", "MPLS", "Configure MPLS interface"),
            ("Huawei", "Nokia", "interface GigabitEthernet0/0/1", "configure router mpls interface 1/1/1", "MPLS", "Configure MPLS interface"),
            
            ("Huawei", "Cisco", "mpls ip", "mpls ip", "MPLS", "Enable MPLS on interface"),
            ("Huawei", "Juniper", "mpls ip", "set protocols mpls interface ge-0/0/1", "MPLS", "Enable MPLS on interface"),
            ("Huawei", "Nokia", "mpls ip", "configure router mpls interface 1/1/1", "MPLS", "Enable MPLS on interface"),
            
            ("Huawei", "Cisco", "mpls label range 100 199", "mpls label range 100 199", "MPLS", "Configure MPLS label range"),
            ("Huawei", "Juniper", "mpls label range 100 199", "set protocols mpls label-range 100-199", "MPLS", "Configure MPLS label range"),
            ("Huawei", "Nokia", "mpls label range 100 199", "configure router mpls label-range 100-199", "MPLS", "Configure MPLS label range"),
        ]

        # SSH Commands
        ssh_commands = [
            # Display Commands
            ("Huawei", "Cisco", "display ssh server status", "show ip ssh", "SSH", "Display SSH server status"),
            ("Huawei", "Juniper", "display ssh server status", "show system services ssh", "SSH", "Display SSH server status"),
            ("Huawei", "Nokia", "display ssh server status", "show system security ssh", "SSH", "Display SSH server status"),
            
            ("Cisco", "Huawei", "show ip ssh", "display ssh server status", "SSH", "Display SSH server status"),
            ("Cisco", "Juniper", "show ip ssh", "show system services ssh", "SSH", "Display SSH server status"),
            ("Cisco", "Nokia", "show ip ssh", "show system security ssh", "SSH", "Display SSH server status"),
            
            ("Juniper", "Huawei", "show system services ssh", "display ssh server status", "SSH", "Display SSH server status"),
            ("Juniper", "Cisco", "show system services ssh", "show ip ssh", "SSH", "Display SSH server status"),
            ("Juniper", "Nokia", "show system services ssh", "show system security ssh", "SSH", "Display SSH server status"),
            
            ("Nokia", "Huawei", "show system security ssh", "display ssh server status", "SSH", "Display SSH server status"),
            ("Nokia", "Cisco", "show system security ssh", "show ip ssh", "SSH", "Display SSH server status"),
            ("Nokia", "Juniper", "show system security ssh", "show system services ssh", "SSH", "Display SSH server status"),

            # Configuration Commands
            ("Huawei", "Cisco", "ssh server enable", "ip ssh server", "SSH", "Enable SSH server"),
            ("Huawei", "Juniper", "ssh server enable", "set system services ssh", "SSH", "Enable SSH server"),
            ("Huawei", "Nokia", "ssh server enable", "configure system security ssh server", "SSH", "Enable SSH server"),
            
            ("Huawei", "Cisco", "ssh server port 22", "ip ssh port 22", "SSH", "Configure SSH port"),
            ("Huawei", "Juniper", "ssh server port 22", "set system services ssh port 22", "SSH", "Configure SSH port"),
            ("Huawei", "Nokia", "ssh server port 22", "configure system security ssh server port 22", "SSH", "Configure SSH port"),
            
            ("Huawei", "Cisco", "ssh server timeout 60", "ip ssh timeout 60", "SSH", "Configure SSH timeout"),
            ("Huawei", "Juniper", "ssh server timeout 60", "set system services ssh connection-limit 60", "SSH", "Configure SSH timeout"),
            ("Huawei", "Nokia", "ssh server timeout 60", "configure system security ssh server timeout 60", "SSH", "Configure SSH timeout"),
            
            ("Huawei", "Cisco", "ssh server authentication-retries 3", "ip ssh authentication-retries 3", "SSH", "Configure SSH authentication retries"),
            ("Huawei", "Juniper", "ssh server authentication-retries 3", "set system services ssh authentication-retries 3", "SSH", "Configure SSH authentication retries"),
            ("Huawei", "Nokia", "ssh server authentication-retries 3", "configure system security ssh server authentication-retries 3", "SSH", "Configure SSH authentication retries"),
        ]

        # Security Commands
        security_commands = [
            # Display Commands
            ("Huawei", "Cisco", "display acl resource", "show ip access-list", "Security", "Display ACL information"),
            ("Huawei", "Juniper", "display acl resource", "show firewall filter", "Security", "Display ACL information"),
            ("Huawei", "Nokia", "display acl resource", "show filter", "Security", "Display ACL information"),
            
            ("Cisco", "Huawei", "show ip access-list", "display acl resource", "Security", "Display ACL information"),
            ("Cisco", "Juniper", "show ip access-list", "show firewall filter", "Security", "Display ACL information"),
            ("Cisco", "Nokia", "show ip access-list", "show filter", "Security", "Display ACL information"),
            
            ("Juniper", "Huawei", "show firewall filter", "display acl resource", "Security", "Display ACL information"),
            ("Juniper", "Cisco", "show firewall filter", "show ip access-list", "Security", "Display ACL information"),
            ("Juniper", "Nokia", "show firewall filter", "show filter", "Security", "Display ACL information"),
            
            ("Nokia", "Huawei", "show filter", "display acl resource", "Security", "Display ACL information"),
            ("Nokia", "Cisco", "show filter", "show ip access-list", "Security", "Display ACL information"),
            ("Nokia", "Juniper", "show filter", "show firewall filter", "Security", "Display ACL information"),

            # Configuration Commands
            ("Huawei", "Cisco", "acl 3000", "ip access-list extended 3000", "Security", "Create extended ACL"),
            ("Huawei", "Juniper", "acl 3000", "set firewall filter 3000", "Security", "Create firewall filter"),
            ("Huawei", "Nokia", "acl 3000", "configure filter 3000", "Security", "Create filter"),
            
            ("Huawei", "Cisco", "rule 10 permit ip source 10.0.0.0 0.0.0.255", "permit ip 10.0.0.0 0.0.0.255 any", "Security", "Configure ACL rule"),
            ("Huawei", "Juniper", "rule 10 permit ip source 10.0.0.0 0.0.0.255", "set firewall filter 3000 term 1 from source-address 10.0.0.0/24", "Security", "Configure ACL rule"),
            ("Huawei", "Nokia", "rule 10 permit ip source 10.0.0.0 0.0.0.255", "configure filter 3000 entry 10 match src-ip 10.0.0.0/24", "Security", "Configure ACL rule"),
            
            ("Huawei", "Cisco", "rule 20 deny ip any any", "deny ip any any", "Security", "Configure default deny rule"),
            ("Huawei", "Juniper", "rule 20 deny ip any any", "set firewall filter 3000 term default then reject", "Security", "Configure default deny rule"),
            ("Huawei", "Nokia", "rule 20 deny ip any any", "configure filter 3000 default-action drop", "Security", "Configure default deny rule"),
            
            ("Huawei", "Cisco", "apply acl 3000 inbound", "ip access-group 3000 in", "Security", "Apply ACL to interface"),
            ("Huawei", "Juniper", "apply acl 3000 inbound", "set interfaces ge-0/0/1 unit 0 family inet filter input 3000", "Security", "Apply ACL to interface"),
            ("Huawei", "Nokia", "apply acl 3000 inbound", "configure port 1/1/1 filter 3000", "Security", "Apply ACL to interface"),
        ]

        # Add all commands to database
        all_commands = (
            bgp_commands + 
            interface_commands + 
            ospf_commands + 
            mpls_commands + 
            ssh_commands + 
            security_commands
        )
        
        for source_vendor, target_vendor, source_cmd, target_cmd, topic, description in all_commands:
            try:
                db_manager.add_command_mapping(
                    source_vendor=source_vendor,
                    target_vendor=target_vendor,
                    source_command=source_cmd,
                    target_command=target_cmd,
                    topic=topic,
                    description=description
                )
                logger.debug(f"Added mapping: {source_vendor} -> {target_vendor}: {source_cmd} -> {target_cmd}")
            except sqlite3.IntegrityError as e:
                logger.debug(f"Mapping already exists: {source_vendor} -> {target_vendor}: {source_cmd} -> {target_cmd}")
                continue
            except Exception as e:
                logger.error(f"Error adding mapping: {str(e)}")
                continue
    except Exception as e:
        logger.error(f"Error in add_example_mappings: {str(e)}")

# Add example mappings
add_example_mappings()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vendors')
def get_vendors():
    return jsonify({'vendors': list(vendors.keys())})

@app.route('/translate', methods=['POST'])
def translate_command():
    data = request.get_json()
    source_vendor = data.get('source_vendor')
    target_vendor = data.get('target_vendor')
    command = data.get('command')
    
    if not all([source_vendor, target_vendor, command]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    try:
        translated = translator.translate(command, source_vendor, target_vendor)
        return jsonify({
            'source_command': command,
            'translated_command': translated
        })
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/topics')
def get_topics():
    # Get all topics from the database
    topics = [
        "BGP", "OSPF", "MPLS", "SSH", 
        "Interface", "Routing", "Security"
    ]
    return jsonify({'topics': topics})

@app.route('/commands/<topic>')
def get_commands_by_topic(topic):
    try:
        logger.debug(f"Getting commands for topic: {topic}")
        commands = db_manager.get_commands_by_topic(topic)
        logger.debug(f"Found commands: {commands}")
        
        if not commands:
            logger.warning(f"No commands found for topic: {topic}")
            return jsonify({'commands': {}})
            
        return jsonify({'commands': commands})
    except Exception as e:
        logger.error(f"Error getting commands by topic: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/suggest_commands', methods=['GET'])
def suggest_commands():
    vendor = request.args.get('vendor')
    term = request.args.get('term', '')
    
    if not vendor:
        return jsonify({'error': 'Vendor parameter is required'}), 400
    
    try:
        logger.debug(f"Getting suggestions for vendor: {vendor}, term: {term}")
        # Get all commands for the vendor from the database
        suggestions = db_manager.get_commands_by_vendor(vendor)
        
        # Filter suggestions based on the search term
        filtered_suggestions = [
            cmd for cmd in suggestions 
            if term.lower() in cmd.lower()
        ]
        
        logger.debug(f"Found suggestions: {filtered_suggestions}")
        return jsonify({'suggestions': filtered_suggestions})
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000) 