import streamlit as st
import sqlite3
import pandas as pd
import altair as alt

st.set_page_config(page_title="LLM Ops Dashboard", layout="wide")
st.title("📊 LLM Project Dashboard")

# DB connection
conn = sqlite3.connect("llm_dashboard.db")
cursor = conn.cursor()

# Load projects
projects_df = pd.read_sql_query("SELECT * FROM projects", conn)

if projects_df.empty:
    st.warning("No projects found. Create one first.")
else:
    project_names = projects_df["name"].tolist()
    selected_project = st.selectbox("Select a Project", project_names)

    # Get selected project ID
    project_id = projects_df[projects_df["name"]
                             == selected_project]["id"].values[0]

    # Load samples
    samples_df = pd.read_sql_query(
        f"SELECT * FROM samples WHERE project_id = {project_id}", conn)

    # --- FILTERS ---
    st.subheader("🔍 Filter Samples")

    # Unique values
    annotators = samples_df["annotator_id"].dropna().unique().tolist()
    labels = samples_df["label"].dropna().unique().tolist()

    # Widgets
    selected_annotator = st.selectbox("Annotator", ["All"] + annotators)
    selected_label = st.selectbox("Label", ["All"] + labels)
    flagged_filter = st.selectbox(
        "Flagged?", ["All", "Flagged", "Not Flagged"])

    # Apply filters
    filtered_df = samples_df.copy()

    if selected_annotator != "All":
        filtered_df = filtered_df[filtered_df["annotator_id"]
                                  == selected_annotator]
    if selected_label != "All":
        filtered_df = filtered_df[filtered_df["label"] == selected_label]
    if flagged_filter == "Flagged":
        filtered_df = filtered_df[filtered_df["is_flagged"] == 1]
    elif flagged_filter == "Not Flagged":
        filtered_df = filtered_df[filtered_df["is_flagged"] == 0]

    # Summary metrics
    total = len(filtered_df)
    labeled = filtered_df["label"].notna().sum()
    flagged = filtered_df["is_flagged"].sum()
    correct = filtered_df[filtered_df["label"] == "Correct"]
    accuracy = 100 * (len(correct)/labeled) if labeled > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Total Samples", total)
    col2.metric("✅ Labeled", labeled)
    col3.metric("🚩 Flagged", flagged)
    col4.metric("🎯 Accuracy", f"{accuracy:.1f}%")

    # Annotator breakdown
    if labeled > 0:
        st.subheader("📋 Annotator Summary")
        ann_df = filtered_df.dropna(subset=["annotator_id"])
        # Group by annotator and compute both total and correct labels
        ann_group = ann_df.groupby("annotator_id").agg(
            samples_labeled=("id", "count"),
            correct_labels=("label", lambda x: (x == "Correct").sum()),
            flagged=("is_flagged", "sum")
        ).reset_index()

        ann_group["accuracy"] = 100 * \
            (ann_group["correct_labels"] / ann_group["samples_labeled"])

        st.dataframe(ann_group)

        # Chart
        chart = alt.Chart(ann_group).mark_bar().encode(
            x=alt.X('annotator_id:N', title='Annotator'),
            y=alt.Y('samples_labeled:Q', title='Samples Labeled'),
            color=alt.Color('accuracy:Q', scale=alt.Scale(scheme='greenblue')),
            tooltip=["samples_labeled", "accuracy"]
        ).properties(width=600, height=400, title="Annotator Label Volume & Accuracy")

        st.altair_chart(chart)

        # Label Distribution Pie
        st.subheader("📈 Label Distribution")

        label_counts = filtered_df["label"].value_counts().reset_index()
        label_counts.columns = ["Label", "Count"]

        pie = alt.Chart(label_counts).mark_arc(innerRadius=50).encode(
            theta="Count:Q",
            color="Label:N",
            tooltip=["Label", "Count"]
        ).properties(title="Label Distribution", height=400)

        st.altair_chart(pie)

        # Raw table
        with st.expander("🔍 View All Samples"):
            st.dataframe(filtered_df)


conn.close()
