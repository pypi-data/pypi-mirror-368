import streamlit as st
from sqlmodel import select

from app.db_connection import get_cached_db_session
from app.state import TypedSessionState
from pelican_data_loader.db import Dataset

# Add parent directory to path to import from main

USAGE_CODE_TEMPLATE = """
# Consume with Hugging Face's `datasets` package
from datasets import load_dataset

dataset = load_dataset("csv", data_files="{pelican_uri}")

# Convert to format of your choice, see https://huggingface.co/docs/datasets/v4.0.0/en/use_with_pytorch
torch_dataset = dataset.with_format("torch")
torch_dataset
"""


USAGE_CODE_TEMPLATE_V2 = """
from pelican_data_loader import load_uw_data
dataset = load_uw_data({key})

# Display the first record
list(dataset["train"].take(1))
"""


def render_discover():
    """Render the view published datasets tab with a list of all datasets in the metadata database."""
    st.header("Published Datasets")
    st.info("Explore datasets published to the UW-Madison Data Repository.", icon="ℹ️")

    # Get SessionState
    typed_state = TypedSessionState.get_or_create()

    if not typed_state.system_config:
        st.error("System configuration not found. Please restart the application.")
        return

    try:
        # Get cached database session
        session = get_cached_db_session(typed_state.system_config.metadata_db_engine_url)

        # Query all datasets from the database
        statement = select(Dataset)
        datasets = session.exec(statement).all()

        if not datasets:
            st.info("No published datasets found in the database.")
            return

        st.markdown(f"**Total datasets:** {len(datasets)}")

        # Display datasets in a expandable format
        for dataset in datasets:
            render_dataset(dataset)

    except Exception as e:
        st.error(f"Error accessing database: {str(e)}")
        st.info("Make sure the database has been initialized and contains data.")


def render_dataset(dataset: Dataset):
    """Renders a single dataset in an expandable format."""
    with st.expander(f"{dataset.name} (v{dataset.version})", icon="📄"):
        st.subheader("Dataset information")

        metadata_rows = {
            "Name": dataset.name,
            "Authors/Creators": ", ".join(f"{creator.first_name} {creator.last_name} ({creator.email})" for creator in dataset.creators)
            if dataset.creators
            else "Not provided",
            "Description": dataset.description or "Not provided",
            "Version": dataset.version,
            "SHA256": f"`{dataset.primary_source_sha256[:16]}...`" if dataset.primary_source_sha256 else "Not provided",
            "Published Date": dataset.published_date,
            "License": dataset.license,
            "Keywords": dataset.keywords or "Not provided",
            "Primary Source URL": dataset.primary_source_url or "Not provided",
            "Croissant Metadata URL": dataset.croissant_jsonld_url or "Not provided",
            "Pelican URI": dataset.pelican_uri or "Not provided",
            "Pelican HTTP URL": dataset.pelican_http_url or "Not provided",
        }
        st.table(metadata_rows)

        # Croissant JSON-LD metadata
        if dataset.pelican_uri:
            st.subheader("Consuming Dataset")

            st.markdown("Use Huggingface's dataset with pelican fs")
            st.code(
                USAGE_CODE_TEMPLATE.format(pelican_uri=dataset.pelican_uri),
            )
            st.markdown("---")
            st.markdown("This is a simpler mockup that will need data uploader identity and NetID integration later:")
            st.code(
                USAGE_CODE_TEMPLATE_V2.format(key='"netid/dataset_key"'),
            )
