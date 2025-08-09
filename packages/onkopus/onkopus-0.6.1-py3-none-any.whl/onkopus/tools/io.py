import adagenes
import onkopus as op
import onkopus.conf.read_config as conf_reader


def divide_list(input_list, chunk_size=100):
    """Divides a list into sublists of specified size."""
    for i in range(0, len(input_list), chunk_size):
        yield input_list[i:i + chunk_size]


def read_file(infile,input_format=None, mapping=None, genome_version=None, sep=","):
    """
    Reads in a variant file of different formats (.vcf, .maf, .csv, .tsv, .xlsx, .txt)

    :param infile:
    :param input_format:
    :param mapping:
    :param genome_version:
    :return:
    """
    bframe = adagenes.read_file(infile, reader=None, input_format=input_format, mapping=mapping, genome_version=genome_version, sep=sep)

    if bframe.data_type == "p":
        bframe.genome_version = "hg38"
        bframe.data = op.CCSGeneToGenomicClient(bframe.genome_version).process_data(bframe.data)
        bframe.data_type="g"

    if bframe.genome_version == "hg19":
        bframe.data = adagenes.LiftoverClient(genome_version=bframe.genome_version).process_data(bframe.data)
        genome_version = "hg38"

    return bframe


def save_variants(outfile, json_obj,file_type=None, genome_version=None, sort_features=True):
    write_file(outfile, json_obj,file_type=None, genome_version=None, sort_features=True)

def save_treatments(outfile, json_obj,file_type=None, genome_version=None, sort_features=True):
    op.ClinSigWriter().write_to_file(outfile, json_obj)

def write_file(outfile, json_obj,file_type=None, genome_version=None, sort_features=True, export_features=None):
    """
    Writes annotated variant data in an output file of the specified output format

    :param outfile:
    :param json_obj:
    :param file_type:
    :param genome_version:
    :param sort_features:
    :return:
    """
    if isinstance(json_obj,dict):
        data = adagenes.BiomarkerFrame()
        data.data = json_obj
        data.genome_version=genome_version

        if export_features is not None:
            mapping = None
        else:
            mapping = conf_reader.tsv_mappings
            if file_type is None:
                writer = adagenes.get_writer(outfile, file_type=file_type)
                if isinstance(writer, adagenes.VCFWriter):
                    mapping = conf_reader.vcf_mappings

        print("Writing file in ",outfile)
        adagenes.write_file(outfile, data,
                          file_type=file_type,
                          genome_version=genome_version,
                          labels=conf_reader.tsv_labels,
                          ranked_labels=conf_reader.tsv_feature_ranking,
                          mapping=mapping,
                            export_features=export_features
                          )
    else:
        if export_features is not None:
            mapping = None
        else:
            mapping = conf_reader.tsv_mappings

        adagenes.write_file(outfile,
                          json_obj,
                          file_type=file_type,
                          genome_version=genome_version,
                          labels=conf_reader.tsv_labels,
                          ranked_labels=conf_reader.tsv_feature_ranking,
                          mapping=mapping,
                            export_features=export_features
                          )

