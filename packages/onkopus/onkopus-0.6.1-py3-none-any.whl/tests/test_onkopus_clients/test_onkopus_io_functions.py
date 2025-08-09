import unittest
import onkopus

class TestOnkopusIOFunctions(unittest.TestCase):

    def test_get_onkopus_clients(self):
        module = "clinvar"
        genome_version = "hg19"

        client = onkopus.get_onkopus_client(module, genome_version)

