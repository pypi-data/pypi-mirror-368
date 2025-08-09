import datetime, requests, traceback, copy, io
import adagenes.tools.module_requests as req
from onkopus.conf import read_config as config
import adagenes.tools
from onkopus.onkopus_clients.processing.parse_json import parse_score_results

qid_key = "q_id"
error_logfile=None


class OnkopusServerClient:

    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.info_lines = config.onkopus_server_info_lines
        self.url_pattern_upload = config.onkopus_server_src_upload
        self.srv_prefix = config.onkopus_server_srv_prefix
        self.extract_keys = config.onkopus_server_keys

        self.qid_key = "q_id"
        self.error_logfile = error_logfile

    def get_request(self, request_id):
        """

        :param request_id:
        :return:
        """
        pass

    def interpret_variant_file(self, file_src, genome_version=""):
        """

        :param file_src:
        :return:
        """
        data = {}
        data['data_dir'] = 'loc'

        with open(file_src, 'rb') as file:
            file_content = file.read()
        file.close()
        bytes_io = io.BytesIO(file_content)
        bytes_io.seek(0)
        file = open(file_src,'rb')
        files = { 'file': file }

        #data['file'] = file_content
        data['genome_version'] = genome_version

        print(self.url_pattern_upload)
        qid = requests.post(self.url_pattern_upload, data=data, files=files).text
        file.close()
        print(qid)

        url = config.onkopus_server_src_analyze_id + "?id="+qid
        print(url)
        variant_data = requests.get(url)
        print(variant_data)

    def interpret_variants(self, vcf_lines):
        """

        :param vcf_lines:
        :return:
        """

        qid_list = copy.deepcopy(list(vcf_lines.keys()))
        while True:
            max_length = int(config.config["DEFAULT"]["MODULE_BATCH_SIZE"])
            if max_length > len(qid_list):
                max_length = len(qid_list)
            qids_partial = qid_list[0:max_length]
            variants = ','.join(adagenes.tools.filter_alternate_alleles(qids_partial))

            try:
                json_body = req.get_connection(variants, self.url_pattern, self.genome_version)
                vcf_lines = parse_score_results(vcf_lines, json_body, self.srv_prefix)
            except:
                if error_logfile is not None:
                    cur_dt = datetime.datetime.now()
                    date_time = cur_dt.strftime("%m/%d/%Y, %H:%M:%S")
                    print("error processing request: ", variants, file=error_logfile+str(date_time)+'.log')

            for i in range(0, max_length):
                del qid_list[0]
            if len(qid_list) == 0:
                break

        return vcf_lines
