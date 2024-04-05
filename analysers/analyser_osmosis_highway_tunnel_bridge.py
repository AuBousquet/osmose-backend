#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
#                                                                       #
# Copyrights Frédéric Rodrigo 2013                                      #
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

from .Analyser_Osmosis import Analyser_Osmosis

sql10 = """
SELECT
    id,
    ST_AsText(way_locate(linestring))
FROM
    {0}ways
WHERE
    tags != ''::hstore AND
    (
        tags?'railway' OR
        (tags?'highway' AND tags->'highway' IN ('motorway', 'trunk', 'primary', 'secondary'))
    ) AND
    tags?'bridge' AND
    tags->'bridge' = 'yes' AND
    ST_Length(linestring::geography) > 500 AND
    NOT tags?'bridge:structure'
"""

sql20 = """
CREATE TEMP TABLE bridge_cross AS
SELECT
    ways.id,
    ways.tags,
    ways.linestring,
    bridge.id AS bid,
    bridge.tags AS btags,
    bridge.linestring AS blinestring
FROM
    ways AS bridge
    JOIN ways ON
        bridge.id != ways.id AND
        bridge.linestring && ways.linestring AND
        ST_Crosses(bridge.linestring, ways.linestring)
WHERE
    bridge.tags != ''::hstore AND
    bridge.tags ?| ARRAY['highway', 'railway'] AND
    bridge.tags?'bridge' AND
    bridge.tags->'bridge' != 'no' AND
    ST_NPoints(bridge.linestring) > 1 AND
    ways.tags != ''::hstore AND
    ways.tags ?| ARRAY['highway', 'railway', 'waterway'] AND
    ST_NPoints(ways.linestring) > 1
"""

sql21 = """
SELECT
    id,
    bid,
    ST_AsText(ST_Centroid(ST_Intersection(blinestring, linestring)))
FROM
    bridge_cross
WHERE
    tags?'highway' AND
    tags->'highway' IN ('motorway_link', 'trunk_link', 'primary', 'primary_link', 'secondary', 'secondary_link')
"""

sql30 = """
SELECT
    bid,
    ST_AsText(way_locate(blinestring))
FROM
    (
        SELECT
            tags->'layer' AS layer,
            btags->'layer' AS blayer,
            bid,
            blinestring
        FROM
            bridge_cross
    ) AS t
GROUP BY
    bid,
    blayer,
    blinestring
HAVING
    0 = SUM(CASE WHEN layer IS NULL THEN 0 ELSE 1 END) + CASE WHEN blayer IS NULL THEN 0 ELSE 1 END
"""


class Analyser_Osmosis_Highway_Tunnel_Bridge(Analyser_Osmosis):

    def __init__(self, config, logger=None):
        Analyser_Osmosis.__init__(self, config, logger)
        self.classs_change[1] = self.def_class(
            item=7012,
            level=3,
            tags=["tag", "highway", "fix:survey"],
            title=T_("Bridge structure missing"),
            detail=T_(
                """The length of the bridge makes it deserve a more detailed tag than
`bridge=yes`."""
            ),
            fix=T_(
                """See the possible [types of
bridges](https://wiki.openstreetmap.org/wiki/Key:bridge)."""
            ),
        )
        # self.classs_change[2] = self.def_class(item = 7130, level = 3, tags = ['tag', 'highway', 'maxheight', "fix:survey"],
        #    title = T_('Missing maxheight tag'))
        # self.classs_change[3] = self.def_class(item = 7130, level = 3, tags = ['tag', 'highway', 'layer', "fix:imagery"],
        #    title = T_('Missing layer tag around bridge'))

        self.callback10 = lambda res: {
            "class": 1,
            "data": [self.way_full, self.positionAsText],
            "fix": [
                {"+": {"bridge:structure": "beam"}},
                {"+": {"bridge:structure": "suspension"}},
            ],
        }
        # self.callback20 = lambda res: {"class":2, "data":[self.way_full, self.way_full, self.positionAsText] }
        # self.callback30 = lambda res: {"class":3, "data":[self.way_full, self.positionAsText] }

    def analyser_osmosis_full(self):
        self.run(sql10.format(""), self.callback10)
        # self.run(sql20.format("", ""))
        # self.run(sql21, self.callback20)
        # self.run(sql30.format("", ""), self.callback30)

    def analyser_osmosis_diff(self):
        self.run(sql10.format("touched_"), self.callback10)
        # self.run(sql20.format("touched_", ""))
        # self.run(sql21, self.callback20)
        # self.run(sql30, self.callback30)
        # self.run(sql20.format("", "touched_"))
        # self.run(sql21, self.callback20)
        # self.run(sql30, self.callback30)
