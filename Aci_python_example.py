# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 10:57:40 2020

@author: kupriianovi
"""

aci_url = "https://URL/"
user = "admin"
pwd = "pwd"

import csv 
# Function to convert a csv file to a list of dictionaries.  Takes in one variable called &quot;variables_file&quot;
 
def csv_dict_list(variables_file):
     
    # Open variable-based csv, iterate over the rows and map values to a list of dictionaries containing key/value pairs
 
    reader = csv.DictReader(open(variables_file))
    dict_list = []
    for line in reader:
        dict_list.append(line)
    return dict_list 

#Retrieve config data into dictionary
data_file = 'aci_data.csv'
data_dict = csv_dict_list(data_file)

#%%
# User serviceable variables
# BGP ASNs
l3out_ext_local_as = '65535'
l3out_ext_remote_as = '65534'
l3out_dci_local_as = '65535'
l3out_dci_remote_as = '65533'

# BGP MD5 password - same for GSU_ACI - NB2_ACI and NB2_ACI - NB2 FW
passwd = 'pwd'

# Leafs terminating L3Outs
leaf1_num = '101'
leaf2_num = '102'

# L3Out Path dn
l3out_path = 'topology/pod-1/protpaths-101-102/pathep-[ipg-bleaf-vpc1]'

# L3 Domain name 
l3_dom_name_dci = 'uni/l3dom-' + 'ext-l3-dci'
l3_dom_name_fw = 'uni/l3dom-' + 'ext-l3-gw'

#%%
import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.fv
import cobra.model.l3ext
import cobra.model.bgp
import cobra.model.pol
import cobra.model.vz
#from cobra.internal.codec.xmlcodec import toXMLStr

# log into an APIC and create a directory object
ls = cobra.mit.session.LoginSession(aci_url, user, pwd)
md = cobra.mit.access.MoDirectory(ls)
md.login()

for vrf in data_dict:
    # Extract values for variables
    tenant_name = vrf['Tenant']
    vrf_name = vrf['Segment']
    bd_name = 'bd-' + vrf['Segment']
    subnet_ip = vrf['Subnet']    
    l3out_ext_name = 'l3out-ext-' + vrf['Segment']
    l3out_dci_name = 'l3out-dci-' + vrf['Segment']
    contract_name = "Any-Any-contract"
    lnp_name = vrf['Segment']
    lip_name = vrf['Segment']
    
    # L3Out to local FW
    l3out1_vlan = 'vlan-' + vrf['l3out1_vlan']
    l3out1_peer_ip = vrf['l3out1_peer_ip']
    l3out1_a_ip = vrf['l3out1_a_ip'] + '/28'
    l3out1_b_ip = vrf['l3out1_b_ip'] + '/28'

    # L3Out to remote ACI Fabric
    l3out2_vlan = 'vlan-' + vrf['l3out2_vlan']
    l3out2_peer_a_ip = vrf['l3out2_peer_a_ip']
    l3out2_peer_b_ip = vrf['l3out2_peer_b_ip']
    l3out2_a_ip = vrf['l3out2_a_ip'] + '/28'
    l3out2_b_ip = vrf['l3out2_b_ip'] + '/28'
    l3out2_ext_epg_name = 'ext-epg-' + vrf['Segment']
    l3out2_remote_sub = vrf['l3out2_remote_sub']
    
    router_id_leaf1 = vrf['router_id_leaf1']
    router_id_leaf2 = vrf['router_id_leaf2']
    leaf1_dn = 'topology/pod-1/node-' + leaf1_num
    leaf2_dn = 'topology/pod-1/node-' + leaf2_num
    
    
    # Create containers - Uni, Tenant and VRF
    polUni = cobra.model.pol.Uni('')
    fvTenant = cobra.model.fv.Tenant(polUni, tenant_name)
    fvCtx = cobra.model.fv.Ctx(fvTenant, vrf_name)
    vzany = cobra.model.vz.Any(fvCtx,dn='uni/tn-'+tenant_name+vrf_name+'/any',prefGrMemb='disabled')
    
    # Attach contracts and BGP Timers
    cobra.model.vz.RsAnyToProv(vzany,tnVzBrCPName="Any-to-GW")
    cobra.model.vz.RsAnyToProv(vzany,tnVzBrCPName="Any-to-DCI")
    cobra.model.fv.RsBgpCtxPol(fvCtx,tnBgpCtxPolName="DCI-BGP-Timers")
    
    # Create BD
    bridge_domain = cobra.model.fv.BD(fvTenant, name=bd_name,multiDstPktAct="encap-flood")
    attached_vrf = cobra.model.fv.RsCtx(bridge_domain, tnFvCtxName=vrf_name)
    subnet = cobra.model.fv.Subnet(bridge_domain, ip=subnet_ip, scope='public', name="")
    
   
  #Create L3Out - External(to the Firewall)
    l3out_ext_obj = cobra.model.l3ext.Out(fvTenant,l3out_ext_name)
    #Attach L3Out to VRF
    l3out_ext_RsEctx = cobra.model.l3ext.RsEctx(l3out_ext_obj, tnFvCtxName=vrf_name)
    #Create Logical Node Profile
    l3out_ext_LNodeP = cobra.model.l3ext.LNodeP(l3out_ext_obj, lnp_name)
    #Attach LNP to leaf switches
    l3out_ext_RsNodeL3OutAtt = cobra.model.l3ext.RsNodeL3OutAtt(l3out_ext_LNodeP, rtrIdLoopBack=u'no', rtrId=router_id_leaf1, tDn=leaf1_dn)
    l3out_ext_RsNodeL3OutAtt2 = cobra.model.l3ext.RsNodeL3OutAtt(l3out_ext_LNodeP, rtrIdLoopBack=u'no', rtrId=router_id_leaf2, tDn=leaf2_dn)
    #Create Logical Interface profiles
    l3out_ext_LIfP = cobra.model.l3ext.LIfP(l3out_ext_LNodeP, lip_name)
    #Not required?
    #l3out_ext_RsNdIfPol = cobra.model.l3ext.RsNdIfPol(l3out_ext_LIfP, tnNdIfPolName=u'')
    #Configure SVI Attributes
    l3out_ext_RsPathL3OutAtt = cobra.model.l3ext.RsPathL3OutAtt(l3out_ext_LIfP, encapScope='ctx', encap=l3out1_vlan, 
                                                                ifInstT='ext-svi', mtu=u'1500', tDn=l3out_path)
    #Assign Transit subnet IPs on both leafs
    l3out_ext_Member = cobra.model.l3ext.Member(l3out_ext_RsPathL3OutAtt, name=u'', side=u'B', addr=l3out1_b_ip, descr=u'', llAddr=u'::')
    l3out_ext_Member2 = cobra.model.l3ext.Member(l3out_ext_RsPathL3OutAtt, name=u'', side=u'A', addr=l3out1_a_ip, descr=u'', llAddr=u'::')
    #Attach to L3Out Domain
    l3out_ext_RsL3DomAtt = cobra.model.l3ext.RsL3DomAtt(l3out_ext_obj, tDn=l3_dom_name_fw)
    #Create External EPG
    l3out_ext_InstP = cobra.model.l3ext.InstP(l3out_ext_obj, prio=u'unspecified', matchT=u'AtleastOne', name='ext-epg-any', descr=u'')
    l3out_ext_Subnet = cobra.model.l3ext.Subnet(l3out_ext_InstP, aggregate=u'', ip='0.0.0.0/0', name=u'', descr=u'')
    #Enable BGP
    l3out_ext_extp = cobra.model.bgp.ExtP(l3out_ext_obj) 
    #Add peer
    l3out_ext_peer = cobra.model.bgp.PeerP(l3out_ext_RsPathL3OutAtt,addr=l3out1_peer_ip,ctrl='nh-self,send-com,send-ext-com',password=passwd)
    #Assign local and remote ASNs
    l3out_ext_localASN = cobra.model.bgp.LocalAsnP(l3out_ext_peer,localAsn=l3out_ext_local_as)
    l3out_ext_remoteAS = cobra.model.bgp.AsP(l3out_ext_peer,asn=l3out_ext_remote_as) 
    #Attach to a contract
    fvRsCons = cobra.model.fv.RsCons(l3out_ext_InstP, tnVzBrCPName="Any-to-FW", prio=u'unspecified') 
    #Attach L3Out to BD
    cobra.model.fv.RsBDToOut(bridge_domain,tnL3extOutName=l3out_ext_name)
    
  #Create L3Out - DCI(to the same VRF in another DC)
    l3out_dci_obj = cobra.model.l3ext.Out(fvTenant,l3out_dci_name)
    #Attach L3Out to VRF
    l3out_dci_RsEctx = cobra.model.l3ext.RsEctx(l3out_dci_obj, tnFvCtxName=vrf_name)
    #Create Logical Node Profile
    l3out_dci_LNodeP = cobra.model.l3ext.LNodeP(l3out_dci_obj, lnp_name)
    #Attach LNP to leaf switches
    l3out_dci_RsNodeL3OutAtt = cobra.model.l3ext.RsNodeL3OutAtt(l3out_dci_LNodeP, rtrIdLoopBack=u'no', rtrId=router_id_leaf1, tDn=leaf1_dn)
    l3out_dci_RsNodeL3OutAtt2 = cobra.model.l3ext.RsNodeL3OutAtt(l3out_dci_LNodeP, rtrIdLoopBack=u'no', rtrId=router_id_leaf2, tDn=leaf2_dn)
    #Create Logical Interface profiles
    l3out_dci_LIfP = cobra.model.l3ext.LIfP(l3out_dci_LNodeP, lip_name)
    #Not required?
    #l3out_dci_RsNdIfPol = cobra.model.l3ext.RsNdIfPol(l3out_dci_LIfP, tnNdIfPolName=u'')
    #Configure SVI Attributes
    l3out_dci_RsPathL3OutAtt = cobra.model.l3ext.RsPathL3OutAtt(l3out_dci_LIfP, encapScope='ctx', encap=l3out2_vlan, ifInstT='ext-svi', 
                                                                mtu=u'1500', tDn=l3out_path)
    #Assign Transit subnet IPs on both leafs
    l3out_dci_Member1 = cobra.model.l3ext.Member(l3out_dci_RsPathL3OutAtt, name=u'', side=u'B', addr=l3out2_b_ip, descr=u'', llAddr=u'::')
    l3out_dci_Member2 = cobra.model.l3ext.Member(l3out_dci_RsPathL3OutAtt, name=u'', side=u'A', addr=l3out2_a_ip, descr=u'', llAddr=u'::')
    #Attach to L3Out Domain
    l3out_dci_RsL3DomAtt = cobra.model.l3ext.RsL3DomAtt(l3out_dci_obj, tDn=l3_dom_name_dci)
    #Create External EPG
    l3out_dci_InstP = cobra.model.l3ext.InstP(l3out_dci_obj, prio=u'unspecified', matchT=u'AtleastOne', name=l3out2_ext_epg_name, descr=u'')
    l3out_dci_Subnet = cobra.model.l3ext.Subnet(l3out_dci_InstP, aggregate=u'', ip=l3out2_remote_sub, name=u'', descr=u'')
    #Enable BGP
    l3out_dci_extp = cobra.model.bgp.ExtP(l3out_dci_obj) 
    #Add peer
    l3out_dci_peer1 = cobra.model.bgp.PeerP(l3out_dci_RsPathL3OutAtt,addr=l3out2_peer_a_ip,ctrl='nh-self,send-com,send-ext-com',password=passwd)
    l3out_dci_peer2 = cobra.model.bgp.PeerP(l3out_dci_RsPathL3OutAtt,addr=l3out2_peer_b_ip,ctrl='nh-self,send-com,send-ext-com',password=passwd)
    #Assign local and remote ASNs
    l3out_dci_localASN1 = cobra.model.bgp.LocalAsnP(l3out_dci_peer1,localAsn=l3out_dci_local_as)
    l3out_dci_remoteAS1 = cobra.model.bgp.AsP(l3out_dci_peer1,asn=l3out_dci_remote_as) 
    l3out_dci_localASN2 = cobra.model.bgp.LocalAsnP(l3out_dci_peer2,localAsn=l3out_dci_local_as)
    l3out_dci_remoteAS2 = cobra.model.bgp.AsP(l3out_dci_peer2,asn=l3out_dci_remote_as) 
    #Attach to a contract
    fvRsCons = cobra.model.fv.RsCons(l3out_ext_InstP, tnVzBrCPName="Any-to-DCI", prio=u'unspecified') 
    #Attach L3Out to BD
    cobra.model.fv.RsBDToOut(bridge_domain,tnL3extOutName=l3out_dci_name)
    
    #Commit to the fabric    
    c = cobra.mit.request.ConfigRequest()
    c.addMo(fvTenant)
    md.commit(c)
    
    #Print confirmation
    print('Tenant', tenant_name, 'VRF', vrf_name, 'is done')
    
print('All Done')