from datasets import load_dataset
import pandas as pd

# Load the dataset
dataset = load_dataset("Anthropic/hh-rlhf", split="train")
df = dataset.to_pandas()

# Preview it
print(df.head())
