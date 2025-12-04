import os
import sys
import time
from datetime import datetime

import streamlit as st
import pandas as pd

# لو في مشكلة imports نضمن إن الجذر في الـ path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from nlp.preprocessing import preprocess_text
from nlp.attribute_extraction import extract_attributes
from search.search_engine import load_products, search_products

# =========================
# إعداد الصفحة
# =========================
st.set_page_config(
    page_title="Smart Shopping Assistant",
    page_icon="🛒",
    layout="wide"
)

# تهيئة الـ session_state للتاريخ
if "history" not in st.session_state:
    st.session_state.history = []  # كل عنصر: {"time", "query", "attrs", "count"}

# =========================
# دوال مساعدة
# =========================

@st.cache_data
def get_products_df():
    return load_products("data/products.csv")

def run_search(df: pd.DataFrame, user_input: str):
    """NLP + Search + إرجاع (tokens, attrs, results_df)."""
    tokens, lang = preprocess_text(user_input)        # 👈 فكّينا الاتنين
    attrs = extract_attributes(tokens, lang)          # 👈 مرّرنا lang
    results = search_products(df, attrs, top_n=50)
    return tokens, attrs, results


def apply_ui_filters(results: pd.DataFrame, sort_by: str, sort_dir: str,
                     max_price: float | None, brand_filter: str | None):
    df = results.copy()

    if max_price is not None and "price" in df.columns:
        df = df[df["price"] <= max_price]

    if brand_filter and brand_filter != "All" and "brand" in df.columns:
        df = df[df["brand"].fillna("").str.contains(brand_filter, case=False, na=False)]

    # ترتيب
    if sort_by and sort_by in df.columns:
        ascending = (sort_dir == "Ascending")
        df = df.sort_values(by=sort_by, ascending=ascending)

    return df

def render_product_card(row: pd.Series):
    """عرض كارت منتج واحد بـ HTML بسيط."""
    name = row.get("product_name", "Unknown product")
    brand = row.get("brand", "-")
    price = row.get("price", "-")
    rating = row.get("rating", "-")
    link = row.get("link", "#")
    img = row.get("image_url", None)

    left, right = st.columns([1, 3])

    with left:
        if isinstance(img, str) and img.strip():
            st.image(img, use_column_width=True)
        else:
            st.markdown(
                "<div style='width:100%;height:100px;border-radius:12px;"
                "background:linear-gradient(135deg,#00D09C33,#ffffff11);"
                "display:flex;align-items:center;justify-content:center;font-size:32px;'>🛍</div>",
                unsafe_allow_html=True
            )

    with right:
        st.markdown(
            f"""
<div style="background:#1A1D23;padding:14px;border-radius:12px;margin-bottom:6px;">
  <div style="font-size:20px;font-weight:700;margin-bottom:4px;">{name}</div>
  <div>🔖 <b>Brand:</b> {brand}</div>
  <div>💲 <b>Price:</b> {price} جنيه</div>
  <div>⭐ <b>Rating:</b> {rating}</div>
  <div style="margin-top:8px;">
    <a href="{link}" target="_blank"
       style="background:#00D09C;color:black;padding:6px 10px;border-radius:6px;
              text-decoration:none;font-weight:600;">
      رابط الشراء
    </a>
  </div>
</div>
""",
            unsafe_allow_html=True
        )


# =========================
# الهيدر العام
# =========================

st.markdown(
    """
<style>
/* شوية تحسينات شكلية عامة */
html, body, [class*="css"]  {
    font-family: "Segoe UI", "Cairo", sans-serif;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div style="text-align:center; font-size:40px; font-weight:700; margin-bottom:4px;">
🛒 Smart Shopping Assistant
</div>
<p style="text-align:center; color:#aaaaaa; margin-top:0;">
Arabic NLP → Attribute Extraction → Product Ranking
</p>
<hr>
""",
    unsafe_allow_html=True,
)

# =========================
# Sidebar (فلترة + Sorting)
# =========================

st.sidebar.header("⚙️ Controls")

df_products = get_products_df()

# أقصى سعر
max_price_val = None
if "price" in df_products.columns:
    sidebar_max_price = st.sidebar.number_input(
        "أقصى سعر (اختياري)",
        min_value=0,
        value=0,
        step=100
    )
    if sidebar_max_price > 0:
        max_price_val = float(sidebar_max_price)

# فلتر البراند
brand_filter = None
if "brand" in df_products.columns:
    brands = sorted([b for b in df_products["brand"].dropna().unique() if str(b).strip()])
    brand_options = ["All"] + brands
    brand_filter = st.sidebar.selectbox("فلترة حسب البراند", brand_options, index=0)

# Sorting
sort_by = st.sidebar.selectbox(
    "ترتيب حسب",
    options=["price", "rating", "product_name"] if "rating" in df_products.columns else ["price", "product_name"],
    index=0
)
sort_dir = st.sidebar.radio("اتجاه الترتيب", ["Ascending", "Descending"], index=0)

st.sidebar.markdown("---")
st.sidebar.write("✳️ كل بحث جديد بيتسجل في صفحة **History**.")


# =========================
# Tabs
# =========================

tab_search, tab_history, tab_about = st.tabs(["🔍 Search", "🕒 History", "ℹ️ About"])

# ---------- TAB 1: Search ----------
with tab_search:
    st.markdown("### 🔍 اكتب وصف المنتج")

    default_text = "عايز كوتش اسود مقاس 46 تحت 1500"
    user_input = st.text_area(
        "وصف المنتج",
        placeholder=default_text,
        height=80
    )

    search_clicked = st.button("🚀 ابحث", use_container_width=True)

    if search_clicked:
        if not user_input.strip():
            st.warning("اكتب وصف المنتج الأول.")
        else:
            with st.spinner("جاري تحليل النص والبحث عن أفضل المنتجات..."):
                tokens, attrs, base_results = run_search(df_products, user_input)
                # تطبيق الفلاتر و الـ Sorting من الـ Sidebar
                final_results = apply_ui_filters(
                    base_results,
                    sort_by=sort_by,
                    sort_dir=sort_dir,
                    max_price=max_price_val,
                    brand_filter=brand_filter
                )
                time.sleep(0.3)

            # حفظ في التاريخ
            st.session_state.history.insert(
                0,
                {
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "query": user_input,
                    "attrs": attrs,
                    "count": int(len(final_results))
                }
            )

            # عرض NLP details
            col_tokens, col_attrs = st.columns(2)
            with col_tokens:
                st.markdown("### 🔤 Tokens بعد الـ Preprocessing")
                st.code(tokens)

            with col_attrs:
                st.markdown("### 🧠 السمات المستخرجة (Attributes)")
                st.json(attrs)

            st.markdown("### 🛍 النتائج")

            if final_results.empty:
                st.info("❌ لا توجد نتائج مطابقة بناءً على الوصف والفلاتر الحالية.")
            else:
                st.success(f"✅ عدد النتائج بعد الفلترة: {len(final_results)} (من {len(base_results)} نتيجة مبدئية)")

                # نعرض أول 5 ككروت مع شوية animation بسيطة
                top_cards = final_results.head(5)
                for _, row in top_cards.iterrows():
                    render_product_card(row)
                    time.sleep(0.05)

                # وبعدين جدول كامل لو حابب
                with st.expander("عرض كل النتائج في جدول"):
                    st.dataframe(final_results.reset_index(drop=True))

# ---------- TAB 2: History ----------
with tab_history:
    st.markdown("### 🕒 Search History")

    if not st.session_state.history:
        st.info("لسه ماعملتش أي بحث.")
    else:
        # عرض قائمة بالتاريخ
        for item in st.session_state.history:
            st.markdown(
                f"""
- **{item['time']}**  
  - Query: `{item['query']}`  
  - Results: **{item['count']}**  
  - Attributes: `{item['attrs']}`
"""
            )

        # جدول ملخص
        st.markdown("---")
        st.markdown("#### Summary Table")
        hist_df = pd.DataFrame(st.session_state.history)
        st.dataframe(hist_df)

        if st.button("🧹 مسح التاريخ بالكامل"):
            st.session_state.history = []
            st.experimental_rerun()

# ---------- TAB 3: About ----------
with tab_about:
    st.markdown("### ℹ️ About Project")
    st.write(
        """
هذا المشروع هو **Smart Shopping Assistant** لمادة **NLP**:

- يفهم وصف المنتج بالعربي (Natural Language).
- يطبق خطوات Text Preprocessing:
  - Normalization
  - Tokenization
  - Stopwords Removal
- يستخرج السمات (Attributes) مثل:
  - نوع المنتج (Product)
  - اللون (Color)
  - المقاس (Size)
  - الميزانية (Budget)
  - البراند (Brand)
- يبحث في قاعدة بيانات منتجات (CSV) ويرتب النتائج حسب السعر أو التقييم.

يمكن تطويره لاحقًا ليتصل بمواقع حقيقية (Jumia / Noon / Amazon) أو استخدام Models أقوى (BERT, LLMs).
"""
    )
    st.markdown("---")
    st.markdown("👨‍💻 *Built by: Your Team (Third Year AI / NLP)*")
