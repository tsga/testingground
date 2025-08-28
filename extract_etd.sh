#!/bin/bash

# Directories containing the folders
base_dirs=("cntrl" "da")
output_file="elapsed_times_dual.txt"

# Empty or create the output file
> "$output_file"

# Get unique list of folder names present in either base dir
folder_names=$(ls cntrl da 2>/dev/null | sort | uniq)

for folder in $folder_names; do
    # Prepare log file paths
    log_cntrl="${base_dirs[0]}/$folder/enkfgdas_earc_tars_04.log"
    log_da="${base_dirs[1]}/$folder/enkfgdas_earc_tars_04.log"

    # Extract elapsed time from cntrl log
    if [ -f "$log_cntrl" ]; then
        elapsed_cntrl=$(grep "time elapsed:" "$log_cntrl" | tail -1 | awk -F'time elapsed: ' '{print $2}')
    else
        elapsed_cntrl=""
    fi

    # Extract elapsed time from da log
    if [ -f "$log_da" ]; then
        elapsed_da=$(grep "time elapsed:" "$log_da" | tail -1 | awk -F'time elapsed: ' '{print $2}')
    else
        elapsed_da=""
    fi

    # Write to output (tab separated)
    echo -e "$folder\t$elapsed_cntrl\t$elapsed_da" >> "$output_file"
done

echo "Compiled elapsed times to $output_file"

