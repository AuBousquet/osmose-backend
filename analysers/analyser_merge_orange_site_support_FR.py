#!/usr/bin/env python
#-*- coding: utf-8 -*-

#########################################################################
#                                                                       #
# Copyrights Oslandia 2024                                              #
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

from .Analyser_Merge import Load, Mapping, Select, SHP, Source
from .Analyser_Merge import Analyser_Merge_Point, Conflate, LoadGeomCentroid


class Analyser_Orange_Site_Support_FR(Analyser_Merge_Point):
    def __init__(self, config, logger=None):
        Analyser_Merge_Point.__init__(self, config, logger)
        # What to do when the line is not referenced in OSM dataset, defined in Analyser_Merge.py
        self.def_class_missing_official(
            item=8393,
            id=1, # conventional class id for def_class_missing_official
            level=3,
            tags=["merge", "telecom"],# Normalized?
            title=T_(""),
        )

        self.init(
            name="Site support - Fibre internet",
            url="",
            parser=SHP(
                Source(
                    attribution="Orange",
                    millesime="2024",
                    encoding="iso-8859-1",
                    file="site_support_rip.zip"
                ),
                zip="site_support_rip.shp",
                srid=4326
            ),
            load=Load("geom"),
            conflate=Conflate(
                select=Select(
                    types=["nodes"],
                    tags=[{"telecom": "connection_point"}]
                ),
                conflationDistance=15,
                mapping=Mapping(
                    static1={"telecom": "connection_point", "operator": "Orange"},
                    static2={"source": self.source},
                    mapping1={
                        "code": lambda fields: (
                            str(fields["code"])
                        ),
                        "app_nature": lambda fields: (
                            str(fields["app_nature"])
                        ),
                        "implantation": lambda fields: (
                            str(fields["implantati"])
                        ),
                        "reseau": lambda fields: (
                            fields["reseau"]
                        ),
                        "app_type": lambda fields: (
                            str(fields["app_type_l"])
                            if fields["app_type_l"] in ("Type EDF 190", "Triple", "Simple", "Renforcé 400daN", "Renforcé", "Réhaussé")
                            else None
                        ),
                    },
                    text=lambda _, fields: {
                        "en": ", ".join(
                            filter(
                                lambda res: res and res != "None", [fields["code"]]
                            )
                        )
                    },
                ),
            ),
        )
