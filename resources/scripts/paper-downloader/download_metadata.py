import requests, json, os
from pathlib import Path

# downloads a batch of metadata objects and appends to the jsonl file. Uses crossref's cursor method for querying. It prevents overlapping results in the queries.
# refer to https://www.crossref.org/documentation/retrieve-metadata/rest-api/tips-for-using-the-crossref-rest-api/ 
def download_crossref_metadata(query, rows, filepath, email, cursor, seen):
        
    headers = {"User-Agent": f"PolymerHarvester/5.0 (mailto:{email})"}
    base_url = "https://api.crossref.org/works"
    
    params = {
        "query": query,
        "rows": rows,
        "cursor": cursor,
        "filter": "type:journal-article"
    }
    
    response = requests.get(base_url, params=params, headers=headers, timeout=120)
    
    if response.status_code != 200:
        raise Exception(f"[Error] Cross returned: {response.status_code} error!")
    
    json_response = response.json()
    
    # Pulling large sets of metadata is best done using cursors. The initial request returns a cursor that we then use to query for subsequent results in batches of 1000
    next_cursor = json_response["message"]["next-cursor"]
       
    # Filter out already-seen DOIs
    items = json_response["message"]["items"]
    filtered_items = []
    skipped = 0

    for item in items:
        doi = item.get("DOI")
        if doi and doi in seen:
            skipped += 1
            continue
        filtered_items.append(item)
        
    json_response["message"]["items"] = filtered_items

    print(f"New items: {len(filtered_items)}")
    print(f"Filtered out {skipped} already-seen DOIs")

    append_object_to_file(filepath, json_response)

    # Return the cursor so we can call it again     
    return next_cursor
    
# function to append metadata object to file
def append_object_to_file(filepath, obj):
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
       
# loads DOIs already downloaded so we don't download duplicates on different queries/runs 
def load_seen_dois(filepath):
    seen = set()
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            for item in record["message"]["items"]:
                seen.add(item.get("DOI"))
    return seen

# loads the seen DOIs, then downloads new DOIs by looping over the download function
def download_loop(filepath, queries, email):
    
    if Path(filepath).exists():
        seen = load_seen_dois(filepath)
        print(f"Unique DOIs: {len(seen)}")
        
    else:
        seen = set()
        
    running = True
    error_count = 0
    cursor = "*"
    count = 1
    for query in queries:
        while running == True:
            try:
                print(f"\nProcessing batch #{count}")
                count += 1
                cursor = download_crossref_metadata(query=query, rows=1000, filepath=filepath, email=email, cursor=cursor, seen=seen) 
                error_count = 0
            except Exception as e:
                print(e)
                error_count += 1
                if error_count == 3:
                    print(f"{error_count} consecutive errors occurred, stopping script!")
                    running = False
                    break
    
if __name__ == "__main__":
    
    queries = [#"polymer", 
               "polymer science", "materials science", "polymer extraction", "polymer chemistry", "polymer physics, polymer synthesis", "polymer composites"]
    download_loop(filepath="paper_metadata.jsonl", queries=queries, email="castro.31@wright.edu") # calls load_seen_dois() and 
            