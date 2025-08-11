# -*- coding: UTF-8 -*-

from bohrium_open_sdk import OpenSDK


class App:
    def __init__(
            self,
            base_url="https://openapi.test.dp.tech",
            access_key="",
            app_key=None,
            timeout=60,
    ):
        # timeout 默认 1min
        self.client = OpenSDK(base_url=base_url, access_key=access_key, app_key=app_key, timeout=timeout)

    def get_user_info(self):
        resp = self.client.user.get_info()
        data = resp.get("data")
        return data.get("user_id"), data.get("org_id")

    def get_app_id(self, app_key):
        resp = self.client.app.get_app_info(app_key)
        return resp.get("data").get("id")

    def insert(self, data):
        return self.client.app_db.insert(data)

    def delete(self, data):
        return self.client.app_db.delete(data)

    def count(self, data):
        return self.client.app_db.count(data)

    def update(self, data):
        return self.client.app_db.update(data)

    def query(self, data):
        return self.client.app_db.query(data)

    def queryv2(self, data):
        return self.client.app_db.queryv2(data)

    def create_table(self, data):
        return self.client.app_db.create_table(data)

    def create_table_v2(self, data):
        return self.client.app_db.create_table_v2(data)

    def delete_table(self, data):
        return self.client.app_db.delete_table(data)

    def table(self, table_ak):
        return self.client.app_db.get_table_detail(table_ak)

    def tables(self, db_ak):
        return self.client.app_db.tables(db_ak)

    def alter_table(self, data):
        return self.client.app_db.alter_table(data)

