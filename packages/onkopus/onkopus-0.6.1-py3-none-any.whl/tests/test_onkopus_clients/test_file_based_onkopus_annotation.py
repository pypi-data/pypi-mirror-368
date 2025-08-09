import unittest, os
import adagenes
import onkopus.onkopus_clients


class TestOnkopusAnnotation(unittest.TestCase):

    def test_single_module_annotation(self):

        infile="../test_files/somaticMutations.vcf"
        outfile="../test_files/somaticMutations.vcf.onkopus.dbsnp"
        module="dbsnp"

        #adagenes.annotate(infile, outfile, module=module)

    def test_full_module_annotation(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/somaticMutations.vcf"
        outfile = infile + ".annotated"
        genome_version='hg38'

        #adagenes.annotate_file_all_modules(infile, outfile, genome_version=genome_version, writer_output_format="json")

    def test_process_file_with_generic_transformer_vcf(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/somaticMutations.vcf"
        outfile = infile + ".generic.vcf"
        genome_version = 'hg38'

        transformer = onkopus.onkopus_clients.DBSNPClient(genome_version)
        #adagenes.process_file(infile, outfile, transformer, genome_version=genome_version)

    def test_process_file_with_generic_transformer_json(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/somaticMutations.vcf"
        outfile = infile + ".generic.json"
        genome_version = 'hg38'

        transformer = onkopus.onkopus_clients.DBSNPClient(genome_version)
        #adagenes.process_file(infile, outfile, transformer, genome_version=genome_version)
