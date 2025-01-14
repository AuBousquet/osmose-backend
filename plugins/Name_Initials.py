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

from modules.OsmoseTranslation import T_
from plugins.Plugin import Plugin


class Name_Initials(Plugin):

    def init(self, logger):
        Plugin.init(self, logger)
        self.errors[902] = self.def_class(
            item=5010,
            level=3,
            tags=["name", "fix:chair"],
            title=T_("Initial stuck to the name"),
        )

        import re

        self.ReInitColleNom = re.compile(r"^(.*[A-Z]\.)([A-Z][a-z].*)$")

    def node(self, data, tags):
        if "name" in tags:
            name = tags["name"]
            r = self.ReInitColleNom.match(name)
            if r:  # and not u"E.Leclerc" in self._DataTags[u"name"]:
                return {
                    "class": 902,
                    "subclass": 0,
                    "text": {"en": tags["name"]},
                    "fix": {"name": "{0} {1}".format(r.group(1), r.group(2))},
                }

    def way(self, data, tags, nds):
        return self.node(data, tags)

    def relation(self, data, tags, members):
        return self.node(data, tags)


###########################################################################
from plugins.Plugin import TestPluginCommon


class Test(TestPluginCommon):
    def setUp(self):
        TestPluginCommon.setUp(self)
        self.p = Name_Initials(None)
        self.p.init(None)

    def test(self):
        self.check_err(self.p.node(None, {"name": "A.Bsuaeuae"}))
        self.check_err(self.p.way(None, {"name": "C.Dkuaeu"}, None))
        assert not self.p.relation(None, {"name": "E. Fiuaeuie"}, None)
        assert not self.p.node(None, {"name": "G.H."})
        assert not self.p.node(None, {"name": "GeHaueue"})
