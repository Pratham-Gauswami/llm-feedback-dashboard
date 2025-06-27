import streamlit as st
import sqlite3
from datetime import datetime

# Connect to database (or create it if it doesn't exist)
conn = sqlite3.connect("llm_dashboard.db")
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        num_samples INTEGER,
        deadline TEXT,
        created_at TEXT,
        status TEXT
    )
''')
conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS samples (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        input_text TEXT,
        label TEXT,
        annotator_id TEXT,
        submitted_at TEXT,
        is_flagged INTEGER DEFAULT 0,
        FOREIGN KEY (project_id) REFERENCES projects(id)
    )
''')
conn.commit()

# Streamlit Form
st.title("📋 Create a New Project")

with st.form("project_form"):
    name = st.text_input("Project Name")
    description = st.text_area("Project Description")
    num_samples = st.number_input("Number of Samples", min_value=1, value=100)
    deadline = st.date_input("Deadline")
    status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])

    submitted = st.form_submit_button("Create Project")

    if submitted:
        created_at = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO projects (name, description, num_samples, deadline, created_at, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, description, num_samples, deadline.isoformat(), created_at, status))
        conn.commit()
        st.success(f"Project '{name}' created successfully!")

        # Generate fake samples
        for i in range(num_samples):
            fake_input = f"This is sample #{i+1} for project '{name}'"
            cursor.execute('''
                INSERT INTO samples (project_id, input_text)
                VALUES (?, ?)
            ''', (cursor.lastrowid, fake_input))
        conn.commit()
