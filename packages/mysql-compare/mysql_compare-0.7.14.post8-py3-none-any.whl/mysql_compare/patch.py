import logging
from datetime import datetime, timedelta

table_ut_cols = {
    "merchant_center_vela_v1.mc_products_sku": "last_modified",
    "merchant_center_mini_v1.mc_products_sku": "last_modified",
    "merchant_center_ouku_v1.mc_products_sku": "last_modified",
    "merchant_center_vela_v1.v3_sku_warehouse": "last_modified",
    "merchant_center_mini_v1.v3_sku_warehouse": "last_modified",
    "merchant_center_ouku_v1.v3_sku_warehouse": "last_modified",
}


def check_litb_diff_row(logger: logging.Logger, src_db: str, src_tab: str, src_row: dict | None, dst_row: dict | None):
    dbtab = f"{src_db}.{src_tab}"

    if src_row is not None and src_row == dst_row:
        return True

    if dst_row is None:
        return False

    if dbtab in table_ut_cols:
        if dbtab in [
            "merchant_center_ouku_v1.mc_products_sku",
            "merchant_center_mini_v1.mc_products_sku",
            "merchant_center_vela_v1.mc_products_sku",
        ]:
            src_row["last_modified"] = src_row["last_modified"] - timedelta(hours=8)
            dst_row["last_modified"] = dst_row["last_modified"] + timedelta(hours=7)

        last_mt = table_ut_cols[dbtab]
        copy_src_row = src_row.copy()
        copy_dst_row = dst_row.copy()
        del copy_src_row[last_mt]
        del copy_dst_row[last_mt]
        if copy_src_row == copy_dst_row and src_row[last_mt] <= dst_row[last_mt]:
            return True
        elif copy_src_row == copy_dst_row:
            logger.debug(f"litb diff timetype: src[{src_row[last_mt]}] dst[{dst_row[last_mt]}]")

    return False
