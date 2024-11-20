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

# filter pa to rows where there is a single pubchem_cid and map to an int
pa1 = rawpa[rawpa['PubChemCID'].progress_apply(lambda x: len(x) == 1)]
pa1['PubChemCID'] = pa1['PubChemCID'].progress_apply(lambda x: int(x[0]))

# let's look at a single row of the table
rawrow = pa1.iloc[0]
row = rawrow.apply(str).to_dict()
rowstr = json.dumps(row, indent=4)
print(rowstr)

data = pa1['Data'].values
data_obj = [json.loads(d) for d in tqdm(data)]

# create annotations
annotations = []
for obj in tqdm(data_obj):
    # Check if the 'Value' key exists and contains 'StringWithMarkup'
    if 'Value' in obj and 'StringWithMarkup' in obj['Value']:
        # Extract the value from the 'StringWithMarkup' key
        value = obj['Value']['StringWithMarkup'][0]['String']
        # Create an annotation with 'have_value' and the extracted value
        annotation = {'has_value': True, 'value': value}
        annotations.append(annotation)

# create chemical
# create chemical has_annotation annotation
# loop through pa1 creating a chemical for each
row = pa1.iloc[0]
for index, row in tqdm(pa1.iterrows()):
    cid = row['PubChemCID']
    chem_iri = f"https://pubchem.ncbi.nlm.nih.gov/rest/rdf/compound/{cid}.html"    

# chemical has_identifier <build the pubchem cid>
# chemical has_annotation <annotation>
# annotation
# annotation has_value "starkljksjdf" 


