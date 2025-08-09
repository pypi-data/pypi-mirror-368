import copy, gzip, os, traceback, time
from multiprocessing import Process, Pool
import copy
import adagenes
import onkopus.onkopus_clients
from threading import Thread
from onkopus.processing.threads import ThreadWithReturnValue


def parallel_requests(annotated_data, genome_version="hg38",oncokb_key=None, include_clinical_data=True):
    """
    Annotates a biomarker frame with parallelized Onkopus requests

    :param annotated_data:
    :param genome_version:
    :param oncokb_key: Private OncoKB account access token (Required for including OncoKB results)
    :return:
    """
    start_time = time.time()

    task1 = onkopus.onkopus_clients.GENCODEGeneNameClient(genome_version=genome_version).process_data

    if include_clinical_data is True:
        task2 = onkopus.onkopus_clients.CIViCGeneClient(genome_version=genome_version).process_data
    task3 = onkopus.onkopus_clients.UTAAdapterProteinSequenceClient(genome_version=genome_version).process_data
    task4 = onkopus.COSMICGeneCensusClient(genome_version=genome_version).process_data
    task5 = onkopus.DGIdbClient(genome_version=genome_version).process_data
    task6 = onkopus.GeneExpressionClient().process_data

    annotated_data_oncokb = copy.deepcopy(annotated_data)
    annotated_data_oncokb["oncokbkey"] = oncokb_key

    t1 = ThreadWithReturnValue(target=task1, args=[annotated_data])
    if include_clinical_data is True:
        t2 = ThreadWithReturnValue(target=task2, args=[annotated_data])
    t3 = ThreadWithReturnValue(target=task3, args=[annotated_data])
    t4 = ThreadWithReturnValue(target=task4, args=[annotated_data,True])
    t5 = ThreadWithReturnValue(target=task5, args=[annotated_data,True])
    t6 = ThreadWithReturnValue(target=task6, args=[annotated_data, True])

    t1.start()
    if include_clinical_data is True:
        t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()

    data1 = t1.join()
    data2 = t2.join()
    data3 = t3.join()
    data4 = t4.join()
    data5 = t5.join()
    data6 = t6.join()

    annotated_data = adagenes.merge_dictionaries(annotated_data, data1)
    if include_clinical_data is True:
        annotated_data = adagenes.merge_dictionaries(annotated_data, data2)
    annotated_data = adagenes.merge_dictionaries(annotated_data, data3)
    annotated_data = adagenes.merge_dictionaries(annotated_data, data4)
    annotated_data = adagenes.merge_dictionaries(annotated_data, data5)
    annotated_data = adagenes.merge_dictionaries(annotated_data, data6)

    stop_time = time.time() - start_time
    print("Time for parallel annotation requests: ",stop_time)

    return annotated_data

