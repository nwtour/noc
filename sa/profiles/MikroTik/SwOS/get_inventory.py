# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.SwOS.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import codecs

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "MikroTik.SwOS.get_inventory"
    interface = IGetInventory

    def execute_cli(self):
        r = []
        v = self.scripts.get_version()
        r += [
            {
                "type": "CHASSIS",
                "vendor": "MikroTik",
                "part_no": [v["platform"]],
                "serial": v["attributes"]["Serial Number"],
            }
        ]
        sfps = self.profile.parseBrokenJson(self.http.get("/sfp.b", cached=True, eof_mark="}"))
        if sfps.get("vnd"):
            sfp_count = len(sfps["vnd"])
            for i in range(0, sfp_count):
                vendor = codecs.decode(sfps["vnd"][i], "hex").strip()
                part_no = codecs.decode(sfps["pnr"][i], "hex").strip()
                revision = codecs.decode(sfps["rev"][i], "hex").strip()
                serial = codecs.decode(sfps["ser"][i], "hex").strip()
                date = codecs.decode(sfps["dat"][i], "hex").strip()
                dt = date.split("-")
                year = "20" + dt[0]
                parts = [year, dt[1], dt[2]]
                mfd = "-".join(parts)

                descr = codecs.decode(sfps["typ"][i], "hex").strip()
                r += [
                    {
                        "type": "XCVR",
                        "vendor": vendor,
                        "serial": serial,
                        "part_no": [part_no],
                        "number": i,
                        "revision": revision,
                        "description": descr,
                        "mfg_date": mfd,
                    }
                ]
        elif sfps.get("vndr"):
            vendor = codecs.decode(sfps["vndr"], "hex").strip()
            part_no = codecs.decode(sfps["ptnr"], "hex").strip()
            revision = codecs.decode(sfps["rev"], "hex").strip()
            serial = codecs.decode(sfps["ser"], "hex").strip()
            date = codecs.decode(sfps["date"], "hex").strip()
            dt = date.split("-")
            year = "20" + dt[0]
            parts = [year, dt[1], dt[2]]
            mfd = "-".join(parts)
            r += [
                {
                    "type": "XCVR",
                    "vendor": vendor,
                    "serial": serial,
                    "part_no": [part_no],
                    "number": 1,
                    "revision": revision,
                    "mfg_date": mfd,
                }
            ]
        return r
