import pandas as pd
import glob
import os

def clean_and_expand_triples(df):
    """
    Splits rows with multiple predicates and returns a cleaned DataFrame.
    Removes all spaces from subject, predicate, and object.
    """
    expanded_rows = []
    for _, row in df.iterrows():
        subject, predicate, obj = (str(x).replace(" ", "") for x in row)
        predicates = [p.strip() for p in predicate.split(',')]
        for p in predicates:
            expanded_rows.append([subject, p.replace(" ", ""), obj])
    return pd.DataFrame(expanded_rows, columns=['subject', 'predicate', 'object'])

def merge_csv_files(directory, output_file):
    """
    Merges all CSV files in a directory into a single cleaned CSV file.

    - Splits multiple predicates into individual rows
    - Removes all spaces from subject, predicate, and object
    - Removes duplicate entries and headers
    """
    all_filenames = glob.glob(os.path.join(directory, "*.csv"))
    all_df = []

    for f in all_filenames:
        df = pd.read_csv(f)
        # Skip headers in middle of files
        df = df[df['subject'] != 'subject']
        cleaned_df = clean_and_expand_triples(df)
        all_df.append(cleaned_df)

    merged_df = pd.concat(all_df, ignore_index=True)
    merged_df.drop_duplicates(inplace=True)
    merged_df.to_csv(output_file, index=False)

# Example usage:
directory_path = "../../schema/diagrams/domain_schemas/csv"
output_file_path = "../../schema/diagrams/domain_schemas/csv/triples.csv"
merge_csv_files(directory_path, output_file_path)
