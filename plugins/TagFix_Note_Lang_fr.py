# -*- coding: utf-8 -*-

###########################################################################
#                                                                       ##
# Copyrights Frederic Rodrigo 2012                                      ##
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
import unicodedata

from modules.OsmoseTranslation import T_
from plugins.Plugin import Plugin


class TagFix_Note_Lang_fr(Plugin):

    only_for = ["fr"]

    def normalize(self, s):
        return "".join(
            (
                c
                for c in unicodedata.normalize("NFD", s)
                if unicodedata.category(c) != "Mn"
            )
        ).lower()

    def init(self, logger):
        Plugin.init(self, logger)
        self.errors[3110] = self.def_class(
            item=3110,
            level=3,
            tags=["fixme", "fix:chair"],
            title=T_("Possible improvement for note or comment tag"),
            detail=T_(
                """Analyzes the tag `note=*` with French and English keywords."""
            ),
            fix=T_(
                """Use a more appropriate tag as `description=*`, `opening_hours=*` or
`fixme=*` so it can be found more easily."""
            ),
            trap=T_("""The analysis can provide crazy result."""),
        )

        self.FixmeFull = (
            "fix me",
            "grosso modo",
            "note de memoire",
        )
        self.FixmeWord = (
            "?",
            "accurate",
            "approximatif",
            "approximation",
            "approximativement",
            "attendre",
            "bad",
            "check",
            "checkme",
            "completer",
            "corriger",
            "crappy",
            "draft",
            "effacer",
            "estimation",
            "exact",
            "gourre",
            "incomplete",
            "renderers",
            "rendering",
            "semblant",
            "semble",
            "tag",
            "tagged",
            "tagguer",
            "todo",
            "uncertain",
            "verified",
            "verifier",
            "wip",
        )
        self.Opening_hours = (
            "lundi",
            "mardi",
            "mercredi",
            "jeudi",
            "vendredi",
            "samedi",
            "dimanche",
            "janvier",
            "fevrier",
            "mars",
            "avril",
            "mai",
            "juin",
            "juillet",
            "aout",
            "septembre",
            "octobre",
            "novembre",
            "decembre",
        )
        self.Destruction = (
            "ferme",
            "fermee",
            "ancien",
            "ancienne",
            "brule",
            "brulee",
            "burn",
            "closed",
            "declasse",
            "declassee",
            "demoli",
            "demolished",
            "demolition",
            "destroyed",
            "detruit",
            "no_longer",
            "rase",
            "rasee",
        )
        self.Construction = ("construction", "travaux", "ouvert", "ouverture")
        self.TagFull = (
            "arret de bus",
            "http://",
            "maison de retraite",
            "reserve naturelle",
            "salle des fetes",
            "voies de service",
            "zone 30",
        )
        self.TagWord = (
            "football",
            "basket",
            "bassin",
            "canal",
            "cyclable",
            "ecluse",
            "ehpad",
            "entree",
            "etang",
            "garages",
            "gare",
            "gendarmerie",
            "gynmase",
            "halles",
            "handball",
            "hangar",
            "jardin",
            "piste",
            "plot",
            "prairie",
            "prive",
            "ruin",
            "ruine",
            "sortie",
            "tel",
            "toilettes",
            "transformateur",
            "verger",
            "volley",
        )
        self.Hours = re.compile(r"[0-9]{1,2}h")
        self.Date = re.compile(r"[0-9]{4,8}|(?:(?:[0-9]{1,2}/){2}/[0-9]{2,4})")
        self.Split = re.compile(r"[- _\(\),.:/" '"+!;<>=\[\]]')  # noqa

    def node(self, data, tags):
        if "note" not in tags and "comment" not in tags:
            return

        for t in ("note", "comment"):
            if t not in tags:
                continue
            if (
                "http://wiki.openstreetmap.org" in tags[t] or "CLC import" in tags[t]
            ):  # Skip French man_made=survey_point note tag
                continue
            tt = self.normalize(tags[t])
            words = re.split(self.Split, tt)
            # Add FIXME on note tag
            if "FIXME" not in tags and (
                "note" not in tags or "fixme" not in tags["note"].lower()
            ):
                for w in self.FixmeFull:
                    if w in tt:
                        return {
                            "class": 3110,
                            "subclass": 100,
                            "text": T_('note tag needs FIXME: "{0}"', tags[t]),
                            "fix": {"note": "FIXME {0}".format(tags[t])},
                        }
                for w in self.FixmeWord:
                    if w in words:
                        return {
                            "class": 3110,
                            "subclass": 101,
                            "text": T_('note tag needs FIXME: "{0}"', tags[t]),
                            "fix": {"note": "FIXME {0}".format(tags[t])},
                        }
            # Destruction
            if (
                "end_date" not in tags
                and "historic" not in tags
                and "disused" not in tags
                and "abandoned" not in tags
            ):
                for w in self.Destruction:
                    if w in tt:
                        return {
                            "class": 3110,
                            "subclass": 500,
                            "text": T_('Use a tag to specify end: "{0}"', tags[t]),
                        }
            # start_date
            if "start_date" not in tags:
                if self.Date.match(tt) or "siecle" in tt:
                    return {
                        "class": 3110,
                        "subclass": 300,
                        "text": T_('Use start_date tag for "{0}"', tags[t]),
                    }
            # opening_hours
            if "opening_hours" not in tags:
                if self.Hours.match(tt):
                    return {
                        "class": 3110,
                        "subclass": 200,
                        "text": T_('Use opening_hours tag for "{0}"', tags[t]),
                    }
                for w in self.Opening_hours:
                    if w in words:
                        return {
                            "class": 3110,
                            "subclass": 201,
                            "text": T_('Use opening_hours tag for "{0}"', tags[t]),
                        }
            # construction
            if "construction" not in tags:
                for w in self.Construction:
                    if w in words:
                        return {
                            "class": 3110,
                            "subclass": 400,
                            "text": T_('Use construction tag for "{0}"', tags[t]),
                        }
            # an other tag
            for w in self.TagFull:
                if w in tt:
                    return {
                        "class": 3110,
                        "subclass": 900,
                        "text": T_('"{0}" can be set in specific tag', tags[t]),
                    }
            for w in self.TagWord:
                if w in words:
                    return {
                        "class": 3110,
                        "subclass": 901,
                        "text": T_('"{0}" can be set in specific tag', tags[t]),
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
        self.p = TagFix_Note_Lang_fr(None)
        self.p.init(None)

    note_gen_err = [
        "fix me",
        "a corriger",
        "Du lundi au vendredi",
        "9h-12h/14h-17h",
        "20091211",
        "travaux",
        "Salle des Fêtes",
        "gendarmerie",
        "See http://gpvlyonduchere",
        "demolished",
    ]
    note_gen_no_err = [
        "http://wiki.openstreetmap.org fix me",
        "CLC import fix me",
        "juste une note",
    ]

    def test_node(self):
        assert not self.p.node(None, {}), "node with no note"
        for d in self.note_gen_err:
            self.check_err(
                self.p.node(None, {"note": d}), ("node with note='{0}'".format(d))
            )
        for d in self.note_gen_no_err:
            assert not self.p.node(None, {"note": d}), "node with note='{0}'".format(d)

    def test_way(self):
        assert not self.p.way(None, {}, []), "way with no note"
        for d in self.note_gen_err:
            self.check_err(
                self.p.way(None, {"note": d}, []), ("way with note='{0}'".format(d))
            )
        for d in self.note_gen_no_err:
            assert not self.p.way(None, {"note": d}, []), "way with note='{0}'".format(
                d
            )

    def test_relation(self):
        assert not self.p.relation(None, {}, []), "relation with no note"
        for d in self.note_gen_err:
            self.check_err(
                self.p.relation(None, {"note": d}, []),
                ("relation with note='{0}'".format(d)),
            )
        for d in self.note_gen_no_err:
            assert not self.p.relation(
                None, {"note": d}, []
            ), "relation with note='{0}'".format(d)
