import datetime, traceback, copy
import adagenes.tools.parse_vcf
import adagenes.processing.parse_http_responses
from onkopus.conf import read_config as config
import adagenes.tools.module_requests as req

qid_key = "q_id"
error_logfile=None


class CIViCClient:

    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.info_lines = config.civic_info_lines
        self.url_pattern = config.civic_src
        self.srv_prefix = config.civic_srv_prefix
        self.extract_keys = config.civic_keys

        self.qid_key = "q_id"
        self.error_logfile = error_logfile
        #if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
        #    self.qid_key = "q_id_hg19"

    def process_data(self, vcf_lines,input_format='json'):
        json_obj = adagenes.tools.filter_wildtype_variants(vcf_lines)

        # get gene names and variant exchange from passed JSON object
        if input_format == 'vcf':
            keys = [config.uta_adapter_srv_prefix + config.concat_char + config.uta_genomic_keys[0],
                    config.uta_adapter_srv_prefix + config.concat_char + config.uta_genomic_keys[1]]
            annotations = adagenes.tools.parse_vcf.extract_annotations_vcf(json_obj, keys)
        else:
            keys = [config.uta_genomic_keys[0], config.uta_genomic_keys[1]]
            annotations = adagenes.tools.parse_vcf.extract_annotations_json(json_obj, config.uta_adapter_srv_prefix, keys)

        gene_names = copy.deepcopy(annotations[keys[0]])
        varexch = copy.deepcopy(annotations[keys[1]])
        qid_list = copy.deepcopy(annotations['q_id'])

        while True:
            max_length = int(config.config["DEFAULT"]["MODULE_BATCH_SIZE"])
            if max_length > len(qid_list):
                max_length = len(qid_list)
            qids_partial = qid_list[0:max_length]

            qids_partial = adagenes.tools.filter_alternate_alleles(qids_partial)

            genompos_str = ','.join(qids_partial)
            gene_names_partial = \
                adagenes.tools.parse_vcf.extract_annotations_json_part(json_obj, config.uta_adapter_srv_prefix,
                                                                     [config.uta_genomic_keys[0]],
                                                                     qids_partial)[config.uta_genomic_keys[0]]
            variant_exchange_partial = adagenes.tools.parse_vcf.extract_annotations_json_part(json_obj,
                                                                                            config.uta_adapter_srv_prefix, [
                                                                                                config.uta_genomic_keys[
                                                                                                    1]],
                                                                                            qids_partial)[
                config.uta_genomic_keys[1]]

            gene_names_str = ",".join(gene_names_partial)
            variant_exchange_str = ",".join(variant_exchange_partial)
            query = 'genesymbol=' + gene_names_str + '&variant=' + variant_exchange_str + '&genompos=' + genompos_str

            q = ""
            for i in range(0, len(gene_names_partial)):
                q += str(gene_names_partial[i]) + ":" + str(variant_exchange_partial[i]) + ","

            q = q.rstrip(",")
            q += '&genompos=' + genompos_str + '&key=genompos'

            #vcf_lines = adagenes.processing.parse_http_responses.parse_module_response(q, vcf_lines,self.url_pattern,self.genome_version,self.srv_prefix)
            try:
                json_body = req.get_connection(q, self.url_pattern, self.genome_version)

                for key in json_body.keys():
                    json_obj = json_body[key]
                    qid = key

                    try:
                        if "Score" in json_obj:
                            if json_obj['Score'] != '':
                                json_obj['score_percent'] = int(float(json_obj['Score']) * 100)
                            else:
                                json_obj['score_percent'] = 0
                        # json_obj.pop('q_id')
                        vcf_lines[qid][self.srv_prefix] = json_obj
                    except:
                        cur_dt = datetime.datetime.now()
                        print(cur_dt, ": error processing variant response: ", qid, ';', traceback.format_exc())
            except:
                print(": error processing variant response: ;", traceback.format_exc())

            for i in range(0, max_length):
                del gene_names[0]
                del varexch[0]
                del qid_list[0]
            if len(qid_list) == 0:
                break

        return vcf_lines
