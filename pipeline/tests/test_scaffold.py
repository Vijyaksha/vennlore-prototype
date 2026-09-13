def test_packages_import():
    import gps_core, gps_data, gps_engines.graph_v1  # noqa: F401
    assert gps_core.__version__ == "0.1.0"
