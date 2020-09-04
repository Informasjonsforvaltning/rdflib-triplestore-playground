"""Test cases for the fuseki triplestore."""
from os import environ as env
from typing import Any

from dotenv import load_dotenv
import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.compare import graph_diff, isomorphic

load_dotenv()
DATASET = env.get("DATASET_1", "ds")
PASSWORD = env.get("PASSWORD")

PREFIX = """
                PREFIX dct:   <http://purl.org/dc/terms/>
                PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX owl:   <http://www.w3.org/2002/07/owl#>
                PREFIX xml:   <http://www.w3.org/XML/1998/namespace>
                PREFIX xsd:   <http://www.w3.org/2001/XMLSchema#>
                PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
                PREFIX dcat:  <http://www.w3.org/ns/dcat#>
                PREFIX dc: <http://purl.org/dc/elements/1.1/>
        """


def test_insert_triples_into_named_graph_with_SPARQLWrapper(http_service: Any) -> None:
    """Should return some status and the graph is persisted."""
    from SPARQLWrapper import SPARQLWrapper, POST, TURTLE

    update_endpoint = f"{http_service}/{DATASET}/update"
    print(update_endpoint)

    sparql = SPARQLWrapper(update_endpoint)
    sparql.setCredentials("admin", PASSWORD)
    sparql.setMethod(POST)

    querystring = (
        PREFIX
        + """
            INSERT DATA
            { GRAPH <http://example.com/publisher/2>
              {
                <http://example.com/publisher/2/catalogs/1>
                        a              dcat:Catalog ;
                        dct:publisher  <https://example.com/publishers/2> ;
                        dct:title      "Dataservicekatalog for Anna Eksempel AS"@nb ;
                        dcat:service   <http://example.com/dataservices/2> ,
                                       <http://example.com/dataservices/1>
                        .
                <http://example.com/dataservices/1> a dcat:DataService ;
                    dct:description "Exposes a model-catalog"@nb ;
                    dct:title "Model-catalog of Digdir"@nb ;
                    dcat:contactPoint <http://example.com/contactpoint/2> ;
                    dcat:endpointDescription
                        <http://example.com/description/model-catalog.yaml> ;
                    .

                <http://example.com/dataservices/2> a dcat:DataService ;
                    dct:description "Exposes a collection of dataservice-catalogs"@nb ;
                    dct:title "Dataservice-catalog of Digdir"@nb ;
                    dcat:contactPoint <http://example.com/contactpoint/2> ;
                    dcat:endpointDescription
                        <http://example.com/description/dataservice-catalog.yaml> ;
                    .

                <http://example.com/contactpoint/2> a vcard:Organization ;
                    vcard:hasOrganizationName "Digitaliseringsdirektoratet"@nb ;
                    vcard:hasURL <https://digdir.no> ;
                    .
              }
            }
        """
    )

    sparql.setQuery(querystring)
    results = sparql.query()
    assert 200 == results.response.status

    query_endpoint = f"{http_service}/{DATASET}/query"
    querystring = """
        CONSTRUCT { ?s ?p ?o }
        WHERE {
            GRAPH <http://example.com/publisher/2> {?s ?p ?o}
        }
    """
    sparql = SPARQLWrapper(query_endpoint)
    sparql.setQuery(querystring)
    sparql.setReturnFormat(TURTLE)
    sparql.setOnlyConneg(True)
    results = sparql.query()
    assert 200 == results.response.status
    assert "text/turtle; charset=utf-8" == results.response.headers["Content-Type"]

    data = results.convert()
    g = Graph()
    g.parse(data=data, format="turtle")
    assert len(g) == 18


def test_insert_graph_into_named_graph_with_SPARQLWrapper(http_service: Any) -> None:
    """Should return some status and the graph is persisted."""
    from SPARQLWrapper import SPARQLWrapper, POST, TURTLE

    identifier = "<http://example.com/publisher/1>"
    g1 = Graph().parse("tests/catalog_1.ttl", format="turtle")

    update_endpoint = f"{http_service}/{DATASET}/update"
    print(update_endpoint)

    sparql = SPARQLWrapper(update_endpoint)
    sparql.setCredentials("admin", PASSWORD)
    sparql.setMethod(POST)

    prefixes = ""
    for ns in g1.namespaces():
        prefixes += f"PREFIX {ns[0]}: <{ns[1]}>\n"
    print(prefixes)

    for s, p, o in g1:
        if isinstance(o, Literal):
            querystring = (
                prefixes
                + """
                INSERT DATA {GRAPH %s {<%s> <%s> "%s"@%s}}
                """
                % (identifier, s, p, o, o.language,)
            )
        else:
            querystring = (
                prefixes
                + """
                INSERT DATA {GRAPH %s {<%s> <%s> <%s>}}
                """
                % (identifier, s, p, o,)
            )

        print(querystring)
        sparql.setQuery(querystring)
        results = sparql.query()
        assert 200 == results.response.status

    query_endpoint = f"{http_service}/{DATASET}/query"
    querystring = """
        CONSTRUCT { ?s ?p ?o }
        WHERE {
            GRAPH %s {?s ?p ?o}
        }
    """ % (
        identifier
    )
    sparql = SPARQLWrapper(query_endpoint)
    sparql.setQuery(querystring)
    sparql.setReturnFormat(TURTLE)
    sparql.setOnlyConneg(True)
    results = sparql.query()
    assert 200 == results.response.status
    assert "text/turtle; charset=utf-8" == results.response.headers["Content-Type"]

    data = results.convert()
    g2 = Graph()
    g2.parse(data=data, format="turtle")

    assert len(g1) == len(g2)

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic


def test_describe_query_with_SPARQLWrapper(http_service: Any) -> None:
    """Should return some status and the graph is persisted."""
    from SPARQLWrapper import SPARQLWrapper, TURTLE

    query_endpoint = f"{http_service}/{DATASET}/query"
    print(query_endpoint)

    querystring = "DESCRIBE <http://example.com/publisher/1/catalogs/1>"
    sparql = SPARQLWrapper(query_endpoint)

    sparql.setQuery(querystring)

    sparql.setReturnFormat(TURTLE)
    sparql.setOnlyConneg(True)
    results = sparql.query()

    assert 200 == results.response.status
    assert "text/turtle; charset=utf-8" == results.response.headers["Content-Type"]

    data = results.convert()
    g1 = Graph()
    g1.parse(data=data, format="turtle")
    src = (
        PREFIX
        + """

        <http://example.com/publisher/1/catalogs/1> a dcat:Catalog ;
            dct:publisher <https://example.com/publishers/1> ;
            dct:title "Dataservicekatalog for Eksempel AS"@nb ;
            dcat:service <http://example.com/dataservices/1>,
                <http://example.com/dataservices/2>
            .
    """
    )
    g2 = Graph().parse(data=src, format="turtle")

    assert len(g1) == len(g2)

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic


def test_construct_query_with_SPARQLWrapper(http_service: Any) -> None:
    """Should return 200 status and the graph."""
    from SPARQLWrapper import SPARQLWrapper, TURTLE

    query_endpoint = f"{http_service}/{DATASET}/query"
    print(query_endpoint)

    querystring = """
        CONSTRUCT { ?s ?p ?o }
        WHERE {
         GRAPH <http://example.com/publisher/1> {?s ?p ?o}
        }
    """
    sparql = SPARQLWrapper(query_endpoint)

    sparql.setQuery(querystring)

    sparql.setReturnFormat(TURTLE)
    sparql.setOnlyConneg(True)
    results = sparql.query()

    assert 200 == results.response.status
    assert "text/turtle; charset=utf-8" == results.response.headers["Content-Type"]

    data = results.convert()
    g1 = Graph()
    g1.parse(data=data, format="turtle")
    g2 = Graph().parse("tests/catalog_1.ttl", format="turtle")

    assert len(g1) == len(g2)

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic


@pytest.mark.xfail
def test_add_graph_with_SPARQLUpdateStore(http_service: Any) -> None:
    """Should return some status and the graph is persisted."""
    from rdflib.plugins.stores import sparqlstore

    query_endpoint = f"{http_service}/{DATASET}/query"
    update_endpoint = f"{http_service}/{DATASET}/update"
    print("query_endpoint: ", query_endpoint)
    print("update_endpoint: ", update_endpoint)
    store = sparqlstore.SPARQLUpdateStore(auth=("admin", PASSWORD))
    store.open((query_endpoint, update_endpoint))

    g = Graph(identifier=URIRef("http://www.example.com/"))

    g.parse("tests/catalog_1.ttl", encoding="utf-8", format="turtle")

    result = store.add_graph(g)
    assert result


def test_construct_graph_of_all_catalogs_with_SPARQLWrapper(http_service: Any) -> None:
    """Should return all the graphs."""
    from SPARQLWrapper import SPARQLWrapper, TURTLE

    query_endpoint = f"{http_service}/{DATASET}/query"
    print(query_endpoint)

    querystring = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        CONSTRUCT { ?s a dcat:Catalog .}
        WHERE { GRAPH ?g { ?s a dcat:Catalog .} }
    """
    sparql = SPARQLWrapper(query_endpoint)

    sparql.setQuery(querystring)

    sparql.setReturnFormat(TURTLE)
    sparql.setOnlyConneg(True)
    results = sparql.query()

    assert 200 == results.response.status
    assert "text/turtle; charset=utf-8" == results.response.headers["Content-Type"]

    data = results.convert()
    g1 = Graph()
    g1.parse(data=data, format="turtle")
    src = (
        PREFIX
        + """
        <http://example.com/publisher/1/catalogs/1>
            a       dcat:Catalog .
        <http://example.com/publisher/2/catalogs/1>
            a       dcat:Catalog .
        """
    )
    g2 = Graph().parse(data=src, format="turtle")

    assert len(g1) == len(g2)

    _isomorphic = isomorphic(g1, g2)
    if not _isomorphic:
        _dump_diff(g1, g2)
        pass
    assert _isomorphic


# ---------------------------------------------------------------------- #
# Utils for displaying debug information


def _dump_diff(g1: Graph, g2: Graph) -> None:
    in_both, in_first, in_second = graph_diff(g1, g2)
    print("\nin both:")
    _dump_turtle(in_both)
    print("\nin first:")
    _dump_turtle(in_first)
    print("\nin second:")
    _dump_turtle(in_second)


def _dump_turtle(g: Graph) -> None:
    for _l in g.serialize(format="turtle").splitlines():
        if _l:
            print(_l.decode())
