import datetime, traceback, copy
import adagenes.tools.parse_vcf
import adagenes.tools.module_requests as req
from onkopus.conf import read_config as conf_reader

qid_key = "q_id"
error_logfile=None


class MVPClient:
    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.info_lines = conf_reader.mvp_info_lines
        self.url_pattern = conf_reader.mvp_src
        self.srv_prefix = conf_reader.mvp_srv_prefix
        self.extract_keys = conf_reader.mvp_keys

        self.qid_key = "q_id"
        #if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
        #    self.qid_key = "q_id_hg19"
        self.error_logfile = error_logfile

    def get_qids_hg38(self,qids_partial,vcf_lines):
        qids_refgen = []

        for qid in qids_partial:
            if "POS_hg19" in vcf_lines[qid][conf_reader.variant_data_key]:
                pos_hg38 = vcf_lines[qid][conf_reader.variant_data_key]["POS_hg19"]
                qid_hg38 = "chr" + vcf_lines[qid][conf_reader.variant_data_key]["CHROM"]+":"+ str(pos_hg38) + \
                    vcf_lines[qid][conf_reader.variant_data_key]["REF"] + ">" + \
                    vcf_lines[qid][conf_reader.variant_data_key]["ALT"]
                qids_refgen.append(qid_hg38)
            else:
                print("No hg19 position found: ",qid)
                qids_refgen.append("")

        return qids_refgen

    def process_data(self, vcf_lines, input_format='json'):

        if (self.genome_version == 'hg38') or (self.genome_version == 'GRCh38'):
            if input_format == 'vcf':
                keys = [conf_reader.uta_adapter_liftover_srv_prefix + "_" + "liftover_position"]
                annotations = adagenes.tools.parse_vcf.extract_annotations_vcf(vcf_lines, keys)
            else:
                keys = ['POS_hg19']
                annotations = adagenes.tools.parse_vcf.extract_annotations_json(vcf_lines, conf_reader.variant_data_key, keys)

            print("extracted positions: ",annotations)
            positions_hg19 = annotations[ keys[0] ]
            positions = dict(zip(annotations[keys[0]], list(vcf_lines.keys())))
            q_ids = annotations[ 'q_id' ]
            try :
                query = ",".join(positions_hg19)
            except:
                print("Error generating MVP query positions")
                print(traceback.format_exc())
                return vcf_lines
        else:
            query = ",".join(list(vcf_lines.keys()))
            list(vcf_lines.keys())
            q_ids = list(vcf_lines.keys())
            positions = None

        qid_list = copy.deepcopy(list(vcf_lines.keys()))

        while True:
            max_length = int(conf_reader.config["DEFAULT"]["MODULE_BATCH_SIZE"])
            if max_length > len(qid_list):
                max_length = len(qid_list)

            qids_partial = qid_list[0:max_length]


            try:
                if (self.genome_version == 'hg38') or (self.genome_version == 'GRCh38'):
                    qids_refgen = self.get_qids_hg38(qids_partial, vcf_lines)
                else:
                    qids_refgen = qids_partial

                variants = ','.join(adagenes.tools.filter_alternate_alleles(qids_refgen))
            except:
                print("Error: Could not retrieve liftover positions")
                print(traceback.format_exc())
                return vcf_lines

            try:
                json_body = req.get_connection(variants, self.url_pattern, 'hg19')

                for i, key in enumerate(json_body.keys()):

                    if "Score" in json_body[key]:
                        # calculate percentage of MVP score
                        json_body[key]['score_percent'] = int(json_body[key]["Score"] * 100)

                        if (self.genome_version=='hg38') or (self.genome_version == 'GRCh38'):
                            pos_hg19 = qids_partial[i]
                            vcf_lines[pos_hg19][self.srv_prefix] = json_body[key]
                        else:
                            #vcf_lines[q_id][self.srv_prefix] = json_body[positions[i]]
                            vcf_lines[key][self.srv_prefix] = json_body[key]

            except:
                if self.error_logfile:
                    print("error processing request: ", query, file=self.error_logfile + str(datetime.date_time) + '.log')
                else:
                    print(": error processing variant response: ;", traceback.format_exc())

            for i in range(0, max_length):
                del qid_list[0]
            if len(qid_list) == 0:
                break

        return vcf_lines
