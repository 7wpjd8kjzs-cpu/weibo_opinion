# 统一加载全局样式
# ========== 页面第一行，强制恢复np.float别名，适配sklearn硬编码 ==========
import numpy as np
# 临时补上sklearn需要的废弃别名，只补sklearn必须的这一条，不额外改int/bool
if not hasattr(np, "float"):
    np.float = np.float64
from utils import load_css
load_css("styles.css")

import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import streamlit as st
# 读取全局缓存数据
from data_loader import load_all_data
all_hot_df, comment_df = load_all_data()
all_hot_df = all_hot_df.copy() if not all_hot_df.empty else pd.DataFrame()
comment_df = comment_df.copy() if not comment_df.empty else pd.DataFrame()

total_hot_count = len(all_hot_df)
date_order = [f"6月{i}日" for i in range(10, 17)]

# 每日聚合统计
if total_hot_count > 0:
    daily_stats = all_hot_df.groupby("日期").agg(
        每日总热度=("热度值", "sum"),
        每日平均热度=("热度值", "mean"),
        每日热搜条数=("热搜话题", "count")
    ).reset_index()
    daily_stats = daily_stats.set_index("日期").reindex(date_order).reset_index()
    daily_stats = daily_stats.fillna(0)
else:
    daily_stats = pd.DataFrame({"日期": date_order, "每日总热度":0, "每日平均热度":0, "每日热搜条数":0})

st.title("📈 微博热搜时序趋势分析")
st.divider()

# 1. 每日总热度折线
st.subheader("🔥 7日每日总热度变化趋势")
fig_trend = px.line(
    daily_stats, x="日期", y="每日总热度",
    markers=True, color_discrete_sequence=["#4285F4"],
    title="6月10日-16日 每日热搜总热度趋势"
)
fig_trend.update_layout(plot_bgcolor="white", xaxis_title="日期", yaxis_title="总热度", hovermode="x unified")
fig_trend.update_traces(line=dict(width=3))
st.plotly_chart(fig_trend, use_container_width=True)
st.divider()

# 2. 上榜排名与热度值关系散点图
st.subheader("🔝 上榜排名与热度值关系散点图")
if total_hot_count > 0:
    fig_scatter = px.scatter(
        all_hot_df, x="上榜排名", y="热度值",
        color="热度值", color_continuous_scale="Blues",
        hover_name="热搜话题", title="热搜上榜排名与热度值分布"
    )
    fig_scatter.update_layout(plot_bgcolor="white")
    fig_scatter.update_xaxes(autorange="reversed")
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("暂无热搜数据，无法生成散点图")
st.divider()

# 3. 热度线性预测【核心修复：reshape(-1, 1)转为二维数组】
st.subheader("🔮 热度值线性预测")
if total_hot_count >= 2:
    X = all_hot_df["上榜排名"].values.reshape(-1, 1)
    y = all_hot_df["热度值"]
    lr = LinearRegression()
    lr.fit(X, y)
    rank_range = pd.DataFrame({"上榜排名": range(1, 51)})
    rank_range["预测热度"] = lr.predict(rank_range["上榜排名"].values.reshape(-1, 1))
    fig_pred = px.line(rank_range, x="上榜排名", y="预测热度", color_discrete_sequence=["#003366"])
    fig_pred.update_traces(line=dict(width=3, dash="dash"))
    fig_pred.add_scatter(x=all_hot_df["上榜排名"], y=all_hot_df["热度值"], mode="markers", marker_color="#4285F4",
                         name="真实热度")

    # 调整布局
    fig_pred.update_layout(
        plot_bgcolor="white",
        height=450,
        margin=dict(l=40, r=80, t=50, b=40),
        legend=dict(
            font=dict(size=12),
            itemwidth=40,
            x=1.02,  # 图例在右侧外部
            y=0.5,
            xanchor="left",
            yanchor="middle"
        ),
        autosize=True
    )
    fig_pred.update_xaxes(autorange="reversed")
    st.plotly_chart(fig_pred, use_container_width=True)
else:
    st.info("数据量不足，无法进行线性预测")