#!/usr/bin/env bash

set -euo pipefail

# Get local path
localpath=$(pwd)
echo "Local path: $localpath"

# Get cache path
cachepath="$localpath/cache"
echo "Cache path: $cachepath"

# Create brick directory
brickpath="$localpath/brick"
mkdir -p $brickpath
echo "Brick path: $brickpath"

export base_uri="http://rdf.ncbi.nlm.nih.gov/pubchem/annotations.hdt"

input_path="$cachepath/process/combined_annotations.ttl"
output_path="$brickpath/annotations.hdt"

rdf2hdt -i -p -B "$base_uri" "$input_path" "$output_path"
