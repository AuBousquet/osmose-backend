# -*- coding: utf-8 -*-
from plugins.Josm_deprecated import Josm_deprecated
from plugins.Plugin import TestPluginCommon


class Test(TestPluginCommon):
    def test(self):
        n = Josm_deprecated(None)

        class _config:
            options = {"country": None, "language": None}

        class father:
            config = _config()

        n.father = father()
        n.init(None)
        data = {"id": 0, "lat": 0, "lon": 0}

        self.check_err(
            n.node(data, {"is_in:sea": "A", "is_in:country:": "B"}),
            expected={
                "class": 9002001,
                "subclass": 1024340790,
                "fix": {"-": ["is_in:sea"]},
            },
        )
        self.check_err(
            n.node(data, {"is_in:country": "A", "is_in:sea": "B"}),
            expected={
                "class": 9002001,
                "subclass": 1024340790,
                "fix": {"-": ["is_in:country"]},
            },
        )
