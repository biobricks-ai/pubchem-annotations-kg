import biobricks as bb
import pandas as pd
import json
import pathlib 
from tqdm import tqdm

tqdm.pandas()

outdir = pathlib.Path('cache/process')
outdir.mkdir(parents=True, exist_ok=True)
pa_brick = bb.assets('pubchem-annotations')

# pa_brick has a single table `annotations_parquet`
# TODO pubchem-annotations isn't big but in the future spark or dask is a better choice.
rawpa = pd.read_parquet(pa_brick.annotations_parquet)
rawpa = rawpa.head(1000)

# get row0 and make it json for a pretty print
row0 = rawpa.iloc[0]
print(json.dumps(row0.apply(str).to_dict(), indent=4))

# - [x] create chemical
# - [x] create annotation
# - [x] create annotation has_subject chemical
# - [x] create annotation has_value value
#       extract this vaue from row.Data.Value.StringWithMarkup
#       create a new triple for each string and the StringWithMarkup array
#       check dcterms ontology for a good predicate to associate string with markup value to its annotation
# - [x] remove filter to allow multiple pubchem CIDs for annotation

annotations = []
annotations.append(
'''@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix pccompound: <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/> .
@prefix pcannotation: <http://rdf.ncbi.nlm.nih.gov/pubchem/annotation/> .
@prefix oa: <http://www.w3.org/ns/oa#> .
@prefix dc: <http://purl.org/dc/elements/1.1/>.
'''
)
with open(outdir / 'annotations.ttl', 'w') as f:
    f.write(annotations[0])

# loop through rawpa creating a chemical for each row
for index, row in tqdm(rawpa.iterrows()):
    cid = row['PubChemCID']
    # chem_iri = f"http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID{cid}"    

    # create an annotation
    anid = row['ANID']
    annotation_iri = f"http://rdf.ncbi.nlm.nih.gov/pubchem/annotation/ANID{anid}"

    # create the value for the annotation
    # # Parse the Data Field as JSON
    data = json.loads(row['Data'])
    string_with_markup = data.get('Value', {}).get('StringWithMarkup', [{}])[0].get('String', '')
    string_with_markup = string_with_markup.replace('\\', '\\\\')
    string_with_markup = string_with_markup.replace('"', r'\"')
    
    annotations.append(
f'''
pcannotation:ANID{anid}
  a oa:Annotation ;
'''
    )

    # add the CID to the annotation, skip if there are no CIDs
    if len(cid) > 0:
      for c in cid:
        annotations[-1] += f'  oa:hasTarget pccompound:CID{c} ;\n'
      for c in cid:
        annotations[-1] += f'  dc:subject   pccompound:CID{c} ;\n'

    # triple quotes used to allow multi-line strings
    # space after {string_with_markup} ensures quotes not broken
    annotations[-1] += \
fr'''  oa:hasBody [
  rdf:value """{string_with_markup} """ ;
  dc:format "text/plain"
] .
'''

    # write the annotation to a turtle file
    with open(outdir / 'annotations.ttl', 'a') as f:
        f.write(annotations[-1])
    
    # add a has_annotation

