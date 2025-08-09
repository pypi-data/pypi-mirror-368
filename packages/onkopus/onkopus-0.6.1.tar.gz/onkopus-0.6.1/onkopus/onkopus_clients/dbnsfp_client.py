import datetime, requests, traceback, copy
import adagenes.tools.module_requests as req
from onkopus.conf import read_config as config
import adagenes.tools
import adagenes as ag

qid_key = "q_id"
error_logfile=None


def normalize_scores(score, val):
    if score == "ESM1b_score_aggregated_value":
        score_norm = (-1) * ((float(val) - 0.0) / (25.0))
        return score_norm
    return 0


def round_raw_scores(variant_data, scores):
    """
    Rounds the score values to 3 decimal places

    :param variant_data:
    :param scores:
    :return:
    """
    for score in scores:
        if score in variant_data:
            try:
                if is_numeric_score(variant_data[score]):
                    if isinstance(variant_data[score],str):
                        if ";" in variant_data[score]:
                            max_score = get_max_value(score,variant_data[score])
                            val = round(float(max_score), 2)
                            variant_data[score+"_aggregated_value"] = val
                        elif "aggregated_value" in score:
                            val = round(float(variant_data[score]), 2)
                            variant_data[score] = val
                        else:
                            max_score = variant_data[score]
                            variant_data[score] = round(float(max_score), 2)
                    else:
                        max_score = variant_data[score]
                        variant_data[score] = max_score
                else:
                    val = variant_data[score]
                    variant_data[score] = val
            except:
                print(score,": ",traceback.format_exc())
    return variant_data


def get_max_value(score_label,score):
    values = score.split(";")
    score_max = 0.0
    # score_max = ""
    for val in values:
        if (val != "") and (val != "."):
            if is_numeric_score(val):
                if isinstance(score, str):
                    score_max = val
                else:
                    if score_label != "ESM1b":
                        if float(val) > score_max:
                            score_max = float(val)
                    else:
                        if float(val) < score_max:
                            score_max = float(val)
            else:
                return val
    return score_max


def is_numeric_score(inputString):
    if isinstance(inputString,str):
        return any(char.isdigit() for char in inputString)
    elif isinstance(inputString,float):
        return True

class DBNSFPClient:
    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.info_lines = config.dbnsfp_info_lines
        self.url_pattern = config.dbnsfp_src
        self.srv_prefix = config.dbnsfp_srv_prefix
        self.extract_keys = config.dbnsfp_keys

        self.qid_key = "q_id"
        self.error_logfile = error_logfile
        #if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
        #    self.qid_key = "q_id_hg19"

    def get_connection(self, variants, url_pattern, genome_version):
        url = url_pattern.format(genome_version) + variants
        print(url)
        r = requests.get(url)
        return r.json()

    def process_data(self, vcf_lines):
        vcf_linesf = adagenes.tools.filter_wildtype_variants(vcf_lines)

        qid_dc = {}
        if self.genome_version == "hg38":
            qid_list = copy.deepcopy(list(vcf_linesf.keys()))
        else:
            qid_dc, qid_list = ag.tools.generate_qid_list_from_other_reference_genome(vcf_linesf)
            self.genome_version = "hg38"
            retransform = True
        #qid_dc, qid_list = ag.tools.generate_qid_list_from_other_reference_genome(vcf_linesf)
        self.genome_version = "hg38"

        while True:
            max_length = int(config.config["DEFAULT"]["MODULE_BATCH_SIZE"])
            if max_length > len(qid_list):
                max_length = len(qid_list)
            qids_partial = qid_list[0:max_length]

            variants = ','.join(adagenes.tools.filter_alternate_alleles(qids_partial))

            try:
                json_body = req.get_connection(variants, self.url_pattern, self.genome_version)

                for qid, json_obj in json_body.items():
                    json_obj = json_obj["dbnsfp"]
                    if json_obj:
                        # scores to be rounded
                        scores_list = [
                            "SIFT_score_aggregated_value",
                            "fathmm-MKL_coding_score",
                            "fathmm-XF_coding_score",
                            "phastCons17way_primate_score",
                            "phyloP17way_primate_score",
                            "MetaLR_score_aggregated_value",
                            "MPC_score_aggregated_value",
                            "M-CAP_score",
                            "HUVEC_fitCons_score",
                            "Eigen-raw_coding",
                            "ClinPred_score",
                            "PROVEAN_score_aggregated_value",
                            "VEST4_score_aggregated_value",
                            "MutationTaster_score_aggregated_value",
                            "MPC_score_aggregated_value",
                            "VEST4_score_aggregated_value",
                            "Polyphen2_HDIV_score_aggregated_value",
                            "Polyphen2_HVAR_score_aggregated_value",
                            "SIFT_score_aggregated_value",
                            "MutationAssessor_score_aggregated_value",
                            "MutationTaster_score_aggregated_value",
                            "CADD_raw_aggregated_value",
                            "DANN_score",
                            "LRT_score",
                            "EVE_score",
                            "ESM1b_score",
                            "VARITY_ER_LOO_score",
                            "gMVP_score",
                            "MVP_score_aggregated_value"
                        ]

                        # calculate percentage
                        scores = ["SIFT_converted_rankscore",
                                  "Polyphen2_HDIV_rankscore",
                                  "Polyphen2_HVAR_rankscore",
                                  "fathmm-MKL_coding_rankscore",
                                  "fathmm-XF_coding_rankscore",
                                  "phastCons17way_primate_rankscore",
                                  "phyloP17way_primate_rankscore",
                                  "MetaLR_rankscore",
                                  "MPC_rankscore",
                                  "M-CAP_rankscore",
                                  "HUVEC_fitCons_rankscore",
                                  "Eigen-raw_coding_rankscore",
                                  "ClinPred_rankscore",
                                  "PROVEAN_converted_rankscore",
                                  "MutationTaster_converted_rankscore",
                                  "VEST4_rankscore",
                                  "CADD_raw_rankscore",
                                  "REVEL_rankscore",
                                  "MutationAssessor_rankscore",
                                  "PrimateAI_rankscore",
                                  "GERP++_RS_rankscore",
                                  "SIFT_converted_rankscore",
                                  "phastCons17way_primate_rankscore",
                                  "LRT_converted_rankscore",
                                  "REVEL_rankscore",
                                  "EVE_rankscore",
                                  "ESM1b_rankscore",
                                  "VARITY_ER_LOO_rankscore",
                                  "gMVP_rankscore"
                                  ]
                        for score in scores:
                            try:
                                if score in json_obj:
                                    score_percent = score + '_percent'
                                    if json_obj[score] != ".":
                                        if ";" in json_obj[score]:
                                            json_obj[score] = get_max_value(score,json_obj[score])
                                        if is_numeric_score(json_obj[score]):
                                            json_obj[score_percent] = int(float(str(json_obj[score])) * 100)
                                else:
                                    print("Could not find score in response: ",score)
                            except:
                                print("error ",score,": ", traceback.format_exc())

                        # split multiple semicolon-separated score values and select maximum value
                        scores = [
                                    "MutationTaster_score",
                                    "MPC_score",
                                    "VEST4_score",
                                    "Polyphen2_HDIV_score",
                                    "Polyphen2_HVAR_score",
                                    "SIFT_score",
                                    "MutationAssessor_score",
                                    "MutationTaster_score",
                                    "CADD_raw",
                                    "DEOGEN2_score",
                                    "FATHMM_score",
                                    "LIST-S2_score",
                                    "LRT_score",
                                    "MPC_score",
                                    "MVP_score",
                                    "MetaRNN_score",
                                    "PROVEAN_score",
                                    "REVEL_score",
                                    "SIFT4G_score",
                                    "VARITY_ER_LOO_score",
                                    "VARITY_ER_score",
                                    "VARITY_R_LOO_score",
                                    "VARITY_R_score",
                                    "gMVP_score",
                                    "VARITY_ER_LOO_score",
                                    "VARITY_ER_score",
                                    "VARITY_R_LOO_score",
                                    "VARITY_R_score",
                                    "EVE_score",
                                    "ESM1b_score",
                                    "VARITY_ER_LOO_score",
                                    "AlphaMissense_score"
                                  ]
                        min_scores = ["PROVEAN_score"]

                        # format semicolon-separated scores, max values as pathogenic
                        for score in scores:
                            try:
                                if score in json_obj:
                                    score_percent = score + '_aggregated_value'
                                    score_max = get_max_value(score,json_obj[score])
                                    json_obj[score_percent] = score_max
                                else:
                                    print("Could not find score in response: ",score,": ",json_obj)
                            except:
                                print("error ",score,": ", traceback.format_exc())

                        # format semicolon-separated scores, min values as pathogenic
                        for score in min_scores:
                            try:
                                if score in json_obj:
                                    score_percent = score + '_aggregated_value'
                                    values = json_obj[score].split(";")
                                    score_max = 0.0
                                    #score_max = ""
                                    for val in values:
                                        if (val != "") and (val != "."):
                                            if float(val) < score_max:
                                                score_max = float(val)
                                    json_obj[score_percent] = score_max
                                else:
                                    print("Could not find score in response: ",score,": ",json_obj)
                            except:
                                print("error ",score,": ", traceback.format_exc())

                        # format multiple semicolon-separated predictions (select highest value)
                        predictions = ["SIFT_pred",
                                       "Polyphen2_HDIV_pred",
                                       "Polyphen2_HVAR_pred"
                                        ]
                        for pred in predictions:
                            if pred in json_obj:
                                try:
                                    pred_formatted= pred+"_formatted"
                                    values = json_obj[pred].split(";")
                                    #score_max = 0.0
                                    score_max=""
                                    for val in values:
                                        if (val!="") and (val!="."):
                                    #        if float(val) > score_max:
                                    #            score_max = float(val)
                                            score_max = val
                                            if val == "D":
                                                score_max += " (probably damaging)"
                                            elif val == "P":
                                                score_max += " (possibly damaging)"
                                            elif val == "B":
                                                score_max += " (benign)"
                                    json_obj[pred_formatted] = score_max
                                except:
                                    print("error formatting scores: ",traceback.format_exc())
                            else:
                                print("Could not find score in response: ",pred)

                        # normalize scores
                        scores_norm = ["ESM1b_score_aggregated_value"]
                        for score in scores_norm:
                            if score in json_obj:
                                score_val_norm = normalize_scores(score, json_obj[score])
                                json_obj[score + "_normalized"] = score_val_norm

                        try:
                            json_obj = round_raw_scores(json_obj, scores_list)
                            if qid in qid_dc:
                                qid_orig = qid_dc[qid]
                            else:
                                qid_orig = qid
                            vcf_lines[qid_orig][self.srv_prefix] = json_obj
                        except:
                            print("error ",traceback.format_exc())

            except:
                print(traceback.format_exc())

            for i in range(0, max_length):
                del qid_list[0]
            if len(qid_list) == 0:
                break

        #print("return dbnsfp ",vcf_lines)
        return vcf_lines
