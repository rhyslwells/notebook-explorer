import streamlit as st
import json
import os
import nbformat
from nbconvert import HTMLExporter
import streamlit.components.v1 as components

GITHUB_BASE_URL = "https://github.com/rhyslwells/notebook-explorer/blob/main/"

with open("metadata.json", "r") as f:
    metadata = json.load(f)

all_tags = sorted({tag for meta in metadata.values() for tag in meta["tags"]})

st.title("Notebook Explorer")

selected_tags = st.multiselect("Filter by tags", all_tags, key="main_tag_filter")
search_query = st.text_input("Search by title or summary", key="main_search_input")

def notebook_matches(meta):
    tag_match = not selected_tags or set(meta["tags"]).intersection(selected_tags)
    text_match = not search_query or (
        search_query.lower() in meta["title"].lower() or
        search_query.lower() in meta["summary"].lower()
    )
    return tag_match and text_match

filtered_metadata = {k: v for k, v in metadata.items() if notebook_matches(v)}

# Group notebooks by parent
grouped = {}
for path, meta in filtered_metadata.items():
    parent = meta.get("parent", "No Parent")
    grouped.setdefault(parent, []).append((path, meta))

# Sort groups by size descending
grouped_sorted = dict(sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True))

def render_notebook_html(notebook_path):
    try:
        nb = nbformat.read(notebook_path, as_version=4)
        html_exporter = HTMLExporter()
        (body, _) = html_exporter.from_notebook_node(nb)
        return body
    except Exception as e:
        return f"<p><b>Error rendering notebook:</b> {e}</p>"

with st.expander(f"Filtered Notebooks ({len(filtered_metadata)})", expanded=True):
    for parent, notebooks in grouped_sorted.items():
        with st.expander(f"{parent} ({len(notebooks)})", expanded=False):
            for path, meta in notebooks:
                with st.expander(meta["title"]):
                    st.write(meta["summary"])
                    local_path = os.path.join("notebooks", path)
                    html = render_notebook_html(local_path)
                    components.html(html, height=50, scrolling=True)

                    github_url = f"{GITHUB_BASE_URL}/{path}"
                    colab_url = f"https://colab.research.google.com/github/rhyslwells/notebook-explorer/blob/main/{path}"
                    binder_url = f"https://mybinder.org/v2/gh/rhyslwells/notebook-explorer/HEAD?filepath=notebooks/{path}"

                    st.markdown(
                        f"[Open on GitHub]({github_url}) | [Open in Colab]({colab_url}) | [Open in Binder]({binder_url})"
                    )
