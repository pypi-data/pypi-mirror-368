import datetime, traceback, copy
import adagenes.tools.module_requests as req
from onkopus.conf import read_config as config
import adagenes.tools


class OncoKBClient:

    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.url_pattern = config.oncokb_src
        self.srv_prefix = config.oncokb_srv_prefix
        self.extract_keys = config.oncokb_keys
        self.info_lines = config.oncokb_info_lines
        self.error_logfile = error_logfile

        self.qid_key = "q_id"
        if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
            self.qid_key = "q_id_hg19"

    def get_headers(self, key):
        """
        Returns the HTTP request header for the OncoKB module

        :return:
        """
        headers = {}
        if key is not None:
            headers["oncokb-key"] = key
            return headers
        else:
            return None

    def process_data(self, vcf_lines, input_format='vcf', key=None):
        """
        Request to OncoKB module

        :param vcf_lines:
        :param input_format:
        :param key
        :return:
        """
        if key is None:
            if "oncokbkey" not in vcf_lines.keys():
                print("No OncoKB defined")
                return vcf_lines
            else:
                key = vcf_lines["oncokbkey"]

        vcf_linesf = adagenes.tools.filter_wildtype_variants(vcf_lines)
        qid_list = copy.deepcopy(list(vcf_linesf.keys()))


        if "oncokbkey" in vcf_linesf.keys():
            vcf_linesf.pop("oncokbkey")
        qid_list.remove("oncokbkey")

        if "oncokbkey" in vcf_linesf.keys():
            key = vcf_linesf["oncokbkey"]
            vcf_linesf.pop("oncokbkey")

        while True:
            max_length = int(config.config["DEFAULT"]["MODULE_BATCH_SIZE"])
            if max_length > len(qid_list):
                max_length = len(qid_list)
            qids_partial = qid_list[0:max_length]

            qids_q = adagenes.tools.filter_alternate_alleles(qids_partial)

            genes = []
            aa_exchanges = []
            for qid in qids_q:
                if qid in vcf_linesf.keys():
                    if "UTA_Adapter" in vcf_linesf[qid]:
                        if "variant_exchange" in vcf_linesf[qid]["UTA_Adapter"]:
                            aa_exchange = vcf_linesf[qid]["UTA_Adapter"]["variant_exchange"]
                            gene = vcf_linesf[qid]["UTA_Adapter"]["gene_name"]
                            genes.append(gene)
                            aa_exchanges.append(aa_exchange)
                    else:
                        genes.append("")
                        aa_exchanges.append("")

            genompos_str = ','.join(qids_q)
            genes_str = ','.join(genes)
            aa_exchange_str = ','.join(aa_exchanges)
            q = ""

            try:
                    q = 'genompos=' + genompos_str + "&genes=" + genes_str + "&aa_exchange=" + aa_exchange_str
                    headers = self.get_headers(key)
                    if headers is None:
                        print("No OncoKB found. Aborting request.")
                        return vcf_lines
                    json_body = req.get_connection(q, self.url_pattern, self.genome_version, headers=headers)

                    for genompos in json_body.keys():
                            json_obj = json_body[genompos]
                            qid = genompos

                            for k in self.extract_keys:
                                if k in json_obj:
                                    pass
                                    #annotations.append('{}_{}={}'.format(self.srv_prefix, k, json_body[i][k]))
                            try:
                                vcf_lines[qid][self.srv_prefix] = json_obj
                            except:
                                if self.error_logfile is not None:
                                    cur_dt = datetime.datetime.now()
                                    date_time = cur_dt.strftime("%m/%d/%Y, %H:%M:%S")
                                    print(cur_dt, ": error processing variant response: ", qid, ';', traceback.format_exc(), file=self.error_logfile+str(date_time)+'.log')
                                else:
                                    print(traceback.format_exc())
            except:
                    if self.error_logfile is not None:
                        print("error processing request: ", vcf_lines, file=self.error_logfile+str(date_time)+'.log')
                    else:
                        print(": error processing variant response: ;", traceback.format_exc())
            for i in range(0, max_length):
                del qid_list[0]
            if len(qid_list) == 0:
                break
        return vcf_lines
