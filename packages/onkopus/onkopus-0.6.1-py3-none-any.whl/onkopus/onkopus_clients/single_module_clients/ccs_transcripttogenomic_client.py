import traceback,copy
import onkopus as op
import adagenes.tools.module_requests as req
import adagenes.tools.parse_genomic_data
from onkopus.conf import read_config as config
from adagenes.tools import split_gene_name
import onkopus.tools
import adagenes as ag


def filter_empty_variants(q):
    """
    Filters all variants without a gene name and protein change from the query string

    :param q:
    :return:
    """
    q_new = ""
    q_elements = q.split(",")
    for el in q_elements:
        if (el == "") or (el == ":"):
            pass
        else:
            q_new += el + ","
    q_new = q_new.rstrip(",")
    return q_new


def generate_variant_str_from_gene_names_prot_change(vcf_lines):
    """
    Generates a GeneToGenomic request to the Coordinates Converter service by extracting the protein information from the biomarker
    keys, where keys should be of the format [gene_symbol]:[aa_exchange] (e.g. BRAF:V600E)

    :param vcf_lines:
    :return:
    """
    q = ""
    for variant in vcf_lines.keys():
        resp = split_gene_name(variant)
        if resp:
            gene, variant_exchange = resp[0], resp[1]
            q += gene+":"+variant_exchange+","
    q = q.rstrip(",")
    return q


def generate_variant_str_from_data_in_json(vcf_lines,q_list):
    """
    Generates a GeneToGenomic request to the Coordinates Converter by extracting gene names and amino acid exchange from the biomarker data.
    Usable if a biomarker frame has already been annotated with the CCS GenomicToGene service and should be enriched with additional
    data by the GeneToGenomic service

    :param vcf_lines:
    :return:
    """
    q = ""
    for variant in q_list:
        if config.uta_adapter_srv_prefix in vcf_lines[variant]:
            if "gene_name" in vcf_lines[variant][config.uta_adapter_srv_prefix]:
                gene = vcf_lines[variant][config.uta_adapter_srv_prefix]["gene_name"]
                aa_exchange = vcf_lines[variant][config.uta_adapter_srv_prefix]["variant_exchange"]
                q += gene + ":" + aa_exchange + ","
    q = q.rstrip(",")
    #print(q)
    return q


class TranscriptToGenomicClient:

    def __init__(self, genome_version, data_type=None, error_logfile=None):
        self.genome_version = genome_version
        self.error_logfile = error_logfile
        self.srv_prefix = config.uta_adapter_transcripttogenomic_srv_prefix
        self.data_type = data_type
        self.extract_keys = config.uta_adapter_transcripttogenomic_extract_keys
        self.url = config.uta_adapter_transcripttogenomic_src


    def generate_request_str_of_gene_names(self, vcf_lines,input_format='json'):
        """


        :param vcf_lines:
        :param input_format:
        :return:
        """

        #print("extract data: ",vcf_lines)
        variant_list=[]

        if input_format == 'vcf':
            keys = [config.uta_adapter_srv_prefix + config.concat_char + config.uta_genomic_keys[0],
                    config.uta_adapter_srv_prefix + config.concat_char + config.uta_genomic_keys[0]]
            annotations = adagenes.tools.parse_vcf.extract_annotations_vcf(vcf_lines, keys)
        elif input_format == 'tsv':
            keys = [config.uta_genomic_keys[0], config.uta_genomic_keys[1]]
            annotations = adagenes.tools.parse_vcf.extract_annotations_json(vcf_lines,
                                                                          self.srv_prefix, keys)
        else:
            keys = [config.uta_genomic_keys[0], config.uta_genomic_keys[1]]
            annotations = adagenes.tools.parse_vcf.extract_annotations_json(vcf_lines, config.uta_adapter_srv_prefix, keys)

        gene_names = annotations[keys[0]]
        variants = annotations[keys[1]]
        for i in range(0,len(gene_names)):
            variant_list.append(gene_names[i]+":"+variants[i])

        #print(variant_list)
        variant_str = ','.join(variant_list)
        variant_str = filter_empty_variants(variant_str)
        #print("req",variant_str)
        return variant_str, variant_list

    def generate_genome_locations_as_keys(self, gene_data):

        annotated_data = {}
        for gene_name, value in gene_data.items():

            # extract genomic locations
            if 'results_string' in value:
                results_string = value['results_string']
                chr, ref_seq, pos, ref, alt = adagenes.tools.parse_genomic_data.parse_genome_position(results_string)
                genompos = "chr" + chr + ":" + pos + ref + ">" + alt

                annotated_data[genompos] = {}
                annotated_data[genompos][self.srv_prefix] = value
                annotated_data[genompos]['variant_data'] = gene_data[gene_name]['variant_data']
            else:
                pass

        return annotated_data

    def process_data(self, vcf_lines,input_format='json',data_type='p'):
        """
        Extracts gene names and protein change from biomarker data and retrieves genomic data from the Coordinates Converter service

        :param gene_data:
        :param input_format:
        :return:
        """
        print("Transcript process ",vcf_lines)

        if self.data_type is None:
            self.data_type = data_type

        # generate query string
        #variant_str, variant_list = self.generate_request_str_of_gene_names(gene_data,input_format=input_format)
        qid_list = list(vcf_lines.keys())
        q_lists = list(op.tools.divide_list(copy.deepcopy(qid_list), chunk_size=100))

        if self.data_type == 'p':
            annotated_data = {}
        elif self.data_type == 'g':
            annotated_data = vcf_lines
        else:
            annotated_data = vcf_lines

        for q_list in q_lists:
                #if self.data_type == 'p':
                #variant_str = generate_variant_str_from_gene_names_prot_change(vcf_lines)
                qid_dc = {}

                plist = []
                for var in q_list:

                    if "type" not in vcf_lines[var]:
                        vcf_lines[var] = ag.TypeRecognitionClient().process_data( { var: vcf_lines[var]} )[var]
                    var_type = vcf_lines[var]["type"]
                    if var_type == "c":
                        converted_identifier = var.replace('C.', 'c.')
                        qid_dc[converted_identifier] = var
                        plist.append(converted_identifier)
                    else:
                        annotated_data[var] = vcf_lines[var]

                variant_str = ",".join(plist)
                #elif self.data_type == 'g':
                #    variant_str = generate_variant_str_from_data_in_json(vcf_lines,q_list)
                #else:
                #    variant_str = generate_variant_str_from_data_in_json(vcf_lines, q_list)

                try:
                    if variant_str != '':
                        json_body = req.get_connection(variant_str,self.url,self.genome_version)
                        for item in json_body:

                            if (item["data"] is not None) and not (isinstance(item["data"],str)):
                                for res in item["data"]:
                                        if res != "Error":
                                            try:
                                                #print("dict ",item["data"])
                                                qid = item["header"]["qid"]
                                                qid_orig = qid_dc[qid]
                                                results_string = item["data"]['parsed_data']

                                                if qid_orig not in vcf_lines.keys():
                                                    preresult = {}
                                                else:
                                                    preresult = vcf_lines[qid_orig]

                                                annotated_data = onkopus.tools.transcript_to_genomic(annotated_data,results_string,item["data"],preresult,
                                                                                         self.srv_prefix, genome_version=self.genome_version)

                                            except:
                                                print("Error retrieving genomic UTA response ",res)
                                                print(traceback.format_exc())
                            else:
                                qid = item["header"]["qid"]
                                gene,protein=qid.split(":")

                                if qid not in annotated_data.keys():
                                    annotated_data[qid] = {}

                                if config.variant_data_key not in annotated_data[qid]:
                                    annotated_data[qid][config.variant_data_key] = {}
                                annotated_data[qid][config.variant_data_key]["gene"] = gene
                                annotated_data[qid][config.variant_data_key]["variant_exchange"] = protein
                                annotated_data[qid][config.variant_data_key]["type"] = "unidentified"
                                annotated_data[qid][config.variant_data_key]["status"] = "error"
                                annotated_data[qid][config.variant_data_key]["status_msg"] = item["data"]
                except:
                    print("error: genomic to gene")
                    print(traceback.format_exc())

        return annotated_data
