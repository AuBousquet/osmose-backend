# -*- coding: utf-8 -*-

###########################################################################
#                                                                       ##
# Copyrights Frederic Rodrigo 2014-2015                                 ##
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


class TagRemove_Layer(Plugin):

    def init(self, logger):
        Plugin.init(self, logger)
        self.errors[41101] = self.def_class(
            item=4110,
            level=3,
            tags=["landuse", "fix:chair"],
            title=T_("Landuse feature not on ground"),
        )
        self.errors[41102] = self.def_class(
            item=4110,
            level=3,
            tags=["natural", "fix:chair"],
            title=T_("Natural feature underground"),
        )
        self.errors[41103] = self.def_class(
            item=4110,
            level=3,
            tags=["highway", "fix:chair"],
            title=T_("Highway underground and no tunnel"),
        )
        self.errors[41104] = self.def_class(
            item=4110,
            level=2,
            tags=["highway", "fix:chair"],
            title=T_("Long Highway underground and no tunnel"),
        )
        self.errors[41105] = self.def_class(
            item=4110,
            level=3,
            tags=["highway", "fix:chair"],
            title=T_("Highway above ground and no bridge"),
        )
        self.errors[41106] = self.def_class(
            item=4110,
            level=2,
            tags=["highway", "fix:chair"],
            title=T_("Long Highway above ground and no bridge"),
        )
        self.errors[41107] = self.def_class(
            item=4110,
            level=3,
            tags=["highway", "fix:chair"],
            title=T_("Waterway/water underground and no tunnel"),
        )
        self.errors[41108] = self.def_class(
            item=4110,
            level=2,
            tags=["highway", "fix:chair"],
            title=T_("Long Waterway/water underground and no tunnel"),
        )
        self.errors[41109] = self.def_class(
            item=4110,
            level=3,
            tags=["highway", "fix:chair"],
            title=T_("Waterway/water above ground and no bridge"),
        )
        self.errors[41100] = self.def_class(
            item=4110,
            level=2,
            tags=["highway", "fix:chair"],
            title=T_("Long Waterway/water above ground and no bridge"),
        )

    def way(self, data, tags, nds):
        if tags.get("layer") and tags.get("layer") != "0":
            layer = tags.get("layer")
            if tags.get("landuse"):
                return {"class": 41101, "subclass": 0}
            elif (
                tags.get("natural")
                and layer[0] == "-"
                and tags.get("natural") != "water"
            ):
                return {"class": 41102, "subclass": 0}
            elif (
                tags.get("highway")
                and tags.get("highway") != "steps"
                and (not tags.get("indoor") or tags.get("indoor") == "no")
            ):
                if layer[0] == "-" and (
                    not tags.get("tunnel") or tags.get("tunnel") == "no"
                ):
                    return {"class": 41104 if len(nds) > 3 else 41103, "subclass": 0}
                elif (
                    layer[0] != "-"
                    and (not tags.get("bridge") or tags.get("bridge") == "no")
                    and tags.get("man_made") != "pier"
                    and tags.get("location") != "roof"
                ):
                    if len(nds) > 3:
                        return {"class": 41106, "subclass": 0, "fix": {"-": ["layer"]}}
                    else:
                        return {
                            "class": 41105,
                            "subclass": 0,
                            "fix": {"+": {"bridge": "yes"}},
                        }
            elif tags.get("waterway") or (
                (tags.get("natural") and tags.get("natural") == "water")
            ):
                if (
                    layer[0] == "-"
                    and (not tags.get("tunnel") or tags.get("tunnel") == "no")
                    and (
                        not tags.get("location")
                        or tags.get("location") != "underground"
                    )
                ):
                    if len(nds) > 3:
                        return {"class": 41108, "subclass": 0, "fix": {"-": ["layer"]}}
                    else:
                        return {"class": 41107, "subclass": 0}
                elif layer[0] != "-" and (
                    not tags.get("bridge") or tags.get("bridge") == "no"
                ):
                    return {"class": 41100 if len(nds) > 3 else 41109, "subclass": 0}


###########################################################################
from plugins.Plugin import TestPluginCommon


class Test(TestPluginCommon):
    def test(self):
        a = TagRemove_Layer(None)
        a.init(None)
        assert not a.way(None, {"layer": "-1"}, None)
        self.check_err(a.way(None, {"layer": "-1", "landuse": "forest"}, None))
        assert not a.way(None, {"layer": "1", "natural": "wood"}, None)
        self.check_err(a.way(None, {"layer": "-1", "natural": "tree"}, None))

        # highway
        self.check_err(a.way(None, {"layer": "-1", "highway": "service"}, [1, 2, 3, 4]))
        # highway with tunnel
        assert not a.way(
            None, {"layer": "-1", "tunnel": "yes", "highway": "service"}, None
        )
        self.check_err(
            a.way(None, {"layer": "-1", "tunnel": "no", "highway": "service"}, [1, 2])
        )
        self.check_err(
            a.way(None, {"layer": "1", "tunnel": "yes", "highway": "service"}, [1, 2])
        )
        self.check_err(
            a.way(None, {"layer": "1", "tunnel": "no", "highway": "service"}, [1, 2])
        )
        # highway with bridge
        self.check_err(
            a.way(
                None,
                {"layer": "-1", "bridge": "no", "highway": "service"},
                [1, 2, 3, 4],
            )
        )
        self.check_err(
            a.way(
                None,
                {"layer": "-1", "bridge": "yes", "highway": "service"},
                [1, 2, 3, 4],
            )
        )
        self.check_err(
            a.way(None, {"layer": "-1", "bridge": "yes", "highway": "service"}, [1, 2])
        )
        assert not a.way(
            None, {"layer": "1", "bridge": "yes", "highway": "service"}, None
        )
        self.check_err(
            a.way(
                None, {"layer": "1", "bridge": "no", "highway": "service"}, [1, 2, 3, 4]
            )
        )
        # other highways
        assert not a.way(
            None, {"layer": "-1", "indoor": "yes", "highway": "service"}, None
        )
        assert not a.way(None, {"layer": "-1", "highway": "steps"}, None)
        # waterways/water
        assert not a.way(
            None,
            {"layer": "1", "bridge": "aqueduct", "waterway": "canal"},
            [1, 2, 3, 4, 5],
        )
        assert not a.way(
            None, {"layer": "-1", "tunnel": "culvert", "natural": "water"}, [1, 2]
        )
        self.check_err(a.way(None, {"layer": "-1", "waterway": "ditch"}, [1, 2, 3]))
        self.check_err(
            a.way(None, {"layer": "1", "natural": "water"}, [1, 2, 3, 4, 5, 6])
        )
        assert not a.way(
            None,
            {"layer": "-1", "waterway": "pressurised", "location": "underground"},
            [1, 2],
        )
