import io, requests, os


def import_file(infile, onkopus_server_url=None, genome_version=None):
    """
    Imports a variant file as a new patient into the Onkopus database

    :param infile:
    :param onkopus_server_url:
    :param genome_version:
    :return:
    """
    print("Request Onkopus server: ",onkopus_server_url)

    data = {}
    data['data_dir'] = 'loc'
    data['file_src'] = infile
    data["genome_version"] = genome_version

    filename = os.path.basename(infile)
    print("Import file ",filename)

    files = {'file': open(infile,'rb')}

    response = requests.post(onkopus_server_url, data=data, files=files)
    pid = response.json()

    print("new ID generated: ",pid)
    return pid

def annotate_variant_data(pid, onkopus_server_url=None,genome_version=None, module=None):
    """

    :param pid:
    :param onkopus_server_url:
    :param genome_version:
    :return:
    """
    url = onkopus_server_url + "?data_dir=loc&id=" + str(pid) + "&module=" + str(module) + "&genome_version=" + str(genome_version)
    print("Onkopus annotation request: ",url)

    res = requests.get(url)

    print(res)
