
tag = "main"

available_modules = ["alphamissense","clinvar","dbsnp","seqcat","dbnsfp","gencode","civic","oncokb",
                     "metakb","protein_analysis","molecular_features","drug_classification",
                     "onkopus-aggregator","onkopus-interpreter","dgidb", "gtex", "onkopus-cache",
                     "onkopus-server", "onkopus-web", "onkopus-database"]

module_ids = {
    "alphamissense": ["alphamissense.yml"],
    "dbsnp": ["dbsnp.yml"],
    "clinvar": ["clinvar.yml"],
    "dgidb": ["dgidb-db.yml", "dgidb-adapter.yml"],
    "gtex": ["gtex-adapter.yml"],
    "fathmm": ["fathmm-adapter.yml"],
    "m3d": ["m3dapp.yml"],
    "uniprot": ["uniprot-adapter.yml"],
    "vep": ["vep-adapter.yml"],
    "vus-predict": ["vus-predict.py"],
    "revel": ["revel.yml"],
    "loftool": ["loftool.yml"],
    "onkopus-server": ["onkopus-server.yml"],
    "onkopus-web": ["onkopus-web.yml"],
    "metakb": ["metakb-adapter.yml"],
    "oncokb": ["oncokb.yml"],
    "civic": ["civic-db.yml", "civic-adapter.yml"],
    "dbnsfp": ["dbnsfp-adapter.yml"],
    "primateai": ["primateai-adapter.yml"],
    "onkopus-database": ["onkopus-database.yml"],
    "onkopus-websocket-server": ["onkopus-server.yml"],
    "onkopus-cache":["onkopus-cache.yml"],
    "protein-analysis":["protein-analysis.yml"],
    "molecular-features":["molecular-features.yml"],
    "onkopus-aggregator":["onkopus-aggregator.yml"],
    "onkopus-interpreter":["onkopus-interpreter.yml"],
    "gencode":["gencode-adapter.yml", "gencode-db.yml"],
    "seqcat": ["uta-adapter.yml", "uta-database.yml"]
}
