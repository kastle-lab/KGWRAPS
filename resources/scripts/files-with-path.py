import os
from lxml import etree

# Directory containing the XML files
XML_DIRECTORY = "../datasets/nanomine"

# XML path to search for
# XML_PATH = "PolymerNanocomposite/CHARACTERIZATION/Rheometery/CapillarSize"
XML_PATH = "PolymerNanocomposite/PolymerNanocomposite/MATERIALS/Filler/FillerComponent/ChemicalName"

def parse_xml_path(xml_path: str):
    """Convert a path string into a list of XML element tags."""
    return xml_path.strip().split('/')

def file_contains_path(file_path: str, tag_path: list) -> bool:
    """Check if the given file contains the specified XML path."""
    try:
        tree = etree.parse(file_path)
        element = tree.getroot()
        for tag in tag_path:
            element = element.find(tag)
            if element is None:
                return False
        return True
    except (etree.XMLSyntaxError, IOError) as e:
        print(f"Skipping file due to error: {file_path} ({e})")
        return False

def search_directory_for_path(directory: str, xml_path: str):
    """Search for files in a directory containing the given XML path."""
    tag_path = parse_xml_path(xml_path)
    matching_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".xml"):
                file_path = os.path.join(root, file)
                # print(file_path)
                if file_contains_path(file_path, tag_path):
                    matching_files.append(file_path)
                    print(matching_files)

    if matching_files:
        print("Matching files:")
        for file in matching_files:
            print(file)
    else:
        print("No matching files found.")

if __name__ == "__main__":
    search_directory_for_path(XML_DIRECTORY, XML_PATH)
