import sqlite3
from datetime import datetime
import random
from datasets import load_dataset
import pandas as pd

# Step 1: Load the dataset
dataset = load_dataset("Anthropic/hh-rlhf", split="train")
df = dataset.to_pandas()

# print(df.columns)  # 👈 Add this line to see actual column names
# exit()  # 👈 Temporarily stop execution here so you can see output


# Step 2: Connect to your DB
conn = sqlite3.connect("llm_dashboard.db")
cursor = conn.cursor()

# Step 3: Choose an existing project or create one
project_name = "Sample project3"
cursor.execute("SELECT id FROM projects WHERE name = ?", (project_name,))
result = cursor.fetchone()

if result:
    project_id = result[0]
else:
    # Create project if not exists
    cursor.execute("INSERT INTO projects (name, description, num_samples, deadline, created_at, status) VALUES (?, ?, ?, ?, ?, ?)",
                   (project_name, "Imported from hh-rlhf", 100, "2025-07-31", datetime.now().isoformat(), "In Progress"))
    conn.commit()
    project_id = cursor.lastrowid

# Step 4: Create and insert samples
samples = []
for i, row in df[:100].iterrows():  # limit to 100 for now
    # sample_text = row["chosen"]
    input_text = f"CHOSEN: {row['chosen']}\nREJECTED: {row['rejected']}"
    label = "Correct" if random.random() > 0.2 else "Incorrect"
    annotator_id = f"A{random.randint(1, 3)}"
    submitted_at = datetime.now().isoformat()
    is_flagged = 1 if random.random() < 0.1 else 0

    samples.append((project_id, input_text, label,
                   annotator_id, submitted_at, is_flagged))

cursor.executemany("""
    INSERT INTO samples (project_id, input_text, label, annotator_id, submitted_at, is_flagged)
    VALUES (?, ?, ?, ?, ?, ?)
""", samples)

conn.commit()
conn.close()
