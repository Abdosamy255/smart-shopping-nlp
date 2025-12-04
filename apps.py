import streamlit as st
import pandas as pd

from nlp.preprocessing import preprocess_text
from nlp.attribute_extraction import extract_attributes
from search.search_engine import load_products, search_products

# =========================
# UI
# =========================

st.set_page_config(
    page_title="Smart Shopping Assistant",
    page_icon="🛒",
    layout="wide"
)

# Header
st.markdown("""
<div style="text-align:center; font-size:42px; font-weight:700;">
🛒 Smart Shopping Assistant
</div>
<p style="text-align:center; color:#aaa;">
Arabic NLP → Attribute Extraction → Product Ranking
</p>
<hr>
""", unsafe_allow_html=True)


# Input section
st.markdown("### 🔍 اكتب وصف المنتج :")
user_input = st.text_area(
    "",
    placeholder="مثال: عايز كوتش اسود مقاس 46 تحت 1500",
    height=80
)

search_btn = st.button("🔎 بحث", use_container_width=True)

@st.cache_data
def get_products_df():
    return load_products("data/products.csv")

df = get_products_df()


if search_btn:
    if not user_input.strip():
        st.warning("❗ اكتب وصف المنتج الأول.")
        st.stop()

    tokens = preprocess_text(user_input)
    attrs = extract_attributes(tokens)
    results = search_products(df, attrs, top_n=5)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### 🔤 1) Tokens")
        st.code(tokens)

        st.markdown("### 🧠 2) Attributes")
        st.json(attrs)

    with col2:
        st.markdown("### 🛍 3) Results")

        if results.empty:
            st.info("مافيش نتائج مناسبة بناءً على وصفك.")
        else:
            for i, row in results.iterrows():
                st.markdown(f"""
<div style="background:#1A1D23;padding:15px;border-radius:12px;margin-bottom:10px;">
<b style="font-size:20px;">{row['product_name']}</b><br>
🔖 Brand: <b>{row.get('brand','-')}</b><br>
💲 Price: <b>{row['price']} جنيه</b><br>
⭐ Rating: <b>{row.get('rating','-')}</b><br><br>
<a href="{row['link']}" target="_blank" style="
background:#00D09C;color:black;padding:6px 10px;border-radius:6px;text-decoration:none;">
رابط الشراء</a>
</div>
                """, unsafe_allow_html=True)
