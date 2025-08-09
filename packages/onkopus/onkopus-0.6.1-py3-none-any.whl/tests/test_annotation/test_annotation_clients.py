import unittest, copy
import onkopus
"""
class AnnotationTestCase(unittest.TestCase):

    def test_oncokb_client(self):
        genome_version = 'hg19'

        data = {"chr17:7681744T>C": {}, "chr10:8115913C>T": {}}
        variant_dc = {"0": "chr17:7681744T>C", "1": "chr10:8115913C>T"}

        variant_data = onkopus.clients.OncoKBClient(
            genome_version=genome_version).process_data(data)

        print("OncoKB response ",variant_data)

    def test_ccs_liftover_client(self):
        genome_version = 'hg19'

        data = {"chr17:7681744T>C": {}, "chr10:8115913C>T": {}}
        variant_dc = {"0": "chr17:7681744T>C", "1": "chr10:8115913C>T"}

        data = onkopus.clients.UTAAdapterClient(
            genome_version=genome_version).process_data(data)

        variant_data = onkopus.clients.LiftOverClient(
            genome_version=genome_version).process_data(data)

        print("LiftOver Response: ", variant_data)

    def test_civic_client(self):
        genome_version = 'hg38'

        data = {"chr7:140753336A>T": {}, "chr17:7673776G>A": {}}
        variant_dc = {"0": "chr7:140753336A>T", "1": "chr17:7673776G>A"}

        variant_data = onkopus.clients.UTAAdapterClient(
            genome_version=genome_version).process_data(data)
        print("uta res", variant_data)

        client = onkopus.clients.CIViCClient(genome_version=genome_version)
        res = client.process_data(variant_data)

        print("CIViC response ",res)

    def test_mvp_client_hg38(self):
        genome_version = 'hg38'

        data = {"chr7:140753336A>T": {}, "chr17:7673776G>A": {}}
        variant_dc = {"0": "chr7:140753336A>T", "1": "chr17:7673776G>A"}

        variant_data = onkopus.clients.UTAAdapterClient(
            genome_version=genome_version).process_data(data)

        variant_data = onkopus.clients.LiftOverClient(
            genome_version=genome_version).process_data(variant_data)

        print("uta res", variant_data)

        client = onkopus.clients.MVPClient(genome_version=genome_version)
        client.process_data(variant_data)

    def test_mvp_client(self):
        genome_version = 'hg19'

        data = {"chr17:7681744T>C": {}, "chr10:8115913C>T": {}}
        variant_dc = {"0": "chr17:7681744T>C", "1": "chr10:8115913C>T"}

        variant_data = onkopus.clients.UTAAdapterClient(
            genome_version=genome_version).process_data(data)

        client = onkopus.clients.MVPClient(genome_version=genome_version)
        client.process_data(variant_data)

    def test_primateai_client(self):
        genome_version = 'hg19'

        data = {"chr17:7681744T>C": {}, "chr10:8115913C>T": {}}
        variant_dc = {"0": "chr17:7681744T>C", "1": "chr10:8115913C>T"}

        variant_data = onkopus.clients.PrimateAIClient(
            genome_version=genome_version).process_data(data)
        print(variant_data)

    def test_dbnsfp_client(self):
        genome_version = 'hg38'

        data = {"chr14:67885931T>G": {}, "chr7:140753336A>T": {}}
        variant_dc = {"0": "chr14:67885931T>G", "1": "chr7:140753336A>T"}

        variant_data = onkopus.clients.DBSNPClient(
            genome_version=genome_version).process_data(data)
        print(variant_data)

    def test_uta_adapter_genomic_client(self):
        genome_version = 'hg19'
        data = {"TP53:R282W": { "UTA_Adapter": {"gene_name":"TP53", "variant_exchange":"R282W"} }}
        variant_data = onkopus.clients.CCSGeneToGenomicClient(
            genome_version=genome_version).process_data(data)
        print("UTA response ", variant_data)

    def test_uta_adapter_client(self):
        genome_version = 'hg19'
        data = {"chr17:7681744T>C": {}, "chr10:8115913C>T": {}}
        variant_dc = {"0": "chr17:7681744T>C", "1": "chr10:8115913C>T"}
        variant_data = onkopus.clients.UTAAdapterClient(
            genome_version=genome_version).process_data(data)
        print("UTA response ",variant_data)

    def test_vuspredict_client(self):
        genome_version='hg19'

        data = { "chr17:7681744T>C" : {  }, "chr10:8115913C>T":{} }
        variant_dc = { "0": "chr17:7681744T>C", "1": "chr10:8115913C>T" }

        variant_data = onkopus.clients.UTAAdapterClient(genome_version=genome_version).process_data(data)

        client = onkopus.clients.VUSPredictClient(genome_version=genome_version)
        variant_data = client.process_data(variant_data)

        print("VUS-Predict annotation ",variant_data)

    def test_loftool_client(self):
        genome_version='hg19'

        data = { "chr17:7681744T>C" : {  }, "chr10:8115913C>T":{} }
        variant_dc = { "0": "chr17:7681744T>C", "1": "chr10:8115913C>T" }

        variant_data = onkopus.clients.UTAAdapterClient(genome_version=genome_version).process_data(data)
        print("uta res",variant_data)

        client = onkopus.clients.LoFToolClient(genome_version=genome_version)
        client.process_data(variant_data)

    def test_metakb_client(self):
        genome_version = 'hg38'

        data = { "chr7:140753336A>T": {}, "chr12:25245350C>T":{} }
        variant_dc = {"0": "chr7:140753336A>T", "1": "chr12:25245350C>T" }

        variant_data = onkopus.clients.UTAAdapterClient(
            genome_version=genome_version).process_data(data)
        print("uta response", variant_data)

        client = onkopus.clients.MetaKBClient(genome_version=genome_version)
        client.process_data(variant_data)

    def test_metakb_client_gene_only(self):
        genome_version = 'hg38'

        data = { "chr7:140753336A>T": {}, "chr12:25245350C>T":{} }
        variant_dc = {"0": "chr7:140753336A>T", "1": "chr12:25245350C>T" }

        variant_data = onkopus.clients.UTAAdapterClient(
            genome_version=genome_version).process_data(data)
        keys = copy.deepcopy(list(variant_data.keys()))
        for key in keys:
            variant_data[key]['UTA_Adapter'].pop('variant_exchange')
        print("uta response", variant_data)

        client = onkopus.clients.MetaKBClient(genome_version=genome_version)
        client.process_data(variant_data)
"""