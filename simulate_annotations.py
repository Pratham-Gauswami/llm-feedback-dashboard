import sqlite3
import random
from datetime import datetime, timedelta
import time

# Connect to your database
conn = sqlite3.connect("llm_dashboard.db")
cursor = conn.cursor()

# Define annotators
annotators = [
    {"id": "A1", "accuracy": 0.95, "avg_delay": 1.0},
    {"id": "A2", "accuracy": 0.85, "avg_delay": 1.5},
    {"id": "A3", "accuracy": 0.65, "avg_delay": 2.0},
]

# Get all unlabelled samples
cursor.execute("SELECT id, project_id FROM samples WHERE label IS NULL")
samples = cursor.fetchall()

for sample_id, project_id in samples:
    # Pick a random annotator
    annotator = random.choice(annotators)

    # Simulate delay
    time.sleep(random.uniform(0.1, annotator["avg_delay"]))

    # Determine if label is correct (simulate quality)
    is_correct = random.random() < annotator["accuracy"]
    label = "Correct" if is_correct else "Incorrect"
    is_flagged = 1 if not is_correct else 0

    submitted_at = datetime.now().isoformat()

    # Update the sample with fake submission
    cursor.execute('''
        UPDATE samples
        SET label = ?, annotator_id = ?, submitted_at = ?, is_flagged = ?
        WHERE id = ?
    ''', (label, annotator["id"], submitted_at, is_flagged, sample_id))

    print(f"Sample {sample_id} → Annotator {annotator['id']} → {label}")

conn.commit()
conn.close()
