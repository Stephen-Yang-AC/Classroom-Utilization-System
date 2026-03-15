"""
台師大教室使用率系統 - Streamlit 儀表板
執行：streamlit run app.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.analysis import (
    load_rooms,
    load_buildings,
    load_schedule,
    utilization_by_room,
    utilization_by_building,
    usage_heatmap_data,
    get_room_usage_detail,
)
from src.config import get_all_slot_labels

st.set_page_config(page_title="台師大教室使用率", layout="wide")
st.title("台師大教室使用率系統")
st.caption("盤點：綜合大樓、教育大樓、科工大樓｜分析時段使用與空間使用率")

rooms = load_rooms()
buildings = load_buildings()
schedule = load_schedule()
room_util = utilization_by_room(rooms, schedule)
building_util = utilization_by_building(room_util)

# ----- 側邊欄：篩選大樓 -----
with st.sidebar:
    st.subheader("篩選")
    building_options = ["全部"] + list(buildings["name"].values)
    sel_building_name = st.selectbox("大樓", building_options)
    building_id = None if sel_building_name == "全部" else buildings[buildings["name"] == sel_building_name].iloc[0]["id"]

# ----- 大樓總覽 -----
st.subheader("大樓使用率總覽")
col1, col2, col3 = st.columns(3)
for i, row in building_util.iterrows():
    bid = row["building_id"]
    name = buildings[buildings["id"] == bid].iloc[0]["name"]
    rate = row["utilization_rate"] * 100
    with col1 if i % 3 == 0 else col2 if i % 3 == 1 else col3:
        st.metric(name, f"{rate:.1f}%", f"已用 {int(row['used_slots'])} / {int(row['total_slots'])} 節")

# ----- 時段熱力圖（有篩選大樓時只顯示該棟） -----
st.subheader("各時段使用情況（熱力圖）")
heat = usage_heatmap_data(rooms, schedule, building_id)
# 轉成 day x slot 矩陣
day_names = ["週一", "週二", "週三", "週四", "週五"]
slot_labels = get_all_slot_labels()
pivot = heat.pivot(index="day_of_week", columns="slot", values="usage_slots").reindex(
    index=range(1, 6), columns=range(1, 15)
).fillna(0)
pivot.index = day_names
pivot.columns = slot_labels

fig = px.imshow(
    pivot,
    labels=dict(x="時段", y="星期", color="使用節數"),
    x=slot_labels,
    y=day_names,
    color_continuous_scale="YlOrRd",
    aspect="auto",
)
fig.update_layout(height=320)
st.plotly_chart(fig, use_container_width=True)

# ----- 教室明細表（使用率） -----
st.subheader("教室使用率明細")
display_rooms = room_util if building_id is None else room_util[room_util["building_id"] == building_id]
display_rooms = display_rooms.merge(
    buildings[["id", "name"]].rename(columns={"id": "building_id", "name": "building_name"}),
    on="building_id",
)
display_rooms["使用率"] = (display_rooms["utilization_rate"] * 100).round(1).astype(str) + "%"
st.dataframe(
    display_rooms[["building_name", "room_name", "room_type", "capacity", "used_slots", "total_slots", "使用率"]],
    use_container_width=True,
    hide_index=True,
)

# ----- 依大樓的使用率長條圖 -----
st.subheader("各棟大樓使用率比較")
fig2 = px.bar(
    building_util.merge(buildings, left_on="building_id", right_on="id"),
    x="name",
    y="utilization_rate",
    text_auto=".1%",
    labels={"name": "大樓", "utilization_rate": "使用率"},
)
fig2.update_layout(yaxis_tickformat=".0%", height=280)
st.plotly_chart(fig2, use_container_width=True)

# ----- 選一間教室看時段明細 -----
st.subheader("單一教室使用時段明細")
room_options = display_rooms["room_name"].tolist()
sel_room_name = st.selectbox("選擇教室", room_options, key="room_detail")
if sel_room_name:
    room_id = display_rooms[display_rooms["room_name"] == sel_room_name].iloc[0]["room_id"]
    detail = get_room_usage_detail(room_id, schedule)
    detail_display = detail[["day_name", "slot_start", "slot_end", "course_or_usage"]].copy()
    detail_display["時段"] = detail_display["slot_start"].astype(str) + "–" + detail_display["slot_end"].astype(str) + " 節"
    st.dataframe(detail_display[["day_name", "時段", "course_or_usage"]], use_container_width=True, hide_index=True)
