import datetime, traceback
import adagenes.tools.module_requests as req
from onkopus.conf import read_config as config
from adagenes.tools import generate_variant_dictionary


class FATHMMClient:
    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.url_pattern = config.fathmm_src
        self.srv_prefix = config.fathmm_srv_prefix
        self.extract_keys = config.fathmm_keys
        self.info_lines = config.fathmm_info_lines
        self.error_logfile = error_logfile

        self.qid_key = "q_id"
        if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
            self.qid_key = "q_id_hg19"

    def process_data(self, vcf_lines):
        variant_dc = generate_variant_dictionary(vcf_lines)
        variants = ','.join(variant_dc.values())

        try:
            json_body = req.get_connection(variants, self.url_pattern, self.genome_version)

            for json_obj in json_body:
                if json_obj:
                    #annotations = []

                    if self.qid_key not in json_obj:
                        continue
                    qid = json_obj[self.qid_key]

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
                            traceback.format_exc()

        except:
            if self.error_logfile is not None:
                print("error processing request: ", variants, file=self.error_logfile+str(date_time)+'.log')
            else:
                print(": error processing variant response: ;", traceback.format_exc())

        return vcf_lines
