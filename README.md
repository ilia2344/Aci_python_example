# Aci_python_example

This script is using Cobra SDK to configure various Networking components of a tenant(Tenant tab) that may be required during build phase of ACI deployment.
Data is collected from CSV file with following headers:
Tenant	Segment	Subnet	l3out1_peer_ip	l3out1_a_ip	l3out1_b_ip	l3out1_vlan	l3out1_net	l3out2_a_ip	l3out2_b_ip	l3out2_peer_a_ip	l3out2_peer_b_ip	l3out2_vlan	l3out2_net	router_id_leaf1	router_id_leaf2	l3out2_remote_sub

Entities that are getting created:
 - Tenant
 - VRF
 - BD
 - Subnet
 - L3Out1 - the one that ACI will use as a default GW. ExtEPG = 0.0.0.0/0. BGP on (with MD5)
 - L3Out2 - another L3Out used for comms with remote DC. ExtEPG = specific subnet(l3out2_remote_sub). BGP on (with MD5)
 
 Expects existing contracts for Any to L3Out1(tnVzBrCPName="Any-to-GW") and Any to L3Out2(tnVzBrCPName="Any-to-DCI")
 
 Tested on ACI fabric running version 3.2
