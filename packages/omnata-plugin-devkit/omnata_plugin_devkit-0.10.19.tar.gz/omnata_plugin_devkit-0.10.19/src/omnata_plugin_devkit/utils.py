import contextlib
import os,json
from typing import Any, Dict, List
from snowflake.snowpark import Session, Row
import snowflake.connector
from snowflake.connector.connection import SnowflakeConnection
from .snowcli.cli.app.snow_connector import connect_to_snowflake as snowcli_connect_to_snowflake

# we set the paramstyle to 'qmark' to be compatible with Snowpark
snowflake.connector.paramstyle='qmark'

@contextlib.contextmanager
def cd_temporarily(new_path):
    original_path = os.getcwd()
    os.chdir(new_path)
    try:
        yield
    finally:
        os.chdir(original_path)

def get_snowflake_connection(connection_name:str="dev", **overrides) -> SnowflakeConnection:
    # Connect to Snowflake
    with cd_temporarily(os.path.expanduser("~")):
        return snowcli_connect_to_snowflake(connection_name=connection_name, **overrides)

def get_snowpark_session(connection_name:str="dev", **overrides) -> Session:
    builder = Session.builder
    builder._options["connection"] = get_snowflake_connection(connection_name, **overrides)
    return builder.create()

def handle_stored_proc_result(rows:List[Row]) -> Any:
    if len(rows) == 0:
        raise ValueError("No result returned from stored procedure")
    result:Dict[str,Any] = json.loads(rows[0][0])
    if result["success"] is not True:
        raise ValueError(result["error"])
    return result["data"]
