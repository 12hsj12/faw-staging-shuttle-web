from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def load_cars() -> pd.DataFrame:
    """读取模拟整车出库数据，并转换时间字段。"""
    df = pd.read_csv(DATA_DIR / "car_orders.csv")
    df["offline_time"] = pd.to_datetime(df["offline_time"])
    df["outbound_time"] = pd.to_datetime(df["outbound_time"])
    return df


def load_lanes() -> pd.DataFrame:
    """读取模拟备车道数据。"""
    return pd.read_csv(DATA_DIR / "staging_lanes.csv")


def dataframe_to_records(df: pd.DataFrame) -> list[dict]:
    """将 DataFrame 转成适合 JSON 返回的记录列表。"""
    normalized = df.copy()
    for col in normalized.columns:
        if pd.api.types.is_datetime64_any_dtype(normalized[col]):
            normalized[col] = normalized[col].dt.strftime("%Y-%m-%d %H:%M")
    return normalized.to_dict(orient="records")
