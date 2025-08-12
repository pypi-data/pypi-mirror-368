import logging
from datetime import datetime, timedelta

# mysql type timestamp
table_ut_cols1 = {
    "merchant_center_vela_v1.v3_sku_warehouse": "last_modified",
    "merchant_center_mini_v1.v3_sku_warehouse": "last_modified",
    "merchant_center_ouku_v1.v3_sku_warehouse": "last_modified",
}

# mysql type datetime
table_ut_cols2 = {
    "merchant_center_vela_v1.mc_products_sku": "last_modified",
    "merchant_center_mini_v1.mc_products_sku": "last_modified",
    "merchant_center_ouku_v1.mc_products_sku": "last_modified",
}


def check_litb_diff_row(logger: logging.Logger, src_db: str, src_tab: str, src_row: dict | None, dst_row: dict | None):
    dbtab = f"{src_db}.{src_tab}"

    if src_row is not None and src_row == dst_row:
        return True

    if dst_row is None:
        return False

    if dbtab in table_ut_cols1.keys() + table_ut_cols2.keys():
        if dbtab in table_ut_cols2.keys():
            last_mt = table_ut_cols2[dbtab]
            src_row[last_mt] = src_row[last_mt] - timedelta(hours=8)
            dst_row[last_mt] = dst_row[last_mt] + timedelta(hours=7)

        if dbtab in table_ut_cols1.keys():
            last_mt = table_ut_cols1[dbtab]

        if src_row[last_mt] <= dst_row[last_mt]:
            return True

    return False
