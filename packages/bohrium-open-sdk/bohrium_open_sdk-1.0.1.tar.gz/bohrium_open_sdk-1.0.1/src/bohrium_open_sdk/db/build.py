# -*- coding: UTF-8 -*-
from typing import List

from bohrium_open_sdk.db.node import Op, OperatorNode, Condition
from bohrium_open_sdk.db.app import App
import json

def Where(key: str, op: Op, value) -> OperatorNode:
    return OperatorNode(None, Condition.AND).And(key, op, value)

class TableExt:
    def __init__(self, desc_rows:int, desc_info: List[list]):
        """初始化表扩展信息。
        Args:
            desc_rows (int): 描述信息的行数。
            desc_info (List[list]): 描述详情。
        """
        self.desc_rows = desc_rows
        self.desc_info = desc_info

class SQLClient:
    def __init__(self, app_key, access_key=None, openapi_addr=None, timeout=60):
        self.app_key = app_key
        self.ak = access_key
        self._app = App(base_url=openapi_addr, access_key=access_key, app_key=app_key, timeout=timeout)
        self._app_id = ""

    def table(self, name):
        if name is None:
            raise ValueError("name not right")

        return SQL(name, self._app_id, self._app)

    def table_with_ak(self, table_ak):
        if table_ak == "":
            raise ValueError("table_ak not right")

        return SQL("", self._app_id, self._app, table_ak)

    def db_with_ak(self, db_ak):
        if db_ak == "":
            raise ValueError("db_ak not right")

        return SQL("", self._app_id, self._app, "", db_ak)


class SQL:
    def __init__(self, table, app_id, app: App, table_ak="", db_ak=""):
        self.table = table
        self.table_ak = table_ak
        self.db_ak = db_ak
        self.root = None
        self._page = 1
        self._page_size = 10
        self._select = []
        self._data = []
        self._order = []
        self._app = app
        self._app_id = app_id

    def Select(self, *args):
        for key in args:
            self._select.append(key)
        return self

    def Where(self, key: str, op: Op, value):
        if self.root is None:
            self.root = Where(key, op, value)
        else:
            self.root.And(key, op, value)
        return self

    def Or(self, *args):
        if self.root is None:
            length = len(args)
            if length == 1:
                self.root = args[0]
            elif length == 3:
                self.root = Where(args[0], args[1], args[2])
            else:
                raise ValueError(f"The number of parameters is incorrect, must be 1 or 3, but got {length}")
        else:
            self.root.Or(*args)
        return self

    def And(self, *args):
        if self.root is None:
            length = len(args)
            if length == 1:
                self.root = args[0]
            elif length == 3:
                self.root = Where(args[0], args[1], args[2])
            else:
                raise ValueError(f"The number of parameters is incorrect, must be 1 or 3, but got {length}")
        else:
            self.root.And(*args)
        return self

    def page(self, count):
        self._page = count
        return self

    def page_size(self, count):
        self._page_size = count
        return self

    def order(self, key, is_asc: bool):
        o = -1
        if is_asc:
            o = 1
        order = {
            "field": key,
            "type": o,
        }

        self._order.append(order)
        return self

    def Insert(self, data: list):
        json_data = {
            "appId": str(self._app_id),
            "tableName": self.table,
            "tableAk": self.table_ak,
            "data": data,
        }
        return self._app.insert(json_data)

    def Delete(self):
        filters = self._dict()
        if filters is None:
            raise ValueError("delete not support filter is none")

        json_data = {
            "appId": str(self._app_id),
            "tableAk": self.table_ak,
            "tableName": self.table,
            "filters": filters
        }
        return self._app.delete(json_data)

    def Count(self):
        filters = self._dict()
        json_data = {
            "appId": str(self._app_id),
            "tableAk": self.table_ak,
            "tableName": self.table,
            "filters": filters
        }
        return self._app.count(json_data)

    def Update(self, obj, upsert: bool = False):
        filters = self._dict()
        if filters is None:
            raise ValueError("update query is none")

        json_data = {
            "appId": str(self._app_id),
            "tableAk": self.table_ak,
            "tableName": self.table,
            "filters": filters,
            "values": obj,
            "options": {
                "upsert": upsert
            }
        }
        return self._app.update(json_data)

    def Find(self):
        filters = self._dict()
        json_data = {
            "appId": str(self._app_id),
            "tableAk": self.table_ak,
            "tableName": self.table,
            "selectedFields": [],
            "orderBy": [],
            "page": self._page,
            "pageSize": self._page_size,
        }

        if filters is not None:
            json_data["filters"] = filters

        if len(self._select) > 0:
            json_data["selectedFields"] = self._select

        if len(self._order) > 0:
            json_data["orderBy"] = self._order
        return self._app.query(json_data)

    def CreateTable(self, fields, index = None):
        if fields is None:
            raise ValueError("param error")

        data = {
            "appId": str(self._app_id),
            "tableName": self.table,
            "fields": fields,
        }

        if index is not None:
            data["index"] = index

        return self._app.create_table(data)

    def CreateTableV2(self, name: str, header_rows: int, schema, ext: TableExt = None):
        data = {
            "dbAK": self.db_ak,
            "name": name,
            "headerRows": header_rows,
            "schema": schema
        }
        if ext is not None:
            data["descRows"] = ext.desc_rows
            data["descInfo"] = ext.desc_info
        return self._app.create_table_v2(data)

    def DeleteTable(self):
        data = {
            "appId": str(self._app_id),
            "tableName": self.table,
        }
        return self._app.delete_table(data)

    def Detail(self):
        return self._app.table(self.table_ak)

    def FindByCond(self, data):
        return self._app.queryv2(data)

    def Tables(self):
        return self._app.tables(self.db_ak)

    def AlterTable(self, schema):
        data = {
            "tableAk": self.table_ak,
            "tableTreeSchema": schema
        }
        return self._app.alter_table(data)

    def _dict(self):
        if self.root is None:
            return None

        return self.root.dict()

    def _build(self):
        return json.dumps(self.root.dict(), indent=4)
