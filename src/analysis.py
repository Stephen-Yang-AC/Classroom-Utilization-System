"""
教室使用率分析：依大樓/教室/時段計算使用時段與使用率。
使用率 = (該空間被使用的節數) / (可排課總節數)，以週為單位。
"""
from pathlib import Path
import pandas as pd
import yaml

from .config import SLOTS_PER_DAY, DAYS_PER_WEEK, get_all_slot_labels

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_rooms():
    rooms = pd.read_csv(DATA_DIR / "rooms.csv")
    return rooms


def load_buildings():
    with open(DATA_DIR / "buildings.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return pd.DataFrame(data["buildings"])


def load_schedule():
    return pd.read_csv(DATA_DIR / "schedule_mock.csv")


def expand_schedule_to_slots(schedule: pd.DataFrame) -> pd.DataFrame:
    """把 slot_start~slot_end 展開成每一節一筆（方便算使用節數與時段熱力）"""
    rows = []
    for _, r in schedule.iterrows():
        for slot in range(int(r["slot_start"]), int(r["slot_end"])):
            rows.append({
                "room_id": r["room_id"],
                "day_of_week": r["day_of_week"],
                "slot": slot,
                "course_or_usage": r["course_or_usage"],
            })
    return pd.DataFrame(rows)


def utilization_by_room(rooms: pd.DataFrame, schedule: pd.DataFrame) -> pd.DataFrame:
    """每間教室：已使用節數、可排課總節數、使用率"""
    total_possible = SLOTS_PER_DAY * DAYS_PER_WEEK
    used = schedule.groupby("room_id").apply(
        lambda g: (g["slot_end"] - g["slot_start"]).sum()
    ).reindex(rooms["room_id"], fill_value=0)
    used = used.astype(int)
    df = rooms[["building_id", "room_id", "room_name", "capacity", "room_type"]].copy()
    df["used_slots"] = used.values
    df["total_slots"] = total_possible
    df["utilization_rate"] = (df["used_slots"] / total_possible).round(4)
    return df


def utilization_by_building(room_util: pd.DataFrame) -> pd.DataFrame:
    """每棟大樓：加總使用節數、總可排課節數、使用率（以節數加總算）"""
    g = room_util.groupby("building_id").agg(
        used_slots=("used_slots", "sum"),
        total_slots=("total_slots", "sum"),
    ).reset_index()
    g["utilization_rate"] = (g["used_slots"] / g["total_slots"]).round(4)
    return g


def usage_by_time_slot(rooms: pd.DataFrame, schedule: pd.DataFrame) -> pd.DataFrame:
    """每時段（週幾 + 第幾節）：有多少間教室在使用（或列出教室）"""
    expanded = expand_schedule_to_slots(schedule)
    merged = expanded.merge(rooms[["room_id", "building_id"]], on="room_id")
    # 每個 (day, slot, building_id) 的使用教室數
    by_building = merged.groupby(["day_of_week", "slot", "building_id"]).agg(
        rooms_used=("room_id", "nunique"),
    ).reset_index()
    return by_building


def usage_heatmap_data(rooms: pd.DataFrame, schedule: pd.DataFrame, building_id: str = None) -> pd.DataFrame:
    """熱力圖用：指定大樓（或全體）下，每個 (day, slot) 被使用的節數或教室數"""
    expanded = expand_schedule_to_slots(schedule)
    merged = expanded.merge(rooms[["room_id", "building_id"]], on="room_id")
    if building_id:
        merged = merged[merged["building_id"] == building_id]
    # 每個 (day, slot) 的「使用節數」（同一時段多間教室 = 多節）
    heat = merged.groupby(["day_of_week", "slot"]).size().reset_index(name="usage_slots")
    return heat


def get_room_usage_detail(room_id: str, schedule: pd.DataFrame) -> pd.DataFrame:
    """單一教室的使用時段明細"""
    r = schedule[schedule["room_id"] == room_id].copy()
    r["day_name"] = r["day_of_week"].map(
        {1: "週一", 2: "週二", 3: "週三", 4: "週四", 5: "週五"}
    )
    return r.sort_values(["day_of_week", "slot_start"])
