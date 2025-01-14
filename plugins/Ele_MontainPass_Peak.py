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


class Ele_MontainPass_Peak(Plugin):

    def init(self, logger):
        Plugin.init(self, logger)
        self.errors[804] = self.def_class(
            item=2020,
            level=3,
            tags=["tag", "fix:survey"],
            title=T_("Missing altitude"),
            detail=T_(
                """Some elements, including the peak (natural=peak) and mountain_pass
(mountain_pass=yes), has an elevation. This is shown in OSM with tag
ele=* in meters."""
            ),
            fix=T_("""Complete the tag ele=* missing."""),
        )

    def node(self, data, tags):
        err = []
        if tags.get("mountain_pass") in ["yes", "1"] and "ele" not in tags:
            err.append({"class": 804, "subclass": 0})
        if tags.get("natural") in ["peak"] and "ele" not in tags:
            err.append({"class": 804, "subclass": 1})
        return err

    def way(self, data, tags, nds):
        return self.node(data, tags)


###########################################################################
from plugins.Plugin import TestPluginCommon


class Test(TestPluginCommon):
    def test(self):
        a = Ele_MontainPass_Peak(None)
        a.init(None)
        for t in [
            {"mountain_pass": "yes"},
            {"mountain_pass": "1"},
            {"natural": "peak"},
        ]:
            self.check_err(a.node(None, t), t)
            self.check_err(a.way(None, t, None), t)

        for t in [
            {"highway": "trunk"},
            {"mountain_pass": "no"},
            {"mountain_pass": "-1"},
            {"mountain_pass": "yes", "ele": "1000"},
            {"natural": "peak", "ele": "1000"},
        ]:
            assert not a.node(None, t), t
