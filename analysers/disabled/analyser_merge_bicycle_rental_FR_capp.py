#!/usr/bin/env python
# -*- coding: utf-8 -*-

###########################################################################
#                                                                      ##
# Copyrights Frédéric Rodrigo 2014                                      ##
#                                                                      ##
# This program is free software: you can redistribute it and/or modify  ##
# it under the terms of the GNU General Public License as published by  ##
# the Free Software Foundation, either version 3 of the License, or     ##
# (at your option) any later version.                                   ##
#                                                                      ##
# This program is distributed in the hope that it will be useful,       ##
# but WITHOUT ANY WARRANTY; without even the implied warranty of        ##
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         ##
# GNU General Public License for more details.                          ##
#                                                                      ##
# You should have received a copy of the GNU General Public License     ##
# along with this program.  If not, see <http://www.gnu.org/licenses/>. ##
#                                                                      ##
###########################################################################

from modules.OsmoseTranslation import T_

from .Analyser_Merge import CSV, Analyser_Merge, Conflate, Load, Mapping, Select, Source


class Analyser_Merge_Bicycle_Rental_FR_CAPP(Analyser_Merge):
    def __init__(self, config, logger=None):
        Analyser_Merge.__init__(self, config, logger)
        self.missing_official = {
            "item": "8160",
            "class": 11,
            "level": 3,
            "tag": ["merge", "public equipment", "bicycle"],
            "desc": T_("CAPP bicycle rental not integrated"),
        }
        self.init(
            "http://opendata.agglo-pau.fr/index.php/fiche?idQ=14",
            "Stations Idécycle du réseau Idelis sur la CAPP",
            CSV(
                Source(
                    attribution="Communauté d'Agglomération Pau-Pyrénées",
                    millesime="01/2013",
                    fileUrl="http://opendata.agglo-pau.fr/sc/call.php?f=1&idf=14",
                    zip="Idecycl_WGS84.csv",
                    filter=lambda t: t.replace("\0", ""),
                )
            ),
            Load("X", "Y", xFunction=Load.float_comma, yFunction=Load.float_comma),
            Conflate(
                select=Select(types=["nodes"], tags={"amenity": "bicycle_rental"}),
                conflationDistance=100,
                mapping=Mapping(
                    static1={"amenity": "bicycle_rental", "operator": "IDEcycle"},
                    static2={"source": self.source},
                    mapping1={
                        "name": "NOM",
                        "capacity": "Nb_velo",
                        "vending": lambda res: (
                            "subscription" if res["Borne_pai"] == "Oui" else None
                        ),
                    },
                ),
            ),
        )
