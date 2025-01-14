# -*- coding: utf-8 -*-

###########################################################################
#                                                                       ##
# Copyrights jmontane 2015                                              ##
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

import re

from plugins.Name_PoorlyWrittenWayType import P_Name_PoorlyWrittenWayType


class Name_PoorlyWrittenWayType_Lang_ca(P_Name_PoorlyWrittenWayType):

    only_for = ["ca"]

    def init(self, logger):
        P_Name_PoorlyWrittenWayType.init(self, logger)

        self.ReTests = {}
        self.ReTests[(200, "Avinguda")] = self.generator(r"Av|inguda")
        self.ReTests[(201, "Avinguda")] = re.compile(r"^([Aa][Vv]([Dd][Aa]?)?\.?) .*$")
        self.ReTests[(202, "Carrer")] = self.generator(r"C|arrer")
        self.ReTests[(203, "Carrer")] = re.compile(r"^([Cc]([Ll]\.?|/)) .*$")
        self.ReTests[(204, "Carretera")] = re.compile(
            r"^([Cc][Aa][Rr][Rr][Ee][Tt][Ee][Rr][Aa]) .*$"
        )
        self.ReTests[(204, "Carretera")] = re.compile(r"^([Cc][Tt][Rr][Aa]\.?) .*$")
        self.ReTests = self.ReTests.items()


###########################################################################
from plugins.Plugin import TestPluginCommon


class Test(TestPluginCommon):
    def test(self):
        a = Name_PoorlyWrittenWayType_Lang_ca(None)
        a.init(None)
        for d in [
            "AVINGUDA ",
            "Av ",
            "Avd ",
            "Av. ",
            "Avd. ",
            "Avda. ",
            "Cl. Grande",
            "C/ A",
            "Ctra. ",
            "avinguda ",
        ]:
            self.check_err(
                a.way(None, {"highway": "h", "name": d}, None), ("name='{0}'".format(d))
            )
            assert not a.way(None, {"highway": d}, None), "highway='{0}'".format(d)

        for d in ["Avinguda Gran"]:
            assert not a.way(
                None, {"highway": "h", "name": d}, None
            ), "name='{0}'".format(d)
