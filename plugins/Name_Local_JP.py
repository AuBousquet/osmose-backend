# -*- coding: utf-8 -*-

###########################################################################
#                                                                       ##
# Copyrights Frédéric Rodrigo 2016                                      ##
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


class Name_Local_JP(Plugin):

    only_for = ["JA"]

    def init(self, logger):
        Plugin.init(self, logger)
        self.errors[50604] = self.def_class(
            item=5060,
            level=1,
            tags=["name", "fix:chair"],
            title=T_("Default and local language name not the same"),
        )
        self.errors[50605] = self.def_class(
            item=5060,
            level=1,
            tags=["name", "fix:chair"],
            title=T_("Local language name without default name"),
        )
        self.errors[50606] = self.def_class(
            item=5060,
            level=1,
            tags=["name", "fix:chair"],
            title=T_("Language name without default name"),
        )

        self.LocalName = re.compile("^name:[a-z][a-z](_.*$|$)")

    def node(self, data, tags):
        if "boundary" in tags:
            return

        default = tags.get("name")
        ja = tags.get("name:ja")
        en = tags.get("name:en")

        if default or ja or en:
            if default:
                if (ja or en) and not (
                    default == ja
                    or default == en
                    or (ja and en and default == "{0} ({1})".format(ja, en))
                ):
                    return {"class": 50604, "subclass": 0}
            elif ja or en:
                return {
                    "class": 50605,
                    "subclass": 0,
                    "fix": [{"+": {"name": ja}}, {"+": {"name": en}}],
                }
        else:
            locales = map(
                lambda y: [{"+": {"name": tags[y]}}],
                filter(lambda x: self.LocalName.match(x), tags.keys()),
            )
            if locales:
                return {"class": 50606, "subclass": 0, "fix": locales}

    def way(self, data, tags, nds):
        return self.node(data, tags)

    def relation(self, data, tags, members):
        return self.node(data, tags)


###########################################################################
from plugins.Plugin import TestPluginCommon


class Test(TestPluginCommon):
    def test_ja(self):
        a = Name_Local_JP(None)

        class _config:
            options = {"country": "JP"}

        class father:
            config = _config()

        a.father = father()
        a.init(None)

        assert a.node(None, {"name": "沖浦 (Okiura)", "name:ja": "沖浦"})
        assert a.node(
            None,
            {
                "name": "セブン−イレブン東城川東店",
                "name:ja": "セブン-イレブン",
                "name:en": "Seven-Eleven",
            },
        )
        assert a.node(None, {"name:ja": "沖浦"})
        assert a.node(None, {"name:it": "Plop"})
        assert not a.node(
            None,
            {
                "name": "広島県道75号三原竹原線 (Route Mihara Takehara)",
                "name:ja": "広島県道75号三原竹原線",
                "name:en": "Route Mihara Takehara",
            },
        )
        assert not a.node(
            None, {"name": "ENEOS", "name:ja": "エネオス", "name:en": "ENEOS"}
        )
        assert not a.node(None, {"name": "沖浦", "name:ja": "沖浦"})
        assert not a.node(None, {"name": "沖浦"})
