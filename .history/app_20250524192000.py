import streamlit as st
import json
import os
import nbformat
from nbconvert import HTMLExporter
import streamlit.components.v1 as components

# GitHub repo base URL for notebooks (adjust if your folder differs)
GITHUB_BASE_URL = "https://github.com/rhyslwells/notebook-explorer/blob/main/"

# Load metadata
with open("metadata.json", "r") as f:
    metadata = json.load(f)

# Sidebar filters with unique keys
all_tags = sorted({tag for meta in metadata.values() for tag in meta["tags"]})
selected_tags = st.sidebar.multiselect("Filter by tags", all_tags, key="sidebar_tag_filter")
search_query = st.sidebar.text_input("Search by title or summary", key="sidebar_search_input")

# Filtering function considering tags and text search
def notebook_matches(meta):
    tag_match = not selected_tags or set(meta["tags"]).intersection(selected_tags)
    text_match = not search_query or (
        search_query.lower() in meta["title"].lower() or
        search_query.lower() in meta["summary"].lower()
    )
    return tag_match and text_match

filtered_metadata = {k: v for k, v in metadata.items() if notebook_matches(v)}

st.title("Notebook Explorer")

st.subheader("Filtered Notebook Summaries")

def render_notebook_html(notebook_path):
    """Render notebook to HTML using nbconvert."""
    try:
        nb = nbformat.read(notebook_path, as_version=4)
        html_exporter = HTMLExporter()
        (body, _) = html_exporter.from_notebook_node(nb)
        return body
    except Exception as e:
        return f"<p><b>Error rendering notebook:</b> {e}</p>"

# Show filtered notebooks with summary, preview, and GitHub link
for path, meta in filtered_metadata.items():
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
