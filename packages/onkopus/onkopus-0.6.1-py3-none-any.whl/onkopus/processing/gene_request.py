import onkopus
from onkopus.processing.parallel_gene_requests import parallel_requests



def identify_genes_from_request(gene_names, genome_version=None):
    """
    Generates a gene JSON object from a text query

    :param gene_names:
    :param genome_version:
    :return:
    """
    if len(gene_names)>0:
        annotated_data = {}

        for gene in gene_names:
            annotated_data[gene] = {}
            annotated_data[gene]["variant_data"] = {}
            annotated_data[gene]["variant_data"]["mutation_type"] = "gene"

        #annotated_data = annotate_gene_request(annotated_data, genome_version=genome_version)
        return annotated_data
    else:
        return {}


def annotate_genes(
        annotated_data,
        genome_version="hg38",
        tumor_type=None,
        request_id=None,include_clinical_data=True,
                  include_gene=True,
                  include_acmg=True):
    """
    Annotates a gene with associated Onkopus modules

    :param annotated_data:
    :param gene:
    :param genome_version:
    :return:
    """
    # get genes from biomarker data
    gene_data = {}
    for var in annotated_data.keys():
        mut_type = ""

        if "variant_data" in annotated_data[var]:
            if "mutation_type" in annotated_data[var]["variant_data"]:
                mut_type = annotated_data[var]["variant_data"]["mutation_type"]
        elif "mutation_type" in annotated_data[var]:
            mut_type = annotated_data[var]["mutation_type"]
        if mut_type == "gene":
            gene_data[var] = annotated_data[var]

    if len(list(gene_data.keys())) > 0:
        gene_data = parallel_requests(gene_data, genome_version=genome_version)
        if include_clinical_data is True:
            gene_data = onkopus.onkopus_clients.AggregatorClient(genome_version=genome_version).process_data(gene_data)

    for var in gene_data.keys():
        annotated_data[var] = gene_data[var]

        annotated_data[var]["UTA_Adapter"] = { "gene_name": var }

    #return annotated_data
    return gene_data
