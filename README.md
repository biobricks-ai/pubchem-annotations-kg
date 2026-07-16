# pubchem-annotations-kg

Transforms [pubchem-annotations](https://github.com/biobricks-ai/pubchem-annotations)
(the tabular PubChem PUG-View annotation dump) into **principled RDF** for the
biobricks knowledge graph serving kg.toxindex.com.

## What it produces

Physicochemical-property measurements modeled with the PubChem-style **SIO
measurement pattern** and **public-ontology** class/unit terms — no bespoke
predicates. One node per distinct measurement:

```
<https://biobricks.ai/physchem/CID<cid>/<hash>>
    a  <property class> ;                       # eNanoMapper / CHEMINF / PATO
    obo:IAO_0000136  pubchem:compound/CID<cid>; # is about
    sio:SIO_000300   <number> ;                 # has value
    sio:SIO_000221   <UO/QUDT unit> ;           # has unit
    rdf:value        "<raw source string>" ;    # always preserved
    dcterms:source   "<SourceName>" ;
    prov:wasDerivedFrom <this repo> .
```

Headings covered (see `stages/physchem_terms.json` for the verified IRIs):
Boiling/Melting Point, LogP, Vapor Pressure, Density, Flash Point, Solubility,
Refractive Index, Dissociation Constant (pKa), Vapor Density, Heat of
Vaporization, Henry's Law Constant, Viscosity. Values come from the annotation
`Value.Number` field or are regex-parsed from `Value.StringWithMarkup`.

Output: `brick/pubchem-annotations-physchem.nt`, loaded as the named graph
`https://biobricks.ai/graph/pubchem-annotations-physchem`. Cross-linked to other
sources via the [compound-bridge](https://github.com/biobricks-ai/compound-bridge)
InChIKey hub.

**Note on identity:** PubChem's `ANID` is a *source-record* id that spans many
headings per compound, so it is not unique per measurement — node ids hash
`(ANID, heading, CID, raw value)` so distinct measurements stay distinct.

## Build
`dvc repro` (needs the `pubchem-annotations` dependency pinned in
`.bb/dependencies.txt`).

## History
Previously emitted a generic `oa:Annotation` HDT (raw text bodies, no numeric
values) for biobricks-okg. Replaced 2026-07 with the principled physchem
transform above.
