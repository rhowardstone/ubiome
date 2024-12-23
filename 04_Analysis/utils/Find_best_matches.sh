#!/bin/bash

# Check if an input file is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <ijk_file>"
    exit 1
fi

ijk_file="$1"

# Use awk to find all ties for minimum edit distance for each ASV
awk -F'\t' '
{
    asv = $2
    edit_distance = $3
    # If this is the first time we see this ASV or if the edit distance is less than the minimum found so far
    if (!seen[asv] || edit_distance < min[asv]) {
        min[asv] = edit_distance
        line[asv] = $0  # Store the current line
        count[asv] = 1  # Reset the count for this ASV
    } else if (edit_distance == min[asv]) {  # If this line is tied for the minimum edit distance
        line[asv] = line[asv] "\n" $0  # Append this line to the existing ones
        count[asv]++  # Increment the count of ties for this ASV
    }
    seen[asv] = 1
}
END {
    for (asv in line) {
        print line[asv]
    }
}
' "$ijk_file"

