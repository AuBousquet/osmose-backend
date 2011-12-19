#!/usr/bin/env python
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Etienne Chové <chove@crans.org> 2009                       ##
##                                                                       ##
## This program is free software: you can redistribute it and/or modify  ##
## it under the terms of the GNU General Public License as published by  ##
## the Free Software Foundation, either version 3 of the License, or     ##
## (at your option) any later version.                                   ##
##                                                                       ##
## This program is distributed in the hope that it will be useful,       ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of        ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         ##
## GNU General Public License for more details.                          ##
##                                                                       ##
## You should have received a copy of the GNU General Public License     ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>. ##
##                                                                       ##
###########################################################################

import sys, re, popen2, urllib, time, getopt
import psycopg2
from modules import OsmSax
from modules import OsmGis

###########################################################################
## some usefull functions

re_points = re.compile("[\(,][^\(,\)]*[\),]")
def get_points(text):
    pts = []
    for r in re_points.findall(text):
        lon, lat = r[1:-1].split(" ")
        pts.append({"lat":lat, "lon":lon})
    return pts

#def get_error_text(osm_id):
#    sql = "SELECT name FROM %spolygon WHERE st_isvalid(way)='f' AND osm_id=%d"%(db_schemaref,osm_id)
#    cmd = "psql --quiet --tuples-only -d %s -c \"%s\""%(db_stringtring.split("=")[1], sql)
#    out, inp, err = popen2.popen3(cmd)
#    inp.close()
#    out = out.read().strip()
#    err = err.read().strip().split(" ", 1)[1].strip()
#    if err:
#        err = err.split("\n")[0]
#    return err
        
###########################################################################

def analyser(config, logger = None):

    ## result file
    
    outxml = OsmSax.OsmSaxWriter(open(config.dst, "w"), "UTF-8")
    outxml.startDocument()
    outxml.startElement("analyser", {"timestamp":time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    
    outxml.startElement("class", {"id":"1", "item":"1040"})
    outxml.Element("classtext", {"lang":"fr", "title":"Polygone non valide (analyse gis)", "menu":"polygone non valide"})
    outxml.Element("classtext", {"lang":"en", "title":"Invalid polygon (gis analysis)", "menu":"invalid polygon"})
    outxml.endElement("class")

    ## sql querry

    sql = """
    SELECT osm_id,
       name,
       astext(st_transform(selfinter,4020)) AS selfinter,
       astext(st_transform(way,4020)) AS way
    FROM (
      SELECT osm_id,name,
        st_difference(
          st_endpoint(
            st_union(
              st_exteriorring(way),
              st_endpoint(st_exteriorring(way))
            )
          ),
          st_endpoint(st_exteriorring(way))
        ) AS selfinter,
        way
      FROM %s_polygon
      WHERE st_isvalid(way)='f'
    ) AS tmp
    WHERE st_isempty(selfinter)='f'
    ;
    """ % config.db_schema

    gisconn = psycopg2.connect(config.db_string)
    giscurs = gisconn.cursor()
    giscurs.execute(sql)
    apiconn = OsmGis.OsmGis(config.db_string, config.db_schema)

    ## format results to outxml

    while True:
        many = giscurs.fetchmany(1000)
        if not many:
            break
        for res in many:
            outxml.startElement("error", {"class":"1"})
            for loc in get_points(res[2]):
                outxml.Element("location", loc)
            #outxml.Element("text", {"lang":"en", "value":get_error_text(res[0])})
            if res[0] < 0:
                outxml.RelationCreate(apiconn.RelationGet(-res[0]))
            else:
                outxml.WayCreate(apiconn.WayGet(res[0]))
            outxml.endElement("error")

    outxml.endElement("analyser")
    outxml._out.close()

    ## update front-end
    #logger.log("update front-end")    
    #urllib.urlretrieve(config.updt, "/dev/null")
