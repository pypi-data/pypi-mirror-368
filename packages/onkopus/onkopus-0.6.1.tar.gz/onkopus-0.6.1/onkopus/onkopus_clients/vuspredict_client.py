import datetime, traceback, re, copy
import adagenes.tools.parse_vcf
import adagenes.tools.module_requests as req
from onkopus.conf import read_config as config

qid_key = "q_id"
error_logfile=None

class VUSPredictClient:
    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.info_lines = config.vuspredict_info_lines
        self.url_pattern = config.vuspredict_src
        self.srv_prefix = config.vuspredict_srv_prefix
        self.extract_keys = config.vuspredict_keys

        self.qid_key = "q_id"
        #if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
        #    self.qid_key = "q_id_hg19"
        self.error_logfile=error_logfile

    def process_data(self, vcf_lines, input_format='json'):
        if input_format == 'vcf':
            keys = [config.uta_adapter_srv_prefix + config.concat_char + config.uta_genomic_keys[0],
                    config.uta_adapter_srv_prefix + config.concat_char + config.uta_genomic_keys[1]]
            annotations = adagenes.tools.parse_vcf.extract_annotations_vcf(vcf_lines, keys)
        else:
            keys = [config.uta_genomic_keys[0],
                    config.uta_genomic_keys[1]]
            annotations = adagenes.tools.parse_vcf.extract_annotations_json(vcf_lines, config.uta_adapter_srv_prefix, keys)
        gene_names = copy.deepcopy(annotations[keys[0]])
        variant_exchange = copy.deepcopy(annotations[keys[1]])

        qid_list = copy.deepcopy(annotations['q_id'])
        #qid_list = copy.deepcopy(list(vcf_lines.keys()))


        while True:
            max_length = int(config.config["DEFAULT"]["MODULE_BATCH_SIZE"])
            if max_length > len(qid_list):
                max_length = len(qid_list)
            qids_partial = qid_list[0:max_length]
            qids_partial = adagenes.tools.filter_alternate_alleles(qids_partial)

            genompos_str = ','.join(qids_partial)
            gene_names_partial = \
            adagenes.tools.parse_vcf.extract_annotations_json_part(vcf_lines, config.uta_adapter_srv_prefix, [config.uta_genomic_keys[0]],
                                                                 qids_partial)[config.uta_genomic_keys[0]]
            variant_exchange_partial = adagenes.tools.parse_vcf.extract_annotations_json_part(vcf_lines,
                                                                                     config.uta_adapter_srv_prefix, [config.uta_genomic_keys[1]],
                                                                                     qids_partial)[config.uta_genomic_keys[1]]

            gene_names_str = ",".join(gene_names_partial)
            variant_exchange_str = ",".join(variant_exchange_partial)
            query = 'genesymbol=' + gene_names_str + '&variant=' + variant_exchange_str + '&genompos=' + genompos_str

            try:
                json_body = req.get_connection(query, self.url_pattern, self.genome_version)

                for json_obj in json_body:
                    if json_obj:
                        #annotations = []

                        if self.qid_key not in json_obj:
                            continue
                        qid = json_obj[self.qid_key]

                        # calculate percentage
                        if 'Score' in json_obj:
                            json_obj['score_percent'] = int( (float(json_obj['Score']) /2) * 100) + 50

                            if float(json_obj['Score']) < 0:
                                json_obj['score_percent_1of2'] = int(float(json_obj['Score']) * 100) * (-1)
                                json_obj['score_percent_2of2'] = 0
                            else:
                                json_obj['score_percent_1of2'] = 0
                                json_obj['score_percent_2of2'] = int( float(json_obj['Score']) * 100)
                            colour = "#00b0d2"
                            if float(json_obj["Score"]) < 0:
                                colour = "#ce8585"
                            json_obj['score_color'] = colour

                            json_obj["Score"] = round(float(json_obj["Score"]), 4)
                        else:
                            json_obj['score_percent_1of2'] = 0
                            json_obj['score_percent_2of2'] = 0
                            json_obj['score_color'] = "#d5d5d5"

                        for k in self.extract_keys:
                            if k in json_obj:
                                pass
                                #annotations.append('{}_{}={}'.format(self.srv_prefix, k, json_body[i][k]))

                        try:
                            json_obj.pop('q_id')
                            vcf_lines[qid][self.srv_prefix] = json_obj
                        except:
                            if self.error_logfile is not None:
                                cur_dt = datetime.datetime.now()
                                date_time = cur_dt.strftime("%m/%d/%Y, %H:%M:%S")
                                print(cur_dt, ": error processing variant response: ", qid, ';', traceback.format_exc(), file=self.error_logfile+str(date_time)+'.log')
                            else:
                                print(cur_dt, ": error processing variant response: ", qid, ';', traceback.format_exc())
            except:
                if error_logfile is not None:
                    print("error processing request: ", vcf_lines, file=error_logfile+str(date_time)+'.log')
                else:
                    traceback.print_exc()

            for i in range(0,max_length):
                del gene_names[0] #gene_names.remove(qid)
                del variant_exchange[0]  #variant_exchange.remove(qid)
                del qid_list[0] # qid_list.remove(qid)
            if len(qid_list) == 0:
                break

        return vcf_lines

    def get_genompos_with_ref_sequence(self, genompos):
        #pattern = "(chr)([0-9]+|X|Y):(g\\.|c\\.|p\\.)?([0-9]+)([A|C|T|G|>|N]+)"
        pattern = "(chr)([0-9]+|X|Y):(g\\.|c\\.|p\\.)([0-9]+)([A|C|T|G|>|N]+)"
        p = re.compile(pattern)
        m = p.match(genompos)
        if m:
            return genompos
        else:
            # add reference sequence
            pattern = "(chr)([0-9]+|X|Y):([0-9]+)([A|C|T|G|>|N]+)"
            p = re.compile(pattern)
            m = p.match(genompos)
            chr = m.group(1)
            chr_num = m.group(2)
            pos = m.group(3)
            ref = m.group(4)
            return chr + chr_num + ':' + 'g.' + pos + ref

    def get_genompos_without_ref_sequence(self, genompos):
        pattern = "(chr)([0-9]+|X|Y):([0-9]+)([A|C|T|G|>|N]+)"
        p = re.compile(pattern)
        m = p.match(genompos)
        if m:
            return genompos
        else:
            # rm reference sequence
            pattern = "(chr)([0-9]+|X|Y):(g\\.|c\\.|p\\.)([0-9]+)([A|C|T|G|>|N]+)"
            p = re.compile(pattern)
            m = p.match(genompos)
            chr = m.group(1)
            chr_num = m.group(2)
            refseq = m.group(3)
            pos = m.group(4)
            ref = m.group(5)
            return chr + chr_num + ':' + pos + ref