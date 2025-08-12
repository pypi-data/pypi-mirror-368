"""
This module contains functions to load data to oracle, postgres, snowflake,
and excel / csv or create dummy data for testing purposes.

Functions included:
- load_df
"""

import logging
import os
import random

import diskcache
import pandas as pd
import sqlalchemy as sql
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from sklearn.datasets import load_breast_cancer, make_classification
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine

from src import config

# set cache location
cache = diskcache.Cache(config.config_cache_path)

# set logger
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


def load_df(source, **kwargs):
    """
    loads data from oracle, postgres, snowflake, excel, csv or create dummy data
    :param: source: select data source
    :param: query: input your (sql) query if needed
    :param: path: path to file (csv or excel)
    :param: cache_duration: number of seconds data should stay in cache, default is 0
    :return: returns a pandas dataframe with result of your query or input file

    :Example:

    from dotenv import find_dotenv, load_dotenv
    from src.load.load_data import load_df

    # load env vars
    load_dotenv(find_dotenv())

    # load data with caching
    load_df(source="oracle", query="select * from ...", cache_duration=3600")

    # load data without caching
    load_df(source="csv", path="data/file.csv")

    # clear cache if data is changed
    cache.clear()

    """

    # set cache duration in seconds
    cache_duration = kwargs.get("cache_duration", 0)

    if source == "oracle":
        # create engine
        engine = sql.create_engine(config.config_oracle_dwh_connection_string)

        # set default query for oracle
        query = kwargs.get("query", "select * from dual")

        # run query
        if cache_duration > 0 and query not in cache:
            _logger.info("cache oracle data")
            cache.set(
                key=query,
                value=pd.read_sql(query, engine),
                expire=cache_duration,
            )
        if cache_duration > 0 and query in cache:
            df = cache[query]
            _logger.info(f"loaded oracle data from cache; {len(df)} rows")
        else:
            df = pd.read_sql_query(sql=query, con=engine)
            _logger.info(f"loaded oracle data; {len(df)} rows")

        del engine

    if source == "postgres":
        # create engine
        engine = sql.create_engine(config.config_postgres_dwh_connection_string)

        # set default query for oracle
        query = kwargs.get("query", "select * from customer_master limit 5")

        # run query
        if cache_duration > 0 and query not in cache:
            _logger.info("cache postgres data")
            cache.set(
                key=query,
                value=pd.read_sql_query(sql=query, con=engine),
                expire=cache_duration,
            )
        if cache_duration > 0 and query in cache:
            df = cache[query]
            _logger.info(f"loaded postgres data from cache; {len(df)} rows")
        else:
            df = pd.read_sql_query(sql=query, con=engine)
            _logger.info(f"loaded postgres data; {len(df)} rows")

        del engine

    if source == "snowflake":

        def get_snowflake_engine():
            account = os.getenv("SF_ACCOUNT")
            user = os.getenv("SF_USERNAME")
            pkb = _get_snowflake_key()
            db = os.getenv("SF_DATABASE")
            schema = os.getenv("SF_SCHEMA")
            warehouse = os.getenv("SF_WAREHOUSE")
            role = os.getenv("SF_ROLE")

            return create_engine(
                URL(
                    account=account,
                    user=user,
                    database=db,
                    schema=schema,
                    warehouse=warehouse,
                    role=role,
                ),
                connect_args={"private_key": pkb},
            )

        def _get_snowflake_key():
            with open(os.getenv("SF_KEY_PATH"), "rb") as key:
                p_key = serialization.load_pem_private_key(
                    key.read(),
                    password=os.getenv("SF_PRIVATE_KEY_PASSPHRASE").encode(),
                    backend=default_backend(),
                )

            pkb = p_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )

            return pkb

        # set default query for snowflake
        query = kwargs.get("query", "select * from kafka_dsp.dsp_nba limit 5")

        # run query
        if cache_duration > 0 and query not in cache:
            _logger.info("cache snowflake data")
            cache.set(
                key=query,
                value=pd.read_sql_query(sql=query, con=get_snowflake_engine()),
                expire=cache_duration,
            )
        if cache_duration > 0 and query in cache:
            df = cache[query]
            _logger.info(f"loaded snowflake data from cache; {len(df)} rows")
        else:
            df = pd.read_sql_query(sql=query, con=get_snowflake_engine())
            _logger.info(f"loaded snowflake data; {len(df)} rows")

    if source == "csv":
        # set default path to dummy csv file
        path = kwargs.get("path", "data/dummy.csv")

        # get data
        if cache_duration > 0 and path not in cache:
            _logger.info("cache postgres data")
            cache.set(
                key=path,
                value=pd.read_csv(path),
                expire=cache_duration,
            )
        if cache_duration > 0 and path in cache:
            df = cache[path]
            _logger.info(f"loaded csv data from cache; {len(df)} rows")
        else:
            df = pd.read_csv(path)
            _logger.info(f"loaded csv data; {len(df)} rows")

    if source == "excel":
        # set default path to dummy csv file
        path = kwargs.get("path", "data/dummy.xlsx")

        # get data
        if cache_duration > 0 and path not in cache:
            _logger.info("cache excel data")
            cache.set(
                key=path,
                value=pd.read_excel(path),
                expire=cache_duration,
            )
        if cache_duration > 0 and path in cache:
            df = cache[path]
            _logger.info(f"loaded excel data from cache; {len(df)} rows")
        else:
            df = pd.read_excel(path)
            _logger.info(f"loaded excel data; {len(df)} rows")

    if source == "make":

        def make_data(n_samples=10, n_features=10, missing_data=False, bins=False):
            """creates training data"""
            X, y = make_classification(
                n_samples=n_samples,
                n_features=n_features,
                n_informative=int(n_features / 2),
                n_classes=2,
                weights=([0.9, 0.1]),
            )
            df_result = pd.DataFrame(X, y)
            df_result = df_result.rename(columns=lambda x: "feature_" + str(x))
            df_result = df_result.reset_index().rename(columns={"index": "label"})
            if bins:
                columns = list(df_result.columns)
                columns.remove("label")
                cols_to_process = random.sample(columns, round(n_features / 3))
                for i in cols_to_process:
                    df_result[i] = pd.qcut(
                        df_result[i], q=3, labels=["a", "b", "c"], duplicates="drop"
                    )
            if missing_data:
                for i in df_result.columns[1:]:
                    # reassign w/ sample results in nan's due to auto-alignment
                    df_result[i] = df_result[i].sample(frac=random.uniform(0.9, 1))
            return df_result

        # make data
        if cache_duration > 0 and "make" not in cache:
            _logger.info("cache dummy data")
            cache.set(
                key="make",
                value=make_data(),
                expire=cache_duration,
            )
        if cache_duration > 0 and "make" in cache:
            df = cache[query]
            _logger.info(f"loaded dummy data from cache; {len(df)} rows")
        else:
            df = make_data()
            _logger.info(f"loaded dummy data; {len(df)} rows")

    if source == "dummy":
        df = load_breast_cancer(as_frame=True)["frame"]

    return df
