# rdflib-triplestore-playground

This project is a playground for testing out various methods to integrate python with the [Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/) triplestore with [rdflib](https://github.com/RDFLib/rdflib).

The code is implemented as test run with pytest.

## Develop and run locally
### Requirements
- [pyenv](https://github.com/pyenv/pyenv) (recommended)
- [poetry](https://python-poetry.org/)
- [nox](https://nox.thea.codes/en/stable/)

### Install software:
```
% git clone https://github.com/Informasjonsforvaltning/rdflib-triplestore-playground.git
% cd rdflib-triplestore-playground
% pyenv install 3.8.3
% pyenv local 3.8.3
% poetry install
```
### Running tests
We use [pytest](https://docs.pytest.org/en/latest/) for contract testing.

To run linters, checkers and tests:
```
% nox
```

## What we are playing with

We try to something analogous to the following in rdflib:
```
curl -g 'http://localhost:3030/ds/sparql?query=SELECT+DISTINCT+?concept+WHERE+{+?s+a+?concept+}+LIMIT+50'
```

## Queries
### SPARQL
#### List all triples
```
SELECT ?g ?s ?p ?o
WHERE {
  {?s ?p ?o}
  UNION
  { GRAPH ?g {?s ?p ?o} }
}
```
#### Select from a specific graph
```
SELECT ?s ?p ?o
WHERE {
  { GRAPH <http://example.com/bokstore/1> {?s ?p ?o} }
}
```
#### Construct from a specific graph
```
PREFIX dc: <http://purl.org/dc/elements/1.1/>
CONSTRUCT { ?s ?p ?o }
WHERE {
  { GRAPH <http://example.com/bookstore/1> {?s ?p ?o} }
}
```
### SPARQL Update
#### Drop all triples
```
DROP ALL
```
#### Drop graph, including all triples in it
```
DROP GRAPH <http://example.com/bokstore/1>
```
#### Insert into specific graph
```
PREFIX dc: <http://purl.org/dc/elements/1.1/>
INSERT DATA
{ GRAPH <http://example.com/bookstore/1>
  {
    <http://example.com/bookstore/1/book4>
                           dc:title    "A new book" ;
                           dc:creator  "A.N.Other" .
  }
}
```
