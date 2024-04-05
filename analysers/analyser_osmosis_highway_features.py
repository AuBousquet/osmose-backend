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

from .Analyser_Osmosis import Analyser_Osmosis

sql10 = """
SELECT
    nodes.id,
    ST_AsText(nodes.geom),
    MIN(ways.id)
FROM
    nodes AS nodes
    JOIN way_nodes ON
        way_nodes.node_id = nodes.id
    JOIN ways AS ways ON
        ways.id = way_nodes.way_id AND
        ways.tags != ''::hstore AND
        ways.tags ?| ARRAY['highway', 'railway']
WHERE
    nodes.tags != ''::hstore AND
    nodes.tags?'railway' AND
    nodes.tags->'railway' IN ('level_crossing', 'crossing')
GROUP BY
    nodes.id,
    nodes.geom
HAVING
    NOT BOOL_OR(ways.tags?'highway') OR NOT BOOL_OR(ways.tags?'railway')
"""

sql30 = """
SELECT
    nodes.id,
    ST_AsText(nodes.geom)
FROM
    nodes
    JOIN way_nodes ON
        way_nodes.node_id = nodes.id
    LEFT JOIN ways ON
        ways.id = way_nodes.way_id AND
        ways.tags != ''::hstore AND
        ways.tags ?| ARRAY['highway', 'railway']
WHERE
    nodes.tags != ''::hstore AND
    nodes.tags?'highway' AND
    nodes.tags->'highway' IN ('crossing', 'turning_circle', 'traffic_signals', 'stop', 'give_way', 'motorway_junction', 'mini_roundabout', 'passing_place', 'ford', 'elevator', 'turning_loop', 'incline_steep', 'stile', 'incline', 'traffic_calming', 'junction')
GROUP BY
    nodes.id,
    nodes.geom
HAVING
    BOOL_AND(ways.id IS NULL)
"""


class Analyser_Osmosis_Highway_Features(Analyser_Osmosis):
    def __init__(self, config, logger=None):
        Analyser_Osmosis.__init__(self, config, logger)
        self.classs[1] = self.def_class(
            item=7090,
            level=2,
            tags=["railway", "highway", "fix:imagery"],
            title=T_("Missing way on level crossing"),
            detail=T_("""Crossing for which it lacks the road or railway. """),
        )
        self.classs[3] = self.def_class(
            item=7090,
            level=2,
            tags=["highway", "fix:chair"],
            title=T_("Lone highway or barrier node"),
            fix=T_("""The node must be common to rail and road."""),
        )

        self.callback10 = lambda res: {
            "class": 1,
            "subclass": 1,
            "data": [self.node_full, self.positionAsText, self.way_full],
        }
        self.callback30 = lambda res: {
            "class": 3,
            "data": [self.node_full, self.positionAsText],
        }

    def analyser_osmosis_common(self):
        self.run(sql10, self.callback10)
        self.run(sql30, self.callback30)
