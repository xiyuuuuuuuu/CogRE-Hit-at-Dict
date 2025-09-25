import pandas as pd

# Path to your parquet file
parquet_file = input("Please enter the path to the parquet file: ").strip()

# Read parquet file
df = pd.read_parquet(parquet_file)

# Show the first row of data
print(df.head(1).to_dict())