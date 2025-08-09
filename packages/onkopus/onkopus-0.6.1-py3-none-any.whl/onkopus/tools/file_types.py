import adagenes
import onkopus.conf.read_config as conf_reader

def avf_to_csv(infile,outfile):
    adagenes.avf_to_csv(infile,outfile,mapping=conf_reader.tsv_mappings,labels=conf_reader.tsv_labels,ranked_labels=conf_reader.tsv_feature_ranking)

