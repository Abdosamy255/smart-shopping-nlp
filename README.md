# Smart Shopping Assistant (NLP Project)

Lightweight Streamlit app that accepts Arabic product descriptions, extracts attributes using simple NLP, and searches a local products dataset.

## Quick start

1. Create and activate a virtual environment (recommended).
2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Run the app:

```powershell
streamlit run app.py
```

## Project structure

- `app.py` — Streamlit front-end
- `nlp/` — NLP components (preprocessing, attribute extraction)
- `search/` — Search engine utilities
- `data/products.csv` — product dataset (update path in `app.py` if needed)

## Suggestions

- Add tests in `tests/` and enable CI (a sample workflow is included).
- Configure `pyproject.toml` or `setup.cfg` if packaging is needed.
