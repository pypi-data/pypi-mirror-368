import requests

def add_patient_to_mtb(pid, mtb, onkopus_server_url):
    """

    :param pid:
    :param mtb
    :param onkopus_server_url:
    :return:
    """
    url = onkopus_server_url + "?pid=" + str(pid) + "&mtb_id=" + str(mtb) + "&action=a"
    print("Add patient to MTB: ", url)
    res = requests.get(url)
    print(res)
