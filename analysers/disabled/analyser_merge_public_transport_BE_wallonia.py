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


class Analyser_Merge_Public_Transport_BE_Wallonia(Analyser_Merge):
    def __init__(self, config, logger=None):
        Analyser_Merge.__init__(self, config, logger)
        self.missing_official = {
            "item": "8040",
            "class": 71,
            "level": 3,
            "tag": ["merge", "public transport"],
            "desc": T_("Wallonia stop not integrated"),
        }
        self.possible_merge = {
            "item": "8041",
            "class": 73,
            "level": 3,
            "tag": ["merge", "public transport"],
            "desc": T_("Wallonia stop, integration suggestion"),
        }
        self.init(
            Source(
                url="http://opendata.awt.be/dataset/tec",
                name="Données TEC",
                file="public_transport_BE_wallonia.csv.bz2",
                bz2=True,
                encoding="ISO-8859-15",
                csv=CSV(separator="|", header=False),
                srid=31370,
            ),
            Load(
                "X coordinate",
                "Y coordinate",
                create="""
                    "Stop identifier" character(8),
                    "Description (Dutch)" character(50),
                    "Description (French)" character(50),
                    "Municipality (Dutch)" character(50),
                    "Municipality (French)" character(50),
                    "Country Abbreviation" character(2),
                    "Streetname (Dutch)" character(50),
                    "Streetname (French)" character(50),
                    "Aricode" character(4),
                    "Accessible" character(1),
                    "X coordinate" character(10),
                    "Y coordinate" character(10),
                    "Public information" character(1),
                    "UIC" character(9)
                """,
            ),
            Conflate(
                select=Select(
                    types=["nodes", "ways"],
                    tags=[{"highway": "bus_stop"}, {"public_transport": "platform"}],
                ),
                osmRef="ref",
                conflationDistance=300,
                mapping=Mapping(
                    static1={
                        "highway": "bus_stop",
                        "public_transport": "platform",
                        "bus": "yes",
                        "operator": "TEC",
                    },
                    static2={"source": "tec-wl.be - 07-2014"},
                    mapping1={
                        "ref": lambda res: res["Stop identifier"][0:7],
                        "name": lambda res: (
                            res["Description (Dutch)"].strip()
                            if res["Description (Dutch)"] == res["Description (French)"]
                            else "%s - %s"
                            % (
                                res["Description (French)"].strip(),
                                res["Description (Dutch)"].strip(),
                            )
                        ),
                        "name:fr": lambda res: (
                            res["Description (French)"].strip()
                            if res["Description (Dutch)"] != res["Description (French)"]
                            else None
                        ),
                        "name:nl": lambda res: (
                            res["Description (Dutch)"].strip()
                            if res["Description (Dutch)"] != res["Description (French)"]
                            else None
                        ),
                        "uic_ref": "UIC",
                        "whellchair": lambda res: {"0": "no", "1": "yes"}[
                            res["Accessible"]
                        ],
                    },
                    text=lambda tags, fields: {
                        "en": "Wallonia stop of %s, %s, %s"
                        % (
                            fields["Description (French)"].strip(),
                            fields["Streetname (French)"].strip(),
                            fields["Municipality (French)"].strip(),
                        )
                    },
                ),
            ),
        )
