import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys

# Verify correct usage
if len(sys.argv) != 4:
    print("Usage: python Plot_ARG_categories.py <input.csv> <group_name> <output_filename>")
    sys.exit(1)
in_fname, group_name, output_filename = sys.argv[1:]

# Load data
df = pd.read_csv(in_fname)
df = df[~df['Sample'].isin(['W1', 'W2'])]  # Remove wildtype

# Extract necessary information from the Sample column
df['Group'] = df['Sample'].str.split('_').str[0]
df['Site'] = df['Sample'].str.split('_').str[2]
df['Day'] = df['Sample'].str.extract(r'_d(-?\d+)_').astype(str)  # Ensure day is integer for proper sorting

# Filter data based on the group
df = df[df['Group'] == group_name]

# Calculate relative abundances
category_columns = ['ARG', 'Ambiguous', 'non-ARG', 'Unmatched']
df[category_columns] = df[category_columns].div(df['Total'], axis=0)# * 100  # Ensure percentages

# Define styles and colors for lines
site_styles = {'LJ': '-', 'GR': '--'}
category_colors = {'ARG': 'red', 'Ambiguous': 'orange', 'non-ARG': 'green', 'Unmatched': 'grey'}

# Create plot
plt.figure(figsize=(9, 6))

# Plot each category and site combination
for category in category_columns:
    for site in df['Site'].unique():
        mask = df['Site'] == site
        sns.lineplot(data=df[mask], x='Day', y=category, label=f"{category} ({site})", linestyle=site_styles[site], color=category_colors[category], errorbar='sd', alpha=0.1)



ax = plt.gca()
for label in ax.get_yticklabels():
    label.set_fontweight('bold')
    label.set_fontsize(20)
for label in ax.get_xticklabels():
    label.set_fontweight('bold')
    label.set_fontsize(20)
   
   
plt.ylim([0,1])
    

plt.xlabel('Day', fontsize=20, fontweight='bold')
plt.ylabel('Relative Abundance', fontsize=20, fontweight='bold')
plt.title(f'{group_name}', fontsize=20, fontweight='bold')
legend  = plt.legend(title='AR status (Site)', fontsize=12,  loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=4, fancybox=True, shadow=True)
legend.get_title().set_fontweight('bold')
plt.setp(legend.get_texts(), fontweight='bold')
plt.autoscale(enable=True, axis='x', tight=True)

plt.grid(True)
plt.tight_layout()



# Save the plot
plt.savefig(output_filename)
print(f"Plot saved as {output_filename}")

