# Lightweight RDF Stream Parser for Python

A lightweight RDF and RDF-Star parser which streams triples directly from disk
or standard input without loading the entire graph into memory.

Supports the N-Triples and N-Quads serialization format.

## Usage

Read and write to disk.

```python
from rdf import NTriples
from rdf import Literal

with NTriples(path = "./pizzacats.nt", mode = 'r') as g:
    with NTriples(path = "./out.nt", mode = 'w') as h:
        for subject, predicate, object in g.parse():
            if type(object) is Literal and object.language == "en":
                # do stuff
            h.write((subject, predicate, object))
```

Read / write from standard input / output.

```python
from os import stdin
from rdf import NQuads
from rdf import IRIRef

g = NQuads(data=stdin.read(), mode = 'r')
h = NQuads(mode = 'w')

target = IRIRef("https://example.org/Pizzacat")
for triple in g.parse():
    if triple[0] == target:  # subject
        # do stuff
        h.write(triple)
        
g.close()
h.close()
```

Adding new triples.

```python
from rdf import IRIRef, Literal, Statement
from rdf import RDF, XSD

EX = IRIRef("https://example.org/")  # define prefix
g = set()

subject = EX + "Pizzacat"
g.add(Statement(subject, RDF+"type", EX+"Cat"))

literal = Literal("Samurai Pizza Cats!!!", datatype=XSD+"string")
g.add(Statement(subject, EX+"tag_phrase", literal))
```
