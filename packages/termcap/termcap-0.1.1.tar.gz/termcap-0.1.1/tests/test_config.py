import unittest

import termcap.config as config


class TestConf(unittest.TestCase):
    def test_default_templates(self):
        templates = config.default_templates()
