import os, time
import onkopus.conf.read_config as conf_reader
import datetime
import adagenes as ag
import onkopus as op


def _db_request(pid, module=None, genome_version=None):
    """

    :param pid:
    :param module:
    :param genome_version:
    :return:
    """
    print("Annotate biomarkers of ID: ", pid, ", genome version: ", genome_version, ", module: ", module)

    onkopus_server_url = conf_reader.__MODULE_PROTOCOL__ + "://" + conf_reader.__MODULE_SERVER__ + conf_reader.__PORT_ONKOPUS_SERVER__
    onkopus_server_url = onkopus_server_url + "/onkopus-server/v1/analyze_variants"

    op.import_data.annotate_variant_data(pid, onkopus_server_url=onkopus_server_url,
                                              genome_version=genome_version, module=module)


def _module_request(input_file, output_file, module, genome_version=None,
                    input_format=None, output_format=None, target=None, data_type="g"):
    """
    Annotates a variant file with the defined module and writes the annotated variant file in the file system.
    Directly employs the Onkopus clients, without writing the results in the Onkopus database

    :param input_file:
    :param output_file:
    :param module:
    :param genome_version:
    :return:
    """
    modules = module.split(",")

    print("Input file ", input_file)

    # Employ CCS GeneToGenomic service if data is in protein format
    # if bframe.data_type == "p":
    #    print("Proteomic data detected: Retrieving genomic locations")
    #    genome_version = "hg38"
    #    client = CCSGeneToGenomicClient(genome_version)
    #    bframe.data = client.process_data(bframe.data, input_format='tsv')

    if (genome_version == "hg19") or (genome_version == "t2t"):
        if module != "liftover":
            print("Annotating variant data to GRCh38...", genome_version)
            output_file_liftover = input_file + ".GRCh38.vcf "
            obj = ag.LiftoverAnnotationClient(genome_version=genome_version, target_genome="hg38")
            print("lo annotation ",input_file,input_format,output_format)
            input_format = None
            output_format = None
            #ag.process_file(input_file, output_file_liftover, obj, genome_version=genome_version,
            #                input_format=input_format,
            #                output_format=output_format, error_logfile=None)
            #ag.process_file(input_file, output_file_liftover, ag.LiftoverAnnotationClient("hg19", target_genome="hg38"))
            ag.process_file(input_file, output_file_liftover, ag.LiftoverClient("hg19", target_genome="hg38"))
            input_file = output_file_liftover
            genome_version = "hg38"
            print("Liftover successful. ",input_file)

    # Annotate
    for m in modules:
        obj = op.get_onkopus_client(m, genome_version, target=target, data_type=data_type)
        # print("client ", type(client))
        if obj is None:
            print("Error: Onkopus module not found: ", m)
            exit(1)#

        #ag.process_file(input_file, output_file, obj, genome_version=genome_version, input_format=input_format,
        #                output_format=output_format, error_logfile=None)
        ag.process_file(input_file, output_file, obj)


def run_interpretation(
                       input_file,
                       output_file,
                       module=None,
                       genome_version=None,
                       pid=None,
                       input_format=None,
                       output_format=None,
                       mode=None,
                       target=None
                       ):
    """
    Annotates an input file with the defined module. The annotated file is saved in the given output path

    :param input_file:
    :param output_file:
    :param module:
    :param genome_version:
    :return:
    """
    if mode == "test":
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        input_file = "somaticMutations.ln50.vcf"
        genome_version = "hg19"
        input_file = __location__ + '/../../tests/test_files' + '/' + input_file

    # print("Starting interpretation")
    time_start = time.time()

    # Check input file parameter
    if input_file == '':
        if pid is None:
            print \
                ("Error: No input file passed. Please define an input file with the -i option, e.g. onkopus run -i /path/to/file/mutations.vcf.gz")
            exit(1)
        else:
            print("Annotate patient biomarkers: " ,pid)
            _db_request(pid, module=module, genome_version=genome_version)
            exit(0)

    file_name, file_extension = os.path.splitext(input_file)
    input_format_recognized = file_extension.lstrip(".")
    if input_format_recognized == "gz":
        # print("Found .gz file")
        file_name, file_extension = os.path.splitext(file_name)
        input_format_recognized = file_extension.lstrip(".")

    if input_format == "":
        input_format = input_format_recognized
        print("Recognized input format: " ,input_format)

    # get output format
    if output_format == "":
        output_format = input_format_recognized
        print("No output format given. Using input file format: " ,input_format)

    if output_file == '':
        datetime_str = str(datetime.datetime.now())
        basefile = os.path.splitext(input_file)[0]
        output_file = basefile + '.' + datetime_str + ".ann." + output_format
        print("No output file defined. Generated output file path: ", output_file)

    if conf_reader.config["DEFAULT"]["MODE"] == "LOC":
        print("local mode")

        # Check if Onkopus modules are running

    elif conf_reader.config["DEFAULT"]["MODE"] == "PUB":
        # print("public mode")

        module_server = conf_reader.__MODULE_PROTOCOL__ + '//' + conf_reader.__MODULE_SERVER__
        print("Module server: ", module_server)


    # Get active modules
    active_modules = []
    try:
        active_modules = conf_reader.config["DEFAULT"]["ACTIVE_MODULES"].split(",")
        print("Active modules: " ,active_modules)

    except:
        print("Error: Could not read active modules")
        exit(1)

    # Query all modules if module is set to 'all'
    # if module == 'all':
    #    for module in active_modules:
    #        self.module_request(input_file, output_file, module, genome_version=genome_version)
    # else:

    _module_request(input_file, output_file, module, genome_version=genome_version,
                         input_format=input_format ,output_format=output_format, target=target)

    print("File annotated: " ,module ,", annotations written in: " ,output_file)

    time_stop = time.time()
    time_total = (time_stop - time_start)
    print("Annotation time: " ,str(time_total))

