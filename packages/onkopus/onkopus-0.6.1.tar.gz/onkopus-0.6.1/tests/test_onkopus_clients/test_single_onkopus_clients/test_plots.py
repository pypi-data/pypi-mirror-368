import unittest
import onkopus


class PllotsTestCase(unittest.TestCase):

    def test_radar_plot_client(self):
        genome_version = 'hg38'

        data = {"chr7:140753336A>T": {}, "chr12:25245350C>T": {}}

        variant_data = onkopus.onkopus_clients.uta_adapter_client.UTAAdapterClient(
            genome_version=genome_version).process_data(data)
        print("uta response", variant_data)

        client = onkopus.onkopus_clients.REVELClient(genome_version=genome_version)
        variant_data = client.process_data(variant_data)
        client = onkopus.onkopus_clients.MVPClient(genome_version=genome_version)
        variant_data = client.process_data(variant_data)
        client = onkopus.onkopus_clients.DBNSFPClient(genome_version=genome_version)
        variant_data = client.process_data(variant_data)
        variant_data = onkopus.InterpreterClient(genome_version="hg38").process_data(variant_data)

        variant_data = onkopus.onkopus_clients.PlotClient(
            genome_version=genome_version).process_data(variant_data,plot="categorical_pathogenicity")

        print("Plot response ",variant_data)
