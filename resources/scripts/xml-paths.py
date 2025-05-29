import os
import xml.etree.ElementTree as ET
from pathlib import Path


def traverse_tree(element, current_path, paths):
    """
    Recursively traverse an XML tree and collect paths.
    """
    # Add current element path to the set
    path = f"{current_path}/{element.tag}"
    paths.add(path)

    # Traverse child elements
    for child in element:
        traverse_tree(child, path, paths)


def get_all_xml_paths(file_path):
    """
    Extract all unique XML paths from a single XML file.
    """
    paths = set()

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        traverse_tree(root, root.tag, paths)
    except ET.ParseError as e:
        print(f"Error parsing {file_path}: {e}")
    except Exception as e:
        print(f"Unexpected error processing {file_path}: {e}")

    return paths


def extract_unique_xml_paths(directory):
    """
    Extract all unique XML paths from all XML files in the directory.
    """
    all_paths = set()

    # Loop through all XML files in the directory
    for file_path in Path(directory).rglob("*.xml"):
        print(f"Processing file: {file_path}")
        file_paths = get_all_xml_paths(file_path)
        all_paths.update(file_paths)

    return all_paths


def write_paths_to_file(paths, output_file):
    """
    Write the unique paths to the output file.
    """
    with open(output_file, "w") as file:
        for path in sorted(paths):
            file.write(path + "\n")


if __name__ == "__main__":
    # Directory containing XML files
    directory = "../datasets/nanomine"

    # Output file for the paths
    output_file = "xml-paths.txt"

    # Extract paths and write to file
    unique_paths = extract_unique_xml_paths(directory)
    write_paths_to_file(unique_paths, output_file)

    print(f"Extracted {len(unique_paths)} unique XML paths. Saved to {output_file}")
