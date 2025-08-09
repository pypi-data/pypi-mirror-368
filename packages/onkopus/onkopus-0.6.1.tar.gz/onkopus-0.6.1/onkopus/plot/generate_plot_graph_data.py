from adagenes.plot.generate_plots.generate_sunburst_plots import generate_sunburst_plot
import adagenes.plot.generate_data.generate_radarplot_data
import adagenes.plot.generate_plots.generate_radarplot
import adagenes as ag
import onkopus as op
import onkopus.onkopus_clients


def generate_plot_graph_data(variant_data, qid, plot_type, width=None, height=None, genome_version=None,mutation_type=None, font_size=18):
    """
    Generates plot data for all Onkopus plots implemented in Plotly. Returns the JSON graph to display the plot

    :param variant_data:
    :param qid:
    :param plot_type:
    :param width:
    :param height:
    :return:
    """
    if mutation_type is not None:
        if mutation_type in variant_data.keys():
            variant_data = variant_data[mutation_type]
    #if "snvs" in variant_data:
    #    variant_data = variant_data["snvs"]

    if plot_type == "pathogenicity-scores-radar":
        #df = adagenes.plot.generate_data.generate_radarplot_data.generate_single_biomarker_radar_plot_data(variant_data,qid)
        #dfs=[]
        #dfs.append(df)
        #names = adagenes.plot.generate_data.generate_biomarker_identifiers(variant_data)
        #if (width is not None) and (height is not None):
        #    return adagenes.plot.generate_plots.generate_radarplot.generate_radar_plot(dfs,names,
        #                                                    "pathogenicity-scores-radar", width=width,height=height)
        #else:
        #    return adagenes.plot.generate_plots.generate_radarplot.generate_radar_plot(dfs, names,
        #                                                                             "pathogenicity-scores-radar")
        return onkopus.onkopus_clients.PlotClient(genome_version="hg38").process_data(variant_data,
                                                                                      plot="pathogenicity-scores-radar")
    elif plot_type == 'pathogenicity-scores-radar-set':
        #dfs = adagenes.plot.generate_data.generate_radarplot_data.generate_multiple_biomarker_radar_plot_data(variant_data)
        #names=adagenes.plot.generate_data.generate_biomarker_identifiers(variant_data)
        #if (width is not None) and (height is not None):
        #    graph = adagenes.plot.generate_plots.generate_radarplot.generate_radar_plot\
        #        (dfs,names, "pathogenicity-scores-radar",width=width,height=height)
        #    return graph
        #else:
        #    return adagenes.plot.generate_plots.generate_radarplot.generate_radar_plot(dfs, names,
        #                                                                             "pathogenicity-scores-radar")
        return onkopus.onkopus_clients.PlotClient(genome_version="hg38").process_data(variant_data,
                                                                                      plot="multi_pathogenicity")
    elif plot_type == 'pathogenicity-scores-radar-categorical':
        #dfs = adagenes.plot.generate_data.generate_radarplot_data.generate_multiple_biomarker_radar_plot_data(variant_data)
        #names = adagenes.plot.generate_data.generate_biomarker_identifiers(variant_data)
        #df_cat = adagenes.plot.generate_data.generate_radarplot_data.generate_categorical_scores(dfs)
        #if (width is not None) and (height is not None):
        #    graph = adagenes.plot.generate_plots.generate_radarplot.generate_radar_plot(df_cat,names, "pathogenicity-scores-radar",width=width,height=height)
        #    return graph
        #else:
        #    return adagenes.plot.generate_plots.generate_radarplot.generate_radar_plot(dfs, names,
        #                                                                             "pathogenicity-scores-radar")
        return onkopus.onkopus_clients.PlotClient(genome_version="hg38").process_data(variant_data,plot="categorical_pathogenicity")
    elif (plot_type == "treatment-sunburst") \
            or (plot_type == "treatment-sunburst-cancer-type") \
            or (plot_type == "treatment-sunburst-match-type-drugs") \
            or (plot_type == "treatment-sunburst-match-type-drugs-all") \
            or (plot_type == "treatment-sunburst-match-type-drug-classes") \
            or (plot_type == "treatment-sunburst-response-type") \
            or (plot_type == "treatments-all-drug-class-drugs") \
            or (plot_type == "treatments-all-cancer-type") \
            or (plot_type == "treatments-all-sunburst-match-type-drug-classes-all") \
            or (plot_type == "treatments-all-sunburst-match-type-drugs-all") \
            or (plot_type == "treatments-all-sunburst-response-type") \
            or (plot_type == "treatments-all-patient-drugs") \
            or (plot_type == "treatments-all-patient-cancer-type") \
            or (plot_type == "treatments-all-patient-match-type-drug-classes") \
            or (plot_type == "treatments-all-patient-drug-class") \
            :
        return generate_sunburst_plot(variant_data, qid, plot_type, font_size=font_size, variant_type=mutation_type)
    elif plot_type == "chromosome-positions":
        ideogram_data = adagenes.generate_data.generate_chromosome_positions_data(variant_data, genome_version)
        return ideogram_data
    elif plot_type == "protein-data":
        graphJSON = onkopus.plot.generate_protein_plot_with_annotations(variant_data)
        return graphJSON
    elif plot_type == "pdb":
        if qid is not None:
            variant_data = variant_data[qid]
        graphJSON = onkopus.onkopus_clients.PDBClient(genome_version).process_data(variant_data)
        return graphJSON
    elif plot_type == "pdb_scannet":
        if qid is not None:
            graphJSON = onkopus.ScanNetBindingSiteClient(genome_version=genome_version).process_data(qid)
            return graphJSON
    elif plot_type == "pdb_openfold_wt":
        if qid is not None:
            variant_data = variant_data[qid]
        graphJSON = onkopus.onkopus_clients.PDBClient(genome_version).process_data(variant_data, plot=plot_type)
        return graphJSON
    elif plot_type == "pdb_openfold_mutated":
        if qid is not None:
            variant_data = variant_data[qid]
        graphJSON = onkopus.onkopus_clients.PDBClient(genome_version).process_data(variant_data, plot=plot_type)
        return graphJSON
    elif plot_type == "median_ge_per_tissue":
        graphJSON = op.GeneExpressionPlotClient().process_data(qid)
        return graphJSON

    return {}
