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
from .Analyser_Merge_Network import Analyser_Merge_Network, ConflateNetwork


class Analyser_Orange_FTTX_Cable_FR(Analyser_Merge_Network):
    def __init__(self, config, logger=None):
        Analyser_Merge_Network.__init__(self, config, logger)
        # What to do when the line is not referenced in OSM dataset, defined in Analyser_Merge.py
        self.def_class_missing_official(
            item=8393,
            id=1, # conventional class id for def_class_missing_official
            level=3,
            tags=["merge", "telecom"],# Normalized?
            title=T_("Internet cable not integrated"),
        )

        self.init(
            name="Câbles FTTX - Fibre internet",
            url="",
            parser=SHP(
                Source(
                    attribution="Orange",
                    millesime="2024",
                    encoding="iso-8859-1",
                    file="cable_fttx_rip.zip"
                ),
                zip="cable_fttx_rip.shp",
                srid=4326
            ),
            load=Load("geom"),
            conflate=ConflateNetwork(
                select=Select(
                    types=["ways"],
                    tags=[{"telecom": "line"}]
                ),
                conflationDistance=15,
                mapping=Mapping(
                    static1={"telecom": "line", "operator": "Orange"},
                    static2={"source": self.source},
                    mapping1={
                        "code": lambda fields: (
                            str(fields["code"])
                        ),
                        "type_cable": lambda fields: (
                            str(fields["type_cable"])
                            if fields["type_cable"] in ("Entreprise", "Transport", "Distribution1", "Distribution2", "DTER")
                            else None
                        ),
                        "ftth": lambda fields: (
                            True
                            if fields["usage_ftth"] == 'O'
                            else False 
                            if fields["usage_ftth"] == 'N'
                            else None
                        ),
                        "deploiement": lambda fields: (
                            fields["statut_lib"]
                        )
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
