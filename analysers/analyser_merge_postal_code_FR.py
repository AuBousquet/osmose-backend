#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
#                                                                       #
# Copyrights Frédéric Rodrigo 2014-2016                                 #
#                                                                       #
# This program is free software: you can redistribute it and/or modify  #
# it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 3 of the License, or     #
# (at your option) any later version.                                   #
#                                                                       #
# This program is distributed in the hope that it will be useful,       #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
# GNU General Public License for more details.                          #
#                                                                       #
# You should have received a copy of the GNU General Public License     #
# along with this program.  If not, see <http://www.gnu.org/licenses/>. #
#                                                                       #
#########################################################################

from modules.OsmoseTranslation import T_

from .Analyser_Merge import (
    CSV,
    Analyser_Merge_Point,
    Conflate,
    Load_XY,
    Mapping,
    Select,
    SourceDataFair,
)


class Analyser_Merge_Postal_Code_FR(Analyser_Merge_Point):
    def __init__(self, config, logger=None):
        Analyser_Merge_Point.__init__(self, config, logger)
        self.def_class_missing_osm(
            item=7160,
            id=2,
            level=3,
            tags=["merge", "post", "fix:chair"],
            title=T_('admin_level 8 without tag "postal_code"'),
        )
        self.def_class_possible_merge(
            item=8221,
            id=3,
            level=3,
            tags=["merge", "post", "fix:chair"],
            title=T_("Postal code, integration suggestion"),
        )

        self.init(
            "https://datanova.laposte.fr/datasets/laposte-hexasmal",
            "Base officielle des codes postaux",
            CSV(
                SourceDataFair(
                    attribution="La Poste",
                    url="https://datanova.laposte.fr/datasets/laposte-hexasmal",
                    file_name="019HexaSmal.csv",
                    encoding="LATIN1",
                ),
                srid=False,
            ),
            Load_XY(),
            Conflate(
                select=Select(
                    types=["relations"],
                    tags={"type": "boundary", "admin_level": "8", "ref:INSEE": None},
                ),
                osmRef="postal_code",
                extraJoin="ref:INSEE",
                mapping=Mapping(
                    static2={"source:postal_code": self.source},
                    mapping1={
                        "ref:INSEE": "#Code_commune_INSEE",
                        "postal_code": "Code_postal",
                    },
                    text=lambda tags, fields: {
                        "en": "Postal code {0} for {1} (INSEE:{2})".format(
                            fields["Code_postal"],
                            (fields["Nom_de_la_commune"] or "").strip(),
                            fields["#Code_commune_INSEE"],
                        )
                    },
                ),
            ),
        )
