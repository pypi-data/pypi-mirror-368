import copy
import traceback, datetime, json
import adagenes.tools.module_requests as req
from onkopus.conf import read_config as conf_reader
import requests


def post_connection_format(biomarker_data, url, genome_version):
    """
    Requests a module over a HTTP POST request

    :param biomarker_data:
    :param url:
    :param genome_version:
    :return:
    """
    url = url.format(genome_version)
    print(url)
    r = requests.post(url, json= biomarker_data, timeout=120)
    #r = requests.post(url, data= biomarker_data, timeout=120)
    print(r.elapsed, " , ", url)
    return r.text

class ScanNetBindingSiteClient:

    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.info_lines= conf_reader.scannet_info_lines
        self.url_pattern = conf_reader.scannet_src
        self.srv_prefix = conf_reader.scannet_srv_prefix
        self.response_keys = conf_reader.scannet_response_keys
        self.extract_keys = conf_reader.scannet_keys

        self.qid_key = "q_id"
        if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
            self.qid_key = "q_id_hg19"
        self.error_logfile = error_logfile


    def process_data(self, protein):
        try:
            pdb_data = req.get_connection(protein, self.url_pattern, self.genome_version)
            #biomarker_data_json = json.loads(biomarker_data["pdb"])
            return pdb_data

        except:
            if self.error_logfile is not None:
                cur_dt = datetime.datetime.now()
                date_time = cur_dt.strftime("%m/%d/%Y, %H:%M:%S")
                print("error processing request: ", protein, file=self.error_logfile + str(date_time) + '.log')
            else:
                print(": error processing variant response: ;", traceback.format_exc())

        return pdb_data
