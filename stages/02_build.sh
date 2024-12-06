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

rdf2hdt -i -p -B "$base_uri"  $cachepath/process/combined_annotations.ttl $brickpath/annotations.hdt
