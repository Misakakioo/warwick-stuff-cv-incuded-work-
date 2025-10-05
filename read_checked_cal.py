import pandas as pd

# Read the CSV file
df = pd.read_csv("100_read_checked.csv")

# Count the number of 1s in the 'Flipped' column
count = (df["Flipped"] == 1).sum()

print(count)
