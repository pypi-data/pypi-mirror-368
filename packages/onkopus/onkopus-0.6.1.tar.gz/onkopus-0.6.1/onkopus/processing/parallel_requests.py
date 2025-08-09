import copy, gzip, os, traceback, time
from multiprocessing import Process, Pool
import copy
import adagenes
import adagenes

import onkopus.onkopus_clients
import multiprocessing
from onkopus.processing.threads import ThreadWithReturnValue


def parallel_interpreter_requests(annotated_data,genome_version, request_id=None):
    """
    Parallelized requests to the data interpretation modules (Treatment aggregator and pathogenicity interpreter)

    :param variant_data:
    :param genome_version:
    :return:
    """
    start_time = time.time()

    task1 = onkopus.onkopus_clients.AggregatorClient(genome_version=genome_version, request_id=request_id).process_data
    #task2 = onkopus.onkopus_clients.InterpreterClient(genome_version=genome_version).process_data

    t1 = ThreadWithReturnValue(target=task1, args=[annotated_data])
    #t2 = ThreadWithReturnValue(target=task2, args=[annotated_data])

    t1.start()
    #t2.start()

    data1 = t1.join()
    #data2 = t2.join()

    annotated_data = adagenes.merge_dictionaries(annotated_data, data1)
    #annotated_data = adagenes.merge_dictionaries(annotated_data, data2)

    stop_time = time.time() - start_time
    print("Time for parallel interpretation requests: ", stop_time)

    return annotated_data


def multiprocess_requests(annotated_data, genome_version):
    """
    Run parallel annotation requests on multiple CPUs

    :param annotated_data:
    :param genome_version:
    :return:
    """

    start_time = time.time()

    tasks = [
        onkopus.onkopus_clients.DBSNPClient(genome_version=genome_version).process_data,
        onkopus.onkopus_clients.ClinVarClient(genome_version=genome_version).process_data,
        onkopus.onkopus_clients.REVELClient(genome_version=genome_version).process_data,
        onkopus.onkopus_clients.LoFToolClient(genome_version=genome_version).process_data,
        onkopus.onkopus_clients.VUSPredictClient(genome_version=genome_version).process_data,
        onkopus.onkopus_clients.MetaKBClient(genome_version=genome_version).process_data,
        onkopus.onkopus_clients.MVPClient(genome_version=genome_version).process_data,
        onkopus.onkopus_clients.PrimateAIClient(genome_version=genome_version).process_data,
        onkopus.onkopus_clients.DBNSFPClient(genome_version=genome_version).process_data,
        onkopus.onkopus_clients.ProteinFeatureClient(genome_version=genome_version).process_data,
        onkopus.onkopus_clients.GENCODEGenomicClient(genome_version=genome_version).process_data,
        onkopus.onkopus_clients.UTAAdapterProteinSequenceClient(genome_version=genome_version).process_data,
        onkopus.onkopus_clients.CIViCClient(genome_version=genome_version).process_data,
        onkopus.onkopus_clients.OncoKBClient(genome_version=genome_version).process_data,
        onkopus.onkopus_clients.AlphaMissenseClient(genome_version=genome_version).process_data
    ]

    data = [
        copy.deepcopy(annotated_data),
        copy.deepcopy(annotated_data),
        copy.deepcopy(annotated_data),
        copy.deepcopy(annotated_data),
        copy.deepcopy(annotated_data),
        copy.deepcopy(annotated_data),
        copy.deepcopy(annotated_data),
        copy.deepcopy(annotated_data),
        copy.deepcopy(annotated_data),
        copy.deepcopy(annotated_data),
        copy.deepcopy(annotated_data),
        copy.deepcopy(annotated_data),
        copy.deepcopy(annotated_data),
        copy.deepcopy(annotated_data),
        copy.deepcopy(annotated_data)
    ]

    p = Pool(processes=len(tasks))#
    for i in range(0, len(tasks)):
        task = tasks[i]
        data[i] = p.apply_async(task, args=(data[i],)) #p.map(tasks[i], annotated_data)
    p.close()
    p.join()

    annotated_data={}
    for module_data in data:
        #print("merge ",module_data.get())
        annotated_data = adagenes.merge_dictionaries(annotated_data,module_data.get())
    #print(annotated_data)

    stop_time = time.time() - start_time
    print("Time for parallel annotation requests: ", stop_time)

    return annotated_data


def parallel_requests0(annotated_data, genome_version,oncokb_key=None, include_clinical_data=True):
    #annotated_data = onkopus.onkopus_clients.UTAAdapterClient(genome_version=genome_version).process_data(
    #        annotated_data)
    start_time=time.time()

    task1 = onkopus.onkopus_clients.UTAAdapterClient(genome_version=genome_version).process_data
    task2 = onkopus.onkopus_clients.DBNSFPClient(genome_version=genome_version).process_data

    t1 = ThreadWithReturnValue(target=task1, args=[annotated_data])
    t2 = ThreadWithReturnValue(target=task2, args=[annotated_data])

    t1.start()
    t2.start()

    data1 = t1.join()
    data2 = t2.join()

    annotated_data = adagenes.merge_dictionaries(annotated_data, data1)
    annotated_data = adagenes.merge_dictionaries(annotated_data, data2)

    stop_time = time.time() - start_time
    print("Time for parallel annotation requests: ", stop_time)

    return annotated_data

def parallel_requests(annotated_data, genome_version,oncokb_key=None, include_clinical_data=True, cc_key=None):
    """
    Annotates a biomarker frame with parallelized Onkopus requests

    :param annotated_data:
    :param genome_version:
    :param oncokb_key: Private OncoKB account access token (Required for including OncoKB results)
    :return:
    """
    start_time = time.time()

    task1 = onkopus.onkopus_clients.DBSNPClient(genome_version=genome_version).process_data
    task2 = onkopus.onkopus_clients.ClinVarClient(genome_version=genome_version).process_data
    task3 = onkopus.onkopus_clients.REVELClient(genome_version=genome_version).process_data
    task4 = onkopus.onkopus_clients.LoFToolClient(genome_version=genome_version).process_data
    task5 = onkopus.onkopus_clients.MolecularFeaturesClient(genome_version=genome_version).process_data
    task6 = onkopus.onkopus_clients.BiomarkerRecognitionClient(
            genome_version=genome_version).process_data
    task7 = onkopus.onkopus_clients.MVPClient(genome_version=genome_version).process_data
    task8 = onkopus.onkopus_clients.PrimateAIClient(genome_version=genome_version).process_data
    #task9 = onkopus.onkopus_clients.DBNSFPClient(genome_version=genome_version).process_data
    task10 = onkopus.onkopus_clients.ProteinFeatureClient(genome_version=genome_version).process_data
    #task11 = onkopus.onkopus_clients.GENCODEGenomicClient(genome_version=genome_version).process_data
    task12 = onkopus.onkopus_clients.UTAAdapterProteinSequenceClient(genome_version=genome_version).process_data

    if include_clinical_data is True:
        task6 = onkopus.onkopus_clients.MetaKBClient(genome_version=genome_version).process_data
        task13 = onkopus.onkopus_clients.CIViCClient(genome_version=genome_version).process_data
        task14 = onkopus.onkopus_clients.OncoKBClient(genome_version=genome_version).process_data

    task15 = onkopus.onkopus_clients.AlphaMissenseClient(genome_version=genome_version).process_data
    task16 = adagenes.BLOSUMClient().process_data
    #task17 = onkopus.onkopus_clients.COSMICGeneCensusClient(genome_version=genome_version).process_data
    task18 = adagenes.LiftoverAnnotationClient(genome_version=genome_version).process_data
    task19 = onkopus.onkopus_clients.GeneExpressionClient().process_data

    annotated_data_oncokb = copy.deepcopy(annotated_data)
    annotated_data_oncokb["oncokbkey"] = oncokb_key

    t1 = ThreadWithReturnValue(target=task1, args=[annotated_data])
    t2 = ThreadWithReturnValue(target=task2, args=[annotated_data])
    t3 = ThreadWithReturnValue(target=task3, args=[annotated_data])
    t4 = ThreadWithReturnValue(target=task4, args=[annotated_data])
    t5 = ThreadWithReturnValue(target=task5, args=[annotated_data])
    t6 = ThreadWithReturnValue(target=task5, args=[annotated_data])
    t7 = ThreadWithReturnValue(target=task7, args=[annotated_data])
    t8 = ThreadWithReturnValue(target=task8, args=[annotated_data])
    #t9 = ThreadWithReturnValue(target=task9, args=[annotated_data])
    t10 = ThreadWithReturnValue(target=task10, args=[annotated_data])
    #t11 = ThreadWithReturnValue(target=task11, args=[annotated_data])
    t12 = ThreadWithReturnValue(target=task12, args=[annotated_data])

    if include_clinical_data is True:
        t6 = ThreadWithReturnValue(target=task6, args=[annotated_data])
        t13 = ThreadWithReturnValue(target=task13, args=[annotated_data])
        t14 = ThreadWithReturnValue(target=task14, args=[annotated_data_oncokb])

    t15 = ThreadWithReturnValue(target=task15, args=[annotated_data])
    t16 = ThreadWithReturnValue(target=task16, args=[annotated_data])
    #t17 = ThreadWithReturnValue(target=task17, args=[annotated_data])
    t18 = ThreadWithReturnValue(target=task18, args=[annotated_data])
    t19 = ThreadWithReturnValue(target=task19, args=[annotated_data])

    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    #t6.start()
    t7.start()
    t8.start()
    #t9.start()
    t10.start()
    #t11.start()
    t12.start()

    if include_clinical_data is True:
        t6.start()
        t13.start()
        t14.start()

    t15.start()
    t16.start()
    #t17.start()
    t18.start()
    t19.start()

    data1 = t1.join()
    data2 = t2.join()
    data3 = t3.join()
    data4 = t4.join()
    data5 = t5.join()
    #data6 = t6.join()
    data7 = t7.join()
    data8 = t8.join()
    #data9 = t9.join()
    data10 = t10.join()
    #data11 = t11.join()
    data12 = t12.join()

    if include_clinical_data is True:
        data6 = t6.join()
        data13 = t13.join()
        data14 = t14.join()

    data15 = t15.join()
    data16 = t16.join()
    #data17 = t17.join()
    data18 = t18.join()
    data19 = t19.join()

    annotated_data = adagenes.merge_dictionaries(annotated_data, data1)
    annotated_data = adagenes.merge_dictionaries(annotated_data, data2)
    annotated_data = adagenes.merge_dictionaries(annotated_data, data3)
    annotated_data = adagenes.merge_dictionaries(annotated_data, data4)
    annotated_data = adagenes.merge_dictionaries(annotated_data, data5)
    #annotated_data = adagenes.merge_dictionaries(annotated_data, data6)
    annotated_data = adagenes.merge_dictionaries(annotated_data, data7)
    annotated_data = adagenes.merge_dictionaries(annotated_data, data8)
    #annotated_data = adagenes.merge_dictionaries(annotated_data, data9)
    annotated_data = adagenes.merge_dictionaries(annotated_data, data10)
    #annotated_data = adagenes.merge_dictionaries(annotated_data, data11)
    annotated_data = adagenes.merge_dictionaries(annotated_data, data12)

    if include_clinical_data is True:
        annotated_data = adagenes.merge_dictionaries(annotated_data, data6)
        annotated_data = adagenes.merge_dictionaries(annotated_data, data13)
        annotated_data = adagenes.merge_dictionaries(annotated_data, data14)

    annotated_data = adagenes.merge_dictionaries(annotated_data, data15)
    annotated_data = adagenes.merge_dictionaries(annotated_data, data16)
    #annotated_data = adagenes.merge_dictionaries(annotated_data, data17)
    annotated_data = adagenes.merge_dictionaries(annotated_data, data18)
    annotated_data = adagenes.merge_dictionaries(annotated_data, data19)

    stop_time = time.time() - start_time
    print("Time for parallel annotation requests: ",stop_time)

    return annotated_data


