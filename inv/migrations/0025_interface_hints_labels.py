# ----------------------------------------------------------------------
# Create interface hints labels scope
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pymongo import InsertOne

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Create wildcard labels
        l_coll = self.mongo_db["labels"]
        current_labels = {ll["name"]: ll["_id"] for ll in l_coll.find()}
        bulk = []
        if "noc::topology::direction::*" not in current_labels:
            bulk += [
                InsertOne(
                    {
                        "name": "noc::topology::direction::*",
                        "description": "Builtin Labels Scope for Interface topology direction: uplink or downlink",
                        "bg_color1": 2719929,
                        "fg_color1": 16777215,
                        "bg_color2": 9323693,
                        "fg_color2": 16777215,
                        "propagate": True,
                        "is_protected": False,
                        "is_autogenerated": False,
                        "enable_interface": True,
                    }
                )
            ]
        if "noc::interface::role::*" not in current_labels:
            bulk += [
                InsertOne(
                    {
                        "name": "noc::interface::role::*",
                        "description": "Builtin Labels Scope for Interface role: nni or uni",
                        "bg_color1": 15965202,
                        "fg_color1": 16777215,
                        "bg_color2": 9323693,
                        "fg_color2": 16777215,
                        "propagate": True,
                        "is_protected": False,
                        "is_autogenerated": False,
                        "enable_interface": True,
                    }
                )
            ]
        if "noc::interface::hints::*" not in current_labels:
            bulk += [
                InsertOne(
                    {
                        "name": "noc::interface::hints::*",
                        "description": "Builtin Labels Scope for Interface hints",
                        "bg_color1": 15965202,
                        "fg_color1": 16777215,
                        "bg_color2": 9323693,
                        "fg_color2": 16777215,
                        "propagate": True,
                        "is_protected": False,
                        "is_autogenerated": False,
                        "enable_interface": True,
                    }
                )
            ]
        if "noc::sensor::mode::*" not in current_labels:
            bulk += [
                InsertOne(
                    {
                        "name": "noc::sensor::mode::*",
                        "description": "Builtin Labels Scope for Sensor mode hints: temperature, voltage, current, impedance, frequence, counter",
                        "bg_color1": 15965202,
                        "fg_color1": 16777215,
                        "bg_color2": 9323693,
                        "fg_color2": 16777215,
                        "propagate": True,
                        "is_protected": False,
                        "is_autogenerated": False,
                        "enable_sensor": True,
                    }
                )
            ]
        if "noc::sensor::placement::*" not in current_labels:
            bulk += [
                InsertOne(
                    {
                        "name": "noc::sensor::placement::*",
                        "description": "Builtin Labels Scope for Sensor placement hints: internal, external, ups",
                        "bg_color1": 2719929,
                        "fg_color1": 16777215,
                        "bg_color2": 9323693,
                        "fg_color2": 16777215,
                        "propagate": True,
                        "is_protected": False,
                        "is_autogenerated": False,
                        "enable_sensor": True,
                    }
                )
            ]
        if bulk:
            l_coll.bulk_write(bulk, ordered=True)