import os
import xml.etree.ElementTree as ET

# Function to extract DOIs from an XML file
def extract_dois_from_xml(xml_file):
    dois = []
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Namespace handling if necessary
        for doi_element in root.findall('.//DOI'):
            if doi_element.text:
                dois.append(doi_element.text.strip())
    except ET.ParseError as e:
        print(f"Error parsing {xml_file}: {e}")
    return dois

# Function to process all XML files in a directory
def extract_dois_from_directory(directory):
    all_dois = []
    for root_dir, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.xml'):
                file_path = os.path.join(root_dir, file)
                dois = extract_dois_from_xml(file_path)
                if dois:
                    all_dois.extend(dois)
    return all_dois

# Output the DOIs to a file
def write_dois_to_file(dois, output_file):
    with open(output_file, 'w') as file:
        for doi in dois:
            file.write(doi + '\n')

if __name__ == "__main__":
    directory = "../datasets/nanomine"
    output_file = "doi.txt"

    dois = extract_dois_from_directory(directory)
    if dois:
        write_dois_to_file(dois, output_file)
        print(f"Extracted {len(dois)} DOIs. Saved to {output_file}")
    else:
        print("No DOIs found.")
