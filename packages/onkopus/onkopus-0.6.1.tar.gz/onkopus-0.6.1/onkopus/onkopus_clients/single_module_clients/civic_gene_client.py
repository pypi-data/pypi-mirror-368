import datetime, traceback, copy
import adagenes.tools.parse_vcf
import adagenes.tools.module_requests as req
from onkopus.conf import read_config as config

qid_key = "q_id"
error_logfile=None


class CIViCGeneClient:
    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.info_lines = config.civic_info_lines
        self.url_pattern = config.civic_gene_src
        self.srv_prefix = config.civic_srv_prefix
        self.extract_keys = config.civic_keys

        self.qid_key = "q_id"
        self.error_logfile = error_logfile
        #if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
        #    self.qid_key = "q_id_hg19"

    def process_data(self, vcf_lines,input_format='json'):

        qid_list = list(vcf_lines.keys())

        while True:
            max_length = int(config.config["DEFAULT"]["MODULE_BATCH_SIZE"])
            if max_length > len(qid_list):
                max_length = len(qid_list)
            qids_partial = qid_list[0:max_length]

            q = ",".join(qids_partial)
            #for i in range(0, len(qids_partial)):
            #    q += str(qids_partial[i]) + ":" + str(variant_exchange_partial[i]) + ","

            q = q.rstrip(",")

            try:
                json_body = req.get_connection(q, self.url_pattern, self.genome_version)

                for key in json_body.keys():
                        json_obj = json_body[key]
                        qid=key

                        for k in self.extract_keys:
                            if k in json_obj:
                                pass
                                #annotations.append('{}_{}={}'.format(self.srv_prefix, k, json_body[i][k]))
                        try:
                            #json_obj.pop('q_id')
                            vcf_lines[qid][self.srv_prefix] = json_obj
                        except:
                            if self.error_logfile is not None:
                                cur_dt = datetime.datetime.now()
                                date_time = cur_dt.strftime("%m/%d/%Y, %H:%M:%S")
                                print(cur_dt, ": error processing variant response: ", qid, ';', traceback.format_exc(), file=self.error_logfile+str(date_time)+'.log')
                            else:
                                print(cur_dt, ": error processing variant response: ", qid, ';', traceback.format_exc())
            except:
                print(": error processing variant response: ;", traceback.format_exc())
                if error_logfile is not None:
                    print("error processing request: ", annotations, file=error_logfile+str(date_time)+'.log')

            for i in range(0, max_length):
                del qid_list[0]
            if len(qid_list) == 0:
                break

        return vcf_lines
