'''

This file contains (will contain, not yet complete) several calls to
APIs of scientific publishers to download papers from scientific publishers

Completed:
- Elsevier (10.1016) https://dev.elsevier.com/
- Wiley (10.1002) https://github.com/WileyLabs/tdm-client?tab=readme-ov-file#wiley-tdm-client

Will likely be able to support:

- Springer / Springer Nature (10.1007, 10.1038) - in progress https://datasolutions.springernature.com/account/api-management/ (forget what was left to do on this)

- IEEE (10.1109)
- IOP Publishing (10.1088)
- AIP (10.1063)
- APS / Physical Review (10.1103)
- ACS (10.1021)
- Wiley () - in progress, needs testing! 
- MDPI (10.3390)
- Royal Society of Chemistry (10.1039) why do I have an API key for this???????? (RCS has weird requirements for text data mining (TDM), I have an email from them I can forward)

UM IDK???:
- SAGE 
    1 request every 6 seconds - Monday to Friday between Midnight and Noon in the "America/Los_Angeles" timezone;
    1 request every 2 seconds - Monday to Friday between Noon and Midnight in the "America/Los_Angeles" timezone, and all day Saturday and Sunday.

Will likely not be able to support:
- World Scientific (10.1142)
- Cambridge / Materials Research Society (10.1557)
- Taylor & Francis (10.1080)

- AIAA (10.2514)
- Smaller / niche publishers (e.g., 10.3144)

'''

import os, json, requests, re

from dotenv import load_dotenv
from wiley_tdm import TDMClient
from requests import RequestException

from colorama import Fore
failed_color = Fore.RED
success_color = Fore.GREEN

# made a custom error class for some reason, I'm sure it was helpful for something, probably debugging parsing for bad links/failed downloads
class DownloadError(Exception):
    def __init__(self, doi, source, error_type, message):
        super().__init__(f"[{source}] {doi} - {error_type}: {message}")
        self.doi = doi
        self.source = source
        self.error_type = error_type
        self.message = message

    def __str__(self):
        return f"[{self.source}] {self.doi} - {self.error_type}: {self.message}"

# I have these API keys if you need them, though it might be better to make your own. Either way I don't mind
load_dotenv()
elsevier_api_key = os.getenv("elsevier_api_key")
wiley_api_key = os.getenv("wiley_api_key")
springer_nature_api_key = os.getenv("springer_nature_open_access_api_key")

wiley_tdm = TDMClient(api_token=wiley_api_key, download_dir="downloads")

# cleans a string for safe file naming
def safe_filename(s: str, maxlen: int = 150) -> str:
    # Replace path separators and other problematic chars
    s = re.sub(r'[\\/*?:"<>|]', "_", s)
    # Collapse whitespace and trim
    s = re.sub(r"\s+", " ", s).strip()
    # Limit length so we don't hit OS limits
    return s[:maxlen] or "untitled"

# saves the resuls of a paper to a file - might need to be modified to save additional metadata
def save_contents_to_file(DOI, contents, outpath, ext):
    # parse filename for save downlaod
    try:
        output_filename = safe_filename(DOI)
        os.makedirs(outpath, exist_ok=True)
    
    except Exception as e:
        print(failed_color + f"{DOI} -> parsing error: {e}")
        return -1
        
    with open(f"{outpath}/{(output_filename)}.{ext}", "wb") as f:
        try: 
            f.write(contents)
            print(success_color + f"{DOI} -> save success!")

        except Exception as e:
            print(failed_color + f"{DOI} -> save error!")

# springer nature - not sure if this works
def download_springer_nature(DOI):
    url = "https://api.springernature.com/openaccess/jats"

    params = {
        "q": f"doi:{DOI}",
        "api_key": springer_nature_api_key
    }

    headers = {
        "Accept": "application/jats+xml"
    }
    
    try:
        res = requests.get(url, headers=headers, params=params, timeout=20)
        
        print(res)
        
        if res.status_code != 200:
            raise DownloadError(DOI, "springer_nature", type(e).__name__, "res.status_code != 200", str(e))
        
        paper_contents = res.content
        try:
            save_contents_to_file(DOI, paper_contents, "springer_nature", "xml")
            
        except Exception as e:
           raise DownloadError(DOI, "springer_nature", type(e).__name__, "save error", str(e))
        
    except RequestException as e:
        raise DownloadError(DOI, "springer_nature", type(e).__name__, "request error", str(e))

    return

# wiley has their own API
def download_wiley(DOI):
    
    try: 
        result = wiley_tdm.download_pdf(DOI)
        if not result or "Api Error" in str(result) or "Invalid" in str(result):
            raise DownloadError(DOI, "wiley", "APIError", str(result))

    except Exception as e:
        raise DownloadError(DOI, "wiley", type(e).__name__, str(e))

import requests

# I think this one is ready to go
def download_elsevier(DOI):
    headers_xml = {
        "X-ELS-APIKey": elsevier_api_key,
        "Accept": "application/xml"
    }

    headers_pdf = {
        "X-ELS-APIKey": elsevier_api_key,
        "Accept": "application/pdf"
    }

    base_url = f"https://api.elsevier.com/content/article/doi/{DOI}"

    # ---------- STEP 1: XML ----------
    try:
        res_xml = requests.get(f"{base_url}?view=FULL", headers=headers_xml)

        if res_xml.status_code != 200:
            raise DownloadError(
                DOI, "elsevier", "HTTPError",
                f"XML status code {res_xml.status_code}"
            )

        xml_content = res_xml.content
        save_contents_to_file(DOI, xml_content, "elsevier/xml", "xml")

    except requests.exceptions.RequestException as e:
        raise DownloadError(DOI, "elsevier", type(e).__name__, str(e))

    # ---------- STEP 2: PDF ----------
    """ I don't think we actually need pdf copies but I was downloading them just to make sure they matched the XML versions
    try:
        res_pdf = requests.get(base_url, headers=headers_pdf)

        if res_pdf.status_code != 200:
            raise DownloadError(
                DOI, "elsevier", "HTTPError",
                f"PDF status code {res_pdf.status_code}"
            )

        pdf_content = res_pdf.content
        save_contents_to_file(DOI, pdf_content, "elsevier/pdf", "pdf")

    except requests.exceptions.RequestException as e:
        raise DownloadError(DOI, "elsevier", type(e).__name__, str(e))
    """
    

def download_from_file(filepath):
"""
    This should search through the jsonl file and hit the appropriate endpoint for each publisher. 
    I think this function was written for an older iteration of how I had the json data structured so this will need to be updated
    
"""
    with open(filepath, "r") as f:

        for i, line in enumerate(f, 1):
            try:
                meta = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"BAD LINE {i}: {e}")
                print(line)  # preview
                break
            
            title = (meta.get("title") or "").strip()
            publisher = (meta.get("publisher") or "").lower()
            cursor = meta.get("cursor")
            doi = meta.get("DOI")
            
            if not title:
                print(f"({i}): no title found!")
                continue

            # pagination / cursor skip
            if cursor == "*":
                print(f"({i}): * cursor entry")
                continue

            # junk title skip
            if is_junk_title(title):
                print(f"({i}): skipping junk title {title}")
                continue

            # publisher routing
            if "elsevier" in publisher:
                print(f"({i}): downloading: {title}")
                try:
                    download_elsevier(doi)
                except DownloadError as e:
                    print(f"could not download {title}: {e}")

def is_junk_title(title: str) -> bool:
    BAD_TITLE_PREFIXES = (
        "calendar",
        "announcement",
        "announcements",
        "editorial",
        "editorial board",
        "contents",
        "contents continued",
        "erratum",
        "errata",
        "contributions to",
    )

    if not title:
        return True
    t = title.strip().lower()
    return t.startswith(BAD_TITLE_PREFIXES)

if __name__ == "__main__":
    download_from_file("./polymer_data_fixed.jsonl")