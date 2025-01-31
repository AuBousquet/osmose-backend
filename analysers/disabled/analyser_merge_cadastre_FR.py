#!/usr/bin/env python
# -*- coding: utf-8 -*-

###########################################################################
#                                                                      ##
# Copyrights Frédéric Rodrigo 2014-2016                                 ##
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


class _Analyser_Merge_Cadastre_Point_ID_calvaire_FR(Analyser_Merge):
    def __init__(self, config, logger=None):
        Analyser_Merge.__init__(self, config, logger)
        self.missing_official = self.def_class(
            item=9992, id=1, level=3, tags=["merge"], title=T_("Misc not integrated")
        )

        self.init(
            "https://www.data.gouv.fr/fr/datasets/58e5924b88ee3802ca255566/",
            "PCI Vecteur (Plan Cadastral Informatisé) - Point_id",
            CSV(
                Source(
                    attribution="Ministère de l’Economie et des Finances",
                    millesime="10/2017",
                    file="cadastre_TPOINT_id_clean.csv.bz2",
                    bz2=True,
                )
            ),
            Load("X", "Y", select={"tex": "%calvaire%"}),
            Conflate(
                select=Select(
                    types=["nodes", "ways"], tags={"historic": "wayside_cross"}
                ),
                conflationDistance=200,
                mapping=Mapping(
                    static1={"historic": "wayside_cross"},
                    static2={"source": self.source},
                    text=lambda tags, fields: {
                        "en": "%s, confidence: %s" % (fields["tex"], 1)
                    },
                ),
            ),
        )


class Analyser_Merge_Cadastre_Point_ID_borne_incendie_FR(Analyser_Merge):
    def __init__(self, config, logger=None):
        Analyser_Merge.__init__(self, config, logger)
        self.missing_official = self.def_class(
            item=9982, id=2, level=3, tags=["merge"], title=T_("Misc not integrated")
        )

        self.init(
            "https://www.data.gouv.fr/fr/datasets/58e5924b88ee3802ca255566/",
            "PCI Vecteur (Plan Cadastral Informatisé) - Point_id",
            CSV(
                Source(
                    attribution="Ministère de l’Economie et des Finances",
                    millesime="10/2017",
                    file="cadastre_TPOINT_id_clean.csv.bz2",
                    bz2=True,
                )
            ),
            Load("X", "Y", select={"tex": "%borne incendie%"}),
            Conflate(
                select=Select(types=["nodes"], tags={"emergency": "ire_hydrant"}),
                conflationDistance=200,
                mapping=Mapping(
                    static1={"emergency": "fire_hydrant"},
                    static2={"source": self.source},
                    text=lambda tags, fields: {
                        "en": "%s, confidence: %s" % (fields["tex"], 1)
                    },
                ),
            ),
        )
