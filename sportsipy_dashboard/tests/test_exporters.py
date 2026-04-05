"""Tests for exporters module."""
import pytest
import pandas as pd
from sportsipy_dashboard.utils.exporters import export_dataframe, EXPORT_FORMATS


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "team": ["BOS", "NYY", "LAD"],
        "wins": [95, 92, 100],
        "losses": [67, 70, 62],
    })


def test_export_csv(sample_df):
    data, filename, mime = export_dataframe(sample_df, "csv")
    assert b"BOS" in data
    assert filename.endswith(".csv")
    assert mime == "text/csv"


def test_export_json(sample_df):
    data, filename, mime = export_dataframe(sample_df, "json")
    assert b"BOS" in data
    assert filename.endswith(".json")


def test_export_excel(sample_df):
    data, filename, mime = export_dataframe(sample_df, "excel")
    assert len(data) > 0
    assert filename.endswith(".xlsx")


def test_export_parquet(sample_df):
    data, filename, mime = export_dataframe(sample_df, "parquet")
    assert len(data) > 0
    assert filename.endswith(".parquet")


def test_export_sqlite(sample_df):
    data, filename, mime = export_dataframe(sample_df, "sqlite")
    assert len(data) > 0
    assert filename.endswith(".db")


def test_export_xml(sample_df):
    data, filename, mime = export_dataframe(sample_df, "xml")
    assert b"<" in data


def test_export_tsv(sample_df):
    data, filename, mime = export_dataframe(sample_df, "tsv")
    assert b"\t" in data


def test_export_h5(sample_df):
    data, filename, mime = export_dataframe(sample_df, "h5")
    assert len(data) > 0


def test_invalid_format(sample_df):
    with pytest.raises(ValueError):
        export_dataframe(sample_df, "invalid_format")


def test_all_formats_in_config():
    for fmt in EXPORT_FORMATS:
        assert "label" in EXPORT_FORMATS[fmt]
        assert "extension" in EXPORT_FORMATS[fmt]
        assert "mime" in EXPORT_FORMATS[fmt]
