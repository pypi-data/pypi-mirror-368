import os, traceback, copy, gzip
import pandas as pd
import adagenes
import adagenes.conf.read_config as conf_reader


class ClinSigWriter():
    """
    Export treatment data on the clinical significance of potential treatments
    """

    def export_feature_results_lv2(self, biomarker_data, record_path=None, meta=None) -> pd.DataFrame:
        """
        Exports biomarker data in full mode with level 2 meta data

        :param biomarker_data:
        :param outfile_src:
        :param feature:
        :param record_path:
        :param meta:
        :param sep:
        :return:
        """
        df_sum = pd.DataFrame()
        for var in biomarker_data.keys():
            if "UTA_Adapter" in biomarker_data[var].keys():
                try:
                    df = pd.json_normalize(data=biomarker_data[var], record_path=record_path, meta=meta, errors='ignore')
                    df_sum = pd.concat([df_sum, df], axis=0)
                except:
                    print(traceback.format_exc())
        return df_sum

    def fill_in_missing_keys_lv2(self,biomarker_data, struc):

        for var in biomarker_data.keys():
            for key in struc:
                if key not in biomarker_data[var]:
                    biomarker_data[var][key] = {}
                for val in struc[key]:
                    if val not in biomarker_data[var][key]:
                        biomarker_data[var][key][val] = {}

        return biomarker_data

    def write_evidence_data_to_file_all_features(self,bframe,
                                                 databases=None,
                                                 format='tsv',
                                                 sep='\t',
                                                 outfile=None):
        """
        Writes data on clinical significance on treatments on molecular targets in an output file,
        where each row represents a potential treatment.

        :param variant_data:
        :param databases:
        :param output_file:
        :param format:
        :param sep:
        :return:
        """

        variant_data = bframe.data

        for var in variant_data.keys():
            if "onkopus_aggregator" not in variant_data[var]:
                variant_data[var]["onkopus_aggregator"] = {}
            if "merged_match_types_data" not in variant_data[var]["onkopus_aggregator"]:
                variant_data[var]["onkopus_aggregator"]["merged_match_types_data"] = []

            if "UTA_Adapter" not in variant_data[var]:
                variant_data[var]["UTA_Adapter"] = {}
            if "gene_name" not in variant_data[var]["UTA_Adapter"]:
                variant_data[var]["UTA_Adapter"]["gene_name"] = ""
            if "variant_exchange" not in variant_data[var]["UTA_Adapter"]:
                variant_data[var]["UTA_Adapter"]["variant_exchange"] = ""

        #record_path = [
        #    ["onkopus_aggregator", "merged_match_types_data",
        #        "exact_match"]]
        record_path = [["onkopus_aggregator", "merged_match_types_data"]]
        meta = [["UTA_Adapter", "gene_name"], ["UTA_Adapter", "variant_exchange"]]

        df = self.export_feature_results_lv2(copy.copy(variant_data), record_path=record_path, meta=meta)
        #print(df.columns)
        #print(df["drugs"])

        #for column in df.columns:
        #    df[column] = df[column].replace("\"","")
        #    df[column] = df[column].replace("\n", "")
        #    df[column] = df[column].replace("'", "")
        #    df[column] = df[column].replace("\t", " ")
        #    df[column] = df[column].replace(",", "")

        df = self.normalize_values(df)

        def remove_brackets_and_quotes(value):
            if isinstance(value, str) and value.startswith("['") and value.endswith("']"):
                return value[2:-2]
            if '"' in str(value):
                value = value.replace('"', '')
            return value

        # Apply the function to each cell in the DataFrame
        df = df.applymap(remove_brackets_and_quotes)

        header = sep.join(df.columns)
        outfile.write(header + '\n')

        #for _, row in df.iterrows():
        #    #line = sep.join(map(str, row.values))  # Convert each value to string and join with commas
        #    row_data = [str(value) for value in row]
        #    print(','.join(row_data) + '\n')
        #    output_file.write(','.join(row_data) + '\n')
        #df.to_csv(output_file)

        #df.to_csv(outfile)

        for i in range(0, df.shape[0]):
            fields = []
            not_empty = False
            not_nans = False
            for j in range(df.shape[1]):
                fields.append(str(df.iloc[i,j]))
                if (j>0) and (str(df.iloc[i,j]) != "") and (str(df.iloc[i,j]) != 'nan'):
                    not_empty = True
                    not_nans = True
            #line = sep.join(fields)
            line = sep.join(f'"{field}"' for field in fields)
            if (line != "") and (not_empty is True) and (not_nans is True):
                #print("line: ",line, "fields: ",fields)
                outfile.write(line + '\n')


    def normalize_values(self,df):
        """
        Formats drug names and drug classifications for treatment export

        :param df:
        :return:
        """
        drug_names = []
        drug_classes = []
        for i in range(0,df.shape[0]):
            drug_str = ""
            dc_str = ""
            if "drugs" in df.columns:
                for drug in df.iloc[i,:].loc["drugs"]:
                    if "drug_name" in drug:
                        drug_name = str(drug["drug_name"])
                        drug_str += drug_name + ", "
                    if isinstance(drug, dict):
                        if "drug_class" in drug.keys():
                            if isinstance(drug["drug_class"], str):
                                dc_str += str(drug["drug_class"]) + ','
                            elif isinstance(drug["drug_class"], list):
                                for dclass in drug["drug_class"]:
                                    dc_str += str(dclass) + ','

                drug_str = drug_str.rstrip(", ")
            #df.at[i,"drugs"] = drug_str

            dc_str = dc_str.rstrip(',')
            drug_names.append(drug_str)
            drug_classes.append(dc_str)
        #print("def shape ",df.shape[0],":", df.shape," len classes ",len(drug_classes))
        try:
            df.drop(["drugs"], axis=1)
        except:
            print(traceback.format_exc())

        df["drug_class"] = drug_classes
        df["drugs"] = drug_names

        return df

    def write_evidence_data_to_file(self,variant_data,outfile,sep="\t"):
        """

        :param outfile:
        :param variant_data:
        :param sep:
        :return:
        """

        fileopen = False
        if isinstance(outfile, str):
            fileopen = True
            file_name, file_extension = copy.deepcopy(os.path.splitext(outfile))
            input_format_recognized = file_extension.lstrip(".")
            if input_format_recognized == "gz":
                outfile = gzip.open(outfile, 'wt')
            else:
                outfile = open(outfile, "w", encoding='utf-8')

        if isinstance(variant_data, dict):
            bframe = adagenes.BiomarkerFrame(data=variant_data)
        else:
            bframe = variant_data
        self.write_evidence_data_to_file_all_features(bframe,sep=sep,outfile=outfile)

        if fileopen is True:
            outfile.close()
        outfile.close()

    def write_evidence_data_to_file2(self,variant_data, databases=None,output_file=None,format='tsv', sep='\t'):

        if isinstance(variant_data,adagenes.BiomarkerFrame):
            variant_data = variant_data.data

        if databases is None:
            databases = conf_reader.config["DEFAULT"]["ACTIVE_EVIDENCE_DATABASES"].split()

        if format == 'csv':
            sep=','

        if output_file is None:
            print("not output file given")
            return

        #print(output_file)
        outfile = open(output_file, 'w')
        line = 'biomarker' + '\t' + 'disease' + '\t' + 'drugs' + '\t' + 'drug_class' + '\t' + 'evidence_level' + '\t' + 'citation_id' + '\t' + 'source'
        print(line, file=outfile)

        for var in variant_data.keys():
            #print(variant_data[var].keys())

            #for db in databases:
            if 'onkopus_aggregator' in variant_data[var]:
                    if 'merged_match_types_data' in variant_data[var]['onkopus_aggregator']:
                            print(len(variant_data[var]['onkopus_aggregator']['merged_match_types_data']))
                            for result in variant_data[var]['onkopus_aggregator']['merged_match_types_data']:
                                #print(result)
                                drugs = result['drugs']
                                drug_name = ""
                                drug_class = ""
                                for drug in drugs:
                                    #print(drug)
                                    if isinstance(drug, dict):
                                        if "drug_name" in drug:
                                            drug_name += drug["drug_name"] + ","
                                        if "drug_class" in drug:
                                            drug_class += drug["drug_clas"] + ','
                                drug_name = drug_name.rstrip(",")
                                line = str(result['biomarker']) + '\t' + str(result['disease']) \
                                       + '\t' + str(drug_name) + '\t' + drug_class + '\t' + str(result['evidence_level']) \
                                       + '\t' + str(result['citation_id']) + '\t' + str(result['source'])
                                print(line, file=outfile)
            else:
                    print("no data: ")

        outfile.close()


    def write_to_file(self, outfile, bframe, databases=None, format="tsv", sep="\t"):
        """

        :param output_file:
        :param bframe:
        :param databases:
        :param format:
        :param sep:
        :return:
        """
        isfile=False
        if isinstance(outfile, str):
            outfile = open(outfile, 'w')
            isffle = True

        self.write_evidence_data_to_file_all_features(bframe, outfile=outfile, format=format,
                                                 sep=sep)

        if isfile is True:
            outfile.close()
