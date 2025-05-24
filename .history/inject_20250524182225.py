import json
import os

def prepare_nodes_edges(metadata):
    nodes = []
    edges = []
    for path, meta in metadata.items():
        nodes.append({
            "data": {
                "id": path,
                "label": meta.get("title", path),
                "parent": meta.get("parent", ""),
                "summary": meta.get("summary", "")
            },
            "classes": "notebook"
        })
        for rel in meta.get("related", []):
            if rel in metadata:
                edges.append({
                    "data": {"source": path, "target": rel}
                })
    return nodes, edges

def main():
    # Load metadata
    with open("metadata.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)

    nodes, edges = prepare_nodes_edges(metadata)

    # Read graph.html template
    with open("graph_component/pre_inject_graph.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Inject metadata and nodes/edges JSON strings into placeholders
    html = html.replace("/*__METADATA__*/", json.dumps(metadata))
    html = html.replace("/*__NODES__*/", json.dumps(nodes))
    html = html.replace("/*__EDGES__*/", json.dumps(edges))

    # Write out updated graph.html
    with open("graph_component/graph.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Injected graph generated with {len(nodes)} nodes and {len(edges)} edges.")

if __name__ == "__main__":
    main()
