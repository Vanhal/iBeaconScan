# test BLE Scanning software

import blescan
import sys

import bluetooth._bluetooth as bluez

dev_id = 0
try:
	sock = bluez.hci_open_dev(dev_id)
	print "ble thread started"

except:
	print "error accessing bluetooth device..."
	sys.exit(1)

blescan.hci_le_set_scan_parameters(sock)
blescan.hci_enable_le_scan(sock)

while True:
	returnedList = blescan.parse_events(sock, 1)
	print "----------"
	for beacon in returnedList:
		print beacon
		#Adstring = beacon[0]
		#Adstring += ","
		#Adstring += beacon[1]
		#Adstring += ","
		#Adstring += "%i" % beacon[2]
		#Adstring += ","
		#Adstring += "%i" % beacon[3]
		#Adstring += ","
		#Adstring += "%i" % beacon[4]
		#Adstring += ","
		#Adstring += "%i" % beacon[5]
		#print Adstring

