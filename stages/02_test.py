import rdflib
import pathlib

outdir = pathlib.Path('cache/test')
outdir.mkdir(parents=True, exist_ok=True)

# Read the turtle file into a graph
graph = rdflib.Graph()
turtle_file = outdir / 'annotations.ttl'

try:
    # Parse the Turtle file into the RDF graph
    graph.parse(source=turtle_file.as_posix(), format="turtle")

    # Generate metadata
    metadata = {
        "triple_count": len(graph),
        "namespaces": list(graph.namespaces()),
        "sample_triples": list(graph)[:5]  # Limit to first 5 triples
    }

    # Write metadata to a file
    metadata_file = outdir / "test.txt"
    with open(metadata_file, "w") as f:
        f.write(f"Triple Count: {metadata['triple_count']}\n")
        f.write("Namespaces:\n")
        for prefix, uri in metadata['namespaces']:
            f.write(f"  {prefix}: {uri}\n")
        f.write("Sample Triples:\n")
        for s, p, o in metadata['sample_triples']:
            f.write(f"  {s} {p} {o}\n")

    print(f"Metadata written to {metadata_file}")

except Exception as e:
    # Explicitly fail if the graph fails to load
    print(f"Failed to parse the graph: {e}")
    raise
