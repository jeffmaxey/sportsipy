"""Export DataFrame to various formats."""
import io
import logging
import os
import sqlite3
import tempfile
from typing import Union

import pandas as pd

logger = logging.getLogger(__name__)

EXPORT_FORMATS = {
    "csv": {"label": "CSV", "extension": ".csv", "mime": "text/csv"},
    "tsv": {"label": "TSV (Text)", "extension": ".tsv", "mime": "text/plain"},
    "json": {"label": "JSON", "extension": ".json", "mime": "application/json"},
    "xml": {"label": "XML", "extension": ".xml", "mime": "application/xml"},
    "excel": {
        "label": "Excel",
        "extension": ".xlsx",
        "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    },
    "parquet": {"label": "Parquet", "extension": ".parquet", "mime": "application/octet-stream"},
    "h5": {"label": "HDF5", "extension": ".h5", "mime": "application/octet-stream"},
    "sqlite": {"label": "SQLite3", "extension": ".db", "mime": "application/octet-stream"},
}


def export_dataframe(df: pd.DataFrame, fmt: str, table_name: str = "data") -> tuple[bytes, str, str]:
    """Export a DataFrame to bytes in the specified format.

    Args:
        df: The DataFrame to export.
        fmt: Format key (e.g. 'csv', 'json', 'excel').
        table_name: Table or key name used for formats that require it.

    Returns:
        Tuple of (data_bytes, filename, mime_type).

    Raises:
        ValueError: If fmt is not a recognized export format.
    """
    if fmt not in EXPORT_FORMATS:
        raise ValueError(
            f"Unknown export format '{fmt}'. Valid options: {list(EXPORT_FORMATS)}"
        )

    config = EXPORT_FORMATS[fmt]
    filename = f"{table_name}{config['extension']}"
    mime = config["mime"]
    logger.info("Exporting DataFrame (%d rows) as %s", len(df), fmt)

    if fmt == "csv":
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        return buf.getvalue().encode("utf-8"), filename, mime

    elif fmt == "tsv":
        buf = io.StringIO()
        df.to_csv(buf, sep="\t", index=False)
        return buf.getvalue().encode("utf-8"), filename, mime

    elif fmt == "json":
        data = df.to_json(orient="records", indent=2)
        return data.encode("utf-8"), filename, mime

    elif fmt == "xml":
        xml_str = df.to_xml(index=False)
        return xml_str.encode("utf-8"), filename, mime

    elif fmt == "excel":
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=table_name[:31])
        return buf.getvalue(), filename, mime

    elif fmt == "parquet":
        buf = io.BytesIO()
        df.to_parquet(buf, index=False, engine="pyarrow")
        return buf.getvalue(), filename, mime

    elif fmt == "h5":
        fd, tmp_path = tempfile.mkstemp(suffix=".h5")
        os.close(fd)
        try:
            df.to_hdf(tmp_path, key=table_name, mode="w")
            with open(tmp_path, "rb") as f:
                data = f.read()
        finally:
            os.unlink(tmp_path)
        return data, filename, mime

    elif fmt == "sqlite":
        fd, tmp_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            conn = sqlite3.connect(tmp_path)
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            conn.close()
            with open(tmp_path, "rb") as f:
                data = f.read()
        finally:
            os.unlink(tmp_path)
        return data, filename, mime

    raise ValueError(f"Unhandled format: {fmt}")
