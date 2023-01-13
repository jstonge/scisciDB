#!/usr/bin/env zsh


# Set the input and output filenames
input_file=$1
output_prefix=${input_file%.*} # Get the input filename without the extension
output_suffix=${input_file##*.} # Get the input file extension

split -l 1000000 -d --additional-suffix=".jsonl" $input_file $output_prefix
