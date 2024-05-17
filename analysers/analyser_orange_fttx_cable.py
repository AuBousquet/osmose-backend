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
from .Analyser_Osmosis import Analyser_Osmosis

sql00 = """
SELECT cable_fttx_rip.id, 
       site_orig.code, 
       ST_AsText(site_orig.geom) as geom_text
FROM osmose.cable_fttx_rip left join osmose.site_support_rip as site_orig on (site_orig.code = cable_fttx_rip.code_site_)
WHERE NOT (site_orig.geom = st_startpoint(st_geometryn(cable_fttx_rip.geom, 1)));
"""

sql10 = """
SELECT cable_fttx_rip.id, 
       site_dest.code, 
       ST_AsText(site_dest.geom) as geom_text
FROM osmose.cable_fttx_rip left join osmose.site_support_rip as site_dest on (site_dest.code = cable_fttx_rip.code_sit_1)
WHERE NOT (site_dest.geom = st_endpoint(st_geometryn(cable_fttx_rip.geom, st_numgeometries(cable_fttx_rip.geom)));
"""

class Analyser_Osmosis_Telecom_Cable(Analyser_Osmosis):

    def __init__(self, config, logger = None):
        Analyser_Osmosis.__init__(self, config, logger)
        self.classs[1] = self.def_class(
            item = 1400, \
            level = 2, \
            tags = ['telecom'], \
            title = T_('The geometrical ends of the cable are not hooked to its sites.'), \
            detail = T_('The first point of the first linestring of the multilinestring must be hooked to the origin site, the last point of the last linestring of the multilinestring must be hooked to the destination site.'), \
            fix = T_('When orig_ok or dest_ok is false, the multilinestring must be changed to be hooked to a site geometry at its ends.') \
        )

        self.classs[2] = self.def_class(
            item = 1400, \
            level = 2, \
            tags = ['telecom'], \
            title = T_('The geometrical ends of the cable are not hooked to its sites.'), \
            detail = T_('The first point of the first linestring of the multilinestring must be hooked to the origin site, the last point of the last linestring of the multilinestring must be hooked to the destination site.'), \
            fix = T_('When orig_ok or dest_ok is false, the multilinestring must be changed to be hooked to a site geometry at its ends.') \
        )

        self.callback00 = lambda res: {"class":1, "data":[self.way_full, self.node_full, self.positionAsText]}
        self.callback10 = lambda res: {"class":2, "data":[self.way_full, self.node_full, self.positionAsText]}

    def analyser_osmosis_common(self):
        self.run(sql00, self.callback00)
        self.run(sql10, self.callback10)
