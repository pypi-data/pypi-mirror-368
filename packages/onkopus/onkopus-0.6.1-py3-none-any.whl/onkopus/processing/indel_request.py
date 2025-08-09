import adagenes
import onkopus.onkopus_clients


def annotate_indels(annotated_data, genome_version="hg38",
                    oncokb_key=None, tumor_type=None,
                    request_id=None,
                    include_clinical_data=True,
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
        if mut_type == "indel":
            snv_data[var] = annotated_data[var]

    if len(list(snv_data.keys())) > 0:
        snv_data = annotate_indel_data(snv_data, genome_version=genome_version, oncokb_key=oncokb_key, tumor_type=tumor_type)

        if include_clinical_data is True:
            snv_data = onkopus.onkopus_clients.AggregatorClient(genome_version=genome_version).process_data(snv_data)

    #for var in snv_data.keys():
    #    annotated_data[var] = snv_data[var]
    #return annotated_data
    return snv_data


def indel_request(indels, genome_version="hg38", tumor_type=None):
    """

    :param indel_str:
    :param genome_version:
    :return:
    """
    if len(indels) == 0:
        return {}
    annotated_data = {}
    if len(indels) > 0:
        for indel in indels:
            annotated_data[indel] = {}

            annotated_data[indel] = adagenes.generate_variant_data_section(annotated_data[indel],qid=indel)

    annotated_data = annotate_indel_data(annotated_data, genome_version=genome_version, tumor_type=tumor_type)
    annotated_data = adagenes.tools.get_biomarker_type_aaexchange(annotated_data)

    return annotated_data


def annotate_indel_data(annotated_data, genome_version="hg38", oncokb_key=None, tumor_type=None):
    """
    Annotate insertions and deletions

    :param annotated_data:
    :param genome_version:
    :param oncokb_key:
    :param tumor_type:
    :return:
    """
    annotated_data = onkopus.GENCODEGenomicClient(genome_version=genome_version).process_data(annotated_data)
    annotated_data = onkopus.ClinVarClient(genome_version=genome_version).process_data(annotated_data)
    annotated_data = onkopus.IndelToGeneClient(genome_version=genome_version).process_data(annotated_data)

    return annotated_data

