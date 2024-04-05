# -*- coding: utf-8 -*-

###########################################################################
#                                                                       ##
# Copyrights Etienne Chové <chove@crans.org> 2009                       ##
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


class Name_Spaces(Plugin):

    def init(self, logger):
        Plugin.init(self, logger)
        self.errors[903] = self.def_class(
            item=5010, level=2, tags=["name", "fix:chair"], title=T_("Too many spaces")
        )

    def node(self, data, tags):
        if "name" not in tags:
            return

        err = []
        name = tags["name"]
        if "  " in name:
            err.append(
                {
                    "class": 903,
                    "subclass": 0,
                    "text": T_("Name contains successive spaces"),
                }
            )
        if name.endswith(" "):
            err.append(
                {"class": 903, "subclass": 1, "text": T_("Name ends with a space")}
            )
        if name.startswith(" "):
            err.append(
                {"class": 903, "subclass": 2, "text": T_("Name begins with a space")}
            )

        if len(err) > 0:
            name = re.sub(r" +", " ", name.strip())
            for e in err:
                e["fix"] = {"name": name}

        return err

    def way(self, data, tags, nds):
        return self.node(data, tags)

    def relation(self, data, tags, members):
        return self.node(data, tags)


###########################################################################
from plugins.Plugin import TestPluginCommon


class Test(TestPluginCommon):
    def test(self):
        a = Name_Spaces(None)
        a.init(None)
        for name in [
            "ertaue u",
            "",
            "auieaue",
            "éeuguiqe",
        ]:
            assert not a.node(None, {"name": name}), name

        for name in [
            "    uertaue u   ",
            "   ",
            " auieaue",
            "éeuguiqe ",
            "a  b",
        ]:
            assert not a.node(None, {"highway": name}), name
            self.check_err(a.node(None, {"name": name}), name)
            self.check_err(a.way(None, {"name": name}, None), name)
            self.check_err(a.relation(None, {"name": name}, None), name)
