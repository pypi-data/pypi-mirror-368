import copy
import adagenes
import adagenes.conf.read_config as config

def split_data_by_mutation_type(data):

    dc = {"snvs": {}, "indels": {}, "fusions": {}, "genes": {},"unidentified": {}}

    for var in data.keys():
        if "mutation_type" in data[var]:
            if data[var]["mutation_type"] == "snv":
                dc["snvs"][var] = data[var]
            elif data[var]["mutation_type"] == "indel":
                dc["indels"][var] = data[var]
            elif data[var]["mutation_type"] == "fusion":
                dc["fusions"][var] = data[var]
            elif data[var]["mutation_type"] == "gene":
                dc["genes"][var] = data[var]
            else:
                dc["unidentified"][var] = data[var]
        else:
            dc["unidentified"][var] = data[var]

    return dc

def get_genomic_qid(data):

    #if "hgnc_symbol"
    pass
    # qid


def protein_to_genomic(annotated_data, results_string, res, vcf_lines,module, genome_version="hg38"):
    """
    Converts data of a single biomarker including IDs on protein level into IDs on genomic level

    :param annotated_data:
    :param results_string:
    :return:
    """
    chr, ref_seq, pos, ref, alt = adagenes.tools.parse_genomic_data.parse_genome_position(
        results_string)
    qid = 'chr' + chr + ':' + pos + ref + '>' + alt

    if qid not in annotated_data:
        annotated_data[qid] = copy.deepcopy(vcf_lines)

    if config.variant_data_key not in annotated_data[qid]:
        annotated_data[qid][config.variant_data_key] = {}

    annotated_data[qid][config.variant_data_key]['CHROM'] = chr
    annotated_data[qid][config.variant_data_key]['reference_sequence'] = ref_seq
    annotated_data[qid][config.variant_data_key]['POS'] = pos
    annotated_data[qid][config.variant_data_key]['REF'] = ref
    annotated_data[qid][config.variant_data_key]['ALT'] = alt
    annotated_data[qid][config.variant_data_key]['POS_' + genome_version] = pos
    annotated_data[qid]["q_id"] = "chr" + chr + ":" + str(pos) + ref + ">" + alt
    annotated_data[qid][config.variant_data_key]['ID'] = ''
    annotated_data[qid][config.variant_data_key]['QUAL'] = ''
    annotated_data[qid][config.variant_data_key]['FILTER'] = ''
    annotated_data[qid][config.variant_data_key]['type'] = 'g'
    annotated_data[qid]["mutation_type_detail"] = 'Missense_Mutation'

    if "refAmino" in res:
        annotated_data[qid][config.variant_data_key]['ref_aa'] = res["refAmino"]
        annotated_data[qid][config.variant_data_key]['alt_aa'] = res["varAmino"]

    if module is not None:
        annotated_data[qid][module] = res
    else:
        annotated_data[qid] = res

    # add previously known information on gene names and aa exchange
    if "hgnc_symbol" in res:
        annotated_data[qid][config.variant_data_key]["gene_name"] = res['hgnc_symbol']
        annotated_data[qid][config.variant_data_key]["amino_acid_exchange"] = res['aminoacid_exchange']
        if "UTA_Adapter" not in annotated_data[qid].keys():
            annotated_data[qid]["UTA_Adapter"] = {}
        annotated_data[qid]["UTA_Adapter"]["gene_name"] = res['hgnc_symbol']
        annotated_data[qid]["UTA_Adapter"]["variant_exchange"] = res['aminoacid_exchange']

    annotated_data[qid][config.uta_adapter_genetogenomic_srv_prefix] = res
    annotated_data[qid]["level"] = "g"
    annotated_data[qid]["type"] = "g"

    return annotated_data

def transcript_to_genomic(annotated_data, results_string, res, vcf_lines,module, genome_version="hg38"):
    """
    Converts data of a single biomarker including IDs on protein level into IDs on genomic level

    :param annotated_data:
    :param results_string:
    :return:
    """
    #nm, ref_seq, pos, ref, alt = adagenes.tools.parse_genomic_data.parse_transcript_cdna(
    #    results_string)
    #print("res ",res)
    variant_g = res["variant_g"]
    chr, ref_seq, pos, ref, alt = adagenes.tools.parse_genomic_data.parse_genome_position(variant_g)
    #qid = 'chr' + chrom + ':' + pos + ref + '>' + alt

    #print("elements ",chr,ref_seq, pos, ref, alt)
    qid = 'chr' + chr + ':' + pos + ref + '>' + alt

    if qid not in annotated_data:
        annotated_data[qid] = copy.deepcopy(vcf_lines)

    if config.variant_data_key not in annotated_data[qid]:
        annotated_data[qid][config.variant_data_key] = {}

    annotated_data[qid][config.variant_data_key]['CHROM'] = chr
    annotated_data[qid][config.variant_data_key]['reference_sequence'] = ref_seq
    annotated_data[qid][config.variant_data_key]['POS'] = pos
    annotated_data[qid][config.variant_data_key]['REF'] = ref
    annotated_data[qid][config.variant_data_key]['ALT'] = alt
    annotated_data[qid][config.variant_data_key]['POS_' + genome_version] = pos
    annotated_data[qid]["q_id"] = "chr" + chr + ":" + str(pos) + ref + ">" + alt
    annotated_data[qid][config.variant_data_key]['ID'] = ''
    annotated_data[qid][config.variant_data_key]['QUAL'] = ''
    annotated_data[qid][config.variant_data_key]['FILTER'] = ''
    annotated_data[qid][config.variant_data_key]['type'] = 'g'
    annotated_data[qid]["mutation_type_detail"] = 'Missense_Mutation'

    if "refAmino" in res:
        annotated_data[qid][config.variant_data_key]['ref_aa'] = res["refAmino"]
        annotated_data[qid][config.variant_data_key]['alt_aa'] = res["varAmino"]

    if module is not None:
        annotated_data[qid][module] = res
    else:
        annotated_data[qid] = res

    # add previously known information on gene names and aa exchange
    if "hgnc_symbol" in res:
        annotated_data[qid][config.variant_data_key]["gene_name"] = res['hgnc_symbol']
        annotated_data[qid][config.variant_data_key]["amino_acid_exchange"] = res['aminoacid_exchange']
        if "UTA_Adapter" not in annotated_data[qid].keys():
            annotated_data[qid]["UTA_Adapter"] = {}
        annotated_data[qid]["UTA_Adapter"]["gene_name"] = res['hgnc_symbol']
        annotated_data[qid]["UTA_Adapter"]["variant_exchange"] = res['aminoacid_exchange']

    annotated_data[qid][config.uta_adapter_genetogenomic_srv_prefix] = res
    annotated_data[qid]["level"] = "g"
    annotated_data[qid]["type"] = "g"

    return annotated_data
