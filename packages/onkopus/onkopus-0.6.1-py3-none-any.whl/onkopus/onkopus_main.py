import argparse
import os, time, datetime
import onkopus.conf.docker_config as docker_config
import onkopus.conf.read_config as conf_reader
import adagenes as ag
import onkopus.import_data
import onkopus.mtb_requests
import onkopus as op
import onkopus.cli.run_interpretation
import onkopus.cli.module_mgt


class OnkopusMain():

    def __init__(self):
        self.__location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.__data_dir__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__))) + "/../data"

        self.title = "Onkopus"

        version = op.conf_reader.config["DEFAULT"]["VERSION"]
        self.version = version
        self.__available_modules__ = self._load_available_modules()
        self.module_labels = docker_config.available_modules

        # Load installed modules
        self.installed_modules = self._load_installed_modules()
        self.__docker_compose_file = self.__data_dir__ + "/docker-compose.yml"

        self.formats=["VCF","MAF","CSV","TSV","XLSX","TXT"]

    def _load_available_modules(self):
        return list(docker_config.module_ids.keys())

    def _load_installed_modules(self):
        installed_modules = []

        # Create data directory if it does not exist
        isExist = os.path.exists(self.__data_dir__)
        if not isExist:
            # Create a new directory because it does not exist
            os.makedirs(self.__data_dir__)
            print("Created data directory: ",self.__data_dir__)

        # Create modules file if it does not exist
        if not os.path.exists(self.__data_dir__ + "/" + conf_reader.config["DEFAULT"]["INSTALLED_MODULES_FILE"]):
            file = open(self.__data_dir__ + "/" + conf_reader.config["DEFAULT"]["INSTALLED_MODULES_FILE"], 'w+')
            file.close()
        #if not os.path.exists(self.__data_dir__ +
        #                      "/docker-compose.yml"):
        #    os.system("cp -v " + self.__location__ + "/conf/docker_compose/docker-compose.yml " + self.__data_dir__ + "/docker-compose.yml")

        file = open(self.__data_dir__ + "/" + conf_reader.config["DEFAULT"]["INSTALLED_MODULES_FILE"], 'r')
        for line in file:
            installed_modules.append(line.strip())
        file.close()

        print("Installed modules: ", installed_modules)

        return installed_modules


    def import_data(self,input_file, genome_version=None,data_dir=None):
        """
        Imports an input file or all files within a directory as patient biomarker data in the Onkopus database

        :param input_file:
        :param genome_version:
        :param data_dir:
        :return:
        """
        if (data_dir is not None) and (data_dir != ''):
            # import all files in directory
            pass
        elif input_file != '':
            # import file
            print("Import file: ",input_file)

            onkopus_server_url = conf_reader.__MODULE_PROTOCOL__ + "://" + conf_reader.__MODULE_SERVER__ + conf_reader.__PORT_ONKOPUS_SERVER__
            onkopus_server_url = onkopus_server_url + "/onkopus-server/v1/upload_variant_data"

            pid = onkopus.import_data.import_file(input_file, onkopus_server_url=onkopus_server_url, genome_version=genome_version)
            return pid
        else:
            print("Error: No input file defined. Define an input file or a data directory")

    def restart_modules(self):
        """
        Restarts all installed Onkopus modules

        :return:
        """
        os.system('docker-compose down')
        os.system('docker-compose pull')
        os.system('docker-compose up -d')

    def list_modules(self):
        """
        Prints a list of all available Onkopus modules

        :return:
        """
        print("Available Onkopus modules: ")
        #print(self.__available_modules__)
        print(self.module_labels)

        print("Install an Onkopus module locally by running 'onkopus install -m [module-name]'")

    def list_formats(self):
        """

        :return:
        """
        print("Available data formats for input format (-if) and output format (-of): ")
        for format in self.formats:
            print(format)

    def add_patient_to_mtb(self,pid,mtb):
        onkopus_server_url = conf_reader.__MODULE_PROTOCOL__ + "://" + conf_reader.__MODULE_SERVER__ + conf_reader.__PORT_ONKOPUS_SERVER__
        onkopus_server_url = onkopus_server_url + "/onkopus-server/v1/updateMTB"
        onkopus.mtb_requests.add_patient_to_mtb(pid,mtb, onkopus_server_url)

    def add_patient_and_perform_annotation(self, input_file, mtb, genome_version=None, data_dir=None):
        pid = self.import_data(input_file, genome_version=genome_version, data_dir=data_dir)
        module = 'all'
        data_dir = "loc"
        self._db_request(pid, module=module, genome_version=genome_version)
        self.add_patient_to_mtb(pid, mtb)

    def show_title(self):
        pass

    def run(self):
        """
        Main Onkopus command-line function

        :return:
        """
        self.show_title()

        parser = argparse.ArgumentParser()
        parser.add_argument('action', choices=['run', 'install', 'list-modules', 'start', 'stop', 'import', 'remote-install'])
        parser.add_argument('-m', '--module', default='all')
        parser.add_argument('-i', '--input_file', default='')
        parser.add_argument('-o', '--output_file', default='')
        parser.add_argument('-g', '--genome_version', default='')
        parser.add_argument('-d', '--data_dir', default='')
        parser.add_argument('-pid', '--patient_id', default='')
        parser.add_argument('-mtb', '--mtb_id', default='')
        parser.add_argument('-if', '--input_format', default='')
        parser.add_argument('-of', '--output_format', default='')
        parser.add_argument('-md', '--mode', default='')
        parser.add_argument('-t', '--target', default='hg38')

        args = parser.parse_args()
        action = args.action
        module = args.module
        input_file = args.input_file
        output_file = args.output_file
        genome_version = args.genome_version
        data_dir = args.data_dir
        pid = args.patient_id
        mtb = args.mtb_id
        input_format = args.input_format
        output_format = args.output_format
        mode = args.mode
        target = args.target

        if action == 'run':
            onkopus.cli.run_interpretation.run_interpretation(input_file, output_file, module=module, genome_version=genome_version, pid=pid,
                                    input_format=input_format,output_format=output_format,mode=mode, target=target)
        elif action == 'install':
            onkopus.cli.module_mgt.install(module, self.installed_modules, self.__available_modules__)
        elif action == 'start':
            onkopus.cli.module_mgt.start_modules(self.installed_modules)
        elif action == 'stop':
            onkopus.cli.module_mgt.stop_modules()
        elif action == 'import':
            self.import_data(input_file, genome_version=genome_version,data_dir=data_dir)
        elif action == 'list-modules':
            self.list_modules()
        elif action == 'list-formats':
            self.list_formats()
        elif action == 'remote-install':
            onkopus.cli.module_mgt.remote_install(module)
        elif action == 'mtb-add':
            self.add_patient_to_mtb(pid,mtb)
        elif action == 'mtb-add-analyze':
            self.add_patient_and_perform_annotation(input_file, mtb, genome_version=genome_version, data_dir=data_dir)

