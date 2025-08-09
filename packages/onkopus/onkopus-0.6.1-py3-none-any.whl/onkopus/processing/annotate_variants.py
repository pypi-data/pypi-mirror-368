import json, datetime
import traceback, redis
from typing import Dict

from requests.packages import target

from onkopus.conf import read_config as conf_reader
from onkopus.onkopus_clients import CCSGeneToGenomicClient
import onkopus.onkopus_clients
import adagenes
from onkopus.processing.parallel_requests import parallel_requests, parallel_interpreter_requests, parallel_requests0


def get_onkopus_client(module, genome_version, target=None, data_type=None):
    """
    Returns an Onkopus module client by identifier

    :param module:
    :param genome_version:
    :return:
    """
    if (module == 'ccs') or (module == 'genomic_to_gene'):
        return onkopus.onkopus_clients.UTAAdapterClient(genome_version=genome_version)
    if module == 'ccs_liftover':
        return onkopus.onkopus_clients.LiftOverClient(genome_version=genome_version)
    if module == 'ccs_gene':
        client = onkopus.onkopus_clients.CCSGeneToGenomicClient(genome_version=genome_version, data_type=data_type)
        return client
    if module == 'dbsnp':
        return onkopus.onkopus_clients.DBSNPClient(genome_version=genome_version)
    if module == 'clinvar':
        return onkopus.onkopus_clients.ClinVarClient(genome_version=genome_version)
    if module == 'revel':
        return onkopus.onkopus_clients.REVELClient(genome_version=genome_version)
    if module == 'loftool':
        return onkopus.onkopus_clients.LoFToolClient(genome_version=genome_version)
    if module == 'vuspredict':
        return onkopus.onkopus_clients.VUSPredictClient(genome_version=genome_version)
    if module == 'metakb':
        return onkopus.onkopus_clients.MetaKBClient(genome_version=genome_version)
    if module == 'mvp':
        return onkopus.onkopus_clients.MVPClient(genome_version=genome_version)
    if module == 'primateai':
        return onkopus.onkopus_clients.PrimateAIClient(genome_version=genome_version)
    if module == 'alphamissense':
        return onkopus.onkopus_clients.AlphaMissenseClient(genome_version=genome_version)
    if module == 'dbnsfp':
        return onkopus.onkopus_clients.DBNSFPClient(genome_version=genome_version)
    if module == 'gencode':
        return onkopus.onkopus_clients.GENCODEGenomicClient(
            genome_version=genome_version)
    if module == 'gencode_genomic':
        return onkopus.onkopus_clients.GENCODEGenomicClient(
            genome_version=genome_version)
    if module == 'uta_adapter_protein_sequence':
        return onkopus.onkopus_clients.UTAAdapterProteinSequenceClient(genome_version=genome_version)
    if module == 'civic':
        return onkopus.onkopus_clients.CIViCClient(genome_version=genome_version)
    if module == 'oncokb':
        return onkopus.onkopus_clients.OncoKBClient(genome_version=genome_version)
    if module == 'aggregator':
        return onkopus.onkopus_clients.AggregatorClient(genome_version=genome_version)
    if module == 'biomarker_types':
        return onkopus.onkopus_clients.BiomarkerRecognitionClient(genome_version=genome_version)
    if module == 'drug_classification':
        return onkopus.onkopus_clients.DrugOnClient(genome_version=genome_version)
    if module == 'all':
        return onkopus.onkopus_clients.AllModulesClient(genome_version=genome_version)
    if module == 'liftover':
        client = adagenes.LiftoverClient(genome_version=genome_version)
        client.target_genome = target
        return client
    if module == 'liftover_annotation':
        return adagenes.LiftoverAnnotationClient(genome_version=genome_version)

    return None


def get_lo_targets(genome_version):
    targets = []

    if genome_version == "hg19":
        targets = ["hg38", "t2t"]
    elif genome_version == "hg38":
        targets = ["hg19", "t2t"]
    elif genome_version == "t2t":
        targets = ["hg19", "hg38"]

    return targets


def annotate_variant_data(
        annotated_data,
        genome_version: str = 'hg38',
        module=None,
        oncokb_key='',
        lo_hg19=None,
        lo_hg38=None,
        lo_t2t=None,
        tumor_type=None,
        request_id=None,
        include_clinical_data=True,
        include_gene=True,
        include_acmg=True,
        cc_key=None
):
    """
    Retrieves all annotation modules for a list of variants and returns an annotated JSON representation of the annotated variants

    Parameters
    ----------
    vcf_data

    Returns
    -------

    """
    redis_client = None
    if request_id is not None:
        redis_client = redis.StrictRedis(host=conf_reader.__REDIS_SERVER__, port=conf_reader.__REDIS_SERVER_PORT__,
                                         db=conf_reader.__REDIS_SERVER_DB__, decode_responses=True)

    if module is None:
        modules = conf_reader.__ACTIVE_MODULES__
    else:
        modules = [module]

    if annotated_data is None:
        return {}

    if (genome_version == "hg19") or (genome_version == "t2t"):
        #annotated_data = onkopus.LiftOverClient(genome_version=genome_version, target_genome="hg38").process_data(
        #    annotated_data)
        annotated_data = adagenes.LiftoverAnnotationClient(genome_version=genome_version, target_genome="hg38").process_data(annotated_data)
        # print("Converted data to GRCh38")

    #if 'ccs' in modules:
    annotated_data = parallel_requests0(annotated_data, genome_version, oncokb_key=oncokb_key, include_clinical_data=include_clinical_data)
    #print("annotated data ",annotated_data.keys())
    #annotated_data = onkopus.onkopus_clients.UTAAdapterClient(genome_version=genome_version).process_data(
    #        annotated_data)
    if include_gene is True:
        annotated_data = onkopus.onkopus_clients.CCSGeneToGenomicClient(genome_version=genome_version,
                                                                    data_type="g").process_data(annotated_data)

    # Parallelized annotation requests
    if "revel" in modules:
        annotated_data = parallel_requests(annotated_data, genome_version, oncokb_key=oncokb_key, include_clinical_data=include_clinical_data, cc_key = cc_key)

    # Parallelized interpretation requests
    if "aggregator" in modules:
        if request_id is not None:
            print("cached request ", annotated_data.keys())
            redis_client.set(request_id, json.dumps({"result": annotated_data, 'genome_version': genome_version,
                                                     "timestamp": str(datetime.datetime.now())}))
            parallel_interpreter_requests(annotated_data, genome_version, request_id=request_id)
            annotated_data = json.loads(redis_client.get(request_id))
            annotated_data = annotated_data["result"]
            # print("New annotated ",annotated_data)
        else:
            if include_clinical_data is True:
                annotated_data = parallel_interpreter_requests(annotated_data, genome_version, request_id=request_id)
        # print("agg ok")
        if isinstance(annotated_data, str):
            annotated_data = json.loads(annotated_data)

    # print(redis_client.get(request_id).keys())
    if request_id is not None:
        # print("cache result ",annotated_data.keys())


        redis_client.set(request_id, json.dumps({"result": annotated_data, 'genome_version': genome_version,
                                                 "timestamp": str(datetime.datetime.now())}))
        if include_acmg is True:
            onkopus.onkopus_clients.InterpreterClient(genome_version=genome_version, request_id=request_id).process_data(
                annotated_data, tumor_type=tumor_type)
        result = json.loads(redis_client.get(request_id))
        # print("new annotated",result)
        variant_data = result['result']
        annotated_data = variant_data
    else:
        if include_acmg is True:
            annotated_data = onkopus.onkopus_clients.InterpreterClient(genome_version=genome_version,
                                                                       request_id=request_id).process_data(annotated_data,
                                                                                                           tumor_type=tumor_type)
            #print("annoted data ", annotated_data.keys())
    # print(redis_client.get(request_id).keys())
    if isinstance(annotated_data, str):
        # print(annotated_data)
        try:
            annotated_data = json.loads(annotated_data)
            #print("annotated data ", annotated_data.keys())
        except:
            print(traceback.format_exc())

    #if 'biomarker_types' in modules:
    #    annotated_data = onkopus.onkopus_clients.BiomarkerRecognitionClient(
    #        genome_version=genome_version).process_data(annotated_data)
    # if 'drug_classification' in modules:
    #    annotated_data = onkopus.onkopus_clients.DrugOnClient(
    #        genome_version=genome_version).process_data(annotated_data)
    #print("return annotated ", annotated_data.keys())

    return annotated_data


def annotate_file_all_modules(
        infile_str,
        outfile_str,
        genome_version='hg38',
        reader_input_format=None,
        writer_output_format=None
):
    """
    Annotates a specified file and writes the annotated file in the specified output path

    :param infile_str:
    :param outfile_str:
    :param genome_version:
    :param reader_input_format:
    :param writer_output_format:
    :return:
    """
    # generate reader
    reader = adagenes.tools.get_reader(infile_str, file_type=reader_input_format)
    writer = adagenes.tools.get_writer(outfile_str, file_type=writer_output_format)

    json_obj = reader.read_file(infile_str)
    annotated_data = json_obj.data

    # variant_dc = adagenes.generate_variant_dictionary(annotated_data)

    if 'ccs_liftover' in conf_reader.__ACTIVE_MODULES__:
        client = onkopus.onkopus_clients.ccs_liftover_client.LiftOverClient(genome_version=genome_version)
        annotated_data = client.process_data(annotated_data)
    if 'ccs' in conf_reader.__ACTIVE_MODULES__:
        client = onkopus.onkopus_clients.UTAAdapterClient(genome_version=genome_version)
        annotated_data = client.process_data(annotated_data)
    if 'dbsnp' in conf_reader.__ACTIVE_MODULES__:
        client = onkopus.onkopus_clients.DBSNPClient(genome_version=genome_version)
        annotated_data = client.process_data(annotated_data)
    if 'clinvar' in conf_reader.__ACTIVE_MODULES__:
        annotated_data = onkopus.onkopus_clients.ClinVarClient(genome_version=genome_version).process_data(
            annotated_data)
    if 'revel' in conf_reader.__ACTIVE_MODULES__:
        annotated_data = onkopus.onkopus_clients.revel_client.REVELClient(
            genome_version=genome_version).process_data(annotated_data)
    if 'loftool' in conf_reader.__ACTIVE_MODULES__:
        annotated_data = onkopus.onkopus_clients.LoFToolClient(
            genome_version=genome_version).process_data(annotated_data)
    if 'vuspredict' in conf_reader.__ACTIVE_MODULES__:
        annotated_data = onkopus.onkopus_clients.VUSPredictClient(
            genome_version=genome_version).process_data(annotated_data)
    if 'metakb' in conf_reader.__ACTIVE_MODULES__:
        annotated_data = onkopus.onkopus_clients.MetaKBClient(
            genome_version=genome_version).process_data(annotated_data)
    if 'mvp' in conf_reader.__ACTIVE_MODULES__:
        annotated_data = onkopus.onkopus_clients.MVPClient(
            genome_version=genome_version).process_data(annotated_data)
    if 'primateai' in conf_reader.__ACTIVE_MODULES__:
        annotated_data = onkopus.onkopus_clients.PrimateAIClient(
            genome_version=genome_version).process_data(annotated_data)
    if 'alphamissense' in conf_reader.__ACTIVE_MODULES__:
        annotated_data = onkopus.onkopus_clients.AlphaMissenseClient(
            genome_version=genome_version).process_data(annotated_data)
    if 'dbnsfp' in conf_reader.__ACTIVE_MODULES__:
        annotated_data = onkopus.onkopus_clients.DBNSFPClient(
            genome_version=genome_version).process_data(annotated_data)
    if 'gencode' in conf_reader.__ACTIVE_MODULES__:
        annotated_data = onkopus.onkopus_clients.GENCODEClient(
            genome_version=genome_version).process_data(annotated_data)
    if 'gencode_genomic' in conf_reader.__ACTIVE_MODULES__:
        annotated_data = onkopus.onkopus_clients.GENCODEGenomicClient(
            genome_version=genome_version).process_data(annotated_data)
    if 'uta_adapter_protein_sequence' in conf_reader.__ACTIVE_MODULES__:
        annotated_data = onkopus.onkopus_clients.UTAAdapterProteinSequenceClient(
            genome_version=genome_version).process_data(annotated_data)
    if 'civic' in conf_reader.__ACTIVE_MODULES__:
        annotated_data = onkopus.onkopus_clients.CIViCClient(
            genome_version=genome_version).process_data(annotated_data)
    if 'oncokb' in conf_reader.__ACTIVE_MODULES__:
        annotated_data = onkopus.onkopus_clients.OncoKBClient(
            genome_version=genome_version).process_data(annotated_data)
    if 'aggregator' in conf_reader.__ACTIVE_MODULES__:
        annotated_data = onkopus.onkopus_clients.AggregatorClient(
            genome_version=genome_version).process_data(annotated_data)
    if 'biomarker_types' in conf_reader.__ACTIVE_MODULES__:
        annotated_data = onkopus.onkopus_clients.BiomarkerRecognitionClient(
            genome_version=genome_version).process_data(annotated_data)
    if 'drug_classification' in conf_reader.__ACTIVE_MODULES__:
        annotated_data = onkopus.onkopus_clients.DrugOnClient(
            genome_version=genome_version).process_data(annotated_data)

    json_obj.data = annotated_data
    writer.write_to_file(outfile_str, json_obj, )


def annotate_file(infile_str, outfile_str, module, genome_version, lo_hg19=None, lo_hg38=None):
    """
    Annotates a biomarker file with an Onkopus client

    :param infile_str:
    :param outfile_str:
    :param module:
    :param genome_version:
    :return:
    """
    infile = adagenes.open_infile(infile_str)
    outfile = adagenes.open_outfile(outfile_str)

    if module == "uta":
        vcf_obj = onkopus.onkopus_clients.UTAAdapterClient(genome_version=genome_version)
    elif module == "uta_gene":
        vcf_obj = onkopus.onkopus_clients.ccs_genomic_client.CCSGeneToGenomicClient(
            genome_version=genome_version)
    elif module == 'ccs_liftover':
        vcf_obj = onkopus.onkopus_clients.LiftOverClient(genome_version=genome_version)
    elif module == 'liftover':
        vcf_obj = onkopus.LiftoverAnnotationClient(genome_version)
    elif module == 'dbsnp':
        vcf_obj = onkopus.onkopus_clients.DBSNPClient(genome_version=genome_version)
    elif module == "clinvar":
        vcf_obj = onkopus.onkopus_clients.ClinVarClient(genome_version=genome_version)
    elif module == "revel":
        vcf_obj = onkopus.onkopus_clients.REVELClient(genome_version=genome_version)
    elif module == "loftool":
        vcf_obj = onkopus.onkopus_clients.LoFToolClient(genome_version=genome_version)
    elif module == "vuspredict":
        vcf_obj = onkopus.onkopus_clients.VUSPredictClient(genome_version=genome_version)
    elif module == 'metakb':
        vcf_obj = onkopus.onkopus_clients.MetaKBClient(genome_version=genome_version)
    elif module == 'mvp':
        vcf_obj = onkopus.onkopus_clients.MVPClient(genome_version=genome_version)
    elif module == 'primateai':
        vcf_obj = onkopus.onkopus_clients.PrimateAIClient(genome_version=genome_version)
    elif module == 'alphamissense':
        vcf_obj = onkopus.onkopus_clients.AlphaMissenseClient(genome_version=genome_version)
    elif module == 'dbnsfp':
        vcf_obj = onkopus.onkopus_clients.DBNSFPClient(genome_version=genome_version)
    elif module == 'gencode':
        vcf_obj = onkopus.onkopus_clients.GENCODEClient(
            genome_version=genome_version)
    elif module == 'gencode_genomic':
        vcf_obj = onkopus.onkopus_clients.GENCODEGenomicClient(
            genome_version=genome_version)
    elif module == 'uta_adapter_protein_sequence':
        vcf_obj = onkopus.onkopus_clients.UTAAdapterProteinSequenceClient(genome_version=genome_version)
    elif module == 'civic':
        vcf_obj = onkopus.onkopus_clients.CIViCClient(genome_version=genome_version)
    elif module == 'oncokb':
        vcf_obj = onkopus.onkopus_clients.OncoKBClient(genome_version=genome_version)
    elif module == 'aggregator':
        vcf_obj = onkopus.onkopus_clients.AggregatorClient(genome_version=genome_version)
    elif module == 'biomarker_types':
        vcf_obj = onkopus.onkopus_clients.BiomarkerRecognitionClient(genome_version=genome_version)
    elif module == 'drug_classification':
        vcf_obj = onkopus.onkopus_clients.DrugOnClient(genome_version=genome_version)
    elif module == 'all':
        vcf_obj = onkopus.onkopus_clients.AllModulesClient(genome_version=genome_version)

    print("perform analysis (", module, "), infile ", infile_str, " output in ", outfile_str)
    if module == 'liftover':
        adagenes.processing.process_files.process_file(infile_str, outfile_str, vcf_obj, genome_version=genome_version,
                                                       input_format='json',
                                                       output_format='json',
                                                       lo_hg19=lo_hg19, lo_hg38=lo_hg38)
    else:
        adagenes.processing.process_files.process_file(infile_str, outfile_str, vcf_obj, genome_version=genome_version,
                                                       input_format='json',
                                                       output_format='json')

    infile.close()
    outfile.close()


def annotate_file_db(variant_data, module, genome_version, lo_hg19=None, lo_hg38=None):
    """
    Annotates a biomarker file with an Onkopus client

    :param module:
    :param genome_version:
    :return:
    """

    vcf_obj = None
    if module == "UTA_Adapter":
        vcf_obj = onkopus.onkopus_clients.UTAAdapterClient(genome_version=genome_version)
    elif module == "UTA_Adapter_gene":
        vcf_obj = onkopus.onkopus_clients.ccs_genomic_client.CCSGeneToGenomicClient(
            genome_version=genome_version)
    elif module == 'ccs_liftover':
        vcf_obj = onkopus.onkopus_clients.LiftOverClient(genome_version=genome_version)
    elif module == 'liftover':
        vcf_obj = adagenes.LiftoverAnnotationClient(genome_version)
    elif module == 'dbsnp':
        vcf_obj = onkopus.onkopus_clients.DBSNPClient(genome_version=genome_version)
    elif module == "clinvar":
        vcf_obj = onkopus.onkopus_clients.ClinVarClient(genome_version=genome_version)
    elif module == "revel":
        vcf_obj = onkopus.onkopus_clients.REVELClient(genome_version=genome_version)
    elif module == "loftool":
        vcf_obj = onkopus.onkopus_clients.LoFToolClient(genome_version=genome_version)
    elif module == "vus_predict":
        vcf_obj = onkopus.onkopus_clients.VUSPredictClient(genome_version=genome_version)
    elif module == "vuspredict":
        vcf_obj = onkopus.onkopus_clients.VUSPredictClient(genome_version=genome_version)
    elif module == 'metakb':
        vcf_obj = onkopus.onkopus_clients.MetaKBClient(genome_version=genome_version)
    elif module == 'mvp':
        vcf_obj = onkopus.onkopus_clients.MVPClient(genome_version=genome_version)
    elif module == 'primateai':
        vcf_obj = onkopus.onkopus_clients.PrimateAIClient(genome_version=genome_version)
    elif module == 'alphamissense':
        vcf_obj = onkopus.onkopus_clients.AlphaMissenseClient(genome_version=genome_version)
    elif module == 'dbnsfp':
        vcf_obj = onkopus.onkopus_clients.DBNSFPClient(genome_version=genome_version)
    elif module == 'gencode':
        vcf_obj = onkopus.onkopus_clients.GENCODEClient(
            genome_version=genome_version)
    elif module == 'gencode_genomic':
        vcf_obj = onkopus.onkopus_clients.GENCODEGenomicClient(
            genome_version=genome_version)
    elif module == 'UTA_Adapter_protein_sequence':
        vcf_obj = onkopus.onkopus_clients.UTAAdapterProteinSequenceClient(genome_version=genome_version)
    elif module == 'civic':
        vcf_obj = onkopus.onkopus_clients.CIViCClient(genome_version=genome_version)
    elif module == 'oncokb':
        vcf_obj = onkopus.onkopus_clients.OncoKBClient(genome_version=genome_version)
    elif module == 'onkopus_aggregator':
        vcf_obj = onkopus.onkopus_clients.AggregatorClient(genome_version=genome_version)
    elif module == 'biomarker_types':
        vcf_obj = onkopus.onkopus_clients.BiomarkerRecognitionClient(genome_version=genome_version)
    elif module == 'drug_classification':
        vcf_obj = onkopus.onkopus_clients.DrugOnClient(genome_version=genome_version)
    elif module == 'all':
        vcf_obj = onkopus.onkopus_clients.AllModulesClient(genome_version=genome_version)

    if module == 'liftover':
        variant_data = vcf_obj.process_data(variant_data, lo_hg19=lo_hg19, lo_hg38=lo_hg38)
    else:
        if vcf_obj is not None:
            variant_data = vcf_obj.process_data(variant_data)
        else:
            print("Error: No client instantiated: ", module)

    return variant_data

