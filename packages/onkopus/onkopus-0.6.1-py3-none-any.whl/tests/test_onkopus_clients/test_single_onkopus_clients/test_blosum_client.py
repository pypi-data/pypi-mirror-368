import unittest, copy
import onkopus.onkopus_clients
import adagenes


class BLOSUMTestCase(unittest.TestCase):

    def test_blosum_client(self):
        genome_version = 'hg38'
        data = {"NRAS:Q61L": {}, "TP53:R282W": {}, "MUTYH:L420M": {}}
        variant_data = onkopus.onkopus_clients.CCSGeneToGenomicClient(
            genome_version=genome_version).process_data(data)
        variant_data = adagenes.BLOSUMClient().process_data(variant_data)


        print("Response ",variant_data)

