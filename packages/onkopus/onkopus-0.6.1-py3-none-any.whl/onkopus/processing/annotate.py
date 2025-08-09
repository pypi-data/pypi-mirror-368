import copy, multiprocessing
import concurrent.futures
import traceback

import adagenes
import onkopus as op


def annotate(bframe:adagenes.BiomarkerFrame,
             genome_version=None,
             oncokb_key=None,
             lo_hg19=None,
             lo_hg38=None,
             lo_t2t=None,
             tumor_type=None,
             request_id=None,
             redis_client=None,
             protein_to_genomic=True,
             transcript_to_genomic=True,
             include_clinical_data=True,
             include_gene=True,
             include_acmg=True
             ) -> adagenes.BiomarkerFrame:
    """
    Runs the full Onkopus annotation pipeline to annotate biomarkers

    :param tumor_type:
    :param lo_t2t:
    :param lo_hg38:
    :param lo_hg19:
    :param oncokb_key:
    :param genome_version:
    :param bframe:
    :return:
    """
    if genome_version is not None:
        bframe.genome_version = genome_version

    if isinstance(bframe,dict):
        bframe = adagenes.BiomarkerFrame(data=bframe)

    # Recognize biomarkers
    bframe = adagenes.recognize_biomarker_types(bframe)

    # Map biomarkers on protein and transcript level to genomic level (MANE Select)
    if protein_to_genomic is True:
        bframe = op.ProteinToGenomic().process_data(bframe)
        bframe = op.TranscriptToGenomic().process_data(bframe)

    # Liftover
    target_genome = None
    if (bframe.genome_version != "hg38") and (bframe.genome_version != ""):
        target_genome = "hg38"
        #bframe = adagenes.LiftoverAnnotationClient(bframe.genome_version, target_genome="hg38").process_data(bframe)
        bframe = adagenes.LiftoverClient(bframe.genome_version, target_genome="hg38").process_data(bframe)
    #bframe = adagenes.liftover(bframe, target_genome=target_genome)

    # Annotate biomarkers
    #bframe.data = op.annotate_snvs(bframe.data,genome_version=bframe.genome_version,oncokb_key=oncokb_key,
    #                               lo_hg19=lo_hg19,lo_hg38=lo_hg38,lo_t2t=lo_t2t, tumor_type=tumor_type)
    #bframe.data = op.annotate_indels(bframe.data,genome_version=bframe.genome_version,oncokb_key=oncokb_key,tumor_type=tumor_type)
    #bframe.data = op.annotate_fusions(bframe.data,genome_version=bframe.genome_version,tumor_type=tumor_type)
    #bframe.data = op.annotate_genes(bframe.data, genome_version=bframe.genome_version,tumor_type=tumor_type)

    data = copy.deepcopy(bframe.data)
    num_cores = multiprocessing.cpu_count()
    if tumor_type is None:
        tumor_type = ""

    t_args = [
              { 'genome_version': bframe.genome_version ,
                'oncokb_key': oncokb_key ,
                'tumor_type': tumor_type,
                'request_id': request_id,
                'include_clinical_data': include_clinical_data,
                'include_gene': include_gene,
                'include_acmg': include_acmg
                },
              {
                  'genome_version': bframe.genome_version,
                  'oncokb_key': oncokb_key,
                  'tumor_type': tumor_type,
                  'request_id': request_id,
                  'include_clinical_data': include_clinical_data,
                  'include_gene': include_gene,
                  'include_acmg': include_acmg
              },
             {
                 'genome_version': bframe.genome_version,
                 'tumor_type': tumor_type,
                 'request_id': request_id,
                 'include_clinical_data': include_clinical_data,
                 'include_gene': include_gene,
                 'include_acmg': include_acmg
             },
             {
                 'genome_version': bframe.genome_version,
                 'tumor_type': tumor_type,
                 'request_id': request_id,
                 'include_clinical_data': include_clinical_data,
                 'include_gene': include_gene,
                 'include_acmg': include_acmg
             },
             {
                 'genome_version': bframe.genome_version,
                 'tumor_type': tumor_type,
                 'request_id': request_id,
                 'include_clinical_data': include_clinical_data,
                 'include_gene': include_gene,
                 'include_acmg': include_acmg
             }
              ]

    result_data = []
    #print("start pooling")
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(op.annotate_snvs, data, **t_args[0]): "snvs",
            executor.submit(op.annotate_indels, data, **t_args[1]): "indels",
            executor.submit(op.annotate_fusions, data, **t_args[2]): "fusions",
            executor.submit(op.annotate_genes, data, **t_args[3]): "genes",
            executor.submit(op.annotate_cnas, data, **t_args[4]): "cnas"
        }

        for future in concurrent.futures.as_completed(futures):
            key = futures[future]
            try:
                #print("result  ",future.result())
                result_data.append(future.result())
            except Exception as exc:
                print(f"{key} generated an exception: {exc}")
                print(traceback.format_exc())

    data_new = {}
    for result in result_data:
        #print("resultt ",result)
        data_new = adagenes.merge_dictionaries(data_new, result)
    bframe.data = data_new

    return bframe

def parallelize_annotations(data, genome_version, oncokb_key, lo_hg19, lo_hg38, lo_t2t, tumor_type, num_cores):
    annotations = []
    with multiprocessing.Pool(processes=num_cores) as pool:
        annotations.append(pool.apply_async(op.annotate_snvs, args=(data, genome_version, oncokb_key, lo_hg19, lo_hg38, lo_t2t, tumor_type)))
        annotations.append(pool.apply_async(op.annotate_indels, args=(data, genome_version, oncokb_key, tumor_type)))
        annotations.append(pool.apply_async(op.annotate_fusions, args=(data, genome_version, tumor_type)))
        annotations.append(pool.apply_async(op.annotate_genes, args=(data, genome_version, tumor_type)))
    results = [a.get() for a in annotations]
    return results

