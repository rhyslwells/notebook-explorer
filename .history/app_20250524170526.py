import streamlit as st
import json
import os
import streamlit.components.v1 as components
import nbconvert
from nbconvert import HTMLExporter

# Load metadata
with open("metadata.json", "r") as f:
    metadata = json.load(f)

# Sidebar: tag and text search filters
all_tags = sorted({tag for meta in metadata.values() for tag in meta["tags"]})
selected_tags = st.sidebar.multiselect("Filter by tags", all_tags, key="tag_selector")
search_query = st.sidebar.text_input("Search by title or summary", key="search_input")

# Filter logic
def notebook_matches(meta):
    tag_match = not selected_tags or set(meta["tags"]).intersection(selected_tags)
    text_match = not search_query or (
        search_query.lower() in meta["title"].lower() or 
        search_query.lower() in meta["summary"].lower()
    )
    return tag_match and text_match

filtered_metadata = {k: v for k, v in metadata.items() if notebook_matches(v)}

# Prepare nodes and edges for Cytoscape
nodes = [
    {"data": {"id": path, "label": meta["title"]}, "classes": "notebook"}
    for path, meta in filtered_metadata.items()
]
edges = []
for path, meta in filtered_metadata.items():
    for rel in meta.get("related", []):
        if rel in filtered_metadata:
            edges.append({"data": {"source": path, "target": rel}})

# Load and inject HTML with updated graph data
with open("graph_component/graph.html") as f:
    graph_html = f.read()

graph_html = graph_html.replace("/*__NODES__*/", json.dumps(nodes))
graph_html = graph_html.replace("/*__EDGES__*/", json.dumps(edges))

# Function to render notebook as HTML string
def render_notebook_html(notebook_path):
    exporter = HTMLExporter()
    exporter.exclude_input_prompt = True
    exporter.exclude_output_prompt = True

    try:
        body, _ = exporter.from_filename(notebook_path)
        return body
    except FileNotFoundError:
        return "<p><em>Notebook file not found.</em></p>"
    except Exception as e:
        return f"<p><em>Error rendering notebook: {e}</em></p>"

# Title and graph
st.title("Notebook Mind Map Explorer")
components.html(graph_html, height=600, scrolling=True)

# Notebook summaries with inline rendered preview
st.subheader("Notebook Summaries")
for path, meta in filtered_metadata.items():
    with st.expander(meta["title"]):
        st.write(meta["summary"])
        notebook_path = os.path.join("notebooks", path)
        html = render_notebook_html(notebook_path)
        components.html(html, height=600, scrolling=True)
        st.markdown(f"[Open raw notebook]({notebook_path})")
