#!/bin/bash


#echo ''
#echo 'Running Filtering steps...'
#python 03_Filtering/1A_Combine_and_Filter.py

echo ''
echo 'Filtering steps already completed. Beginning analysis and plot generation.'
echo 'Output will be written to tables.txt in:'
pwd
echo ''
./04_Analysis/1A_Generate_figs-curr.sh > tables.txt

echo ''
echo 'Finished plot generation. Plots and data files are in 03_Filtering/ and 04_Analysis/'



