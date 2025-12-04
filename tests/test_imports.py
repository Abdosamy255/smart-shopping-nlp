def test_app_imports():
    """Smoke test: importing `app` should expose `main` callable."""
    import importlib

    app = importlib.import_module('app')
    assert hasattr(app, 'main')
