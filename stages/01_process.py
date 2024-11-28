import biobricks as bb
import pandas as pd
import json
import pathlib
import shutil
from tqdm import tqdm
from rdflib import Graph, Literal, Namespace, RDF, URIRef
import subprocess

tqdm.pandas()

# cachedir for ttl and nt files, if needed
cachedir = pathlib.Path('cache/process')
cachedir.mkdir(parents=True, exist_ok=True)
# remove unneeded files after (ttl, nt)

# outdir should be brick (hdt file only)
outdir = pathlib.Path('./brick')
outdir.mkdir(parents=True, exist_ok=True)

pa_brick = bb.assets('pubchem-annotations')

# pa_brick has a single table `annotations_parquet`
# TODO pubchem-annotations isn't big but in the future spark or dask is a better choice.
rawpa = pd.read_parquet(pa_brick.annotations_parquet)
rawpa = rawpa.head(1000)

# get row0 and make it json for a pretty print
row0 = rawpa.iloc[0]
print(json.dumps(row0.apply(str).to_dict(), indent=4))

# Create a new RDF graph
g = Graph()

# Define namespaces
namespaces_sources = {
    "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "pccompound" : "http://rdf.ncbi.nlm.nih.gov/pubchem/compound/",
    "pcsubstance" : "http://rdf.ncbi.nlm.nih.gov/pubchem/substance/",
    "pcannotation" : "http://rdf.ncbi.nlm.nih.gov/pubchem/annotation/",
    "oa" : "http://www.w3.org/ns/oa#",
    "dc" : "http://purl.org/dc/elements/1.1/",
}

namespaces = {key: Namespace(val) for key, val in namespaces_sources.items()}

# Bind namespaces
for key, val in namespaces.items():
    g.bind(key, val)

''' VISUAL REPRESENTATION OF GRAPH COMPONENT
*markup is short for string_with_markup

                         +------------------+
                 +-------|  annotation_iri  |
                 |       +------------------+
                 |             |      |      
            RDF.type           |   OA.hasBody       
                 |             |      |      
                 v             |      |  +-------------------+
       +-----------------+     |      +->|       body        |
       |  OA.Annotation  |     |         +-------------------+
       +-----------------+     |            |               |
                               |         RDF.value      DC["format"]
                               |            |               |
                               |            v               v
                               |  +-----------------+ +-----------------------+
                               |  | Literal(markup) | | Literal("text/plain") |
                               |  +-----------------+ +-----------------------+
                               |
                  OA.hasTarget / DC.subject
                               |
                  +---------+--o--------------+-------------+
                  |         |                 |             |
                  v         |                 v             |
	  +-------------------+ |        +-------------------+  |
	  |   compound_iri_1  | |  ...   |   compound_iri_m  |  | 
	  +-------------------+ |        +-------------------+  |
	                        v                               v
				  +-------------------+          +-------------------+ 
				  |  substance_iri_1  |   ...    |  substance_iri_n  |   
				  +-------------------+          +-------------------+
'''

# loop through rawpa creating a chemical for each row
# convert to list? for ETC
for index, row in tqdm(rawpa.iterrows(), total = len(rawpa), desc = "Processing rows"):
    cid = row['PubChemCID']
    sid = row['PubChemSID']
    anid = row['ANID']

    # Create URIs
    annotation_iri = URIRef(namespaces["pcannotation"] + f"ANID{anid}")
    compound_iri = [URIRef(namespaces["pccompound"] + f"CID{c}") for c in cid]
    substance_iri = [URIRef(namespaces["pcsubstance"] + f"CID{s}") for s in sid]

    # create the value for the annotation
    # # Parse the Data Field as JSON
    data = json.loads(row['Data'])
    # # annotation may have multiple values
    string_with_markup_list = [markup.get('String', '') for markup in data.get('Value', {}).get('StringWithMarkup', [])]

    # add triples to the graph
    g.add((annotation_iri, RDF.type, namespaces["oa"].Annotation))

    # add the CID to the annotation, skip if there are no CIDs
    for ci in compound_iri:
        g.add((annotation_iri, namespaces["oa"].hasTarget, ci))
        g.add((annotation_iri, namespaces["dc"].subject, ci))

    # add SID to the annotation, skip if there are no SIDs
    for si in substance_iri:
        g.add((annotation_iri, namespaces["oa"].hasTarget, si))
        g.add((annotation_iri, namespaces["dc"].subject, si))

    body = URIRef(f"{annotation_iri}/body")
    g.add((annotation_iri, namespaces["oa"].hasBody, body))
    # triple quotes used to allow multi-line strings
    for swm in string_with_markup_list:
        g.add((body, RDF.value, Literal(swm)))

    g.add((body, namespaces["dc"]["format"], Literal("text/plain")))

print("Creating HDT file ...")
# Serialize the graph to a string in Turtle format
turtle_file = str(cachedir / "temp_graph.ttl")
g.serialize(destination=turtle_file, format='turtle')

# Convert the Turtle file to an HDT file
hdt_file = str(outdir / 'annotations.hdt')
# # Conversion using the command-line tool rdf2hdt
subprocess.run(["rdf2hdt", turtle_file, hdt_file], check=True)
print(f"Done writing HDT file to {hdt_file}")

# delete cache directory
shutil.rmtree(pathlib.Path('cache'))