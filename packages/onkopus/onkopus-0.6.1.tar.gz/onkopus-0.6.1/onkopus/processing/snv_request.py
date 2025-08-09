from onkopus.conf import read_config as config
import copy, traceback
import adagenes as ag
from adagenes.tools.preprocessing import generate_biomarker_frame_from_gene_name_str
from adagenes.tools import generate_keys
from onkopus.processing import annotate_variant_data
from adagenes.tools.format_requests import separate_unidentified_snvs
from adagenes.tools.data_structures import merge_dictionaries
import onkopus


def annotate_snvs(annotated_data, genome_version="hg38", oncokb_key=None,
                  lo_hg19=None,lo_hg38=None,lo_t2t=None,
                  tumor_type=None, request_id=None,
                  include_clinical_data=True,
                  include_gene=True,
                  include_acmg=True
                  ):
    """

    :param annotated_data:
    :param genome_version:
    :param oncokb_key:
    :param lo_hg19:
    :param lo_hg38:
    :param lo_t2t:
    :param tumor_type:
    :return:
    """
    snv_data = {}
    for var in annotated_data.keys():
        mut_type = ""
        if "variant_data" in annotated_data[var]:
            if "mutation_type" in annotated_data[var]["variant_data"]:
                mut_type = annotated_data[var]["variant_data"]["mutation_type"]
        if "mutation_type" in annotated_data[var]:
            mut_type = annotated_data[var]["mutation_type"]
        #print("mut ",mut_type, ": ",annotated_data[var])
        if mut_type == "snv":
            snv_data[var] = annotated_data[var]

    if len(list(snv_data.keys())) > 0:
        snv_data = annotate_variant_data(snv_data, genome_version=genome_version, oncokb_key=oncokb_key,lo_hg19=lo_hg19,
                                         lo_hg38=lo_hg38,lo_t2t=lo_t2t, tumor_type=tumor_type, request_id=request_id,
                                         include_clinical_data=include_clinical_data,
                                        include_gene=include_gene,
                                        include_acmg=include_acmg
                                         )
    #snv_data = onkopus.onkopus_clients.AggregatorClient(genome_version=genome_version).process_data(snv_data)

    for var in snv_data.keys():
        annotated_data[var] = snv_data[var]

    return annotated_data


def analyze_genomic_location_request(genompos, genome_version: str = 'hg38', data=None, tumor_type=None):
    """

    :param genompos:
    :param genome_version:
    :param data:
    :return:
    """
    print("analyze genomic location request: ",genompos)

    if data is None:
        annotated_data = {}
    else:
        annotated_data = data

    perform_query = False
    if genompos is not None:
        if genompos != '':
            # Check if the input string has the required format
            # TODO
            print("gpos ",genompos)

            # parse genome location
            variant_str = genompos.split(",")
            for var in variant_str:
                try:
                    if var != "":
                        var_form = var.replace("CHR", "chr")
                        annotated_data[var_form] = {config.__FEATURE_QID__: var_form}


                        gene_data = {}
                        #for key in annotated_data.keys():
                        #    gene, variant_exchange = annotated_data[key][config.uta_adapter_srv_prefix]["gene_name"], \
                        #                             annotated_data[key][config.uta_adapter_srv_prefix][
                        #                                 "variant_exchange"]
                        #    gene_data[gene] = {}
                        #    gene_data[gene][config.uta_adapter_srv_prefix] = {
                        #        config.__FEATURE_VARIANT__: variant_exchange,
                        #        config.__FEATURE_GENE__: gene
                        #    }

                        #client = adagenes.onkopus_clients.CCSGeneToGenomicClient(
                        #    genome_version=genome_version)
                        #gene_data_annotated = client.process_data(gene_data)
                        #gene_data_annotated = client.generate_genome_locations_as_keys(gene_data_annotated)

                        #gene_data_annotated_upper = {}
                        #for key in gene_data_annotated.keys():
                        #    newkey = key.upper()
                        #    newkey = newkey.replace("CHR", "chr")
                        # #   gene_data_annotated_upper[newkey] = gene_data_annotated[key]
                        #for key in annotated_data.keys():
                        #    annotated_data[key][config.uta_adapter_genetogenomic_srv_prefix] = \
                        #        gene_data_annotated_upper[key][adagenes.config.uta_adapter_genetogenomic_srv_prefix]
                        #    annotated_data[key][config.variant_data_key] = \
                        #        annotated_data[key][config.variant_data_key] | gene_data_annotated_upper[key][
                        #            adagenes.config.variant_data_key]
                except:
                    print("error parsing genomic positions")
                    print(traceback.format_exc())
                perform_query = True

        if (len(annotated_data) > 0) and perform_query:

            #annotated_data = generate_keys(annotated_data)
            #annotated_data = adagenes.tools.reference_genomes.transform_hg19_in_hg38_bframe(annotated_data,genome_version)
            if genome_version != "hg38":
                print("Run liftover from ",genome_version," to hg38")
                annotated_data = ag.LiftoverClient(genome_version=genome_version).process_data(annotated_data, target_genome="hg38")
                print("after li ",annotated_data)
            genome_version = "hg38"
            annotated_data = ag.clients.LiftoverAnnotationClient(
                genome_version=genome_version).process_data(annotated_data)

            annotated_data = onkopus.onkopus_clients.UTAAdapterClient(
                genome_version=genome_version).process_data(annotated_data)

            annotated_data = annotate_variant_data(annotated_data, genome_version=genome_version, tumor_type=tumor_type)

        for var in annotated_data.keys():
            if "variant_data" in annotated_data[var]:
                annotated_data[var]["variant_data"]["genomic_location"] = var

        return annotated_data


def analyze_snv_request(
                            gene_names_prot_change=None,
                            genome_version: str = 'hg38',
                            data=None,
                            oncokb_key='',
                            lo_hg19=None,
                            lo_hg38=None,
                            lo_t2t=None,
                            tumor_type=None
                        ):
    """
    Annotates variants identified by gene name and protein change

    :param gene_names_prot_change: Comma-separated list of genes and protein change ('BRAF:V600E,TP53:R282W')
    :param genome_version:
    :param data
    :return:
    """
    print("analyze variant search: ", gene_names_prot_change)
    if gene_names_prot_change == "":
        return {}, {}

    if data is None:
        annotated_data = {}
    else:
        annotated_data = data

    perform_query = False
    unidentified_snvs={}

    # retrieve genomic data if gene name and protein change are given
    if (gene_names_prot_change is not None) and (gene_names_prot_change != ''):
        gene_data = generate_biomarker_frame_from_gene_name_str(gene_names_prot_change)

        client = onkopus.onkopus_clients.CCSGeneToGenomicClient(genome_version=genome_version)
        annotated_data = client.process_data(copy.deepcopy(gene_data), input_format='json')

        annotated_data = separate_unidentified_snvs(annotated_data)

        annotated_data = onkopus.onkopus_clients.UTAAdapterClient(
            genome_version=genome_version).process_data(annotated_data)

        perform_query = True

    if (len(annotated_data) > 0) and perform_query:
        annotated_data = generate_keys(annotated_data,config.onkopus_modules)
        #print("analyze variant data request")
        #print("gv",genome_version," keys ", list(annotated_data.keys()))
        #annotated_data = ag.tools.reference_genomes.transform_hg19_in_hg38_bframe(annotated_data, genome_version)

        if genome_version != "hg38":
            #annotated_data = ag.clients.LiftoverClient(
            #    genome_version=genome_version).process_data(annotated_data, lo_hg19=lo_hg19, lo_hg38=lo_hg38)
            # print("Liftover: ",annotated_data)
            #annotated_data = generate_keys(annotated_data)
            annotated_data = ag.LiftoverClient(genome_version=genome_version).process_data(annotated_data,
                                                                                                 target_genome="hg38")
        genome_version = "hg38"

        if genome_version == "hg38":
            annotated_data = ag.tools.reference_genomes.add_hg38_positions(annotated_data)
        genome_version = "hg38"
        #print("keys ", list(annotated_data.keys()))
        annotated_data = annotate_variant_data(annotated_data, genome_version=genome_version, oncokb_key=oncokb_key,
                                               lo_hg19=lo_hg19,lo_hg38=lo_hg38,lo_t2t=lo_t2t,
                                               tumor_type=tumor_type)

    for var in annotated_data.keys():
        if "variant_data" in annotated_data[var]:
            annotated_data[var]["variant_data"]["genomic_location"] = var

    #annotated_data = merge_dictionaries(annotated_data,unidentified_snvs)

    return annotated_data
