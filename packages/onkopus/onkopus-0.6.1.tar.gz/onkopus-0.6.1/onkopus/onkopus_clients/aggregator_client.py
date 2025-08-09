import traceback, datetime, json
import redis
import adagenes.tools.module_requests as req
from onkopus.conf import read_config as config
import adagenes as ag


def get_clinev_data(biomarker_data):
    ce_data = {}

    for var in biomarker_data.keys():
        ce_data[var] = {}
        if "civic" in biomarker_data[var].keys():
            if "civic_features_norm" in biomarker_data[var]["civic"].keys():
                ce_data[var]["civic"] = {}
                ce_data[var]["civic"]["civic_features_norm"] =biomarker_data[var]["civic"]["civic_features_norm"]

        if "metakb" in biomarker_data[var].keys():
            if "metakb_features_norm" in biomarker_data[var]["metakb"].keys():
                ce_data[var]["metakb"] = {}
                ce_data[var]["metakb"]["metakb_features_norm"] =biomarker_data[var]["metakb"]["metakb_features_norm"]

        if "oncokb" in biomarker_data[var].keys():
            if "oncokb_features_norm" in biomarker_data[var]["oncokb"].keys():
                ce_data[var]["oncokb"] = {}
                ce_data[var]["oncokb"]["oncokb_features_norm"] =biomarker_data[var]["oncokb"]["oncokb_features_norm"]
    return ce_data


class AggregatorClient:

    def __init__(self, genome_version, request_id=None, tumor_type = None, error_logfile=None):
        self.genome_version = genome_version
        self.info_lines= config.onkopus_aggregator_info_lines
        self.url_pattern = config.onkopus_aggregator_src
        self.srv_prefix = config.onkopus_aggregator_srv_prefix
        self.response_keys = config.onkopus_aggregator_response_keys
        self.extract_keys = config.onkopus_aggregator_keys

        self.request_id = request_id
        self.tumor_type = tumor_type

        self.qid_key = "q_id"
        if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
            self.qid_key = "q_id_hg19"
        self.error_logfile = error_logfile

        self.redis_client = redis.StrictRedis(host=config.__REDIS_SERVER__, port=config.__REDIS_SERVER_PORT__,
                                         db=config.__REDIS_SERVER_DB__, decode_responses=True)

    def process_data(self, biomarker_data, tumor_type=None):

        #print("request id ",self.request_id)

        if (self.tumor_type is None) and (tumor_type is not None):
            self.tumor_type = tumor_type

        try:
            if self.request_id is None:
                ce_data = get_clinev_data(biomarker_data)
                clinev_data = req.post_connection(ce_data,self.url_pattern,self.genome_version, tumor_type=tumor_type)
                clinev_data_json = json.loads(clinev_data)
                biomarker_data_json = ag.merge_dictionaries(biomarker_data, clinev_data_json)
                return biomarker_data_json
            else:
                request_data = {
                    "request_id": self.request_id,
                    "tumor_type": self.tumor_type
                }
                req.post_connection_params(request_data, self.url_pattern)
                cached_result = self.redis_client.get(self.request_id)
                result = json.loads(cached_result)
                # Get cached request from Redis client
                if cached_result:
                    biomarker_data = result["result"]
                    genome_version = result["genome_version"]

        except:
            print(traceback.format_exc())
            if self.error_logfile is not None:
                cur_dt = datetime.datetime.now()
                date_time = cur_dt.strftime("%m/%d/%Y, %H:%M:%S")
                print("error processing request: ", biomarker_data, file=self.error_logfile+str(date_time)+'.log')
            else:
                print(": error processing variant response: ;", traceback.format_exc())

        return biomarker_data
