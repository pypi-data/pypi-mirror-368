def test_version_imports():
    import importlib
    pkg = importlib.import_module("adaptive_solve_planner")
    assert hasattr(pkg, "__version__")
