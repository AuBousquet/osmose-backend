#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
#                                                                       #
# Copyrights Frédéric Rodrigo 2019                                      #
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

import json
from datetime import datetime

from modules.OsmoseTranslation import T_

from .Analyser_Merge import CSV, Conflate, Load_XY, Mapping, Select, Source
from .Analyser_Merge_Dynamic import Analyser_Merge_Dynamic, SubAnalyser_Merge_Dynamic


class Analyser_Merge_Street_Objects(Analyser_Merge_Dynamic):

    def __init__(self, config, logger=None):
        Analyser_Merge_Dynamic.__init__(self, config, logger)
        if "country" not in self.config.options:
            return

        mapping = "merge_data/mapillary-street-objects.mapping.json"
        mapingfile = json.loads(open(mapping).read())
        for r in mapingfile:
            self.classFactory(
                SubAnalyser_Merge_Street_Objects,
                r["class"],
                r["class"],
                r["level"],
                r["otype"],
                r["conflation"],
                r["title"],
                r["object"],
                r["select_tags"],
                r["generate_tags"],
                mapping,
                "map_features",
                "points",
            )


class SubAnalyser_Merge_Street_Objects(SubAnalyser_Merge_Dynamic):
    def __init__(
        self,
        config,
        error_file,
        logger,
        classs,
        level,
        otype,
        conflation,
        title,
        object,
        selectTags,
        generateTags,
        mapping,
        source,
        layer,
    ):
        SubAnalyser_Merge_Dynamic.__init__(self, config, error_file, logger)
        self.def_class_missing_official(
            item=8360,
            id=classs,
            level=level,
            tags=["merge", "leisure", "fix:survey", "fix:picture"],
            title=T_("Unmapped {0}", T_(title)),
            detail=T_(
                'Street object ({1}) detected by Mapillary, but no nearby "{0}" tagging.',
                ", ".join(
                    map(
                        lambda kv: "{0}={1}".format(kv[0], kv[1] if kv[1] else "*"),
                        generateTags.items(),
                    )
                ),
                T_(title),
            ),
            fix=T_(
                "Map the corresponding object if the imagery is up-to-date and object detection is correct."
            ),
        )

        self.init(
            "https://www.mapillary.com",
            "Street Objects from Street-level imagery",
            CSV(
                Source(
                    attribution="Mapillary Street Objects",
                    fileUrl=f"http://proxy.osmose.openstreetmap.fr/mapillary/mapillary_objects-{config.osmosis_manager.db_schema}.csv.bz2",
                    bz2=True,
                )
            ),
            Load_XY("lon", "lat", select={"value": object}),
            Conflate(
                select=Select(types=otype, tags=selectTags),
                conflationDistance=conflation,
                subclass_hash=lambda fields: {
                    "id": fields["id"],
                    "value": fields["value"],
                },
                mapping=Mapping(
                    static1=dict(filter(lambda kv: kv[1], generateTags.items())),
                    static2={"source": self.source},
                    mapping1={
                        "survey:date": lambda res: str(
                            datetime.fromtimestamp(int(res["last_seen_at"]) / 1000)
                        )[0:10]
                    },
                    text=lambda tags, fields: (
                        T_(
                            "Observed between {0} and {1}",
                            str(
                                datetime.fromtimestamp(
                                    int(fields["first_seen_at"]) / 1000
                                )
                            )[0:10],
                            str(
                                datetime.fromtimestamp(
                                    int(fields["last_seen_at"]) / 1000
                                )
                            )[0:10],
                        )
                        if fields["first_seen_at"] != fields["last_seen_at"]
                        else T_(
                            "Observed on {0}",
                            str(
                                datetime.fromtimestamp(
                                    int(fields["first_seen_at"]) / 1000
                                )
                            )[0:10],
                        )
                    ),
                ),
            ),
        )
