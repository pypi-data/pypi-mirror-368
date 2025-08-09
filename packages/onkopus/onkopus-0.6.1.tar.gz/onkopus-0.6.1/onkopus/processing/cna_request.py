import onkopus as op
from onkopus.processing.parallel_cna_requests import parallel_requests, parallel_requests1


def annotate_cnas(
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
    #print("Annotate CNAS")

    # get genes from biomarker data
    gene_data = {}
    #print(annotated_data)
    for var in annotated_data.keys():
        mut_type = ""

        if "variant_data" in annotated_data[var]:
            if "mutation_type" in annotated_data[var]["variant_data"]:
                mut_type = annotated_data[var]["variant_data"]["mutation_type"]
            elif "mutation_type" in annotated_data[var]:
                mut_type = annotated_data[var]["mutation_type"]
        elif "mutation_type" in annotated_data[var]:
            mut_type = annotated_data[var]["mutation_type"]
        if mut_type == "cnv":
            gene_data[var] = annotated_data[var]

    #print("cna data keys ",gene_data)
    if len(list(gene_data.keys())) > 0:
        gene_data = parallel_requests(gene_data, genome_version=genome_version)

        gene_data = parallel_requests1(gene_data)


    for var in gene_data.keys():
        annotated_data[var] = gene_data[var]

        #annotated_data[var]["UTA_Adapter"] = { "gene_name": var }

    #return annotated_data
    return gene_data
