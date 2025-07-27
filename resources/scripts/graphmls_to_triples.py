import os

# resources
schema_dirname_graphml = "../../schema/diagrams/domain_schemas/graphml"
schema_dir_graphml = os.fsencode(schema_dirname_graphml)

schema_dirname_csv = "../../schema/diagrams/domain_schemas/csv2"

# run code
for graphml in os.listdir(schema_dir_graphml):
    graphml_name = os.fsdecode(graphml)
    if graphml_name.endswith(".graphml"):
        graphml_path = os.path.join(schema_dirname_graphml, graphml_name)
        csv_name = graphml_name.replace(".graphml", ".csv")
        csv_path = os.path.join(schema_dirname_csv, csv_name)
        os.system(f"python3 graphml_to_triples.py {graphml_path} {csv_path}")