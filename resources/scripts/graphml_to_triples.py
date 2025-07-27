import networkx as nx
import csv
import re
import sys
import xml.etree.ElementTree as ET

# Parameters
args = sys.argv[1:]
graphml_path = args[0]
csv_path = args[1]

# Load GraphML with networkx
G = nx.read_graphml(graphml_path)

# === Step 1: Clean labels ===
def clean_label(label):
    if not label:
        return None
    if isinstance(label, str):
        label = label.strip()
        if re.fullmatch(r"n\d+", label):
            return None
    return label

def get_node_label(node_id):
    node_data = G.nodes[node_id]
    return clean_label(node_data.get('label') or node_id)

def get_edge_label(edge_elem):
    label_elem = edge_elem.find('.//y:EdgeLabel', namespaces)
    if label_elem is not None and label_elem.text:
        return ' '.join(label_elem.text.strip().split())
    # return edge_elem.attrib.get('type', 'relatedTo')
    return edge_elem.attrib.get('type', 'subClassOf')

def sanitize(value):
    if isinstance(value, str):
        return value.replace('\n', ' ').replace('\r', ' ').strip()
    return value

triples = []

# === Step 2: Parse XML for group structures and edges ===
tree = ET.parse(graphml_path)
root = tree.getroot()

graphml_ns = {'g': 'http://graphml.graphdrawing.org/xmlns'}
namespaces = {
    'y': 'http://www.yworks.com/xml/graphml',
    'g': 'http://graphml.graphdrawing.org/xmlns'
}

# Map from node id to label
id_to_label = {}
group_members = {}          # group_label -> set(member_labels)
member_to_group = {}        # member_label -> group_label
group_ids = set()

# Extract all node labels
for node in root.findall('.//g:node', graphml_ns):
    node_id = node.attrib['id']
    label_elem = node.find('.//y:NodeLabel', namespaces)
    label = clean_label(label_elem.text if label_elem is not None else None)
    if label:
        id_to_label[node_id] = label

    # Identify group node
    subgraph = node.find('g:graph', graphml_ns)
    if subgraph is not None:
        group_ids.add(node_id)
        group_label = id_to_label.get(node_id)
        if group_label:
            group_members[group_label] = set()
            for subnode in subgraph.findall('g:node', graphml_ns):
                subnode_id = subnode.attrib['id']
                sub_label_elem = subnode.find('.//y:NodeLabel', namespaces)
                sub_label = clean_label(sub_label_elem.text if sub_label_elem is not None else None)
                if sub_label:
                    id_to_label[subnode_id] = sub_label
                    group_members[group_label].add(sub_label)
                    member_to_group[sub_label] = group_label

# === Step 3: Extract edges from XML (not from NetworkX) ===
for edge in root.findall('.//g:edge', graphml_ns):
    source_id = edge.attrib['source']
    target_id = edge.attrib['target']

    source_label = id_to_label.get(source_id)
    target_label = id_to_label.get(target_id)
    pred = get_edge_label(edge)

    if source_label and target_label:
        triples.append((source_label, pred, target_label))

        # Handle group edges if source/target is a group
        if source_label in group_members:
            for member in group_members[source_label]:
                triples.append((member, pred, target_label))
        if target_label in group_members:
            for member in group_members[target_label]:
                triples.append((source_label, pred, member))

# === Step 4: Add explicit containment relationships ===
for group_label, members in group_members.items():
    for member in members:
        # triples.append((member, 'relatedTo', group_label))
        triples.append((member, 'subClassOf', group_label))

# === Step 5: Deduplicate and export ===
triples = list(set(triples))

with open(f'{csv_path}', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['subject', 'predicate', 'object'])
    for triple in triples:
        writer.writerow([sanitize(t) for t in triple])
