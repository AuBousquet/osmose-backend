# -*- coding: utf-8 -*-

###########################################################################
#                                                                       ##
# Copyrights Frederic Rodrigo 2012                                      ##
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

import sqlite3 as lite

from modules.OsmoseTranslation import T_
from plugins.Plugin import Plugin


class Wiki(Plugin):

    def init(self, logger):
        Plugin.init(self, logger)
        self.errors[3140] = self.def_class(
            item=3140, level=2, tags=["tag"], title=T_("Object taggin type")
        )

        # Taginfo wiki extract database
        # http://taginfo.openstreetmap.org/download/taginfo-wiki.db.bz2
        con = lite.connect("taginfo-wiki.db")

        with con:
            cur = con.cursor()
            cur.execute(
                "select tag, on_node, on_way, on_area, on_relation from wikipages where lang='en' and (on_node or on_way or on_area or on_relation)"
            )
            rows = cur.fetchall()

            self.tag_supported = set()
            self.tag_node = set()
            self.tag_way = set()
            self.tag_area = set()
            self.tag_relation = set()
            for row in rows:
                if not "=" in row[0]:
                    self.tag_supported.add(row[0])
                    if row[1]:
                        self.tag_node.add(row[0])
                    if row[2]:
                        self.tag_way.add(row[0])
                    if row[3]:
                        self.tag_area.add(row[0])
                    if row[4]:
                        self.tag_relation.add(row[0])

    def node(self, data, tags):
        ret = []
        for tag in tags:
            if tag in self.tag_supported and tag not in self.tag_node:
                ret.append(
                    (
                        3140,
                        1,
                        {
                            "fr": 'Le tag "{0}" ne s\'applique pas aux nœuds'.format(
                                tag
                            ),
                            "en": 'Tag "{0}" not for nodes'.format(tag),
                        },
                    )
                )
        return ret

    def way(self, data, tags, nds):
        ret = []
        for tag in tags:
            if (
                tag in self.tag_supported
                and tag not in self.tag_way
                and tag not in self.tag_area
            ):
                ret.append(
                    (
                        3140,
                        2,
                        {
                            "fr": 'Le tag "{0}" ne s\'applique pas aux ways'.format(
                                tag
                            ),
                            "en": 'Tag "{0}" not for ways'.format(tag),
                        },
                    )
                )
        return ret

    def relation(self, data, tags, members):
        ret = []
        for tag in tags:
            if tag in self.tag_supported and tag not in self.tag_relation:
                ret.append(
                    (
                        3140,
                        3,
                        {
                            "fr": 'Le tag "{0}" ne s\'applique pas aux relations'.format(
                                tag
                            ),
                            "en": 'Tag "{0}" not for relations'.format(tag),
                        },
                    )
                )
        return ret


if __name__ == "__main__":
    a = Wiki(None)
    a.init(None)
    for d in ["fsdkfjdklsfkleqnhkflerklg", "sport"]:
        if a.node(None, {d: "a"}):
            print("fail: {0}".format(d))
    for d in ["building"]:
        if not a.node(None, {d: "a"}):
            print("nofail: {0}".format(d))
