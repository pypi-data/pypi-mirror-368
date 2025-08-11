import json

import pandas as pd
from sqlalchemy import create_engine


def get_connection_string(
    engine: str,
    driver: str,
    username: str,
    password: str,
    host: str,
    database: str,
) -> str:
    return f"{engine}+{driver}://{username}:{password}@{host}/{database}"


def flash_to_database_format(data: pd.DataFrame) -> pd.DataFrame:
    """Transform the data in *flash* format to data in *database* format

    This operation takes a little while"""

    data.columns.name = "name"
    stacked_data = data.stack().to_frame(name="value")
    database_data = stacked_data.reset_index()
    database_data["dimensions"] = database_data.apply(
        lambda row: json.dumps(
            {
                "offset": row["offset"],
                "difference_type": row["difference_type"],
                "stat": row["stat"],
            }
        ),
        axis=1,
    )
    database_data = database_data.drop(
        columns=["offset", "difference_type", "stat"]
    )
    database_data["value_meta"] = pd.NA
    print(database_data)
    return database_data


def database_to_flash_format():
    pass


def push_to_database(data: pd.DataFrame, conn_string: str, table: str) -> None:
    engine = create_engine(url=conn_string)
    data.to_sql(
        name=table, con=engine, if_exists="append", chunksize=1000, index=False
    )


# this may be just as a datasource (maybe a common protocol?)
# check the api long video for further reference
def pull_from_database(
    conn_string: str, start: str, end: str, series: list[str]
):
    # just testing...
    pd.read_sql_query(
        """
        SELECT date, value
            FROM measurements
            WHERE
                date BETWEEN '2007-12-31' AND '2025-04-10' AND name='ES10YT=RR_DIFF' AND
                dimensions @> '{"offset":"no", "stat":"value"}'
            ORDER BY date ASC
        """
    )
