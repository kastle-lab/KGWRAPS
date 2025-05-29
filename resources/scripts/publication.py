import os
import xml.etree.ElementTree as ET

# Function to extract publications from an XML file
def extract_publications_from_xml(xml_file):
    publications = []
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Namespace handling if necessary
        for publication_element in root.findall('.//Publication'):
            if publication_element.text:
                publications.append(publication_element.text.strip())
    except ET.ParseError as e:
        print(f"Error parsing {xml_file}: {e}")
    return publications

# Function to process all XML files in a directory
def extract_publications_from_directory(directory):
    all_publications = []
    for root_dir, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.xml'):
                file_path = os.path.join(root_dir, file)
                publications = extract_publications_from_xml(file_path)
                if publications:
                    all_publications.extend(publications)
    return all_publications

# Output the publications to a file
def write_publications_to_file(publications, output_file):
    with open(output_file, 'w') as file:
        for publication in publications:
            file.write(publication + '\n')

if __name__ == "__main__":
    directory = "../datasets/nanomine"
    output_file = "publication.txt"

    publications = extract_publications_from_directory(directory)
    if publications:
        unique_publications = list(set(publications))
        write_publications_to_file(unique_publications, output_file)
        print(f"Extracted {len(unique_publications)} unique publications out of {len(publications)} total publications. Saved to {output_file}")
    else:
        print("No publications found.")
