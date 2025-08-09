import unittest

import adagenes.tools.json_mgt


class TestPreprocessing(unittest.TestCase):

    def test_default_key_generation(self):
        variant_data = {"chr1:114713908T>A": {}}

        #variant_data = adagenes.tools.json_mgt.generate_keys(variant_data)
        #print(variant_data)
