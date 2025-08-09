import traceback, datetime, json
import adagenes.tools.module_requests as req
from onkopus.conf import read_config as conf_reader
import requests
from json import JSONDecodeError


class GeneExpressionPlotClient:

    def __init__(self, error_logfile=None):
        #self.genome_version = genome_version
        self.info_lines= conf_reader.onkopus_plots_info_lines
        self.url_pattern = conf_reader.onkopus_plots_src
        self.srv_prefix = conf_reader.onkopus_plots_srv_prefix
        self.response_keys = conf_reader.onkopus_plots_response_keys
        self.extract_keys = conf_reader.onkopus_plots_keys

        self.qid_key = "q_id"
        self.error_logfile = error_logfile

    def process_data(self, variant_data):
            """
            Generates JSON data for a Plotly variant needle plot with added variant annotations

            :param variant_data:
            :return:
            """
            if "UTA_Adapter" in variant_data:
                if ("gene_name" in variant_data["UTA_Adapter"]):

                    url = conf_reader.ge_plot_module_src + "?gene=" + variant_data["UTA_Adapter"]["gene_name"]

                    print(url)
                    graphJSON = requests.get(url, timeout=60)
                    try:
                        return graphJSON.json()
                    except JSONDecodeError:
                        print("Could not decode JSON: ", graphJSON,": ",traceback.format_exc())
                        return {}
            else:
                url = conf_reader.ge_plot_module_src + "?gene=" + variant_data

                print(url)
                graphJSON = requests.get(url, timeout=60)
                try:
                    return graphJSON.json()
                except JSONDecodeError:
                    print("Could not decode JSON: ", graphJSON, ": ", traceback.format_exc())
                    return {}
