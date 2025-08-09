
def get_gene_names(vcf_lines):
    gene_names = []
    for var in vcf_lines.keys():
        if "UTA_Adapter" in var.keys():
            if "gene_name" in var["UTA_Adapter"]:
                gene_names.append(var["UTA_Adapter"]["gene_name"])
            else:
                gene_names.append("")
        elif "UTA_Adapter_gene_name" in var.keys():
            gene_names.append(var["UTA_Adapter_gene_name"])
        else:
            gene_names.append("")
    return gene_names
