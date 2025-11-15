import pandas as pd

# Load the CSV you scraped
df = pd.read_csv("books.csv")

# 1. See what your data looks like
print(df.head())

# 2. Basic info
print(df.info())

# 3. Summary statistics
print(df.describe())

# 4. Some quick insights
print("Average book price:", df['price'].mean())
print("Highest rated book(s):")
print(df[df['rating_num'] == 5][['title', 'price']])
