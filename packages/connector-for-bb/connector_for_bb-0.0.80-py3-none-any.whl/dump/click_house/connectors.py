from typing import Any, Dict

import clickhouse_connect
from pandas import DataFrame as PandasDataFrame

from dump.config_utils import load_config


CH_TO_PYTHON_TYPE_MAPPER = {
    # Boolean
    "Bool": "bool",
    # Integers (signed)
    "Int8": "Int8",
    "Int16": "Int16",
    "Int32": "Int32",
    "Int64": "Int64",
    # Integers (unsigned)
    "UInt8": "Int8",
    "UInt16": "Int16",
    "UInt32": "Int32",
    "UInt64": "Int64",
    # Floating point
    "Float32": "float32",
    "Float64": "float64",
    # Temporal
    "timestamp": "timestamp",
    "date": "timestamp",
    # Strings
    "String": "str",
}


class ConnectorCH:
    def __init__(
        self,
        db_config_name: str = "click_house",
    ) -> None:
        self.db_config_name = db_config_name
        self.__config = load_config(section=self.db_config_name)

        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                self._client = clickhouse_connect.get_client(**self.__config)
                # print("Connected to the ClickHouse server.")
            except Exception as error:
                print(error)
        return self._client


class TableCH(ConnectorCH):
    def __init__(self, db_config_name: str = "click_house") -> None:
        super().__init__(db_config_name)

    def get_df(self, query: str) -> PandasDataFrame:
        return self.client.query_df(query)


class DBUtilsCH(ConnectorCH):
    @staticmethod
    def _validate_output(inp: list):
        return [x[0] for x in inp]

    def get_table_structure(
        self, table_name: str, database: str = "default"
    ) -> Dict[str, Any]:
        query = f"""
            SELECT name, type, position
            FROM system.columns
            WHERE table = '{table_name}' AND database = '{database}'
        """

        schema = {}
        result = self.client.query(query)
        for column_name, data_type, position in result.result_rows:
            orig_data_type = data_type
            if "int" in data_type and data_type not in CH_TO_PYTHON_TYPE_MAPPER.keys():
                data_type = "integer"
            if (
                "numeric" in data_type or "decimal" in data_type
            ) and data_type not in CH_TO_PYTHON_TYPE_MAPPER.keys():
                data_type = "decimal"
            if "time" in data_type:
                data_type = "timestamp"

            schema[column_name] = {
                "data_type": CH_TO_PYTHON_TYPE_MAPPER.get(data_type, "str"),
                "orig_data_type": orig_data_type,
                "is_nullable": False,
                "position": position,
            }
        return schema
