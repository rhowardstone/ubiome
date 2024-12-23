import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Error - usage:\n >>> python3 plot_ar_percentage.py <input_file.csv> <title> <output_file.png>\n")
        print("\tYou wrote:")
        print(" >>> "+" ".join(sys.argv)+"\n")
        sys.exit()

    input_file, title, output_file = sys.argv[1:]
    
    # Read the data, transpose to have samples as rows and calculate % AR
    data = pd.read_csv(input_file, index_col=0)
    data = data.loc[:, ~data.columns.str.contains('W1|W2', regex=True)].transpose()
    data['% AR'] = (data['AR'] / (data['AR'] + data['non-AR'])) #* 100
    data.reset_index(inplace=True)
    data[['Treatment', 'Day', 'Site', 'Sex', 'Animal']] = data['index'].str.split('_', expand=True)
    data['Day'] = data['Day'].str.extract('(\d+)')

    # Define custom color palette and line styles
    palette = sns.color_palette("deep", 4)
    group_colors = {"CMT": palette[2], "ABX10": palette[3], "ABX3CMT": palette[1], "UNTR": palette[0]}
    category_styles = {'GR': '--', 'LJ': '-'}

    # Plotting
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(9, 6))

    # Plot each group and category with specific style and color
    for (treatment, site), group_data in data.groupby(['Treatment', 'Site']):
        line_style = category_styles.get(site, '-')
        line_color = group_colors.get(treatment, "gray")
        sns.lineplot(data=group_data, x='Day', y='% AR', label=f"{treatment} ({site})", linestyle=line_style, color=line_color, markers=True)
    
    
    ax = plt.gca()
    for label in ax.get_yticklabels():
        label.set_fontweight('bold')
    for label in ax.get_xticklabels():
        label.set_fontweight('bold')
        
    #pct = ".".join(input_file.split("/")[-1].split("_")[3].split(".")[:-1])
    plt.title(title, fontsize=24, fontweight='bold')
    plt.xlabel('Day', fontsize=24, fontweight='bold')
    plt.ylabel('')
    legend  = plt.legend(title='Treatment (Site)', fontsize=12,  loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=4, fancybox=True, shadow=True)
    legend.get_title().set_fontweight('bold')
    plt.setp(legend.get_texts(), fontweight='bold')
    plt.ylim(0, 1) #0.37 for real plots
    plt.tight_layout()
    plt.savefig(output_file)


exit()



import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Error - usage:\n >>> python3 plot_ar_percentage.py <input_file.csv> <output_file.png>")
        sys.exit()

    input_file, output_file = sys.argv[1:]
    
    # Read the data, transpose to have samples as rows and calculate % AR
    data = pd.read_csv(input_file, index_col=0)
    data = data.loc[:, ~data.columns.str.contains('W1|W2', regex=True)].transpose()
    data['% AR'] = (data['AR'] / (data['AR'] + data['non-AR'])) * 100
    data.reset_index(inplace=True)
    data[['Treatment', 'Day', 'Site', 'Sex', 'Animal']] = data['index'].str.split('_', expand=True)
    data['Day'] = data['Day'].str.extract('(\d+)')
    
    # Plotting
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=data, x='Day', y='% AR', hue='Treatment', style='Site', markers=True, dashes=False)
    
    pct = ".".join(input_file.split("/")[-1].split("_")[3].split(".")[:-1])
    plt.title(f"T = {pct}% - %AR between sites")
    plt.xlabel('Day')
    plt.ylabel('% AR')
    plt.legend(title='Treatment and Site', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.ylim(0, 37)
    plt.tight_layout()
    plt.savefig(output_file)


exit()



import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Error - usage:\n >>> python3 plot_ar_percentage.py <input_file.csv> <output_file.png>")
        sys.exit()

    input_file, output_file = sys.argv[1:]
    
    # Read the summarized AR/non-AR data
    data = pd.read_csv(input_file, index_col=0)
    
    # The data is transposed to make samples as rows and AR status as columns
    data = data.transpose()
    
    # Adding a 'Total' row to calculate percentages
    data['Total'] = data['AR'] + data['non-AR']
    data['% AR'] = (data['AR'] / data['Total']) * 100
    
    # Reset index to turn the sample IDs into a column
    data.reset_index(inplace=True)
    
    # Parsing sample annotations from sample IDs
    data[['Treatment', 'Day', 'Site', 'Sex', 'Animal']] = data['index'].str.split('_', expand=True)
    data['Day'] = data['Day'].str.extract('(\d+)')  # Extracting numerical day from the string
    
    # Handle 'W1' and 'W2' if they do not follow the same structure or are not included in 'Day'
    # This approach assumes 'W1' and 'W2' are conditions or treatments rather than days
    # Plotting
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))

    # Filter out 'W1' and 'W2' from the main plot if necessary
    main_data = data[data['Day'].notna()]
    sns.lineplot(data=main_data, x='Day', y='% AR', hue='Treatment', dashes=False) # style='Site', markers=True, 

    # Find 'W1' and 'W2' values and plot them as horizontal lines
    # Assuming 'W1' and 'W2' are represented in the 'Treatment' column with their '% AR' values being constant
    
    pct = ".".join(input_file.split("/")[-1].split("_")[3].split(".")[:-1])
    print(pct)
    
    plt.title(f"T = {pct}% - %AR between sites")
    plt.xlabel('Day')
    plt.ylabel('% AR')
    plt.legend(title='Treatment and Site', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.ylim(0, 37)
    plt.tight_layout()
    plt.savefig(output_file)







'''


import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Error - usage:\n >>> python3 plot_ar_percentage.py <input_file.csv> <output_file.png>")
        sys.exit()

    input_file, output_file = sys.argv[1:]
    
    # Read the summarized AR/non-AR data
    data = pd.read_csv(input_file, index_col=0)
    
    # The data is transposed to make samples as rows and AR status as columns
    data = data.transpose()
    
    # Adding a 'Total' row to calculate percentages
    data['Total'] = data['AR'] + data['non-AR']
    data['% AR'] = (data['AR'] / data['Total']) * 100
    
    # Reset index to turn the sample IDs into a column
    data.reset_index(inplace=True)
    
    # Parsing sample annotations from sample IDs
    # Assuming your sample IDs follow a similar structure to the 'UNTR_d0_GR_M_a1' example
    data[['Treatment', 'Day', 'Site', 'Sex', 'Animal']] = data['index'].str.split('_', expand=True)
    data['Day'] = data['Day'].str.extract('(\d+)')  # Extracting numerical day from the string
    
    # Plotting
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=data, x='Day', y='% AR', hue='Treatment', style='Site', markers=True, dashes=False)
    
    
    # ARGs/ARG_ASVs_x1_best_${n}_ASVs.txt
    
    
    
    pct = ".".join(input_file.split("/")[-1].split("_")[3].split(".")[:-1])
    print(pct)
    
    plt.title(f"T = {pct}% - %AR between sites")
    plt.xlabel('Day')
    plt.ylabel('% AR')
    plt.legend(title='Treatment and Site', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    
    plt.ylim(0,37)
    plt.tight_layout()
    plt.savefig(output_file)
'''
