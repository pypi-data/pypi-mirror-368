import unittest, os
import onkopus as op
import adagenes as ag


class ProteinDomainsTestCase(unittest.TestCase):

    def test_protein_domains_client_hg19(self):
        genome_version = 'hg19'
        #data = {"chr7:140453136A>T": {}}
        #data = ag.LiftoverAnnotationClient(genome_version=genome_version,target_genome="hg38").process_data(data)
        data = {"chr7:140753336A>T":{}}
        genome_version="hg38"
        data = op.uta_adapter_client.UTAAdapterClient(
            genome_version=genome_version).process_data(data)
        data = op.ProteinDomainClient(
            genome_version=genome_version).process_data(data)
        #print(data)
        expected_content = ('{"protein_acession":{"0":"BRAF;","1":"BRAF;","2":"BRAF;"},"seq_MD5_digest":{"0":"74c9b69323bd112084c1b5b385e7e6c5","1":"74c9b69323bd112084c1b5b385e7e6c5","2":"74c9b69323bd112084c1b5b385e7e6c5"},"seq_length":{"0":766,"1":766,"2":766},"analysis":{"0":"Pfam","1":"Pfam","2":"Pfam"},"sig_accession":{"0":"PF02196","1":"PF07714","2":"PF00130"},"sig_description":{"0":"Raf-like '
 'Ras-binding domain","1":"Protein tyrosine and serine\\/threonine '
 'kinase","2":"Phorbol esters\\/diacylglycerol binding domain (C1 '
 'domain)"},"start_location":{"0":157,"1":457,"2":235},"stop_location":{"0":225,"1":712,"2":281},"e_value":{"0":1.2e-23,"1":1.5e-59,"2":0.0000000006},"match_status":{"0":"T","1":"T","2":"T"},"date":{"0":"25-10-2024","1":"25-10-2024","2":"25-10-2024"},"ipr_accession":{"0":"IPR003116","1":"IPR001245","2":"IPR002219"},"ipr_description":{"0":"Raf-like '
 'Ras-binding","1":"Serine-threonine\\/tyrosine-protein kinase, catalytic '
 'domain","2":"Protein kinase C-like, phorbol ester\\/diacylglycerol-binding '
 'domain"},"go_terms":{"0":"-","1":"-","2":"-"},"pathway_annotation":{"0":"-","1":"-","2":"-"}}')
        self.assertEqual(data["chr7:140753336A>T"]["protein_domains"], expected_content, "")

    def test_protein_domain_client_cna(self):
        genome_version = 'hg19'
        # data = {"chr7:140453136A>T": {}}
        # data = ag.LiftoverAnnotationClient(genome_version=genome_version,target_genome="hg38").process_data(data)
        data = {"chr15:30103918><DUP>": { "variant_data":{"CHROM":15,"POS":30103918, "POS2":30644082} }}
        genome_version = "hg38"
        #data = op.uta_adapter_client.UTAAdapterClient(
        #    genome_version=genome_version).process_data(data)
        data = op.GENCODECNAClient(genome_version=genome_version).process_data(data)
        data = op.ProteinDomainCNAClient(
            genome_version=genome_version).process_data(data)
        # print(data)
        expected_content = {'CHRFAM7A': '{"protein_acession":{"0":"CHRFAM7A;","1":"CHRFAM7A;"},"seq_MD5_digest":{"0":"c6c9eb6631ad75594b2ca964296df951","1":"c6c9eb6631ad75594b2ca964296df951"},"seq_length":{"0":412,"1":412},"analysis":{"0":"Pfam","1":"Pfam"},"sig_accession":{"0":"PF02932","1":"PF02931"},"sig_description":{"0":"Neurotransmitter-gated '
             'ion-channel transmembrane region","1":"Neurotransmitter-gated '
             'ion-channel ligand binding '
             'domain"},"start_location":{"0":147,"1":28},"stop_location":{"0":396,"1":140},"e_value":{"0":4.9e-58,"1":1.9e-29},"match_status":{"0":"T","1":"T"},"date":{"0":"27-10-2024","1":"27-10-2024"},"ipr_accession":{"0":"IPR006029","1":"IPR006202"},"ipr_description":{"0":"Neurotransmitter-gated '
             'ion-channel transmembrane domain","1":"Neurotransmitter-gated '
             'ion-channel ligand-binding '
             'domain"},"go_terms":{"0":"-","1":"-"},"pathway_annotation":{"0":"-","1":"-"}}',
 'GOLGA8R': '{"protein_acession":{"0":"GOLGA8R;","1":"GOLGA8R;","2":"GOLGA8R;"},"seq_MD5_digest":{"0":"110809df137b429e351f1e9bd0f30bdf","1":"110809df137b429e351f1e9bd0f30bdf","2":"110809df137b429e351f1e9bd0f30bdf"},"seq_length":{"0":631,"1":631,"2":631},"analysis":{"0":"Pfam","1":"Pfam","2":"Pfam"},"sig_accession":{"0":"PF19046","1":"PF15070","2":"PF15070"},"sig_description":{"0":"GM130 '
            'C-terminal binding motif","1":"Putative golgin subfamily A member '
            '2-like protein 5","2":"Putative golgin subfamily A member 2-like '
            'protein '
            '5"},"start_location":{"0":594,"1":365,"2":226},"stop_location":{"0":631,"1":493,"2":364},"e_value":{"0":0.0,"1":0.0000000063,"2":2e-19},"match_status":{"0":"T","1":"T","2":"T"},"date":{"0":"28-10-2024","1":"28-10-2024","2":"28-10-2024"},"ipr_accession":{"0":"IPR043937","1":"IPR043976","2":"IPR043976"},"ipr_description":{"0":"Golgin '
            'subfamily A member 2, C-terminal binding motif","1":"Golgin '
            'subfamily A, conserved domain","2":"Golgin subfamily A, conserved '
            'domain"},"go_terms":{"0":"-","1":"-","2":"-"},"pathway_annotation":{"0":"-","1":"-","2":"-"}}'}
        self.assertEqual(data["chr15:30103918><DUP>"]["protein_domains"], expected_content, "")


