import os
import re

print(os.getcwd())

def main() -> None:
    print("Combining all XML files...")
    directory:str = f"{os.getcwd()}/../"

    combinedPath:str = f"{os.getcwd()}/Combined.csv"
    combined = open(combinedPath, 'a')

    for fileName in os.listdir(directory):
        if fileName.endswith(".xml"):
            print(fileName)
            file = open(f"{directory}{fileName}", "r")
            contents:str = grabContents(file, fileName)
            file.close()
            combined.write(f"{contents}\n")

    combined.close()

def grabContents(file, fileName) -> str:
    content:str = ""
    DOI:str = "N/A"
    Publication:str = "N/A"
    Title:str = "N/A"
    Volume: str = "N/A"
    with file:
        for line in file:
            line = line.strip()
            # DOI,Publication,Title,Volume
            if "<DOI>" in line:
                clean = cleanStr(line)
                if clean is not None:
                    DOI = clean

            if "<Publication>" in line:
                clean = cleanStr(line)
                if clean is not None:
                    Publication = clean

            if "<Title>" in line:
                clean = cleanStr(line)
                if clean is not None:
                    Title = clean
            if "<Volume>" in line:
                clean = cleanStr(line)
                if clean is not None:
                    Volume = clean

    content = f"{DOI}\t{Publication}\t{Title}\t{Volume}\t{fileName}"
    return content

def cleanStr(string:str) -> str:
    clean = re.search(r'>(.*?)<', string)
    return clean.group(1)

if __name__ == "__main__":
    main()
