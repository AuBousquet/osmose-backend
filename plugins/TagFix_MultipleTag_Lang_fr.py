# -*- coding: utf-8 -*-

###########################################################################
#                                                                       ##
# Copyrights Frédéric Rodrigo 2011                                      ##
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


class TagFix_MultipleTag_Lang_fr(Plugin):

    only_for = ["fr"]

    def init(self, logger):
        Plugin.init(self, logger)
        self.errors[3032] = self.def_class(
            item=3032,
            level=1,
            tags=["tag", "fix:chair"],
            title=T_("Watch multiple tags"),
        )

        import re

        self.Eglise = re.compile(
            "(.glise|chapelle|basilique|cath.drale) de .*", re.IGNORECASE
        )
        self.EgliseNot1 = re.compile(
            "(.glise|chapelle|basilique|cath.drale) de la .*", re.IGNORECASE
        )
        self.EgliseNot2 = re.compile(
            "(.glise|chapelle|basilique|cath.drale) de l'.*", re.IGNORECASE
        )
        self.MonumentAuxMorts = re.compile("monument aux morts.*", re.IGNORECASE)
        self.SalleDesFetes = re.compile(".*salle des f.tes.*", re.IGNORECASE)
        self.MaisonDeQuartier = re.compile(".*maison de quartier.*", re.IGNORECASE)
        self.Marche = re.compile("marché( .+)?", re.IGNORECASE)

    def node(self, data, tags):
        err = []

        if "name" not in tags:
            return err

        if "amenity" in tags:
            if tags["amenity"] == "place_of_worship":
                if (
                    self.Eglise.match(tags["name"])
                    and not self.EgliseNot1.match(tags["name"])
                    and not self.EgliseNot2.match(tags["name"])
                ):
                    err.append(
                        {
                            "class": 3032,
                            "subclass": 1,
                            "text": T_(
                                '"name={0}" is the localisation but not the name',
                                tags["name"],
                            ),
                        }
                    )
        else:
            if (
                "shop" not in tags
                and "public_transport" not in tags
                and self.Marche.match(tags["name"])
            ):
                err.append(
                    {"class": 3032, "subclass": 5, "fix": {"amenity": "marketplace"}}
                )

        if "historic" in tags:
            if tags["historic"] == "monument":
                if self.MonumentAuxMorts.match(tags["name"]):
                    err.append(
                        {
                            "class": 3032,
                            "subclass": 2,
                            "text": T_("A war memorial is not a historic=monument"),
                            "fix": {"historic": "memorial"},
                        }
                    )

        if (
            (
                "highway" not in tags
                and "public_transport" not in tags
                and "leisure" not in tags
                and ("type" not in tags or tags["type"] != "associatedStreet")
            )
            and (
                self.SalleDesFetes.match(tags["name"])
                or self.MaisonDeQuartier.match(tags["name"])
            )
            and not ("amenity" in tags and tags["amenity"] == "community_centre")
        ):
            err.append(
                {
                    "class": 3032,
                    "subclass": 3,
                    "text": T_("Put a tag for a village hall or a community centre"),
                    "fix": {"+": {"amenity": "community_centre"}},
                }
            )

        return err

    def way(self, data, tags, nds):
        return self.node(data, tags)

    def relation(self, data, tags, members):
        return self.node(data, tags)


###########################################################################
from plugins.Plugin import TestPluginCommon


class Test(TestPluginCommon):
    def test(self):
        a = TagFix_MultipleTag_Lang_fr(None)

        class _config:
            options = {"language": "fr"}

        class father:
            config = _config()

        a.father = father()
        a.init(None)
        for t in [
            {"amenity": "place_of_worship", "name": "Église de Paris"},
            {"amenity": "place_of_worship", "name": "Cathédrale de Notre-Dame"},
            {"name": "Marché des Capucines"},
            {"historic": "monument", "name": "Monument aux morts du quartier"},
            {"name": "Salle des fêtes"},
            {"name": "Maison de quartier"},
        ]:
            self.check_err(a.node(None, t), t)
            self.check_err(a.way(None, t, None), t)
            self.check_err(a.relation(None, t, None), t)

        for t in [
            {"amenity": "place_of_worship", "name": "Église de l'endroit"},
            {"shop": "yes", "name": "Marché des Capucines"},
            {"amenity": "place_of_worship"},
            {"historic": "yes", "name": "Monument aux morts du quartier"},
            {"historic": "monument", "name": "Monument typique du quartier"},
            {"highway": "primary", "name": "Salle des fêtes"},
            {"highway": "residential", "name": "Maison de quartier"},
            {"amenity": "community_centre", "name": "Salle des fêtes"},
            {"amenity": "community_centre", "name": "Maison de quartier"},
            {"type": "associatedStreet", "name": "Rue de la Salle des Fêtes"},
            {"leisure": "park", "name": "Rue de la Salle des Fêtes"},
        ]:
            assert not a.way(None, t, None), t
