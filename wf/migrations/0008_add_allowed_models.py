# ----------------------------------------------------------------------
# Add Allowed Models to workflow
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        # Moved to 0009 for fixed bad typo
        pass
