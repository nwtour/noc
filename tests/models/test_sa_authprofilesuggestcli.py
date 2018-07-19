# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# sa.AuthProfileSuggestCLI tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseModelTest
from noc.sa.models.authprofile import AuthProfileSuggestCLI


class TestTestSaAuthProfileSuggestCLI(BaseModelTest):
    model = AuthProfileSuggestCLI