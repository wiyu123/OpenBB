# openbb_custom_data.py
import akshare as ak
import pandas as pd

def get_a_stock_universe():
    """获取全市场A股列表（AkShare）"""
    df = ak.stock_zh_a_spot_em()
    df = df[~df["名称"].str.contains("ST|退|\\*")]
    return df

def screen_with_openbb_logic():
    """
    使用你想要的 OpenBB 筛选逻辑
    但数据来自 AkShare
    """
    # 1. 从 AkShare 获取全市场 A 股
    df = get_a_stock_universe()

    # 2. 在这里使用 OpenBB 的筛选逻辑（你可以自己写）
    # 示例：OpenBB 风格的筛选
    df = df[
        (df["最新价"] > 5) &
        (df["成交额"] > 100000000) &
        (df["涨跌幅"] > 0) &
        (df["涨跌幅"] < 6)
    ]

    # 3. 返回筛选后的股票
    return df.sort_values(by="成交额", ascending=False).head(10)
