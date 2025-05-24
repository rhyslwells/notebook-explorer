import os
import json
import nbformat


import re

def extract_metadata_from_markdown(nb):
    metadata = {"title": None, "tags": [], "summary": "No summary available.", "related": []}
    for cell in nb.cells:
        if cell.cell_type == 'markdown':
            match = re.search(r'<!--(.*?)-->', cell.source, re.DOTALL)
            if match:
                block = match.group(1)
                for line in block.splitlines():
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip().lower()
                        value = value.strip()
                        if key == "tags":
                            metadata[key] = json.loads(value)
                        elif key == "related":
                            metadata[key] = json.loads(value)
                        else:
                            metadata[key] = value
                break
            else:
                # fallback summary
                lines = cell.source.strip().splitlines()
                if lines:
                    metadata["summary"] = lines[0].strip()
                break
    return metadata

def generate_metadata(root_dir="notebooks"):
    metadata = {}
    for dirpath, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".ipynb"):
                full_path = os.path.join(dirpath, file)
                rel_path = os.path.relpath(full_path, root_dir)
                posix_path = os.path.join(root_dir, rel_path).replace("\\", "/")

                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        nb = nbformat.read(f, as_version=4)
                    meta = extract_metadata_from_markdown(nb)
                    if not meta["title"]:
                        meta["title"] = os.path.splitext(file)[0].replace("_", " ").title()
                    if not meta["tags"]:
                        meta["tags"] = dirpath.replace("\\", "/").split("/")[1:]
                    metadata[posix_path] = meta
                except Exception as e:
                    print(f"Error processing {full_path}: {e}")
    return metadata


if __name__ == "__main__":
    out = generate_metadata("notebooks")
    with open("metadata.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"Metadata for {len(out)} notebooks written to metadata.json")

#python generate_metadata.py
