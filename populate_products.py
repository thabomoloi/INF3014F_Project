import pandas as pd


def populate(db, Product):
    # Load CSV file into DataFrame
    df = pd.read_excel('products.xlsx')
    # Iterate through rows and update 'age' column
    for index, row in df.iterrows():
        prod = Product(name=row["name"],
                       price=row["price"],
                       stock=row["stock"],
                       brand=row["brand"],
                       category=row["category"],
                       description=row["description"],
                       average_ratings=row["average_ratings"],
                       ratings_count=row["ratings_count"],
                       image=row["image"])
        db.session.add(prod)
        db.session.commit()

