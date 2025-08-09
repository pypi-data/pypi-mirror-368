import traceback
from json import JSONDecodeError
import requests
import onkopus.conf.read_config as conf_reader


def generate_protein_plot(variant_data):
    """
    Generates JSON data for a Plotly variant needleplot

    :param variant_data:
    :return:
    """
    if "UTA_Adapter" in variant_data:
        if ("gene_name" in variant_data["UTA_Adapter"]) and ("variant_exchange" in variant_data["UTA_Adapter"]):
            q = variant_data["UTA_Adapter"]["gene_name"] + ':' + variant_data["UTA_Adapter"]["variant_exchange"]
            url = conf_reader.protein_module_src + q
            #print(url)
            try:
                graphJSON = requests.get(url, timeout=60)
                return graphJSON.json()
            except JSONDecodeError:
                print(traceback.format_exc())
                return {}
        elif "gene_name" in variant_data["UTA_Adapter"]:
            q = variant_data["UTA_Adapter"]["gene_name"]
            url = conf_reader.protein_module_src + q
            #print(url)
            try:
                graphJSON = requests.get(url, timeout=60)
                return graphJSON.json()
            except JSONDecodeError:
                print(traceback.format_exc())
                return {}
    else:
        print(variant_data)
        return {}


def generate_protein_plot_with_annotations(variant_data, module_server=conf_reader.__MODULE_SERVER__):
    """
    Generates JSON data for a Plotly variant needleplot with added variant annotations

    :param variant_data:
    :return:
    """
    if "UTA_Adapter" in variant_data:
        if ("gene_name" in variant_data["UTA_Adapter"]) and ("variant_exchange" in variant_data["UTA_Adapter"]):
            q = variant_data["UTA_Adapter"]["gene_name"] + ':' + variant_data["UTA_Adapter"]["variant_exchange"]
            #url = conf_reader.protein_module_src + q
            url = conf_reader.protein_module_annotations_src
            #print(url)
            #graphJSON = requests.get(url, timeout=60)

            data = {}
            data["web_prefix"] = conf_reader.__MODULE_PROTOCOL__ + "://" + module_server + ":" + conf_reader.__PORT_ONKOPUS_WEB__ + "/"
            data["gene_variant"] = variant_data["UTA_Adapter"]["gene_name"] + ":" + variant_data["UTA_Adapter"]["variant_exchange"]
            print(data)

            graphJSON = requests.post(url, json=data, timeout=60)
            try:
                return graphJSON.json()
            except JSONDecodeError:
                print("Could not decode JSON: ",graphJSON)
                return {}
        elif "gene_name" in variant_data["UTA_Adapter"]:
            q = variant_data["UTA_Adapter"]["gene_name"]
            url = conf_reader.protein_module_src + q
            #print(url)
            try:
                graphJSON = requests.get(url, timeout=60)
                return graphJSON.json()
            except JSONDecodeError:
                print(traceback.format_exc())
                return {}
    else:
        print(variant_data)
        return {}
