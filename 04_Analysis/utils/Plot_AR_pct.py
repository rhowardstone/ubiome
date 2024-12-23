import pandas as pd
import matplotlib.pyplot as plt
import sys

# Verify correct usage
if len(sys.argv) != 4:
    print("Usage: python script.py <input.csv> <abx_resistant_asvs.txt> <Out.png>")
    sys.exit(1)

# Load data and resistant ASVs
df = pd.read_csv(sys.argv[1], header=0)
df = df.loc[:, ~df.columns.str.contains('W1|W2', regex=True)]
abx_resistant_asvs = pd.read_csv(sys.argv[2], header=None)[0].values

# Filter for resistant ASVs
df_resistant = df[df['seqID'].isin(abx_resistant_asvs)]

# Sum counts per sample for all and resistant ASVs
total_counts = df.iloc[:, 9:].sum(axis=1)
resistant_counts = df_resistant.iloc[:, 9:].sum(axis=1)
percent_abx_resistant = (resistant_counts / total_counts) * 100

# Check outputs for debugging
print("Total counts:", total_counts.head())
print("Resistant counts:", resistant_counts.head())
print("Percentage resistant:", percent_abx_resistant.head())

# Extract metadata from sample IDs
metadata = df.columns[9:].str.extract(r'(\w+)_(d\d+)_(\w+)_\w+_\w+')

# Handle missing or malformed 'Day' entries
metadata[1] = metadata[1].str.lstrip('d').astype(int)

# Create DataFrame for plotting
plot_data = pd.DataFrame({
    'Group': metadata[0],
    'Day': metadata[1],
    'Site': metadata[2],
    'Percent_ABX_Resistant': percent_abx_resistant
}).sort_values(['Group', 'Day'])

# Plot settings
colors = {'UNTR': 'blue', 'FMT': 'green', 'ABX3FMT': 'orange', 'ABX10': 'red'}
plt.figure(figsize=(10, 6))

# Plot each group and site combination
for group, group_df in plot_data.groupby('Group'):
    for site, site_df in group_df.groupby('Site'):
        days = site_df['Day']
        means = site_df['Percent_ABX_Resistant'].mean()
        errors = site_df['Percent_ABX_Resistant'].std()
        plt.errorbar(days, means, yerr=errors, fmt='-o', label=f'{group} ({site})', color=colors[group])

plt.xlabel('Day')
plt.ylabel('% Antibiotic Resistant ASVs')
plt.title('Percentage of Antibiotic Resistant ASVs Over Time')
plt.legend()
plt.tight_layout()
plt.savefig(sys.argv[3])

