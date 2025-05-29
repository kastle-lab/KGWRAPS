import os
import logging
import xml.etree.ElementTree as ET


from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

# Set up logging
logging.basicConfig(level=logging.WARNING)    

################################################################
##### MAPPING INIT #####
################################################################
# Directory stuff
mapping_dir = "../mapping"
mapping_file = "nanomine.yaml"
mapping_path = os.path.join(mapping_dir, mapping_file)

# Open the mapping file
logging.info(f"Opening: {mapping_path}")
mapping = None
with open(mapping_path, "r") as mapping_stream:
    logging.info("Open success.")
    mapping = load(mapping_stream, Loader=Loader)
    logging.info("Load success.")

if mapping is None:
    raise Exception("Mapping not properly loaded.")
# Get the root mapping (i.e., what will be recursively applied to the data)
root = mapping.get("root")
if root is None:
    msg = "Missing root in mapping file, which is required"
    logging.error(msg)
    raise Exception(msg)

################################################################
##### GRAPH INIT #####
################################################################
##### Graph stuff
import rdflib
from rdflib import URIRef, Graph, Namespace, Literal
from rdflib import OWL, RDF, RDFS, XSD, TIME

name_space = "http://kgwraps.wsu.edu/"
pfs = {
    "kgwrapsr": Namespace(f"{name_space}lod/resource/"),
    "kgwraps-ont": Namespace(f"{name_space}lod/ontology/"),
    "geo": Namespace("http://www.opengis.net/ont/geosparql#"),
    "geof": Namespace("http://www.opengis.net/def/function/geosparql/"),
    "sf": Namespace("http://www.opengis.net/ont/sf#"),
    "wd": Namespace("http://www.wikidata.org/entity/"),
    "wdt": Namespace("http://www.wikidata.org/prop/direct/"),
    "rdf": RDF,
    "rdfs": RDFS,
    "xsd": XSD,
    "owl": OWL,
    "time": TIME,
    "dbo": Namespace("http://dbpedia.org/ontology/"),
    "time": Namespace("http://www.w3.org/2006/time#"),
    "ssn": Namespace("http://www.w3.org/ns/ssn/"),
    "sosa": Namespace("http://www.w3.org/ns/sosa/"),
    "cdt": Namespace("http://w3id.org/lindt/custom_datatypes#"),
    "ex": Namespace("https://example.com/")
}

def init_kg(prefixes=pfs):
    kg = Graph()
    for prefix in pfs:
        kg.bind(prefix, pfs[prefix])
    return kg

a = pfs["rdf"]["type"]

################################################################
##### DO MAPPING #####
################################################################
def create_uri_from_string(s):
    tokens = s.split(":")
    if len(tokens) == 1:  # use default namespace
        prefix = pfs["ex"]
    elif len(tokens) == 2:
        prefix, classname = tokens
    else:
        msg = f"Malformed type found: {mapping['type']}"
        logging.error(msg)
        raise Exception(msg)
    return pfs[prefix][classname]

# def get_xml_value(element, path):
#     """
#     Retrieves text value from an XML element given a path, supporting nested paths.
#     """
#     for part in path.split('/'):
#         element = element.find(part)
#         if element is None:
#             return None
#     return element.text

def get_xml_value(element, path):
    """
    Retrieves text value from an XML element given a path, supporting nested paths and filtering by child presence.
    """
    parts = path.split('/')
    for part in parts:
        matches = element.findall(part)
        
        # If multiple matches exist, filter by checking for the next part in each match
        if len(matches) > 1 and parts.index(part) < len(parts) - 1:
            next_part = parts[parts.index(part) + 1]
            # Filter matches to find one containing the next part in the path
            filtered_matches = [match for match in matches if match.find(next_part) is not None]
            if filtered_matches:
                element = filtered_matches[0]  # Choose the first filtered match that has the next part
            else:
                return None
        else:
            # Default to the first match if no filtering is needed
            element = matches[0] if matches else None
            
        if element is None:
            return None  # Early return if any part in the path is not found
    
    return element.text if element is not None else None


def apply_mapping(element, mapping, graph):
    if isinstance(mapping, str):
        return create_uri_from_string(mapping)

    try:
        datatype = create_uri_from_string(mapping["datatype"])
        try:
            val = get_xml_value(element, mapping["val_source"])
        except (KeyError, AttributeError):
            try:
                val = mapping["value"]
            except KeyError: 
                msg = "'value' or 'val_source' must be defined for a datatype node."
                logging.error(msg)
                raise Exception(msg)
        return Literal(val, datatype=datatype)
    except KeyError:
        pass

    instance_uri_string = create_uri_from_string(mapping["uri"])
    try:
        varids = mapping["varids"]
        varid_vals = [get_xml_value(element, varid) for varid in varids]
        # varid_vals = [val if val is not None else "unknown" for val in varid_vals]
        instance_uri_string += "." + '.'.join(varid_vals)
        if "appellation" in mapping:
            instance_uri_string += "." + mapping["appellation"]
    except KeyError:
        pass

    instance_uri = URIRef(instance_uri_string)

    try:
        types = mapping["type"]
        if isinstance(types, str):
            types = [types]
        for t in types:
            class_uri = create_uri_from_string(t)
            graph.add((instance_uri, a, class_uri))
    except KeyError:
        if not mapping.get("ref", False):
            logging.warning(f"Added instance without type: {instance_uri}")

    try:
        for connection in mapping["connections"]:
            # Recursively apply mapping to nested elements if specified
            nested_elements = element.findall(connection.get("nested_source", "."))
            for nested_element in nested_elements:
                target_uri = apply_mapping(nested_element, connection["o"], graph)
                # Do not triplify None's -- the very inexistence is enough.
                if(str(target_uri) == "None"):
                    # print(str(target_uri))
                    continue
                preds = connection["p"]
                if not isinstance(preds, list):
                    preds = [preds]
                for pred in preds:
                    pred_uri = create_uri_from_string(pred)
                    graph.add((instance_uri, pred_uri, target_uri))
                if "inv" in connection:
                    inv_uri = create_uri_from_string(connection["inv"])
                    graph.add((target_uri, inv_uri, instance_uri))
    except KeyError:
        pass
    return instance_uri

# Open the data file
data_dir = "../datasets/nanomine"
# data_file = "L175_S1_O'Reilly_2015.xml"
# data_file = "L882_S14_Wu_2011.xml"
# data_path = os.path.join(data_dir, data_file)
output_dir = "../output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for data_file in os.listdir(data_dir):
    data_path = os.path.join(data_dir, data_file)
    logging.info(f"Opening: {data_path}")
    tree = ET.parse(data_path)
    root_element = tree.getroot()
    id = root_element.find("ID").text
    # print(str(root_element))
    # for element in root_element.findall(".//CommonFields"):
    graph = init_kg()
    apply_mapping(root_element, root, graph)
    output_file = f"output-{id}.ttl"
    output_path = os.path.join(output_dir, output_file)
    graph.serialize(format="turtle", encoding="utf-8", destination=output_path)
    logging.info("Serialized.")
