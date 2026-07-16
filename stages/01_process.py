#!/usr/bin/env python3
"""
Transform PubChem annotations (physicochemical headings) into principled RDF
using the SIO measurement pattern + public-ontology class/unit terms.

Model per measurement (one node per distinct annotation value):
  <physchem/CID{c}/{hash}> a <PROPERTY_CLASS_IRI> ;           # e.g. boiling point (eNanoMapper/CHEMINF)
        obo:IAO_0000136  pubchem:compound/CID{c} ;            # is about
        sio:SIO_000300   "<number>"^^xsd:double ;             # has value (when parseable)
        sio:SIO_000221   <UO/QUDT unit IRI> ;                 # has unit (when mapped)
        rdf:value        "<raw value string>" ;               # always preserved
        dcterms:source   "<SourceName>" ;
        rdfs:seeAlso     <reference url> ;                     # when present
        prov:wasDerivedFrom <this repo> .                     # statement-level provenance

Numeric value comes from Value.Number when present, else is regex-parsed from
Value.StringWithMarkup[].String. The node id hashes (ANID, heading, CID, raw
value): ANID is a PubChem *source-record* id that spans many headings per
compound, so it is NOT unique per measurement — hashing keeps distinct
measurements distinct while collapsing true duplicates.

Output: brick/pubchem-annotations-physchem.nt  (named graph
        https://biobricks.ai/graph/pubchem-annotations-physchem)
"""
import json, re, hashlib, pathlib
import duckdb
import biobricks as bb

HERE  = pathlib.Path(__file__).resolve().parent
TERMS = json.load(open(HERE / "physchem_terms.json"))
OUTDIR = pathlib.Path("brick"); OUTDIR.mkdir(parents=True, exist_ok=True)
OUT   = OUTDIR / "pubchem-annotations-physchem.nt"
GRAPH = "https://biobricks.ai/graph/pubchem-annotations-physchem"
SRC_REPO = "https://github.com/biobricks-ai/pubchem-annotations-kg"

PROP  = TERMS["properties"]      # heading -> class IRI
UNITS = TERMS["units"]           # normalized unit string -> UO/QUDT IRI

SIO_VALUE = "http://semanticscience.org/resource/SIO_000300"
SIO_UNIT  = "http://semanticscience.org/resource/SIO_000221"
IAO_ABOUT = "http://purl.obolibrary.org/obo/IAO_0000136"
RDF_TYPE  = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
RDF_VALUE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#value"
RDFS_SEE  = "http://www.w3.org/2000/01/rdf-schema#seeAlso"
DCT_SRC   = "http://purl.org/dc/terms/source"
PROV_DER  = "http://www.w3.org/ns/prov#wasDerivedFrom"
CPD       = "http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID"
BASE      = "https://biobricks.ai/physchem/"
UO_DIMLESS= "http://purl.obolibrary.org/obo/UO_0000186"
DIMLESS_PROPS = {"LogP", "Dissociation Constants", "Refractive Index"}

NUM_RE = re.compile(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?')

def norm_unit(u):
    if not u: return None
    u = u.replace('º', '°').replace('−', '-').strip()
    u = re.sub(r'\(.*?\)', '', u)
    u = re.sub(r'\bat\b.*$', '', u, flags=re.I)
    u = u.strip().rstrip('.,;').strip()
    u = re.sub(r'^dec\s+', '', u)
    u = u.replace('mm Hg', 'mmHg').replace('cu cm', 'cm3').replace('²', '2')
    for a, b in {'g/l':'g/L','mg/l':'mg/L','mg/ml':'mg/mL','g/ml':'g/mL','/ml':'/mL','µ':'u','μ':'u',
                 'g/100 mL':'g/100mL','kj/mol':'kJ/mol'}.items():
        u = u.replace(a, b)
    return u or None

def esc(s):
    return s.replace('\\','\\\\').replace('"','\\"').replace('\n',' ').replace('\r',' ').replace('\t',' ')

def parse_value(v):
    if not v: return (None, None, None)
    nums = v.get('Number')
    if nums:
        return (nums[0], v.get('Unit'), str(nums[0]) + (' ' + v['Unit'] if v.get('Unit') else ''))
    sw = v.get('StringWithMarkup') or []
    if sw:
        raw = (sw[0].get('String') or '').strip()
        m = NUM_RE.search(raw)
        if m:
            return (float(m.group()), raw[m.end():].strip(), raw)
        return (None, None, raw)
    return (None, None, None)

def main():
    pq = bb.assets('pubchem-annotations').annotations_parquet
    con = duckdb.connect()
    heads = list(PROP.keys())
    ph = ",".join("?" * len(heads))
    cur = con.execute(
        f"SELECT ANID, heading, Data, PubChemCID, SourceName FROM read_parquet(?) "
        f"WHERE heading IN ({ph}) AND Data IS NOT NULL AND PubChemCID IS NOT NULL",
        [pq, *heads])
    n_rows = n_trip = n_num = 0
    with open(OUT, 'w') as out:
        while True:
            batch = cur.fetchmany(20000)
            if not batch: break
            for anid, heading, data, cids, source in batch:
                if not cids: continue
                try: d = json.loads(data)
                except Exception: continue
                num, raw_unit, raw_str = parse_value(d.get('Value', {}))
                if raw_str is None: continue
                cls = PROP[heading]; refs = d.get('Reference') or []
                nu = norm_unit(raw_unit); uo = UNITS.get(nu) if nu else None
                n_rows += 1
                for c in cids:
                    h = hashlib.md5(f"{anid}|{heading}|{c}|{raw_str}".encode()).hexdigest()[:16]
                    node = f"{BASE}CID{c}/{h}"
                    def T(p, o_iri=None, lit=None, dt=None):
                        nonlocal n_trip
                        if o_iri is not None:
                            out.write(f"<{node}> <{p}> <{o_iri}> .\n")
                        else:
                            out.write(f'<{node}> <{p}> "{esc(lit)}"' + (f"^^<{dt}>" if dt else "") + " .\n")
                        n_trip += 1
                    T(RDF_TYPE, o_iri=cls)
                    T(IAO_ABOUT, o_iri=f"{CPD}{c}")
                    T(RDF_VALUE, lit=raw_str)
                    T(PROV_DER, o_iri=SRC_REPO)
                    if source: T(DCT_SRC, lit=source)
                    for r in refs[:3]:
                        if isinstance(r, str) and r.startswith('http'):
                            out.write(f"<{node}> <{RDFS_SEE}> <{esc(r)}> .\n"); n_trip += 1
                    if num is not None:
                        T(SIO_VALUE, lit=repr(float(num)), dt="http://www.w3.org/2001/XMLSchema#double")
                        n_num += 1
                        if uo: T(SIO_UNIT, o_iri=uo)
                        elif heading in DIMLESS_PROPS: T(SIO_UNIT, o_iri=UO_DIMLESS)
    print(f"rows={n_rows} triples={n_trip} numeric_values={n_num} -> {OUT} (graph {GRAPH})")

if __name__ == "__main__":
    main()
