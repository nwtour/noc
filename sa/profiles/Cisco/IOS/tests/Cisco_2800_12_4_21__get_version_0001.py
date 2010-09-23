# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_version test
## Auto-generated by manage.py debug-script at 2010-09-23 19:47:26
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ScriptTestCase
class Cisco_IOS_get_version_Test(ScriptTestCase):
    script="Cisco.IOS.get_version"
    vendor="Cisco"
    platform='2800'
    version='12.4(21)'
    input={}
    result={'image': 'C2800NM-ADVIPSERVICESK9-M',
 'platform': '2800',
 'vendor': 'Cisco',
 'version': '12.4(21)'}
    motd=''
    cli={'terminal length 0': 'terminal length 0\n',
            'show version': 'show version\nCisco IOS Software, 2800 Software (C2800NM-ADVIPSERVICESK9-M), Version 12.4(21), RELEASE SOFTWARE (fc1)\nTechnical Support: http://www.cisco.com/techsupport\nCopyright (c) 1986-2008 by Cisco Systems, Inc.\nCompiled Thu 10-Jul-08 02:21 by prod_rel_team\n\nROM: System Bootstrap, Version 12.4(13r)T, RELEASE SOFTWARE (fc1)\n\nRouter1 uptime is 9 weeks, 23 hours, 30 minutes\nSystem returned to ROM by power-on\nSystem restarted at 20:15:27 MSD Wed Jul 21 2010\nSystem image file is "flash:c2800nm-advipservicesk9-mz.124-21.bin"\n\n\nThis product contains cryptographic features and is subject to United\nStates and local country laws governing import, export, transfer and\nuse. Delivery of Cisco cryptographic products does not imply\nthird-party authority to import, export, distribute or use encryption.\nImporters, exporters, distributors and users are responsible for\ncompliance with U.S. and local country laws. By using this product you\nagree to comply with applicable laws and regulations. If you are unable\nto comply with U.S. and local laws, return this product immediately.\n\nA summary of U.S. laws governing Cisco cryptographic products may be found at:\nhttp://www.cisco.com/wwl/export/crypto/tool/stqrg.html\n\nIf you require further assistance please contact us by sending email to\nexport@cisco.com.\n\nCisco 2821 (revision 53.51) with 245760K/16384K bytes of memory.\nProcessor board ID FCZ120670NF\n2 Gigabit Ethernet interfaces\n1 Virtual Private Network (VPN) Module\nDRAM configuration is 64 bits wide with parity enabled.\n239K bytes of non-volatile configuration memory.\n62720K bytes of ATA CompactFlash (Read/Write)\n\nConfiguration register is 0x2102\n\n'}
    snmp_get={}
    snmp_getnext={}
        
