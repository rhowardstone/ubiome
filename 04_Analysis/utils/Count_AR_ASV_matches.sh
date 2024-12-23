#!/bin/bash

# Check if an input file was provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <input_file>"
    exit 1
fi

input_file="$1"

awk -F'\t' '
{
    asvCount[$2]++;  # Count occurrences of each ASV
    if ($NF == "Y") {
        yesCount[$2]++;  # Count Ys for each ASV
    } else if ($NF == "N") {
        noCount[$2]++;  # Count Ns for each ASV
    }
}
END {
    print "ASV\t#Ys\t#Ns";  # Print header
    for (id in asvCount) {
        if (!(id in yesCount)) { yesCount[id] = 0; }  # If no Ys, count is 0
        if (!(id in noCount)) { noCount[id] = 0; }    # If no Ns, count is 0
        print id "\t" yesCount[id] "\t" noCount[id];  # Print ASV, #Ys, #Ns
    }
}
' "$input_file"

