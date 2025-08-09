import traceback, datetime, json
import adagenes.tools.module_requests as req
from onkopus.conf import read_config as config


class PlotClient:

    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.info_lines= config.onkopus_plots_info_lines
        self.url_pattern = config.onkopus_plots_src
        self.srv_prefix = config.onkopus_plots_srv_prefix
        self.response_keys = config.onkopus_plots_response_keys
        self.extract_keys = config.onkopus_plots_keys

        self.qid_key = "q_id"
        if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
            self.qid_key = "q_id_hg19"
        self.error_logfile = error_logfile

    def process_data(self, biomarker_data, plot=None, type="graph"):

        if plot is not None:
            if plot == "categorical_pathogenicity":
                service = "categorical_pathogenicity_radar_plot"
            elif plot== "multi_pathogenicity":
                service = "pathogenicity_all_variants"
            elif plot=="pathogenicity-scores-radar":
                service = "pathogenicity_radar_plot"
        else:
            service = "pathogenicity_radar_plot"

        url_full = self.url_pattern + service

        try:
            biomarker_data = req.post_connection(biomarker_data,url_full,self.genome_version, type=type)
            biomarker_data_json = json.loads(biomarker_data)
            return biomarker_data_json

        except:
            if self.error_logfile is not None:
                cur_dt = datetime.datetime.now()
                date_time = cur_dt.strftime("%m/%d/%Y, %H:%M:%S")
                print("error processing request: ", biomarker_data, file=self.error_logfile+str(date_time)+'.log')
            else:
                print(": error processing variant response: ;", traceback.format_exc())

        return biomarker_data
