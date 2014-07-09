# BLE iBeaconScanner based on https://github.com/switchdoclabs/iBeacon-Scanner-/blob/master/blescan.py
import os
import sys
import struct
import bluetooth._bluetooth as bluez

LE_META_EVENT = 0x3e
LE_PUBLIC_ADDRESS=0x00
LE_RANDOM_ADDRESS=0x01
LE_SET_SCAN_PARAMETERS_CP_SIZE=7
OGF_LE_CTL=0x08
OCF_LE_SET_SCAN_PARAMETERS=0x000B
OCF_LE_SET_SCAN_ENABLE=0x000C
OCF_LE_CREATE_CONN=0x000D

LE_ROLE_MASTER = 0x00
LE_ROLE_SLAVE = 0x01

# these are actually subevents of LE_META_EVENT
EVT_LE_CONN_COMPLETE=0x01
EVT_LE_ADVERTISING_REPORT=0x02
EVT_LE_CONN_UPDATE_COMPLETE=0x03
EVT_LE_READ_REMOTE_USED_FEATURES_COMPLETE=0x04

# Advertisment event types
ADV_IND=0x00
ADV_DIRECT_IND=0x01
ADV_SCAN_IND=0x02
ADV_NONCONN_IND=0x03
ADV_SCAN_RSP=0x04


def returnnumberpacket(pkt):
    myInteger = 0
    multiple = 256
    for c in pkt:
        myInteger +=  struct.unpack("B",c)[0] * multiple
        multiple = 1
    return myInteger 

def returnstringpacket(pkt):
    myString = "";
    for c in pkt:
        myString +=  "%02x" %struct.unpack("B",c)[0]
    return myString 

def packed_bdaddr_to_string(bdaddr_packed):
    return ':'.join('%02x'%i for i in struct.unpack("<BBBBBB", bdaddr_packed[::-1]))

def hci_enable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x01)

def hci_disable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x00)

def hci_toggle_le_scan(sock, enable):
    cmd_pkt = struct.pack("<BB", enable, 0x00)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)


def hci_le_set_scan_parameters(sock):
    old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)
    SCAN_RANDOM = 0x01
    OWN_TYPE = SCAN_RANDOM
    SCAN_TYPE = 0x01


    
def parse_events(sock, loop_count=100):
    old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)
    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, flt )
    done = False
    results = []
    myFullList = []
    for i in range(0, loop_count):
        pkt = sock.recv(255)
        ptype, event, plen = struct.unpack("BBB", pkt[:3])
	if event == bluez.EVT_INQUIRY_RESULT_WITH_RSSI:
		i =0
	elif event == bluez.EVT_NUM_COMP_PKTS:
		i =0
	elif event == bluez.EVT_DISCONN_COMPLETE:
		i =0 
        elif event == LE_META_EVENT:
            	subevent, = struct.unpack("B", pkt[3])
            	pkt = pkt[4:]
            	if subevent == EVT_LE_CONN_COMPLETE:
            	    	le_handle_connection_complete(pkt)
            	elif subevent == EVT_LE_ADVERTISING_REPORT:
            	    	#print "advertising report"
            	    	num_reports = struct.unpack("B", pkt[0])[0]
            	    	report_pkt_offset = 0
            	    	for i in range(0, num_reports):
				# build the return list
				Advalues = []
				Advalues.append(packed_bdaddr_to_string(pkt[report_pkt_offset + 3:report_pkt_offset + 9]))
				Advalues.append(returnstringpacket(pkt[report_pkt_offset -22: report_pkt_offset - 6]))
				Advalues.append(returnnumberpacket(pkt[report_pkt_offset -6: report_pkt_offset - 4]))
				Advalues.append(returnnumberpacket(pkt[report_pkt_offset -4: report_pkt_offset - 2]))
				Advalues.append(struct.unpack("b", pkt[report_pkt_offset -2]))
				Advalues.append(struct.unpack("b", pkt[report_pkt_offset -1]))
				myFullList.append(Advalues)
			done = True
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, old_filter )
    return myFullList


