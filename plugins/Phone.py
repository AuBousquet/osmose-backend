#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Francois Gouget fgouget free.fr 2017                       ##
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

from plugins.Plugin import Plugin
import re


class Phone(Plugin):

    only_for = ["FR", "NC", "CA"]

    PHONE_TAGS = set((u"contact:fax", u"contact:phone", u"fax", u"phone"))

    def init(self, logger):
        Plugin.init(self, logger)

        self.errors[30920] = {"item": 3092, "level": 2, "tag": ["value", "fix:chair"], "desc": T_(u"Phone number does not match the expected format")}
        self.errors[30921] = {"item": 3092, "level": 2, "tag": ["value", "fix:chair"], "desc": T_(u"Extra \"0\" after international code")}
        self.errors[30922] = {"item": 3092, "level": 2, "tag": ["value", "fix:chair"], "desc": T_(u"Local short code can't be internationalized")}
        self.errors[30923] = {"item": 3092, "level": 3, "tag": ["value", "fix:chair"], "desc": T_(u"Missing international prefix")}

        self.code = self.father.config.options.get("phone_code")
        self.size = self.father.config.options.get("phone_len")
        self.size_short = self.father.config.options.get("phone_len_short")
        self.format = self.father.config.options.get("phone_format")

        country = self.father.config.options.get("country")

        if country and country.startswith("FR"):
            # Regular numbers must not have a 0 after +[code]
            self.BadInter = re.compile(r"^[+]%s[- ./]*0([-0-9 ./]{%s,})$" % (self.code, self.size))
        else:
            self.BadInter = None

        if self.size_short:
            # Short numbers cannot be internationalized
            self.BadShort = re.compile(r"^[+]%s[- ./]*([0-9]{%s,%s})$" % (self.code, min(self.size_short), max(self.size_short)))
        else:
            self.BadShort = None

        if country and country.startswith("FR"):
            # Local numbers to internationalize. Note that in addition to
            # short numbers this also skips special numbers starting with 08
            # or 09 since these may or may not be callable from abroad.
            self.Local = re.compile(r"^0 *([1-7][-0-9 ./]{%s,})$" % (self.size - 2))
        else:
            self.Local = re.compile(r"^([-0-9 ./]{%s,})$" % self.size)

        if self.format:
            self.Good = re.compile(self.format % self.code)
        else:
            self.Good = None

    def check(self, tags):
        err = []
        for tag in self.PHONE_TAGS:
            if tag not in tags:
                continue
            phone = tags[tag]

            if self.BadInter:
                r = self.BadInter.match(phone)
                if r:
                    err.append({"class": 30921, "fix": {tag: "+" + self.code + " " + r.group(1)}})
                    continue

            r = self.Local.match(phone)
            if r:
                err.append({"class": 30923, "fix": {tag: "+" + self.code + " " + r.group(1)}})
                continue

            if self.BadShort:
                r = self.BadShort.match(phone)
                if r:
                    err.append({"class": 30922, "fix": {tag: r.group(1)}})
                    continue

            if self.Good:
                r = self.Good.match(phone)
                if not r:
                    err.append({"class": 30920, "text": {"en": phone}})
                    continue

        return err

    def node(self, _data, tags):
        return self.check(tags)

    def way(self, _data, tags, _nds):
        return self.check(tags)

    def relation(self, _data, tags, _members):
        return self.check(tags)


###########################################################################
from plugins.Plugin import TestPluginCommon

class Test(TestPluginCommon):
    def test_FR(self):
        p = Phone(None)
        class _config:
            options = {"country": "FR", "phone_code": "33", "phone_len": 9, "phone_len_short": [4, 6], "phone_format": r"([+]%s ?([0-9] ?){9})|[0-9]{4}|[0-9]{6}"}
        class father:
            config = _config()
        p.father = father()
        p.init(None)

        for (bad, good) in ((u"+330102030405", u"+33 102030405"),
                            # Preserve formatting
                            (u"+33 0102030405", u"+33 102030405"),
                            (u"+33  01 02 03 04 05", u"+33 1 02 03 04 05"),
                            (u"+33  3631", u"3631"),
                            (u"0102030405", u"+33 102030405"),
                            (u"01 02 03 04 05", u"+33 1 02 03 04 05"),
                            (u"01 02 03 04 05 06", u"+33 1 02 03 04 05 06")):
            # Check the bad number's error and fix
            err = p.node(None, {"phone": bad})
            self.check_err(err, ("phone='%s'" % bad))
            self.assertEquals(err[0]["fix"]["phone"], good)

            # The correct number does not need fixing
            assert not p.node(None, {"phone": good}), ("phone='%s'" % good)

        # Verify we got no error for other correct numbers
        for good in (u"3631", u"118987"):
            assert not p.node(None, {"phone": good}), ("phone='%s'" % good)

    def test_NC(self):
        p = Phone(None)
        class _config:
            options = {"country": "NC", "phone_code": "687", "phone_len": 6, "phone_format": r"[+]%s ?([0-9] ?){6}"}
        class father:
            config = _config()
        p.father = father()
        p.init(None)

        for (bad, good) in ((u"43 43 43", u"+687 43 43 43"),
                            (u"434343", u"+687 434343")):
            # Check the bad number's error and fix
            err = p.node(None, {"phone": bad})
            self.check_err(err, ("phone='%s'" % bad))
            self.assertEquals(err[0]["fix"]["phone"], good)

            # The correct number does not need fixing
            assert not p.node(None, {"phone": good}), ("phone='%s'" % good)

        # Verify we got error for other correct numbers
        for bad in (u"3631"):
            assert p.node(None, {"phone": bad}), ("phone='%s'" % bad)

    def test_CA(self):
        p = Phone(None)
        class _config:
            options = {"country": "CA", "phone_code": "1", "phone_len": 10, "phone_format": r"[+]%s[- ][0-9]{3}[- ][0-9]{3}[- ][0-9]{4}"}
        class father:
            config = _config()
        p.father = father()
        p.init(None)

        for (bad, good) in ((u"800-555-0000", u"+1 800-555-0000"),):
            # Check the bad number's error and fix
            err = p.node(None, {"phone": bad})
            self.check_err(err, ("phone='%s'" % bad))
            self.assertEquals(err[0]["fix"]["phone"], good)

            # The correct number does not need fixing
            assert not p.node(None, {"phone": good}), ("phone='%s'" % good)

        # Verify we got error for other correct numbers
        for bad in (u"3631", u"(123) 123-4567", "+1 123 1234567"):
            assert p.node(None, {"phone": bad}), ("phone='%s'" % bad)
