import traceback, datetime, json
import adagenes.tools.module_requests as req
from onkopus.conf import read_config as conf_reader
import requests
from json import JSONDecodeError


class PDBClient:

    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.info_lines= conf_reader.onkopus_plots_info_lines
        self.url_pattern = conf_reader.onkopus_plots_src
        self.srv_prefix = conf_reader.onkopus_plots_srv_prefix
        self.response_keys = conf_reader.onkopus_plots_response_keys
        self.extract_keys = conf_reader.onkopus_plots_keys

        self.qid_key = "q_id"
        if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
            self.qid_key = "q_id_hg19"
        self.error_logfile = error_logfile

    def process_data(self, variant_data, plot=None):
            """
            Generates JSON data for a Plotly variant needleplot with added variant annotations

            :param variant_data:
            :return:
            """
            if "UTA_Adapter" in variant_data:
                if ("gene_name" in variant_data["UTA_Adapter"]):# and ("variant_exchange" in variant_data["UTA_Adapter"]):
                    #q = variant_data["UTA_Adapter"]["gene_name"] + ':' + variant_data["UTA_Adapter"]["variant_exchange"]
                    # url = conf_reader.protein_module_src + q

                    if plot is not None:
                        if plot == "pdb_openfold_wt":
                            url = conf_reader.protein_module_pdb_openfold_wt_src + "/" + variant_data["UTA_Adapter"][
                                "gene_name"] + "/True"
                        elif plot == "pdb_openfold_mutated":
                            url = conf_reader.protein_module_pdb_openfold_mutated_src + "/" + variant_data["UTA_Adapter"][
                                "gene_name"] + ":" + variant_data["UTA_Adapter"][
                                "variant_exchange"] + "/True"
                        else:
                            url = conf_reader.protein_module_pdb_src + "/" + variant_data["UTA_Adapter"]["gene_name"] + "/True"
                    else:
                        url = conf_reader.protein_module_pdb_src + "/" + variant_data["UTA_Adapter"][
                            "gene_name"] + "/True"

                    print(url)
                    graphJSON = requests.get(url, timeout=60)
                    try:
                        return graphJSON.json()
                    except JSONDecodeError:
                        print("Could not decode JSON: ", graphJSON,": ",traceback.format_exc())
                        return {}
            else:
                print("Could not find UTA adapter section")
                return {}
