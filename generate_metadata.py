import os
import json
import nbformat

def extract_summary(nb_path):
    try:
        with open(nb_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        for cell in nb.cells:
            if cell.cell_type == 'markdown':
                lines = cell.source.strip().split('\n')
                return lines[0].strip()
    except Exception as e:
        print(f"Failed to parse {nb_path}: {e}")
    return "No summary available."

def generate_metadata(root_dir="notebooks"):
    metadata = {}
    for dirpath, _, files in os.walk(root_dir):
        for file in files:
            if not file.endswith('.ipynb'):
                continue
            full_path = os.path.join(dirpath, file)
            rel_path = os.path.relpath(full_path, root_dir)
            posix_path = os.path.join(root_dir, rel_path).replace("\\", "/")

            title = os.path.splitext(file)[0].replace("_", " ").title()
            tags = dirpath.replace("\\", "/").split("/")[1:]
            summary = extract_summary(full_path)

            metadata[posix_path] = {
                "title": title,
                "tags": tags,
                "summary": summary,
                "related": []  # Optional: fill later
            }
    return metadata

if __name__ == "__main__":
    out = generate_metadata("notebooks")
    with open("metadata.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"Metadata for {len(out)} notebooks written to metadata.json")

#python generate_metadata.py
