# -*- coding: utf-8 -*-

###########################################################################
#                                                                       ##
# Copyrights Frédéric Rodrigo 2012                                      ##
#                                                                       ##
# This program is free software: you can redistribute it and/or modify  ##
# it under the terms of the GNU General Public License as published by  ##
# the Free Software Foundation, either version 3 of the License, or     ##
# (at your option) any later version.                                   ##
#                                                                       ##
# This program is distributed in the hope that it will be useful,       ##
# but WITHOUT ANY WARRANTY; without even the implied warranty of        ##
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         ##
# GNU General Public License for more details.                          ##
#                                                                       ##
# You should have received a copy of the GNU General Public License     ##
# along with this program.  If not, see <http://www.gnu.org/licenses/>. ##
#                                                                       ##
###########################################################################

import re

from modules.OsmoseTranslation import T_
from plugins.Plugin import Plugin


class TagFix_Role(Plugin):

    def init(self, logger):
        Plugin.init(self, logger)
        self.errors[31700] = self.def_class(
            item=3170,
            level=2,
            tags=["relation", "fix:chair"],
            title=T_("Inadequate role"),
            detail=T_("""The role is not a keyword as expected."""),
            fix=T_(
                """Determine the right role, possibly set the value of the role in a
tag."""
            ),
        )

        self.Role = re.compile("^[a-z_:]*$")

    def relation(self, data, tags, members):
        roles = []
        for member in members:
            if not self.Role.match(member["role"]):
                roles.append(member["role"])

        if len(roles) > 0:
            return {
                "class": 31700,
                "subclass": 1,
                "text": {"en": "role={0}".format(", ".join(roles))},
            }


###########################################################################
from plugins.Plugin import TestPluginCommon


class Test(TestPluginCommon):
    def test(self):
        a = TagFix_Role(None)
        a.init(None)
        self.check_err(a.relation(None, None, [{"role": "<std>"}, {"role": "$$"}]))
