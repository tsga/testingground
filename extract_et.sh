#!/bin/bash

# Directory containing the year-month-day-hour folders
base_dir="da"

# Output file for the compiled results
output_file="elapsed_times.txt"

# Empty or create the output file
> "$output_file"

# Loop through all directories matching the date-time pattern
for dir in "$base_dir"/*; do
    # Check if it's a directory
    if [ -d "$dir" ]; then
        # The expected log file path
        log_file="$dir/enkfgdas_earc_tars_04.log"
        # Check if the log file exists
        if [ -f "$log_file" ]; then
            # Extract the last line containing 'time elapsed'
            elapsed_line=$(grep "time elapsed:" "$log_file" | tail -1)
            # Extract the time value
            elapsed_time=$(echo "$elapsed_line" | awk -F'time elapsed: ' '{print $2}')
            # Get the directory name (date-time string)
            dir_name=$(basename "$dir")
            # Only write if elapsed_time was found
            if [ -n "$elapsed_time" ]; then
                echo -e "$dir_name\t$elapsed_time" >> "$output_file"
            fi
        fi
    fi
done

echo "Compiled elapsed times to $output_file"
