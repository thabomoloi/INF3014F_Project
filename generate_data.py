import pandas as pd
from random import randint


def get_average_ratings():

    total = randint(50, 300)
    ratings = 0
    for i in range(0, total):
        ratings += randint(3, 5)

    return ratings / total, total


# Load CSV file into DataFrame
df = pd.read_excel('products.xlsx')

brands = ["Farm2Table", "HarvestBox", "GreenThumb Organics", "PureFresh Market", "Sun-Kissed Farms", "FreshPicks Co"]

# Iterate through rows and update 'age' column
for index, row in df.iterrows():
    ratings = get_average_ratings()
    df.loc[index, 'stock'] = randint(1000, 2000)

# Save updated DataFrame to CSV file
df.to_excel('updated_data.xlsx', index=False)
