#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
#                                                                       #
# Copyrights Francesco Ansanelli 2020                                   #
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

from modules import italian_strings
from modules.OsmoseTranslation import T_

from .Analyser_Merge import (
    CSV,
    Analyser_Merge_Point,
    Conflate,
    Load_XY,
    Mapping,
    Select,
    Source,
)


class Analyser_Merge_Parapharmacy_IT(Analyser_Merge_Point):
    def __init__(self, config, logger=None):
        Analyser_Merge_Point.__init__(self, config, logger)
        self.def_class_missing_official(
            item=8210,
            id=21,
            level=3,
            tags=["merge", "amenity", "fix:picture", "fix:survey"],
            title=T_("Pharmacy not integrated"),
        )
        self.def_class_missing_osm(
            item=7150,
            id=22,
            level=3,
            tags=["merge", "amenity", "fix:chair"],
            title=T_("Pharmacy without tag `ref:msal` or invalid"),
        )
        self.def_class_possible_merge(
            item=8211,
            id=23,
            level=3,
            tags=["merge", "amenity", "fix:picture", "fix:chair"],
            title=T_("Pharmacy integration suggestion"),
        )
        self.def_class_update_official(
            item=8212,
            id=24,
            level=3,
            tags=["merge", "amenity", "fix:survey", "fix:chair"],
            title=T_("Pharmacy update"),
        )

        self.init(
            "http://www.dati.salute.gov.it/dataset/parafarmacie.jsp",
            "Ministero della Salute",
            CSV(
                Source(
                    attribution="Ministero della Salute",
                    fileUrl="http://www.dati.salute.gov.it/imgs/C_17_dataset_7_download_itemDownload0_upFile.CSV",
                ),
                separator=";",
            ),
            Load_XY(
                "LONGITUDINE",
                "LATITUDINE",
                xFunction=lambda x: Load_XY.float_comma(
                    x.replace("'", "")
                ),  # '9,258444
                yFunction=Load_XY.float_comma,
                where=lambda row: row["DATAFINEVALIDITA"] == "-"
                and row["LONGITUDINE"] != "-"
                and row["LATITUDINE"] != "-",
            ),
            Conflate(
                select=Select(
                    types=["nodes", "ways"],
                    tags={"amenity": "pharmacy", "dispensing": "no"},
                ),
                osmRef="ref:msal",
                conflationDistance=80,
                mapping=Mapping(
                    static1={"amenity": "pharmacy", "dispensing": "no"},
                    static2={"source": self.source},
                    mapping1={
                        "ref:msal": "CODICEIDENTIFICATIVOSITO",
                        "ref:vatin": lambda res: italian_strings.osmRefVatin(
                            res["PARTITAIVA"]
                        ),
                    },
                    mapping2={
                        "operator": lambda res: italian_strings.normalize_pharmacy(
                            res["DENOMINAZIONESITOLOGISTICO"]
                        ),
                        "source:start_date": lambda res: Mapping.date_format(
                            res["DATAINIZIOVALIDITA"]
                        ),
                    },
                    text=lambda tags, fields: {
                        "en": "{0}, {1}".format(
                            fields["INDIRIZZO"], fields["DESCRIZIONECOMUNE"]
                        )
                    },
                ),
            ),
        )
