# search/search_engine.py
import pandas as pd
import re

# ---- Keyword maps ----
PHONE_KEYWORDS = [
    "galaxy", "iphone", "redmi", "note", "infinix",
    "tecno", "vivo", "realme", "poco", "pixel", "nokia"
]

EXCLUDE_KEYWORDS = ["buds", "earbuds", "airpods", "headphone", "earphone", "earbud"]

def load_products(path="data/products.csv"):
    """
    Load cleaned dataset
    """
    return pd.read_csv(path)

def search_products(df, attrs, top_n=5):
    """
    Product filtering and ranking
    """
    result = df.copy()

    # Convert to lowercase strings
    for col in ["product_name", "category", "brand"]:
        if col in result.columns:
            result[col] = result[col].astype(str).str.lower()

    # ---- Filter by product type ----
    product = attrs.get("product")

    if product == "phone":
        phone_pattern = "|".join(re.escape(k) for k in PHONE_KEYWORDS)
        result = result[result["product_name"].str.contains(phone_pattern, na=False)]

        exclude_pattern = "|".join(EXCLUDE_KEYWORDS)
        result = result[~result["product_name"].str.contains(exclude_pattern, na=False)]

    # ---- Budget ----
    if attrs.get("budget") is not None and "price" in result.columns:
        result = result[result["price"] <= attrs["budget"]]

    # ---- Brand ----
    brand = attrs.get("brand")
    if brand:
        b = str(brand).lower()
        result = result[result["product_name"].str.contains(b, na=False)]

    # ---- Sort by price ----
    if "price" in result.columns:
        result = result.sort_values(by="price", ascending=True)

    return result.head(top_n)
