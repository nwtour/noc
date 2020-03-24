# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# IfNameCollator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
import six

# NOC modules
from .base import BaseCollator


class IfNameCollator(BaseCollator):
    """
    Direct map between connection name and interface name
    """

    def __init__(self):
        super(IfNameCollator, self).__init__()
        self.names = None

    def collate(self, physical_path, interfaces):
        if not self.names:
            # Interface name
            self.names = {self.name_hash(if_name): if_name for if_name in interfaces}
            # Default name, if any
            for if_name, iface in six.iteritems(interfaces):
                if iface.default_name:
                    self.names[self.name_hash(iface.default_name)] = if_name
        cn = self.name_hash(physical_path[-1].connection.name)
        if_name = self.names.get(cn)
        if if_name:
            return if_name
        # internal name
        if physical_path[-1].connection.internal_name:
            cn = self.name_hash(physical_path[-1].connection.name)
            return self.names.get(cn)
        return None

    @staticmethod
    def name_hash(s):
        """
        Normalized interface name hash
        :param s:
        :return:
        """
        return s.replace(" ", "").lower()
