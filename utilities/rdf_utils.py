import json

from rdflib import Graph
from pyshacl import validate


def is_credential_compliant(ld_credential_dict, shacl_shapes_graph_serialized, print_details=False):
  """
  Checks whether a Linked-Data Credential (stored as a Python Dictionary) fulfills a SHACL Shapes Definition.

  The credential is parsed as an RDF Graph which is then validated with the SHACL Shapes.

  :param print_details: Bool: Whether to print details about the validation
  :param ld_credential_dict: Linked Data Credential as Python Dictionary
  :param shacl_shapes_graph_serialized: Turtle Serialization of an RDF Graph containing SHACL Shapes
  :return: True iff the credential's RDF Graph fulfills the SHACL Shapes
  """
  shacl_shapes_graph = parse_ttl_graph(shacl_shapes_graph_serialized)
  credential_graph = parse_ld_credential_dict(ld_credential_dict)
  return __is_graph_valid(credential_graph, shacl_shapes_graph, print_details)


def is_credential_compliant_graphs(ld_credential_graph, shacl_shapes_graph):
  """
  Checks whether a Linked-Data Credential fulfills a SHACL Shapes Definition.

  The credential and the SHACL Shapes are already provided as RDF Graphs.

  :param ld_credential_graph: Linked Data Credential as RDF Graph
  :param shacl_shapes_graph: RDF Graph containing SHACL Shapes
  :return: True iff the credential's RDF Graph fulfills the SHACL Shapes
  """
  return __is_graph_valid(ld_credential_graph, shacl_shapes_graph)


def parse_ld_credential_dict(credential_dict):
  credential_data = json.dumps(credential_dict)
  credential_graph = Graph()
  credential_graph.parse(data=credential_data, format='json-ld')
  return credential_graph


def __is_graph_valid(rdf_graph, shacl_shapes_graph, print_details=False):
  conforms, v_graph, v_text = validate(rdf_graph, shacl_graph=shacl_shapes_graph,
                                       shacl_graph_format='turtle',
                                       inference='rdfs', debug=False,
                                       serialize_report_graph=True)
  if print_details:
    print()
    print(rdf_graph.serialize())
    print()
    print(v_text)
  return conforms


def serialize_graph_ttl(graph):
  return graph.serialize(format='ttl')


def parse_ttl_graph(graph_turtle):
  g = Graph()
  g.parse(data=graph_turtle, format='turtle')
  return g
