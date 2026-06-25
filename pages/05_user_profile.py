from utils import load_css
load_css("styles.css")

import pandas as pd
import plotly.express as px
import streamlit as st
from data_loader import load_all_data
all_hot_df, comment_df = load_all_data()
all_hot_df = all_hot_df.copy()
comment_df = comment_df.copy()

st.title("👤 热搜受众用户画像分析")
st.divider()

# 1.分类雷达图
st.subheader("🎯 用户话题兴趣偏好雷达图")
if not all_hot_df.empty and "话题分类" in all_hot_df.columns:
    cat_df = all_hot_df["话题分类"].value_counts().reset_index()
    cat_df.columns = ["分类名称", "热搜数量"]
    fig_radar = px.line_polar(cat_df, r="热搜数量", theta="分类名称", line_close=True, template="seaborn", title="受众话题偏好")
    fig_radar.update_traces(fill="toself", opacity=0.5, line_color="#4285F4", fillcolor="rgba(66,133,244,0.7)")
    fig_radar.update_layout(height=800, width=1400, plot_bgcolor="white")
    st.plotly_chart(fig_radar, use_container_width=True)
else:
    st.warning("无分类数据，无法生成雷达图")
st.divider()

# 2.话题互动柱状图
st.subheader("👥 各话题用户互动量")
if comment_df.empty:
    st.info("暂无评论数据")
else:
    topic_cnt = comment_df["热搜话题"].value_counts().reset_index()
    topic_cnt.columns = ["热搜话题", "互动博文数"]
    fig_bar = px.bar(topic_cnt, x="热搜话题", y="互动博文数", color="互动博文数", color_continuous_scale="Blues", title="各话题互动博文总量")
    fig_bar.update_xaxes(tickangle=-35)
    fig_bar.update_layout(height=600, plot_bgcolor="white")
    st.plotly_chart(fig_bar, use_container_width=True)
