#!/usr/bin/env python
# -*- coding: utf-8 -*-

###########################################################################
#                                                                       ##
# Copyrights Frédéric Rodrigo 2012                                      ##
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

from .Analyser_Merge import CSV, Conflate, Load, Mapping, SourceOpenDataSoft
from .analyser_merge_street_number import _Analyser_Merge_Street_Number


class Analyser_Merge_Street_Number_Nantes(_Analyser_Merge_Street_Number):
    def __init__(self, config, logger=None):
        _Analyser_Merge_Street_Number.__init__(
            self,
            config,
            2,
            "Nantes",
            logger,
            "https://data.nantesmetropole.fr/explore/dataset/244400404_adresses-postales-nantes-metropole",
            "Adresses postales de Nantes Métropole",
            CSV(
                SourceOpenDataSoft(
                    attribution="Nantes Métropole {0}",
                    url="https://data.nantesmetropole.fr/explore/dataset/244400404_adresses-postales-nantes-metropole",
                )
            ),
            Load(
                "Géolocalisation",
                "Géolocalisation",
                xFunction=lambda geo: float(geo.split(",")[1].strip()),
                yFunction=lambda geo: float(geo.split(",")[0]),
            ),
            Conflate(
                mapping=Mapping(
                    static2={"source": self.source},
                    mapping1={"addr:housenumber": "Numéro adresse"},
                    text=lambda tags, fields: {"en": fields["Adresse"]},
                )
            ),
        )
