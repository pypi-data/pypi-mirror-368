import requests
import adagenes.conf.read_config as conf_reader


files = [
]

import os

for file in os.listdir(os.getenv("source_data_dir")):
    if os.path.isdir(os.getenv("source_data_dir") + "/" + file):
        for infile in os.listdir(os.getenv("source_data_dir") + "/" + file):
            if infile.endswith(".maf"):
                files.append(os.getenv("source_data_dir") + "/" + file + "/" + infile)
# print("files: ",files)

base_url = conf_reader.__MODULE_PROTOCOL__ + "://" + conf_reader.__MODULE_SERVER__ + ':10100'

for file in files:
    data = {}
    data['data_dir'] = 'loc'
    data['file_src'] = file

    headers= { 'Content-Type':'multipart/form-data' }
    url = base_url + '/onkopus-server/v1/upload_variant_data'
    print(url)
    response = requests.post(url, files={}, data=data)
    print(response.text)

    pid = response.text

    # add patient to MTB
    mtb_id = ""
    url = base_url + '/onkopus-server/v1/updateMTB?action=a&mtb_id=' + mtb_id + '&pid=' + str(pid)
    print(url)
    response = requests.get(url)
    print(response.json())

    # annotate files
    url = base_url + '/onkopus-server/v1/analyze_variants?data_dir=loc&id=' + str(pid)
    print(url)
    response = requests.get(url)
    print(response.json())

