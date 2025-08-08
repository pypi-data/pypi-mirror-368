from pathlib import Path
import sqlite3
import pandas as pd

from dew_gwdata import utils


def connect_to_webapp_database():
    from dew_gwdata.webapp.utils import open_db

    return open_db()


class ExtractionInjectionDatabase:
    def __init__(self, webapp_db=None, sagd_db=None, sagd_env="prod"):
        if webapp_db is None:
            self.webapp_db = connect_to_webapp_database()
        else:
            self.webapp_db = webapp_db

        if sagd_db is None:
            from dew_gwdata.sageodata_database import connect

            self.sagd_db = connect(service_name=sagd_env)
        else:
            self.sagd_db = sagd_db

    def query(self, sql, **kwargs):
        dfs = []
        query = utils.SQL(sql, **kwargs)
        query.chunksize = 1000
        for subquery in query:
            dfs.append(pd.read_sql(subquery, self.webapp_db))
        return pd.concat(dfs)

    def query_usage_for_drillholes(self, dh_nos):
        sql = """select * from usage
        where unit_hyphen in {UNIT_HYPHEN}
        and month is null
        """
        dh_df = self.sagd_db.drillhole_details(dh_nos)
        unit_hyphens = dh_df.dropna(subset=["unit_hyphen"]).unit_hyphen.unique()
        return self.query(sql, unit_hyphen=unit_hyphens)
        # usage = pd.read_sql(
        #     f"select * from usage where unit_hyphen = '{well.unit_hyphen}' and month is null",
        #     wdb,
        # )
