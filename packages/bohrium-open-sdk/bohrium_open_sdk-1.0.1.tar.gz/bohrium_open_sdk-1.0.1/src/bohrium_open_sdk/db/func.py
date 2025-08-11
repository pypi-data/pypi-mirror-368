from pathlib import Path
from typing import List

import pandas as pd
from bohrium_open_sdk.db import Op, SQL
from numpy import int64
from tqdm import tqdm


def query2df(raw_data, table_columns):
    data = []
    for item in raw_data:
        single_dict = {}
        for col in table_columns:
            col_value = item.get(col, "")
            if type(col_value) != dict:
                single_dict.update({col: col_value})
            else:
                if col_value.get("name", None) is not None:
                    single_dict.update({col: col_value["name"]})
                else:
                    single_dict.update({col: ""})

        if item.get("authors", None) is not None:
            single_dict.update({"创建者": item["authors"][0]['userName'], "更新时间": item["updateTime"]})

        data.append(single_dict)

    df = pd.DataFrame(data)

    return df


def db_query(table: SQL, page: int = 1, page_size: int = 10) -> tuple[int, pd.DataFrame]:
    table_columns = [item['name'] for item in table.Detail()["fields"]]
    table.page(count=page).page_size(count=page_size)
    data_count, raw_data = table.Find()

    df = query2df(raw_data, table_columns)

    return data_count, df


def db_query_cond(table: SQL, table_columns, conditions_dict, page: int = 1, page_size: int = 10) -> tuple[
    int, pd.DataFrame]:
    conditions_dict["offset"] = page - 1
    conditions_dict["pageSize"] = page_size
    data_count, raw_data = table.FindByCond(conditions_dict)
    df = query2df(raw_data, table_columns)

    return data_count, df


def db_query_full(table: SQL, batch_size: int = 1000) -> tuple[int, pd.DataFrame]:
    """
    自动分页查询整个表数据并返回完整DataFrame（带美观进度条）

    参数:
        table: SQL表对象
        batch_size: 每批查询的数据量，默认为1000

    返回:
        包含完整表数据的DataFrame
    """
    # 获取总记录数
    total_count = table.Count()

    # 初始化变量
    all_data = []
    current_page = 1
    retrieved_count = 0

    # 创建进度条
    with tqdm(total=total_count, desc="查询进度", unit="行",
              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]") as pbar:
        # 分页查询直到获取所有数据
        while retrieved_count < total_count:
            try:
                # 查询当前页数据
                data_count, batch_df = db_query(table=table, page=current_page, page_size=batch_size)

                # 如果没有数据或查询失败，退出循环
                if data_count == 0 or batch_df.empty:
                    break

                # 添加当前批次数据
                all_data.append(batch_df)
                new_records = len(batch_df)
                retrieved_count += new_records
                current_page += 1

                # 更新进度条
                pbar.update(new_records)

            except Exception as e:
                tqdm.write(f"查询出错: {str(e)}")
                break

    # 合并所有批次数据
    if all_data:
        full_df = pd.concat(all_data, ignore_index=True)
        tqdm.write(f"✅ 数据获取完成，共获取 {len(full_df)} 条记录")
        return retrieved_count, full_df
    else:
        tqdm.write("⚠️ 未获取到任何数据")
        return 0, pd.DataFrame()


def db_add(table: SQL, data: List[dict]):
    res = table.Insert(data)
    return res


def db_delete(table: SQL, id: str):
    delete_count = table.Where("id", Op.EQ, id).Delete()
    return delete_count


def db_upload_file_h(database_client, tiefblue_client, file_dir: Path, table_ak: str, match_col: str,
                     file_suffix: str, file_col: str):
    table = database_client.table_with_ak(table_ak)
    _, df = db_query_full(table, batch_size=100)

    names = df[match_col].values
    for name in names:
        file_path = file_dir / f"{name}.{file_suffix}"
        if not file_path.exists():
            print(f"{file_path} is not exist, continue")
            continue
        else:
            print(f"{name} start")
            if isinstance(name, int64):
                name = int(name)
            db_item = database_client.table_with_ak(table_ak).Where(match_col, Op.EQ, name)
            search_results = db_item.Find()[1]
            if len(search_results):
                db_item_fig_detail = search_results[0][file_col]
                if db_item_fig_detail.get("url", None) is None:
                    file_name = f"{name}.{file_suffix}"
                    with open(file_path, "rb") as f:
                        file_content = f.read()
                    file_object = tiefblue_client.upload_file_bytes(file_name=file_name, file_bytes=file_content)
                    db_item.Update({file_col: file_object['data']})
                    print(f"{name} update successful")
                else:
                    print(f"{name} exist!")
            else:
                print(f"{name} search failed")
