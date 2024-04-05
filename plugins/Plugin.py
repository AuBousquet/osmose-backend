# -*- coding: utf-8 -*-

###########################################################################
#                                                                       ##
# Copyrights Black Myst <black.myst@free.fr> 2011                       ##
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

import os
from inspect import getframeinfo, stack
from typing import Dict, List, Union

from analysers.Analyser import Analyser
from modules.Stablehash import stablehash


class Plugin(object):

    def __init__(self, father):
        self.father = father

    def init(self, logger):
        """
        Called before starting analyse.
        @param logger:
        """
        self.errors = {}
        pass

    def availableMethodes(self):
        """
        Get a list of overridden methods.
        This is usefull to optimize call from analyser_sax.
        """
        capabilities = []
        currentClass = self.__class__
        if currentClass.node != Plugin.node:
            capabilities.append("node")
        if currentClass.way != Plugin.way:
            capabilities.append("way")
        if currentClass.relation != Plugin.relation:
            capabilities.append("relation")
        return capabilities

    def node(self, node: Dict[str, Union[str, int]], tags: Dict[str, str]):
        """
        Called each time a node is found on data source.

        @param node: dict with details.
            example: node[u"id"], node[u"lat"], node[u"lon"], node[u"version"]
        @param tags: dict with all tags and values.
        @return: error list.
        """
        pass

    def way(
        self, way: Dict[str, Union[str, int]], tags: Dict[str, str], nodes: List[int]
    ):
        """
        Called each time a way is found on data source.

        @param way: dict with details.
            example: node[u"id"], node[u"lat"], node[u"lon"], node[u"version"]
        @param tags: dict with all tags and values.
        @param nodes: list of all nodes id.
        @return: error list.
        """
        pass

    def relation(
        self,
        relation: Dict[str, Union[str, int]],
        tags: Dict[str, str],
        members: List[Dict[str, Union[str, int]]],
    ):
        """
        Called each time a relation is found on data source.

        @param relation: dict with details.
            example: node[u"id"], node[u"lat"], node[u"lon"], node[u"version"]
        @param tags: dict with all tags and values.
        @param members:  list of all relation members.
        @return: error list.
        """
        pass

    def end(self, logger):
        """
        Called after starting analyse.
        @param logger:
        """
        pass

    def def_class(self, **kwargs):
        if "source" not in kwargs and self.father and self.father.config:
            config = self.father.config
            caller = getframeinfo(stack()[1][0])
            kwargs["source"] = "{0}/plugins/{1}#L{2}".format(
                config and hasattr(config, "source_url") and config.source_url or None,
                os.path.basename(caller.filename),
                caller.lineno,
            )

        return Analyser.def_class_(self.father and self.father.config or None, **kwargs)

    def merge_doc(self, *docs):
        return Analyser.merge_doc(*docs)

    def ToolsStripAccents(self, mot):
        mot = mot.replace("à", "a").replace("â", "a")
        mot = (
            mot.replace("é", "e").replace("è", "e").replace("ë", "e").replace("ê", "e")
        )
        mot = mot.replace("î", "i").replace("ï", "i")
        mot = mot.replace("ô", "o").replace("ö", "o")
        mot = mot.replace("û", "u").replace("ü", "u").replace("ù", "u")
        mot = mot.replace("ÿ", "y")
        mot = mot.replace("ç", "c")
        mot = mot.replace("À", "A").replace("Â", "A")
        mot = (
            mot.replace("É", "E").replace("È", "E").replace("Ë", "E").replace("Ê", "E")
        )
        mot = mot.replace("Î", "I").replace("Ï", "I")
        mot = mot.replace("Ô", "O").replace("Ö", "O")
        mot = mot.replace("Û", "U").replace("Ü", "U").replace("Ù", "U")
        mot = mot.replace("Ÿ", "Y")
        mot = mot.replace("Ç", "C")
        mot = mot.replace("œ", "oe")
        mot = mot.replace("æ", "ae")
        mot = mot.replace("Œ", "OE")
        mot = mot.replace("Æ", "AE")
        return mot


class with_options:
    def __init__(self, plugin, options):
        self.plugin = plugin
        self.options = options

    def __enter__(self):
        self.old_options = self.plugin.father.config.options
        self.plugin.father.config.options = self.plugin.father.config.options.copy()
        self.plugin.father.config.options.update(self.options)

    def __exit__(self, type, value, traceback):
        self.plugin.father.config.options = self.old_options


###########################################################################
import unittest


class TestPluginCommon(unittest.TestCase):
    def setUp(self):
        # import for gettext functions
        import analysers.Analyser

        assert analysers.Analyser  # silence pyflakes

    def set_default_config(self, plugin):
        class _config:
            options = {"project": "openstreetmap"}

        class father:
            config = _config()

        plugin.father = father()

    # Check errors generation, and unicode encoding
    def check_err(self, errors, log="Valid errors expected", expected=None):
        if isinstance(errors, dict):
            errors = [errors]
        assert errors, log
        for error in errors:
            assert "class" in error, error
            assert isinstance(error["class"], int), error["class"]
            if "subclass" in error:
                assert isinstance(error["subclass"], int), error["subclass"]
            if "text" in error:
                self.check_dict(error["text"], log)
            if "fix" in error:
                # TODO: check fix format
                self.check_array([error["fix"]], log)
            for k in error.keys():
                if k not in ("class", "subclass", "text", "fix", "allow_fix_override"):
                    assert False, "key '{0}' is not accepted in error: {1}".format(
                        k, error
                    )

        if expected:
            found = False
            for e in errors:
                for exk, exv in expected.items():
                    if exk not in e or e[exk] != exv:
                        e = None
                        break
                if e:
                    # Found a match
                    found = e
                    break
            assert found, str(expected) + " Not found in the errors list" + str(errors)

    def check_not_err(self, errors, log="Error not expected", expected=None):
        if not errors:
            return
        if isinstance(errors, dict):
            errors = [errors]
        assert log

        if expected:
            found = False
            for e in errors:
                for exk, exv in expected.items():
                    if exk not in e or e[exk] != exv:
                        e = None
                        break
                if e:
                    # Found a match
                    found = e
                    break
            assert not found, str(found) + " Found in the errors list"

    def check_dict(self, d, log):
        for _k, v in d.items():
            if isinstance(v, list):
                self.check_array(v, log)
            elif isinstance(v, dict):
                self.check_dict(v, log)

    def check_array(self, a, log):
        for v in a:
            if isinstance(v, list):
                self.check_array(v, log)
            elif isinstance(v, dict):
                self.check_dict(v, log)


class Test(TestPluginCommon):

    def test(self):
        a = Plugin(None)
        self.assertEqual(a.init(None), None)
        self.assertEqual(a.errors, {})
        self.assertEqual(a.node(None, None), None)
        self.assertEqual(a.way(None, None, None), None)
        self.assertEqual(a.relation(None, None, None), None)
        self.assertEqual(a.end(None), None)
        for n in [
            ("bpoue", "bpoue"),
            ("bpoué", "bpoue"),
            ("bpoùé", "bpoue"),
            ("bpôùé", "bpoue"),
        ]:
            self.assertEqual(a.ToolsStripAccents(n[0]), n[1], n)

        for n in [
            ("1", "beppu"),
            ("1", "lhnsune"),
            ("1", "uae"),
            ("1", "bue"),
        ]:
            self.assertNotEqual(stablehash(n[0]), stablehash(n[1]))

    def test_check_err(self):
        import pytest

        self.assertEqual(self.check_err([{"class": 1, "subclass": 2}]), None)
        self.assertEqual(
            self.check_err([{"class": 1, "subclass": 2, "text": {"en": "titi"}}]), None
        )
        self.assertEqual(
            self.check_err([{"class": 1, "subclass": 2, "fix": {"name": "toto"}}]), None
        )
        self.assertEqual(
            self.check_err(
                [{"class": 1, "subclass": 2, "fix": {"+": {"name": "toto"}}}]
            ),
            None,
        )

        with pytest.raises(Exception):
            self.check_err([{"unknown": "x"}])
        with pytest.raises(Exception):
            self.check_err([{"class": "a", "subclass": 2}])
        with pytest.raises(Exception):
            self.check_err([{"class": 1, "subclass": "b"}])
        with pytest.raises(Exception):
            self.check_err([{"class": 1, "subclass": 2, "text": "toto"}])

        with pytest.raises(Exception):
            self.check_err(["unknown"])

    def test_check_dict(self):
        self.assertEqual(self.check_dict({"a": "toto"}, None), None)
        self.assertEqual(self.check_dict({"a": ["toto"]}, None), None)
        self.assertEqual(self.check_dict({"a": ["toto", "titi"]}, None), None)
        self.assertEqual(self.check_dict({"a": ["toto", {"a": "titi"}]}, None), None)

    def test_check_array(self):
        self.assertEqual(self.check_array("toto", None), None)
        self.assertEqual(self.check_array(["toto"], None), None)
        self.assertEqual(self.check_array(["toto", "titi"], None), None)
        self.assertEqual(self.check_array(["toto", {"a": "titi"}], None), None)
        self.assertEqual(self.check_array(["toto", ["a", "titi"]], None), None)

    def test_availableMethodes(self):
        class Plugin_with_node(Plugin):
            def node(self, node, tags):
                pass  # pragma: no cover

        a = Plugin_with_node(None)
        self.assertEqual(a.availableMethodes(), ["node"])

        class Plugin_with_way(Plugin):
            def way(self, node, tags, nodes):
                pass  # pragma: no cover

        a = Plugin_with_way(None)
        self.assertEqual(a.availableMethodes(), ["way"])

        class Plugin_with_relation(Plugin):
            def relation(self, relation, tags, members):
                pass  # pragma: no cover

        a = Plugin_with_relation(None)
        self.assertEqual(a.availableMethodes(), ["relation"])

        class Plugin_with_all(Plugin_with_node, Plugin_with_way, Plugin_with_relation):
            pass

        a = Plugin_with_all(None)
        self.assertEqual(a.availableMethodes(), ["node", "way", "relation"])
