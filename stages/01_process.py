import biobricks as bb
import pandas as pd
import json
import pathlib 
from tqdm import tqdm
import random

tqdm.pandas()

outdir = pathlib.Path('cache/process')
outdir.mkdir(parents=True, exist_ok=True)
pa_brick = bb.assets('pubchem-annotations')

# pa_brick has a single table `annotations_parquet`
# TODO pubchem-annotations isn't big but in the future spark or dask is a better choice.
rawpa = pd.read_parquet(pa_brick.annotations_parquet)
rawpa = rawpa.head(1000)

# filter pa to rows where there is a single pubchem_cid and map to an int
pa1 = rawpa[rawpa['PubChemCID'].progress_apply(lambda x: len(x) == 1)]
pa1['PubChemCID'] = pa1['PubChemCID'].progress_apply(lambda x: int(x[0]))

# get row1 and make it json for a pretty print
print(json.dumps(pa1.iloc[0].apply(str).to_dict(), indent=4))

# create annotations
# annotations = []
# for obj in tqdm(data_obj):
#     # Check if the 'Value' key exists and contains 'StringWithMarkup'
#     if 'Value' in obj and 'StringWithMarkup' in obj['Value']:
#         # Extract the value from the 'StringWithMarkup' key
#         value = obj['Value']['StringWithMarkup'][0]['String']
#         # Create an annotation with 'have_value' and the extracted value
#         annotation = {'has_value': True, 'value': value}
#         annotations.append(annotation)

# - [x] create chemical
# - [x] create annotation
# - [x] create annotation has_subject chemical
# - [ ] create annotation has_value value
# loop through pa1 creating a chemical for each
row = pa1.iloc[0]
for index, row in tqdm(pa1.iterrows()):
    cid = row['PubChemCID']
    chem_iri = f"http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID{cid}"    

    # create an annotation
    # anid = row['ANID']
    anid = random.randint(100000, 999999)
    annotation_iri = f"http://rdf.ncbi.nlm.nih.gov/pubchem/annotation/ANID{anid}"

    # create the value for the annotation

    # create a relationship between the chemical and the annotation
    has_subject = "http://purl.org/dc/terms/subject"
    triple = (annotation_iri, has_subject, chem_iri)

    # write the triple to a turtle file
    with open(outdir / 'annotations.ttl', 'a') as f:
        f.write(f"<{triple[0]}> <{triple[1]}> <{triple[2]}> .\n")
    
    # add a has_annotation

