#!/bin/bash



#After coming from 03_filtering and running Method1.py,
#  Run Combine_run_results_script.py first!  ## this may be that now^^
if [ 1 == 1 ]; then
	#Move to the working directory, copy the start data into the working data directory. data_start needs to be in there.
	cd 04_Analysis/
	mkdir Figs/ data/

	# Here is where you load the rosetta:
	cp ../03_Filtering/Method1-Rosetta_I30_r10_s2_L1.csv data_start/Rosetta.csv

	cp data_start/* data/
	mkdir temp

	#Script begins:


	(head -1 data_start/Rosetta.csv | cut -f10- -d',' | tr ',' '\n' | awk -F'_' '
	BEGIN {
	    # Define custom sorting orders for treatments
	    order["UNTR"] = 1;
	    order["CMT"] = 2;
	    order["ABX3CMT"] = 3;
	    order["ABX10"] = 4;
	}
	{
	    # Extract the day from the field (e.g., d5, d30)
	    match($2, /d([0-9]+)/, arr);
	    day = arr[1];
	    treatment = $1;
	    # Output for sorting: day, custom treatment order, rest of the fields, original line
	    print day, order[treatment], $3, $4, $5, $0
	}' | sort -k1,1n -k2,2n -k3,3 -k4,4 -k5,5 | cut -d' ' -f6-) > data/Rosetta_sortOrder.tsv

	python3 utils/Sort_rosetta_columns.py data_start/Rosetta.csv data/Rosetta_sortOrder.tsv data/Rosetta.csv


	echo Pre-processing - improved taxonomy, remove outliers...
	python utils/Replace_rosetta_taxonomy.py data/Rosetta.csv /data/shoreline/athena/athena_v2_2z.tax data/Rosetta_improved_tax.csv  #here is where I change from day 0 to d-2
	python utils/Report_outlier_samples.py data/Rosetta_improved_tax.csv 500 data/outliers.txt #Filter samples with fewer than 500 reads
	python utils/Subset_rosetta_columns.py data/Rosetta_improved_tax.csv 0 data/outliers.txt data/Filt.csv


	### Now, if we would like to collapse some more stuff: ###
	python3 utils/Calculate_all_Rosetta_PW_edit_distances_and_corr_par.py data/Filt.csv 80 temp/ data/Filt_PW_edist_and_corr.tsv
	# [Rosetta.csv] [n_threads (-1 for all)] [temp_dir] [Out.tsv]

	python3 utils/Extract_clusters_edist_corr_connected_components.py data/Filt_PW_edist_and_corr.tsv 1 0.99 0 data/Filt_PW_edist_and_corr_1_0.99_0.tsv
	python3 utils/Extract_clusters_edist_corr_connected_components.py data/Filt_PW_edist_and_corr.tsv 1 0.99 1 data/Filt_PW_edist_and_corr_1_0.99_1.tsv

	awk '$3 < 10' data/Filt_PW_edist_and_corr.tsv > data/Filt_PW_edist_and_corr_lt10.tsv
	python3 utils/Plot_scatter_marginal.py data/Filt_PW_edist_and_corr_lt10.tsv 0 $'\t' 2 3 -1 1 0 'Edit Distance' 'Correlation' Figs/Filt_PW_edist_and_corr_lt10.png

	python3 utils/Plot_scatter_marginal.py data/Filt_PW_edist_and_corr.tsv 0 $'\t' 2 3 -1 1 0 'Edit Distance' 'Correlation' Figs/Filt_PW_edist_and_corr.png
	# python3 Plot_scatter_marginal.py [In.tsv] [0/1 Headers?] [delim] [ind-x] [ind-y] [ind-series] [log-x (0/1)] [log-y (0/1)] [xlabel] [ylabel] [Out.png]

	### ###



	echo Create condensed files for easy processing later...
	python utils/Condense_rosetta_columns.py data/Filt.csv data/Condensed_column_mapper_Animal+Sex.tsv 1 data/Filt-AS.csv
	python utils/Condense_rosetta_columns.py data/Filt.csv data/Condensed_column_mapper_Animal.tsv 1 data/Filt-A.csv

	python utils/Subset_rosetta_columns.py data/Filt-AS.csv 1 data/AS_cols_UNTR.txt data/Filt-AS_UNTR.csv
	python utils/Sort_rosetta_columns.py data/Filt-AS.csv data/AS_cols_sortOrder.txt data/Filt-AS_sorted.csv


	echo summarizing by taxonomy
	python utils/Summarize_by_tax.py data/Filt.csv 1 data/Filt_phylum.csv
	python utils/Summarize_by_tax.py data/Filt.csv 2 data/Filt_class.csv
	python utils/Summarize_by_tax.py data/Filt.csv 3 data/Filt_order.csv
	python utils/Summarize_by_tax.py data/Filt.csv 4 data/Filt_family.csv
	python utils/Summarize_by_tax.py data/Filt.csv 5 data/Filt_genus.csv
	python utils/Summarize_by_tax.py data/Filt.csv 6 data/Filt_species.csv
	cp data/Filt.csv data/Filt_ASV.csv


	echo getting sort orders
	python utils/Get_sort_order.py data/Filt-AS.csv 1 data/Filt-AS_sortOrder_phylum.txt
	python utils/Get_sort_order.py data/Filt-AS.csv 2 data/Filt-AS_sortOrder_class.txt
	python utils/Get_sort_order.py data/Filt-AS.csv 3 data/Filt-AS_sortOrder_order.txt
	python utils/Get_sort_order.py data/Filt-AS.csv 4 data/Filt-AS_sortOrder_family.txt
	python utils/Get_sort_order.py data/Filt-AS.csv 5 data/Filt-AS_sortOrder_genus.txt
	python utils/Get_sort_order.py data/Filt-AS.csv 6 data/Filt-AS_sortOrder_species.txt

	python utils/Calculate_alpha_diversity.py data/Filt.csv data/Filt_alpha_diversity.tsv
	
	
	python utils/Calculate_alpha_diversity.py data/Filt_species.csv data/Filt_species_alpha_diversity.tsv
	
	
	python utils/Calculate_nReads_samp.py data/Filt.csv data/Filt_nReads_samp.tsv

	python3 utils/Convert_Rosetta_to_fa.py data/Filt.csv data/Filt.fa

	for n in UNTR ABX10 ABX3CMT CMT W
	do
		python utils/Subset_rosetta_columns.py data/Filt-AS_sorted.csv 1 data/AS_cols_$n\.txt data/Filt-AS_sorted_$n\.csv
	done

	echo Finished pre-processing.






	####   FIGURE 1:   ####
	echo Fig 1D - Number of ASVs
	
	
	python utils/Plot_alpha_diversity_linegraph.py data/Filt_alpha_diversity.tsv 0 Figs/1D_alpha_diversity.png
	python utils/Plot_alpha_diversity_linegraph.py data/Filt_alpha_diversity.tsv 1 Figs/1D_alpha_diversity_legend.png
	
	
	echo Fig 1D - Number of species
	#(Number of species):
	python utils/Plot_alpha_diversity_linegraph.py data/Filt_species_alpha_diversity.tsv 0 Figs/Suppl_species_alpha_diversity.png  #move this down to suppl code block
	python utils/Plot_alpha_diversity_linegraph.py data/Filt_species_alpha_diversity.tsv 1 Figs/Suppl_species_alpha_diversity_legend.png
	
	
	python utils/Plot_nReads_samp_linegraph.py data/Filt_nReads_samp.tsv Figs/Suppl_nReads_samp.png  #move this down to suppl code block
	echo ''
	####   END FIG 1   ####







	####   FIGURE 2:   ####
	echo Figure 2 - Sites are different

	for n in ASV species genus
	do
		echo 'Generating PCoA for ' $n
		python utils/Generate_PCoA.py data/Filt_$n\.csv d-2,d1,d3,d5,d8,d10,d30,d60 1 80 data/Filt_PCoA_$n\.tsv data/Filt_PCoA_$n\_varRats.tsv
		
		echo 'Running permanova for ' $n
		python utils/Run_permanova_sex.py data/Filt_$n\.csv 80 data/permANOVA_sex_$n\.tsv
		python utils/Run_permanova_site.py data/Filt_$n\.csv 80 data/permANOVA_site_$n\.tsv
		
		echo 'Plotting venn diagrams for ' $n
		python utils/Plot_venn_variable.py data/Filt_$n\.csv 5 2 -2 -1 36 "Figs/Venn_baseline_${n}"
		convert -trim Figs/Venn_baseline_$n\_taxa.png Figs/Venn_baseline_$n\_taxa.png
		convert -trim Figs/Venn_baseline_$n\_abund.png Figs/Venn_baseline_$n\_abund.png
		convert Figs/Venn_baseline_$n\_taxa.png -bordercolor White -border 2x2 Figs/Venn_baseline_$n\_taxa.png
		convert Figs/Venn_baseline_$n\_abund.png -bordercolor White -border 2x2 Figs/Venn_baseline_$n\_abund.png
		python utils/Combine_images.py Figs/2A_$n\.png 1 Figs/Venn_baseline_$n\_{taxa,abund}.png
		rm Figs/Venn_baseline_$n\_{taxa,abund}.png
		
		python utils/Plot_jitter.py "data/Filt_${n}.csv" "${n}" 0 "Figs/2C_${n}.png"
		echo ''
	done


	python utils/Plot_PCA_wEllipses_baseline.py data/Filt_PCoA_genus.tsv data/Filt_PCoA_genus_varRats.tsv data/permANOVA_site_genus.tsv '' '' '' 0 -0.4 0.25 -0.6 0.4 Figs/2B_genus
	python utils/Plot_PCA_wEllipses_baseline.py data/Filt_PCoA_species.tsv data/Filt_PCoA_species_varRats.tsv data/permANOVA_site_species.tsv '' '' '' 0 -0.5 0.2 -0.3 0.35 Figs/2B_species
	python utils/Plot_PCA_wEllipses_baseline.py data/Filt_PCoA_ASV.tsv data/Filt_PCoA_ASV_varRats.tsv data/permANOVA_site_ASV.tsv '' '' '' 0 -0.5 0.5 -0.25 0.25 Figs/2B_ASV


	echo ''
	
	
#fig2 scratchwork:
for n in ASV species genus
do
	python utils/Plot_jitter.py "data/Filt_${n}.csv" "${n}" 0 "Figs/2C_${n}.png"
done





	####   END FIG 2   ####



	####   FIGURE 3:   ####
	echo Figure 3 - Sites remain different
	echo processing #(move above?) - wait till we're 100% sure nothing else is going to change - maybe move 'preprocessing' steps to where they're first needed?
	python utils/Subset_rosetta_columns.py data/Filt-AS.csv 1 data/AS_cols_UNTR_LJ.txt data/Filt-AS_UNTR_LJ.csv
	python utils/Subset_rosetta_columns.py data/Filt-AS.csv 1 data/AS_cols_UNTR_GR.txt data/Filt-AS_UNTR_GR.csv
	python utils/Get_sort_order.py data/Filt-AS_UNTR.csv 6 data/Filt-AS_UNTR_sortOrder_species.txt

	echo Figure 3-A...
	python utils/Plot_stacked_barplot.py data/Filt-AS_UNTR_LJ.csv 6 0.03 'La Jolla' data/Filt-AS_UNTR_sortOrder_species.txt 0 1 1 Figs/3A_LJ.png
	python utils/Plot_stacked_barplot.py data/Filt-AS_UNTR_GR.csv 6 0.03 'Groton' data/Filt-AS_UNTR_sortOrder_species.txt 0 1 0 Figs/3A_GR.png

	###   Temporal Jitter Plots (Mutivaculum, Streptomyces, L. murinus)   ###
	echo Figure 3-B...
	python utils/Plot_jitter_temporal.py data/Filt_genus.csv UNTR Muribaculum Figs/3B_Muribaculum.png
	python utils/Plot_jitter_temporal.py data/Filt_genus.csv UNTR Streptomyces Figs/3B_Streptomyces.png
	python utils/Plot_jitter_temporal.py data/Filt_species.csv UNTR Lactobacillus_murinus Figs/3B_Lactobacillus_murinus.png

	echo ''
	####   END FIG 3   ####





	#Do this at the phylum level (index 1)
	####   FIGURE 4:   ####
	echo Figure 4 - CMT best at converging composition between sites - stacked barplot of top 11 most abundant
	for n in UNTR ABX10 ABX3CMT CMT
	do
		echo "Beginning Figure 4 - ${n}"
		python utils/Plot_stacked_barplot_topN.py data/Filt-AS_sorted_$n\.csv 6 11 "$n" data/Filt-AS_sortOrder_species.txt 0 0 0 Figs/4A_$n\.png
		echo "end Figure 4 - ${n}"
		echo ""
	done
	python utils/Plot_stacked_barplot_topN.py data/Filt-AS_sorted_CMT.csv 6 12 "" data/Filt-AS_sortOrder_species.txt 0 0 1 Figs/4A_legend.png

	echo ''
	####   END FIG 4   ####

	for n in UNTR ABX10 ABX3CMT CMT
	do
		python utils/Plot_stacked_barplot_topN.py data/Filt-AS_sorted_$n\.csv 1 11 "$n" data/Filt-AS_sortOrder_phylum.txt 0 0 0 Figs/4A_$n\_phylum.png
	done
	python utils/Plot_stacked_barplot_topN.py data/Filt-AS_sorted_CMT.csv 1 11 "" data/Filt-AS_sortOrder_phylum.txt 0 0 1 Figs/4A_legend_phylum.png

	for n in UNTR ABX10 ABX3CMT CMT
	do
		python utils/Plot_stacked_barplot_topN.py data/Filt-AS_sorted_$n\.csv 2 11 "$n" data/Filt-AS_sortOrder_class.txt 0 0 0 Figs/4A_$n\_class.png
	done
	python utils/Plot_stacked_barplot_topN.py data/Filt-AS_sorted_CMT.csv 2 11 "" data/Filt-AS_sortOrder_class.txt 0 0 1 Figs/4A_legend_class.png

	for n in UNTR ABX10 ABX3CMT CMT
	do
		python utils/Plot_stacked_barplot_topN.py data/Filt-AS_sorted_$n\.csv 3 11 "$n" data/Filt-AS_sortOrder_order.txt 0 0 0 Figs/4A_$n\_order.png
	done
	python utils/Plot_stacked_barplot_topN.py data/Filt-AS_sorted_CMT.csv 3 11 "" data/Filt-AS_sortOrder_order.txt 0 0 1 Figs/4A_legend_order.png

	for n in UNTR ABX10 ABX3CMT CMT
	do
		python utils/Plot_stacked_barplot_topN.py data/Filt-AS_sorted_$n\.csv 4 11 "$n" data/Filt-AS_sortOrder_family.txt 0 0 0 Figs/4A_$n\_family.png
	done
	python utils/Plot_stacked_barplot_topN.py data/Filt-AS_sorted_CMT.csv 4 11 "" data/Filt-AS_sortOrder_family.txt 0 0 1 Figs/4A_legend_family.png

	for n in UNTR ABX10 ABX3CMT CMT
	do
		python utils/Plot_stacked_barplot_topN.py data/Filt-AS_sorted_$n\.csv 5 11 "$n" data/Filt-AS_sortOrder_genus.txt 0 0 0 Figs/4A_$n\_genus.png
	done
	python utils/Plot_stacked_barplot_topN.py data/Filt-AS_sorted_CMT.csv 5 11 "" data/Filt-AS_sortOrder_genus.txt 0 0 1 Figs/4A_legend_genus.png
	
	
	python utils/analyze_cmt_shifts.py
	python utils/analyze_bc_stability_within.py data/Filt.csv Figs/BC_boxplots_within.png data/BC_boxplots_stats_within.tsv
	python utils/analyze_bc_stability_consecutives.py data/Filt.csv Figs/4B_BC_boxplots_consecutives.png data/BC_boxplots_stats_consecutives.tsv


	for f in consecutives within; do
		echo "$f T-test results for BC dissimilarity vs UNTR (d60)"
		head -1 "data/BC_boxplots_stats_$f.tsv" | cut -f1,2,3,4,5
		grep 'd60' "data/BC_boxplots_stats_$f.tsv" | cut -f1,2,3,4,5
		echo ''
	done




	####   FIGURE 5:   ####
	echo Figure 5 - CMT best at converging composition between sites - BC dissimilarity and PCoAs

	python utils/Calculate_BC_distance_par.py data/Filt.csv data/Filt_BCs.tsv 80 temp  #PCoA generation code already did this work...
	sort -k2,2n data/Filt_BCs.tsv > temp.txt
	mv temp.txt data/Filt_BCs.tsv
	
	python utils/Plot_BC_facetgrid_wBaseline.py data/Filt_BCs.tsv Figs/5A.png

	python utils/Plot_PCA_wEllipses_byday.py data/Filt_PCoA_ASV.tsv data/Filt_PCoA_ASV_varRats.tsv data/permANOVA_site_ASV.tsv d60 1 -0.6 0.75 -0.75 0.65 Figs/5B
	python utils/Plot_PCA_wEllipses_baseline.py data/Filt_PCoA_ASV.tsv data/Filt_PCoA_ASV_varRats.tsv data/permANOVA_site_ASV.tsv '' '' '' 1 -0.6 0.75 -0.75 0.65 Figs/5B
	rm Figs/5B_UNTR_d60.png

	echo ''
	####   END FIG 5   ####







	####   FIGURE 6:   ####
	echo Figure 6 - CMT best at transferring Donor microbes

	echo processing..
	python utils/Calculate_pct_DonorASVs.py data/Filt.csv data/Filt_pct_DonorASVs.tsv
	python utils/Calculate_pct_DonorASVs_nReads.py data/Filt.csv data/Filt_pct_DonorASVs_nReads.tsv

	echo plotting
	python utils/Plot_pct_DonorASVs_linegraph.py data/Filt_pct_DonorASVs.tsv Figs/6A_nASVs.png
	python utils/Plot_pct_DonorASVs_linegraph_nReads.py data/Filt_pct_DonorASVs_nReads.tsv Figs/6A_nReads.png

	for n in UNTR CMT ABX3CMT ABX10
	do
		python utils/Plot_venn_variable.py data/Filt.csv 5 1.2 60 $n 28 Figs/Venn_d60_$n
		convert -trim Figs/Venn_d60_$n\_abund.png Figs/Venn_d60_$n\_abund.png
		convert -trim Figs/Venn_d60_$n\_taxa.png Figs/Venn_d60_$n\_taxa.png
		convert Figs/Venn_d60_$n\_abund.png -bordercolor White -border 2x2 Figs/Venn_d60_$n\_abund.png
		convert Figs/Venn_d60_$n\_taxa.png -bordercolor White -border 2x2 Figs/Venn_d60_$n\_taxa.png
		python utils/Combine_images.py Figs/6B_$n\.png 1 Figs/Venn_d60_$n\_{taxa,abund}.png
		rm Figs/Venn_d60_$n\_{taxa,abund}.png
	done

	
	echo 'Suppl T-Tests for X/ASVs and abundance - CMT and ABX3CMT against UNTR'
	#Figure 6 / suppl: 
	python utils/analyze_donor_stats.py data/Filt.csv

	echo ''
	####   END FIG 6   ####






	####   FIGURE 7:   ####
	echo 'Figure 7 - lactobacillus'
	python utils/Plot_genus_linegraphs.py data/Filt.csv 'Lactobacillus' tempfile.tsv 0 Figs/7A_Genus_Lactobacillus.png
	python utils/Plot_genus_linegraphs.py data/Filt.csv 'Lactobacillus' tempfile.tsv 1 Figs/7A_Genus_Lactobacillus_legend.png
	for n in reuteri #murinus johnsonii reuteri acidophilus animalis amylovorus
	do
		python utils/Plot_species_linegraph_Donor_v_not.py data/Filt.csv "Lactobacillus_${n}" tempfile.tsv data/Filt_Donor_ASVs.txt 0 "Figs/7B_Lactobacillus_${n}_donorpct.png"
	done
	python utils/Plot_species_linegraph_Donor_v_not.py data/Filt.csv "Lactobacillus_reuteri" tempfile.tsv data/Filt_Donor_ASVs.txt 1 "Figs/7B_Lactobacillus_species_donorpct_legend.png"
	####   END FIG 7   ####

	echo ''

fi







########## Antibiotic Resistance ##########


#########   Antibiotic resistant ASV detection (not necessary to re-run w/ new Rosetta):
if [ 1 == 0 ]; then

	echo 'Figure 8 - Operon extraction and genome detection'
	#Download all genomes, Make blast DB
	#Split into chunks
	python utils/Chunk_fasta_file_par.py genomes/BlastDB/All_genomes.fasta genomes/Chunks/ 250
	
	#Operon sequence extraction and edit distance calculations:
	
	python utils/Extract_StrainID_regions_par_mem.py genomes/Chunks/ 0 genomes/Chunks_out/
	cat genomes/Chunks_out/* > genomes/All_amplicons_raw.fa
	awk '/^>/ {print; next} {print substr($0, 21, length($0)-38)}' genomes/All_amplicons_raw.fa > genomes/All_amplicons_noprimers.fa 
	
	#Filter to 1700 - 3200 BPs
	python3 utils/Filter_fasta_by_length.py genomes/All_amplicons_noprimers.fa 1700 3200 genomes/All_amplicons.fa
	
	# And the BLAST search for assigning genomes as AR/not AR:
	ulimit -n 9999
	date; nice blastn -query ARGs/CARD_combined.fasta -db genomes/BlastDB/All_genomes -num_threads 90 -out ARGs/CARD_combined_results.txt -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qlen slen"; date;
	date; nice blastn -query ARGs/resFinder.fasta -db genomes/BlastDB/All_genomes -num_threads 90 -out ARGs/resFinder_results.txt -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qlen slen"; date;
	cat ARGs/resFinder_results.txt ARGs/CARD_combined_results.txt > ARGs/All_results.txt

	python ARGs/Report_ARG_genomes.py ARGs/All_results.txt ARGs/ARG_results.txt
	cut -f2 'ARGs/ARG_results.txt' | sort | uniq -c | sort -nr | sed 's/^[ \t]*//;s/[ \t]*$//' | tr ' ' '\t' > ARGs/ARG_results_counts.tsv
	#fi




	echo 'Figure 8 - ARGs: edit distance calculations'
	#########   Antibiotic resistant ASV detection (IS necessary to re-run w/ new Rosetta):
	mkdir temp_dir

	echo 'Calculating edit distances'

	python utils/Calculate_all_edit_distances_par_mem.py genomes/All_amplicons.fa data/Filt.fa 70 temp_dir genomes/Filt_amplicons.ijk
	# here we get a cat error from the os.system command in ^^: too many files. would need to run ulimit -n 99999999 or something, or:

	echo 'Concatenating output and finding best matches'

	cat temp_dir/* > genomes/Filt_amplicons_noprimers.ijk  #need to fix --fix what?seems fixed?
	./utils/Find_best_matches.sh genomes/Filt_amplicons_noprimers.ijk > genomes/Filt_amplicons_noprimers_best.ijk

	rm -r temp_dir
	#fi


	echo 'Figure 8 - ARGs: match_counting'
	echo 'Identifying AR ASVs'

	#Finally, identification of AR ASVs:  #some steps here will need to be filled in when doing final re-creation(s)/automations  ..ya think? slightly improved
	python utils/Identify_AR_ASVs.py ARGs/ARG_results_counts.tsv data/Filt.fa genomes/Filt_amplicons_noprimers_best.ijk 98 ARGs/ARG_ASVs_x1_best

	sort "ARGs/ARG_ASVs_x1_best_98.0.tsv" | uniq > temp.txt;
	mv temp.txt "ARGs/ARG_ASVs_x1_best_98.0.tsv";

	./utils/Count_AR_ASV_matches.sh "ARGs/ARG_ASVs_x1_best_98.0.tsv" > "ARGs/ARG_ASVs_x1_best_98.0_counts.tsv"
	(head -n 1 "ARGs/ARG_ASVs_x1_best_98.0_counts.tsv" && tail -n +2 "ARGs/ARG_ASVs_x1_best_98.0_counts.tsv" | sort -t$'\t' -k2,2n -k3,3n) > temp.txt;
	mv temp.txt "ARGs/ARG_ASVs_x1_best_98.0_counts.tsv";
	tail -n +2 "ARGs/ARG_ASVs_x1_best_98.0_counts.tsv" | awk -F'\t' '$2 != 0 && $3 == 0 {print $1}' | sort | uniq > "ARGs/ARG_ASVs_x1_best_98.0_ASVs_ARG.txt"
	tail -n +2 "ARGs/ARG_ASVs_x1_best_98.0_counts.tsv" | awk -F'\t' '$2 != 0 && $3 != 0 {print $1}' | sort | uniq > "ARGs/ARG_ASVs_x1_best_98.0_ASVs_Ambiguous.txt"
	tail -n +2 "ARGs/ARG_ASVs_x1_best_98.0_counts.tsv" | awk -F'\t' '$2 == 0 && $3 != 0 {print $1}' | sort | uniq > "ARGs/ARG_ASVs_x1_best_98.0_ASVs_non-ARG.txt"

	#python utils/03_Plot_better_linegraphs.py data/Filt-AS.csv "ARGs/ARG_ASVs_x1_best_98.0_ASVs_ARG.txt" 0 "AR ASVs" 0 "Figs/ARG_ASVs_x1_best_98.0_ASVs.png"


	cat ARGs/ARG_ASVs_x1_best_98.0_ASVs_{ARG,Ambiguous,non-ARG}.txt > ARGs/All_matched_ASVs.txt
	tail -n +2 data/Filt.csv | cut -d',' -f1 > ARGs/All_ASVs.txt

	grep -Fvx -f ARGs/All_matched_ASVs.txt ARGs/All_ASVs.txt > ARGs/ARG_ASVs_x1_best_98.0_ASVs_Unmatched.txt

fi

echo 'Calculating and plotting figure 8'



####   FIGURE 8:   ####

grep -f 'ARGs/ARG_ASVs_x1_best_98.0_ASVs_ARG.txt' data/Filt.csv > temp1.txt  #Take just the ARG-positive taxa:
head -1 data/Filt.csv > temp2.txt
cat temp{2,1}.txt > data/Filt_ARG_ASVs.csv
rm temp{2,1}.txt

python utils/Summarize_by_tax.py data/Filt_ARG_ASVs.csv 6 data/Filt_ARG_ASVs_species.csv  #summarize by species

python utils/Get_sample_sums.py data/Filt.csv data/Filt_sample_sums.tsv  #normalize and convert to tabular form
python utils/Normalize_rosetta.py data/Filt_ARG_ASVs_species.csv data/Filt_sample_sums.tsv data/Filt_ARG_ASVs_species_normalized.csv
python utils/Convert_rosetta_to_linegraph_format.py data/Filt_ARG_ASVs_species_normalized.csv data/Filt_ARG_ASVs_species_normalized_linegraph.tsv

for n in ABX3CMT ABX10  #subsets to highest 10 by average relative abundance calculated this way ...
do
	python utils/Plot_ARG_ASV_species_linegraph.py data/Filt_ARG_ASVs_species_normalized_linegraph.tsv $n LJ 0.12 0 Figs/Filt_ARG_ASVs_species_normalized_linegraph_$n\_LJ.png
	python utils/Plot_ARG_ASV_species_linegraph.py data/Filt_ARG_ASVs_species_normalized_linegraph.tsv $n GR 0.12 0 Figs/Filt_ARG_ASVs_species_normalized_linegraph_$n\_GR.png
	
	python utils/Plot_ARG_ASV_species_linegraph.py data/Filt_ARG_ASVs_species_normalized_linegraph.tsv $n LJ 0.12 1 Figs/Filt_ARG_ASVs_species_normalized_linegraph_$n\_LJ_legend.png
	python utils/Plot_ARG_ASV_species_linegraph.py data/Filt_ARG_ASVs_species_normalized_linegraph.tsv $n GR 0.12 1 Figs/Filt_ARG_ASVs_species_normalized_linegraph_$n\_GR_legend.png
done

#python utils/Plot_ARG_ASV_species_linegraph.py data/Filt_ARG_ASVs_species_normalized_linegraph.tsv ABX3CMT LJ 1 Figs/Filt_ARG_ASVs_species_normalized_linegraph_legend_GR.png
#python utils/Plot_ARG_ASV_species_linegraph.py data/Filt_ARG_ASVs_species_normalized_linegraph.tsv ABX10 1 Figs/Filt_ARG_ASVs_species_normalized_linegraph_legend_check.png




#8B:

awk -F, 'BEGIN {OFS=","} {printf $1; for (i = 10; i <= NF; i++) printf OFS$i; print ""}' data/Filt.csv > data/Filt_nometa.csv  #remove the metadata, just keep matrix

for n in Unmatched ARG Ambiguous non-ARG
do
	python utils/Sum_AR_vs_not.py data/Filt_nometa.csv "ARGs/ARG_ASVs_x1_best_98.0_ASVs_${n}.txt" "ARGs/AR_vs_not_98.0_${n}_abund.csv";
	python utils/Sum_AR_vs_not_numASVs.py data/Filt_nometa.csv "ARGs/ARG_ASVs_x1_best_98.0_ASVs_${n}.txt" "ARGs/AR_vs_not_98.0_${n}_ntaxa.csv";
done

python utils/Combine_ARG_totals.py

for n in ABX10 ABX3CMT
do
	python utils/Plot_ARG_categories.py data/combined_ARG_counts_abund.csv "${n}" "Figs/AR_pct_${n}.png"
done

####   END FIG 8   ####





#to here = CHECK



####   FIGURE 9:   ####
echo 'RNA-Seq plots..'

python3 ../0X_RNA-Seq/PCA/Plot_PCA_wEllipses_byday_wSig.py ../0X_RNA-Seq/PCA/tpm_pca_2d.tsv ../0X_RNA-Seq/PCA/tpm_pca_2d_varrats.tsv d2,d11,d61 1 ../0X_RNA-Seq/PCA/tpm_wsig ../0X_RNA-Seq/pyPERMANOVA/sites.tsv
./../0X_RNA-Seq/PCA/Combine_images_command.sh ../0X_RNA-Seq/PCA/tpm_wsig ../0X_RNA-Seq/PCA/tpm_wsig.png


####   END FIG 9   ####






### ### ###  #############  ### ### ###
### ### ###  Supplemental:  ### ### ###
### ### ###  #############  ### ### ### 



echo 'Reviewer-suggested supplemental figure:'

python utils/Calculate_BC_distance_par.py data/Filt_genus.csv data/Filt_genus_BCs.tsv 80 temp  #PCoA generation code already did this work...
sort -k2,2n data/Filt_genus_BCs.tsv > temp.txt
mv temp.txt data/Filt_genus_BCs.tsv

python utils/Plot_BC_facetgrid_wBaseline.py data/Filt_genus_BCs.tsv Figs/5A_genus.png



python utils/Calculate_BC_distance_par.py data/Filt_species.csv data/Filt_species_BCs.tsv 80 temp  #PCoA generation code already did this work...
sort -k2,2n data/Filt_species_BCs.tsv > temp.txt
mv temp.txt data/Filt_species_BCs.tsv

python utils/Plot_BC_facetgrid_wBaseline.py data/Filt_species_BCs.tsv Figs/5A_species.png






####   FIGURE X:   ####
####   END FIG X   ####

#Extract all subregions from https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8544895/, added V1-V9 (manually)



echo 'SUBREGION PLOTS - supplemental'

mkdir -p data/Subregions/Input
python utils/Convert_Rosetta_to_fa.py data/Filt.csv data/Filt.fa
python utils/Add_forward_primer.py data/Filt.fa AGAGTTTGATCCTGGCTCAG data/Subregions/Input/Filt_wV1.fa 

#What does this ^^ even do? adds forward primer to ASVs? Why doesn't it add the reverse primers?

cut -f1,4,5 'data_start/Primer_pairs.tsv' | tr -d ' -' > data/Primer_pairs.tsv
FILE="data/Primer_pairs.tsv"
while IFS=$'\t' read -r ID Forward Reverse; do
    # Execute the series of commands for each row
    echo "Processing $ID"
    mkdir data/Subregions/$ID/
    python utils/Extract_StrainID_subregions_par_mem.py data/Subregions/Input "$Forward" "$Reverse" 0 "data/Subregions/$ID/"
    python utils/Summarize_Rosetta_by_subregion.py data/Filt.csv "data/Subregions/$ID/Filt_wV1.fa_amplicons.fa" "data/Filt_${ID}.csv"
    echo "Generating PCoA for $ID"
    python utils/Generate_PCoA.py "data/Filt_${ID}.csv" d-2,d1,d3,d5,d8,d10,d30,d60 1 90 "data/Filt_PCoA_${ID}.tsv" "data/Filt_PCoA_${ID}_varRats.tsv"
    echo "Running permanova"
    python utils/Run_permanova_sex.py "data/Filt_${ID}.csv" 80 "data/permANOVA_sex_${ID}.tsv"
    python utils/Run_permanova_site.py "data/Filt_${ID}.csv" 80 "data/permANOVA_site_${ID}.tsv"
    echo "Plotting..."
    python utils/Plot_PCA_wEllipses_baseline.py "data/Filt_PCoA_${ID}.tsv" "data/Filt_PCoA_${ID}_varRats.tsv" "data/permANOVA_site_${ID}.tsv" '' '' '' 0 -1 -1 -1 -1 "Figs/Filt_PCoA_${ID}"

    python utils/Plot_venn_baseline.py "data/Filt_${ID}.csv" "Figs/Venn_baseline_${ID}"
    
    python utils/Plot_venn_variable.py "data/Filt_${ID}.csv" 5 2 -2 -1 28 "Figs/Filt_${ID}_venn"
    convert -trim "Figs/Venn_baseline_${ID}_taxa.png" "Figs/Venn_baseline_${ID}_taxa.png"
    convert -trim "Figs/Venn_baseline_${ID}_abund.png" "Figs/Venn_baseline_${ID}_abund.png"
    python utils/Combine_images.py "Figs/Venn_baseline_${ID}.png" 1 Figs/Venn_baseline_${ID}_{taxa,abund}.png
    rm Figs/Venn_baseline_${ID}_{taxa,abund}.png
    python utils/Plot_jitter.py "data/Filt_${ID}.csv" "$ID" 0 "Figs/Jitter_top10_${ID}.png"

done < "$FILE"




#FILE="data/Primer_pairs.tsv"
#while IFS=$'\t' read -r ID Forward Reverse; do
#    python utils/Plot_PCA_wEllipses_baseline.py "data/Filt_PCoA_${ID}.tsv" "data/Filt_PCoA_${ID}_varRats.tsv" "data/permANOVA_site_${ID}.tsv" '' '' '' 0 -1 -1 -1 -1 "Figs/Filt_PCoA_${ID}"
#done < "$FILE"

python utils/Plot_PCA_wEllipses_baseline.py "data/Filt_PCoA_ASV.tsv" "data/Filt_PCoA_ASV_varRats.tsv" "data/permANOVA_site_ASV.tsv" '' '' '' 0 -1 -1 -1 -1 "Figs/Filt_PCoA_ASV"





python utils/Run_permanova_sex.py "data/Filt_V6V8.csv" 80 "data/permANOVA_sex_V6V8.tsv"
python utils/Run_permanova_site.py "data/Filt_V6V8.csv" 80 "data/permANOVA_site_V6V8.tsv"
echo "Plotting..."
python utils/Plot_PCA_wEllipses_baseline.py "data/Filt_PCoA_V6V8.tsv" "data/Filt_PCoA_V6V8_varRats.tsv" "data/permANOVA_site_V6V8.tsv" '' '' '' 0 -0.5 0.5 -0.3 0.3 "Figs/Filt_PCoA_V6V8"

python utils/Plot_venn_baseline.py "data/Filt_V6V8.csv" "Figs/Venn_baseline_V6V8"

python utils/Plot_venn_variable.py "data/Filt_V6V8.csv" 5 2 -2 -1 28 "Figs/Filt_V6V8_venn"
convert -trim "Figs/Venn_baseline_V6V8_taxa.png" "Figs/Venn_baseline_V6V8_taxa.png"
convert -trim "Figs/Venn_baseline_V6V8_abund.png" "Figs/Venn_baseline_V6V8_abund.png"
python utils/Combine_images.py "Figs/Venn_baseline_V6V8.png" 1 Figs/Venn_baseline_V6V8_{taxa,abund}.png
rm Figs/Venn_baseline_V6V8_{taxa,abund}.png
python utils/Plot_jitter.py "data/Filt_V6V8.csv" "V6V8" 0 "Figs/Jitter_top10_V6V8.png"





# supplement to 3B:
python utils/Plot_jitter_temporal.py data/Filt_genus.csv UNTR Muribaculum Figs/Suppl_3B_Muribaculum_UNTR.png
python utils/Plot_jitter_temporal.py data/Filt_genus.csv CMT Muribaculum Figs/Suppl_3B_Muribaculum_CMT.png
python utils/Plot_jitter_temporal.py data/Filt_genus.csv ABX3CMT Muribaculum Figs/Suppl_3B_Muribaculum_ABX3CMT.png
python utils/Plot_jitter_temporal.py data/Filt_genus.csv ABX10 Muribaculum Figs/Suppl_3B_Muribaculum_ABX10.png
###





if [ 1 == 0 ]; then
	####   FIGURE 2:   ####
	echo Figure 2 - Sites are different

	for n in ASV species genus
	do
		echo 'Generating PCoA for ' $n
		python utils/Generate_PCoA.py data/Filt_$n\.csv d-2,d1,d3,d5,d8,d10,d30,d60 1 80 data/Filt_PCoA_$n\.tsv data/Filt_PCoA_$n\_varRats.tsv
		
		echo 'Running permanova'
		python utils/Run_permanova_sex.py data/Filt_$n\.csv 80 data/permANOVA_sex_$n\.tsv
		python utils/Run_permanova_site.py data/Filt_$n\.csv 80 data/permANOVA_site_$n\.tsv
		
		echo 'Plotting...'
		python utils/Plot_venn_variable.py data/Filt_$n\.csv 5 2 -2 -1 36 "Figs/Venn_baseline_${n}"
		convert -trim Figs/Venn_baseline_$n\_taxa.png Figs/Venn_baseline_$n\_taxa.png
		convert -trim Figs/Venn_baseline_$n\_abund.png Figs/Venn_baseline_$n\_abund.png
		convert Figs/Venn_baseline_$n\_taxa.png -bordercolor White -border 2x2 Figs/Venn_baseline_$n\_taxa.png
		convert Figs/Venn_baseline_$n\_abund.png -bordercolor White -border 2x2 Figs/Venn_baseline_$n\_abund.png
		python utils/Combine_images.py Figs/2A_$n\.png 1 Figs/Venn_baseline_$n\_{taxa,abund}.png
		rm Figs/Venn_baseline_$n\_{taxa,abund}.png
		
		python utils/Plot_jitter.py "data/Filt_${n}.csv" "${n}" 0 "Figs/2C_${n}.png"
		echo ''
	done


	python utils/Plot_PCA_wEllipses_baseline.py data/Filt_PCoA_genus.tsv data/Filt_PCoA_genus_varRats.tsv data/permANOVA_site_genus.tsv '' '' '' 0 -0.4 0.25 -0.6 0.4 Figs/2B_genus
	python utils/Plot_PCA_wEllipses_baseline.py data/Filt_PCoA_species.tsv data/Filt_PCoA_species_varRats.tsv data/permANOVA_site_species.tsv '' '' '' 0 -0.5 0.2 -0.3 0.35 Figs/2B_species
	python utils/Plot_PCA_wEllipses_baseline.py data/Filt_PCoA_ASV.tsv data/Filt_PCoA_ASV_varRats.tsv data/permANOVA_site_ASV.tsv '' '' '' 0 -0.5 0.2 -0.25 0.27 Figs/2B_ASV


	echo ''
	####   END FIG 2   ####
fi











# Additional Genus linegraphs depicting species for which the mice were SPF:
for n in Candidatus_Arthromitus Helicobacter Salmonella
do
	python utils/Plot_genus_linegraphs.py data/Filt.csv "${n}" tempfile.tsv 0 "Figs/Genus_${n}.png"
	python utils/Plot_genus_linegraphs.py data/Filt.csv "${n}" tempfile.tsv 1 "Figs/Genus_${n}_legend.png"
done




## full ARG plot

for n in UNTR CMT ABX10 ABX3CMT
do
	python utils/Plot_ARG_categories.py data/combined_ARG_counts_abund.csv "${n}" "Figs/AR_pct_abund_${n}.png"
done

for n in UNTR CMT ABX10 ABX3CMT
do
	python utils/Plot_ARG_categories.py data/combined_ARG_counts_ntaxa.csv "${n}" "Figs/AR_pct_ntaxa_${n}.png"
done



#Factor analysis:
python3 utils/Plot_permANOVA_directly_site.py data/permANOVA_site_ASV.tsv Figs/permANOVA_site_ASV.png
python3 utils/Plot_permANOVA_directly_sex.py data/permANOVA_sex_ASV.tsv Figs/permANOVA_sex_ASV.png





#Individual mouse plots (may not make it to pub):
awk -F, 'BEGIN {OFS=","} {printf $1; for (i = 10; i <= NF; i++) printf OFS$i; print ""}' data/Filt_species.csv > data/Filt_species_nometa.csv
python3 utils/Plot_stacked_barplot_topN_bymouse.py data/Filt_species_nometa.csv Figs/bymouse_grp --global_top_n 20 --by_group
python3 utils/Plot_stacked_barplot_topN_bymouse.py data/Filt_species_nometa.csv Figs/bymouse --global_top_n 20
python3 utils/Plot_stacked_barplot_topN_bymouse.py data/Filt_species_nometa.csv Figs/bymouse_checkdiff











#Supplemental wilcoxon rank results:: change topN to 100000000 in Plot_jitter.py, then:
for n in ASV species genus
do
	python utils/Create_wilcoxon_supplemental_table.py "data/Filt_${n}.csv" "${n}" "data/Wilcoxon_table_${n}.tsv"
	echo ''
done




####   END SUPPLEMENTAL  ####










