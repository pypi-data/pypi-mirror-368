import unittest, os
import onkopus as op


class TestWriteAnnotatedData(unittest.TestCase):

    def test_write_annotated_data(self):
        data = { "chr7:140753336A>T": {} }
        data = op.UTAAdapterClient(genome_version="hg38").process_data(data)
        data = op.DBNSFPClient(genome_version="hg38").process_data(data)

        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        outfile = __location__ + "/../test_files/chr7_140753336AT.csv"
        print("write file")
        op.write_file(outfile,data)

        file = open(outfile)
        contents = file.read()
        contents_expected = """genomic_location_hg38,chrom,pos_hg38,pos_hg19,ref,alt,mutation_type,hgnc_gene_symbol,aa_exchange,aa_exchange_long,ncbi_transcript_mane_select,ncbi_cdna_string,ncbi_cds_start,ncbi_cds_end,ncbi_cds_strand,ncbi_prot_location,ncbi_protein_id,clinvar_clinical_significance,clinvar_review_status,clinvar_cancer_type,clinvar_id,dbsnp_population_frequency,dbsnp_rsid,gnomAD_exomes_ac,gnomAD_exomes_af,1000genomes_af,1000genomes_ac,alfa_total_af,alfa_total_ac,ExAC_AF,ExAC_AC,revel_score,alphamissense_score,mvp_score,loftool_score,vuspredict_score,missense3D_pred,SIFT_score,SIFT_pred,GERP++_score,MetaLR_score,MetaSVM_score,phastCons17way_primate_score,phyloP17way_primate,MutationAssessor_score,MutationTaster_score,fathmm-MKL_coding_score,fathmm-XF_coding_score,uniprot_id,alphamissense_class,Interpro_domain,protein_sequence_MANE_Select,Secondary_protein_structure,RelASA,BLOSUM62
,7,140753336,,A,T,,BRAF,V600E,Val600Glu,NM_004333.6,,,,,,,,,,,,,1,3.979940e-06,.,.,.,.,1.647e-05,2,,,,,,,0.0,,5.65,0.2357,-0.7685,0.999000,0.750000,0.65,1.0,0.99,0.91,,,|Serine-threonine/tyrosine-protein kinase  catalytic domain||Protein kinase domain||Protein kinase domain;Serine-threonine/tyrosine-protein kinase  catalytic domain||Protein kinase domain||Protein kinase domain;Serine-threonine/tyrosine-protein kinase  catalytic domain||Protein kinase domain||Protein kinase domain;Serine-threonine/tyrosine-protein kinase  catalytic domain||Protein kinase domain||Protein kinase domain|,,,,\n"""
        self.assertEqual(contents, contents_expected, "")
        file.close()
