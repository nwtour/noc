# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Axis.VAPIX.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Axis.VAPIX.get_version"
    interface = IGetVersion
    cache = True

    def execute(self):
        c = self.profile.get_dict(self)
        """
        root.Brand.Brand=AXIS
        root.Brand.ProdFullName=AXIS 211 Network Camera
        root.Brand.ProdShortName=AXIS 211
        root.Brand.ProdNbr=211
        root.Brand.ProdType=Network Camera
        root.Brand.WebURL=http://www.axis.com/
        """
        platform = c.get("root.Brand.ProdNbr")  # I don't sure
        version = c.get("root.Properties.Firmware.Version")
        serial = c.get("root.Properties.System.SerialNumber")

        r = {
            "vendor": 'Axis',
            "platform": platform,
            "version": version
        }
        if serial:
            r["attributes"] = {}
            r["attributes"]["Serial Number"] = serial

        return r
