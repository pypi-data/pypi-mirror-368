import traceback, datetime


def parse_score_results(vcf_lines,
                            json_body, srv_prefix, error_logfile = None):
    """


    :param vcf_lines:
    :param json_body:
    :param srv_prefix:
    :param error_logfile:
    :return:
    """
    for qid, json_obj in json_body.items():
        if json_obj:

            # calculate percentage
            if 'score' in json_obj:
                json_obj['score_percent'] = int(float(json_obj['score']) * 100)
            elif 'Score' in json_obj:
                json_obj['score_percent'] = int(float(json_obj['Score']) * 100)

            # colour = "#00b0d2"
            #colour = "#ce8585"
            #json_obj['score_color'] = colour

            #for k in self.extract_keys:
            #    if k in json_obj:
            #        pass
            #        # annotations.append('{}_{}={}'.format(self.srv_prefix, k, json_body[i][k]))
            try:
                # json_obj.pop('q_id')
                vcf_lines[qid][srv_prefix] = json_obj
            except:
                print("error")
                if error_logfile is not None:
                    cur_dt = datetime.datetime.now()
                    date_time = cur_dt.strftime("%m/%d/%Y, %H:%M:%S")
                    print(cur_dt, ": error processing variant response: ", qid, ';', traceback.format_exc(),
                          file=error_logfile + str(date_time) + '.log')
    return vcf_lines