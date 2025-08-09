from onkopus.onkopus_clients import CCSGeneFusionClient
from adagenes.tools import generate_keys
from onkopus.conf import read_config as conf_reader
import onkopus as op


def annotate_fusions(annotated_data, genome_version="hg38",
                     oncokb_key=None, tumor_type=None,
                     request_id=None,include_clinical_data=True,
                  include_gene=True,
                  include_acmg=True):
    snv_data = {}
    for var in annotated_data.keys():
        mut_type = ""
        if "variant_data" in annotated_data[var]:
            if "mutation_type" in annotated_data[var]["variant_data"]:
                mut_type = annotated_data[var]["variant_data"]["mutation_type"]
        elif "mutation_type" in annotated_data[var]:
            mut_type = annotated_data[var]["mutation_type"]
        if mut_type == "fusion":
            snv_data[var] = annotated_data[var]

    if len(list(snv_data.keys())) > 0:
        snv_data = annotate_fusion_data(snv_data, genome_version=genome_version,tumor_type=tumor_type)
        snv_data = op.AggregatorClient(genome_version=genome_version).process_data(snv_data)

    for var in snv_data.keys():
        annotated_data[var] = snv_data[var]

    #return annotated_data
    return snv_data

def fusion_request(gene_fusion_str: str, genome_version='hg38', tumor_type=None):
    """
    Annotates gene fusions with associated Onkopus modules

    :param gene_fusion_str:
    :param genome_version:
    :return:
    """
    print("gene fusion query: ", gene_fusion_str)
    if gene_fusion_str == "":
        return {}
    annotated_data = {}
    if gene_fusion_str != "":
        annotated_data[gene_fusion_str] = {}

    annotated_data = annotate_fusion_data(annotated_data, genome_version=genome_version, tumor_type=tumor_type)

    return annotated_data


def annotate_fusion_data(annotated_data, genome_version="hg38", tumor_type=None):
    """

    :param annotated_data:
    :param genome_version:
    :param tumor_type:
    :return:
    """
    client = CCSGeneFusionClient(
        genome_version=genome_version)
    annotated_data = client.process_data(annotated_data)
    annotated_data = generate_keys(annotated_data, conf_reader.onkopus_modules)

    return annotated_data
