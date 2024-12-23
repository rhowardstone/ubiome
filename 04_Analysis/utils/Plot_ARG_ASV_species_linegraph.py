import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sys
from matplotlib import cm
from scipy import stats

if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("Error - usage:\n >>> python Plot_ARG_ASV_species_linegraph.py [In.tsv] [group] [site] [ymax] [0/1 toLegend?] [Out.png]\n")
        print("\t[site] should be either 'LJ' or 'GR'\n")
        exit()
    in_fname, group, site, ymax, toLegend, out_fname = sys.argv[1:]
    ymax = float(ymax)

    if site not in ['LJ', 'GR']:
        print("Error: site must be either 'LJ' or 'GR'")
        exit()

    data_unfiltered = pd.read_csv(in_fname, sep="\t", header=None, 
                       names=["Group", "Day", "Site", "Category", "Value"])

    # Filter data for the specified group and site
    data = data_unfiltered[(data_unfiltered['Group'] == group) & (data_unfiltered['Site'] == site)]

    # --- 1) Do T-tests on **all** categories first --- #
    if toLegend == '0':
        # Conduct T-tests for each species (Category) comparing day 8 to day 0
        day0_data = data[data['Day'] == -2]
        day8_data = data[data['Day'] == 8]

        significant_species = []
        results = []

        for category in data['Category'].unique():
            day0_values = day0_data[day0_data['Category'] == category]['Value']
            day8_values = day8_data[day8_data['Category'] == category]['Value']

            # Only run t-test if we have at least 2 data points in each group
            if len(day0_values) > 1 and len(day8_values) > 1:
                t_stat, p_val = stats.ttest_ind(day8_values, day0_values)
                is_significant = p_val <= 0.05

                results.append({
                    'Category': category,
                    'T-Statistic': t_stat,
                    'P-Value': p_val,
                    'Significant': is_significant
                })

                if is_significant:
                    significant_species.append(f"{category} (p={p_val:.4e})")

        # Save results to a CSV file
        results_df = pd.DataFrame(results)
        results_df.to_csv(f"ARG_d8_t_test_results_{group}_{site}.csv", index=False)

        # Print summary of significant species
        print(f"Group {group}, site {site}")
        print(f"Number of significant species (Day 8 vs Day 0): {len(significant_species)} out of {len(data['Category'].unique())}")
        print("Significant species:", ", ".join(significant_species))

    # --- 2) Determine Top 10 most abundant categories (summed across all days) --- #
    # (You can swap .sum() with .mean() or any metric you prefer.)
    category_sums = data_unfiltered.groupby('Category')['Value'].sum()
    top_10_categories = category_sums.nlargest(10).index

    # --- 3) Filter the data for **plotting** only to those Top 10 categories --- #
    plot_data = data[data['Category'].isin(top_10_categories)]

    # Adjusted plot for line graph
    plot_data['Day'] = plot_data['Day'].astype(str)
    sns.set(style="whitegrid")

    color_cycle = [cm.tab10(i) for i in range(20)]
    plt.figure(figsize=(10, 6))
    ax = plt.gca()

    # Use plot_data instead of data
    n = 0
    for category, group_data in plot_data.groupby("Category"):
        sns.lineplot(
            data=group_data, x="Day", y="Value", 
            label=category, errorbar=None, 
            color=color_cycle[n], linewidth=2.5
        )
        n += 1

    # Set x-ticks in the order you want (make sure they align with the unique Day values you have)
    day_order = ["-2", "1", "3", "5", "8", "10", "30", "60"]
    plt.xticks(ticks=range(len(day_order)), labels=day_order)

    for label in ax.get_yticklabels():
        label.set_fontweight('bold')
        label.set_fontsize(20)
    for label in ax.get_xticklabels():
        label.set_fontweight('bold')
        label.set_fontsize(20)

    plt.title(f"{group} - {site}", fontsize=20, fontweight='bold')
    plt.xlabel("Day", fontsize=20, fontweight='bold')
    plt.ylabel("Relative Abundance", fontsize=20, fontweight='bold')

    if toLegend == '1':
        legend = plt.legend(title='Species', loc='center left', 
                            bbox_to_anchor=(1,0.5), ncol=2, 
                            fancybox=True, shadow=True, fontsize=12)
        legend.get_title().set_fontweight('bold')
        plt.setp(legend.get_texts(), fontweight='bold')
    else:
        plt.legend().remove()

    plt.ylim(0, ymax)
    sns.despine()

    plt.autoscale(enable=True, axis='x', tight=True)
    plt.tight_layout()
    plt.savefig(out_fname)

