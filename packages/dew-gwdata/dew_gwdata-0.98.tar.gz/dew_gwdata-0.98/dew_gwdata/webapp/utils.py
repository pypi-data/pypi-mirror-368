from datetime import datetime
from pathlib import Path
import sqlite3
import tempfile
import zipfile

import pandas as pd
import ausweather
import dew_gwdata as gd

import logging

logger = logging.getLogger(__name__)


def prep_table_for_html(df, query=None, env="prod"):
    for idx, well in df.reset_index().iterrows():
        query_params = [f"dh_no={well.dh_no:.0f}"]
        dh_query_params = "&".join(query_params)
    if not query is None:
        env = query.env
    title_series = df.apply(
        lambda well: (
            f'<nobr><a href="/app/well_summary?dh_no={well.dh_no}&env={env}">'
            f'{make_dh_title(well, elements=("unit_no", "obs_no"))}</a></nobr>'
        ),
        axis=1,
    )
    df.insert(0, "title", title_series)
    df.insert(6, "suburb", gd.locate_wells_in_suburbs(df))
    df.insert(
        7,
        "rf_site",
        df.unit_hyphen.apply(
            lambda n: f"<a href='/app/rainfall_stations?nearest_to_well={n}'><img src='/static/external-link.svg' width=12 height=12 /></a>"
        ),
    )
    for col in ["unit_hyphen", "obs_no"]:
        if col in df.columns:
            df = df.drop([col], axis=1)
    if "aquifer" in df.columns:
        df["aquifer"] = df.apply(
            lambda row: (
                f"<a href='/app/aquifer_unit?aquifer_code={row.aquifer}&env={env}'>{row.aquifer}</a>"
                if row.aquifer
                else ""
            ),
            axis=1,
        )
    return df


def make_dh_title(well, elements=("unit_no", "obs_no", "dh_name")):
    data = dict(
        dh_no=f"DH {well.dh_no}",
        unit_no=str(well.unit_hyphen).replace("None", ""),
        obs_no=str(well.obs_no).replace("None", ""),
        dh_name=str(well.dh_name).replace("None", ""),
        aquifer=str(well.aquifer).replace("None", ""),
    )
    components = [data[x] for x in elements]
    valid_components = [c for c in components if c]
    if len(valid_components) == 0:
        valid_components = [data["dh_no"]]
    title = " / ".join(valid_components)
    if data["aquifer"]:
        title += f" ({data['aquifer']})"
    return title


def format_datetime(dt):
    try:
        tstamp = pd.Timestamp(dt)
    except:
        return dt
    else:
        if pd.isnull(tstamp):
            return ""
        else:
            if tstamp.hour == tstamp.minute == tstamp.second == 0:
                return tstamp.strftime("%d/%m/%Y")
            else:
                return tstamp.strftime("%d/%m/%Y %H:%M:%S")


def frame_to_html(
    df,
    transpose_last=False,
    apply=None,
    apply_kws=None,
    remove_col_underscores=True,
    bold_rows=False,
    add_username_links=True,
    **kwargs,
):
    if apply_kws is None:
        apply_kws = {}
    if remove_col_underscores:
        df.columns = [str(c).replace("_", " ") for c in df.columns]
    for col in df.columns:
        if "date" in col:
            df[col] = df[col].apply(lambda v: f"<nobr>{format_datetime(v)}</nobr>")
        if col in ("unit hyphen", "unit no"):
            df[col] = df[col].apply(lambda v: f"<nobr>{v}</nobr>")
    df = df.fillna("")
    kwargs["escape"] = False
    if add_username_links:
        url = "/app/schema_data?owner=DHDB&table_name=MS_USER_VW&limit=200&filter_by=&select=*&where=user_code%3D%27{username}%27&order_by=&env=prod&transpose=Y"
        for col in df.columns:
            if col.endswith("_by") or col.endswith(" by"):
                df[col] = df[col].apply(
                    lambda v: f"<a href='{url.format(username=v)}'>{v}</a>"
                )

    if transpose_last:
        df = df.T
    df = df.map(lambda s: s.replace("\n", "<br />") if isinstance(s, str) else s)
    df = df.map(lambda s: s.replace("\n", "<br />") if isinstance(s, str) else s)

    if apply is None:
        table_html = df.to_html(classes="", bold_rows=bold_rows, **kwargs)
    else:
        if "subset" in apply_kws:
            apply_kws["subset"] = [col.replace("_", " ") for col in apply_kws["subset"]]

        styler = df.style.apply(apply, **apply_kws)
        table_html = styler.to_html(bold_rows=bold_rows)
    return "<div class='table-outer-wrapper'>" + table_html + "</div>"


def series_to_html(s, transpose=True, **kwargs):
    assert isinstance(s, pd.Series)
    df = s.to_frame()
    if transpose:
        df = df.T
    return frame_to_html(df, transpose_last=True, **kwargs)


import numpy as np

BASE_CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-~_"


def to_deltas(arr):
    arr = np.asarray(arr)
    arr = np.sort(arr)
    return np.diff(arr, prepend=0)


def from_deltas(arr):
    return np.cumsum(arr)


def encode(n, characters):
    base = len(characters)
    result = []
    i = 0
    while n > 0:
        i += 1
        quotient = n // base
        remainder = n % base
        result.append(characters[remainder])
        n = quotient
    encoded = "".join(result[::-1])
    return encoded


def decode(s, characters):
    base = len(characters)
    n = 0
    for i, char in enumerate(s[::-1]):
        n += (base**i) * characters.index(char)
    return n


def dhnos_to_urlstr(dh_nos):
    deltas = to_deltas(dh_nos)
    encoded = [encode(d, BASE_CHARS) for d in deltas]
    return ".".join(encoded)


def urlstr_to_dhnos(url_str):
    decoded = [decode(s, BASE_CHARS) for s in url_str.split(".")]
    return from_deltas(decoded)


def fmt_for_js(x):
    if str(x).startswith("new Date("):
        return x
    elif isinstance(x, str):
        return '"' + x.replace('"', "'") + '"'
    elif x is None:
        return '""'
    elif pd.isnull(x):
        return ""
    else:
        return str(x)


def open_db(fn=None):
    """Open the local webapp database

    Returns:
        sqlite3.Connection: A database connection. You need to remember
        to close it."""

    if fn is None:
        fn = Path(__file__).parent / "dew_gwdata.webapp.db"
        logger.debug(f"opening db fn=None therefore fn={fn}")

    create_table = """
    CREATE TABLE IF NOT EXISTS "daily_rainfall" (
    	"id"	TEXT UNIQUE,
    	"station_id"	TEXT NOT NULL,
    	"date"	TEXT NOT NULL,
    	"rainfall"	REAL NOT NULL,
    	"interpolated_code"	INTEGER NOT NULL,
    	"quality"	INTEGER NOT NULL,
        "date_added" TEXT NOT NULL
    );
    """
    conn = sqlite3.connect(str(fn))
    cursor = conn.cursor()
    cursor.execute(create_table)
    conn.commit()
    return conn


def write_daily_rainfall_to_db(station_id, df, conn):
    """Write daily rainfall data to the database.

    Args:
        station_id (str)
        df (pd.DataFrame): daily data with columns "date", "rainfall", "interpolated_code", and "quality"
        conn (sqlite3.Connection): the table "daily_rainfall" will be used.

    """
    if isinstance(station_id, float):
        station_id = int(station_id)
    station_id = str(station_id)

    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")

    for idx, row in df.iterrows():
        db_id = f"{station_id}.{row.date.strftime('%Y%m%d')}"
        values = (
            db_id,
            station_id,
            row["date"].strftime("%Y-%m-%d"),
            row.rainfall,
            row.interpolated_code,
            row.quality,
            today,
        )
        cursor.execute(
            """
            INSERT OR IGNORE INTO daily_rainfall (id, station_id, date, rainfall, interpolated_code, quality, date_added)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            values,
        )
        cursor.execute(
            """
            UPDATE daily_rainfall SET rainfall = ?, interpolated_code = ?, quality = ?, date_added = ? WHERE id = ?
            """,
            (row.rainfall, row.interpolated_code, row.quality, today, db_id),
        )
    conn.commit()


def load_rainfall_from_db(station_id, conn, **kwargs):
    """Read rainfall data from database.

    Args:
        station_id (str)
        conn (sqlite3.Connection)

    Returns:
        ausweather.RainfallStationData

    """
    cursor = conn.cursor()
    df = pd.read_sql(
        f"select * from daily_rainfall where station_id = '{station_id}'", conn
    )
    df["date"] = pd.to_datetime(df.date)
    df["year"] = df.date.dt.year
    df["dayofyear"] = df.date.dt.dayofyear
    df["finyear"] = [ausweather.date_to_finyear(d) for d in df["date"]]
    return ausweather.RainfallStationData.from_data(station_id, df, **kwargs)


def multiprocess_photo_zipfile(args, ret_dict):
    zfn = produce_photo_zip(args)
