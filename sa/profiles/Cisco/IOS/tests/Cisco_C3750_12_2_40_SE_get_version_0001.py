# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_version test
## Auto-generated by manage.py debug-script at 2010-09-23 19:43:42
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ScriptTestCase
class Cisco_IOS_get_version_Test(ScriptTestCase):
    script="Cisco.IOS.get_version"
    vendor="Cisco"
    platform='C3750'
    version='12.2(40)SE'
    input={}
    result={'image': 'C3750-IPSERVICESK9-M',
 'platform': 'C3750',
 'vendor': 'Cisco',
 'version': '12.2(40)SE'}
    motd=''
    cli={'terminal length 0': 'terminal length 0\n', 'show version': 'show version\nCisco IOS Software, C3750 Software (C3750-IPSERVICESK9-M), Version 12.2(40)SE, RELEASE SOFTWARE (fc3)\nCopyright (c) 1986-2007 by Cisco Systems, Inc.\nCompiled Fri 24-Aug-07 00:53 by myl\nImage text-base: 0x00003000, data-base: 0x01680000\n\nROM: Bootstrap program is C3750 boot loader\nBOOTLDR: C3750 Boot Loader (C3750-HBOOT-M) Version 12.2(25r)SEE3, RELEASE SOFTWARE (fc1)\n\nRouter1 uptime is 1 year, 44 weeks, 6 days, 14 hours, 1 minute\nSystem returned to ROM by power-on\nSystem restarted at 04:26:33 MSK Thu Nov 13 2008\nSystem image file is "flash:/c3750-ipservicesk9-mz.122-40.SE.bin"\n\n\nThis product contains cryptographic features and is subject to United\nStates and local country laws governing import, export, transfer and\nuse. Delivery of Cisco cryptographic products does not imply\nthird-party authority to import, export, distribute or use encryption.\nImporters, exporters, distributors and users are responsible for\ncompliance with U.S. and local country laws. By using this product you\nagree to comply with applicable laws and regulations. If you are unable\nto comply with U.S. and local laws, return this product immediately.\n\nA summary of U.S. laws governing Cisco cryptographic products may be found at:\nhttp://www.cisco.com/wwl/export/crypto/tool/stqrg.html\n\nIf you require further assistance please contact us by sending email to\nexport@cisco.com.\n\ncisco WS-C3750G-12S (PowerPC405) processor (revision N0) with 118784K/12280K bytes of memory.\nProcessor board ID FCZ1133Y010\nLast reset from power-on\n66 Virtual Ethernet interfaces\n12 Gigabit Ethernet interfaces\nThe password-recovery mechanism is enabled.\n\n512K bytes of flash-simulated non-volatile configuration memory.\nBase ethernet MAC Address       : 00:07:0E:07:FB:80\nMotherboard assembly number     : 73-9678-07\nPower supply part number        : 341-0048-03\nMotherboard serial number       : FDO112706DT\nPower supply serial number      : DTN112231W8\nModel revision number           : N0\nMotherboard revision number     : B0\nModel number                    : WS-C3750G-12S-S\nSystem serial number            : FCZ1133Y010\nTop Assembly Part Number        : 800-25856-04\nTop Assembly Revision Number    : C0\nVersion ID                      : V06\nCLEI Code Number                : CNM81V0GRB\nHardware Board Revision Number  : 0x06\n\n\nSwitch   Ports  Model              SW Version              SW Image            \n------   -----  -----              ----------              ----------          \n*    1   12     WS-C3750G-12S      12.2(40)SE              C3750-IPSERVICESK9-M\n\n\nConfiguration register is 0xF\n\n'}
    snmp_get={}
    snmp_getnext={}
        
