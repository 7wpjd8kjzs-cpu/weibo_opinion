import streamlit as st
import pandas as pd
import plotly.express as px
from pyecharts.charts import Liquid
from pyecharts import options as opts

# 加载全局样式
from utils import load_css, create_metric_card
load_css("styles.css")

# 加载缓存数据
from data_loader import load_all_data
all_hot_df, comment_df = load_all_data()
# 使用副本避免修改缓存数据
all_hot_df = all_hot_df.copy() if isinstance(all_hot_df, pd.DataFrame) else pd.DataFrame()
comment_df = comment_df.copy() if isinstance(comment_df, pd.DataFrame) else pd.DataFrame()

# 核心指标计算
total_hot_count = len(all_hot_df)
million_hot_count = 0
avg_hot_value = 0
top1_title = "暂无数据"
top1_heat = 0
pct_million = "0%"

if total_hot_count > 0:
    all_hot_df["热度值"] = pd.to_numeric(all_hot_df["热度值"], errors="coerce")
    million_hot_count = len(all_hot_df[all_hot_df["热度值"] > 1000000])
    avg_hot_value = round(all_hot_df["热度值"].mean(), 0)
    top1_hot = all_hot_df.loc[all_hot_df["热度值"].idxmax()]
    top1_title = top1_hot["热搜话题"]
    top1_heat = top1_hot["热度值"]
    pct_million = f"{million_hot_count / total_hot_count * 100:.1f}%"

# 评论指标
total_comment_count = len(comment_df)
valid_comment_count = 0
pct_comment = "0%"
if total_comment_count > 0:
    valid_mask = comment_df["博文内容"].fillna("").str.strip() != ""
    valid_comment_count = len(comment_df[valid_mask])
    pct_comment = f"{valid_comment_count / total_comment_count * 100:.1f}%"

# 页面渲染
st.title("📊 微博舆情总览驾驶舱")
st.subheader("核心数据概览")

# 第一行4张指标卡片
c1, c2, c3, c4 = st.columns([1,1,1,1])
with c1:
    st.markdown(create_metric_card(total_hot_count, "7日总热搜条数", "#4285F4"), unsafe_allow_html=True)
with c2:
    st.markdown(create_metric_card(million_hot_count, "百万热度热搜数", "#34A853", f"↑{pct_million}"), unsafe_allow_html=True)
with c3:
    st.markdown(create_metric_card(f"{avg_hot_value:,}", "单条平均热度", "#FBBC05"), unsafe_allow_html=True)
with c4:
    st.markdown(create_metric_card(f"{top1_heat:,}", "TOP1热搜热度", "#9C27B0"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 第二行2张评论卡片
cc1, cc2 = st.columns([1,1])
with cc1:
    st.markdown(create_metric_card(total_comment_count, "总评论条数", "#4285F4"), unsafe_allow_html=True)
with cc2:
    st.markdown(create_metric_card(valid_comment_count, "有效评论数", "#34A853", f"↑{pct_comment}"), unsafe_allow_html=True)

st.markdown(f"<p style='margin-top:20px;color:#555;'>热度最高热搜话题：{top1_title}</p>", unsafe_allow_html=True)
st.divider()

# TOP20热搜热度排行
st.subheader("🔥 TOP20热搜热度排行")
if total_hot_count > 0:
    top20_hot = all_hot_df.sort_values("热度值", ascending=False).head(20)
    fig_top20 = px.bar(
        top20_hot, x="热搜话题", y="热度值",
        color="热度值", color_continuous_scale="Blues",
        title="TOP20热搜热度值排行"
    )
    fig_top20.update_layout(xaxis_tickangle=-30, plot_bgcolor="white")
    st.plotly_chart(fig_top20, use_container_width=True)
else:
    st.info("暂无热搜数据，无法生成热度排行图")

st.divider()

# 水滴动态水球图
st.subheader("💧 热搜热度占比分布")
if total_hot_count > 0:
    def classify_hot(val):
        if pd.isna(val):
            return "其他热度"
        if val >= 1000000:
            return "百万热度热搜"
        elif val >= 100000:
            return "十万热度热搜"
        else:
            return "其他热度"

    all_hot_df["热度区间"] = all_hot_df["热度值"].apply(classify_hot)
    target_df = all_hot_df[all_hot_df["热度区间"].isin(["百万热度热搜", "十万热度热搜"])]
    count_stat = target_df["热度区间"].value_counts().reset_index()
    count_stat.columns = ["区间", "数量"]

    total_target = count_stat["数量"].sum()
    million_num = count_stat[count_stat["区间"] == "百万热度热搜"]["数量"].iloc[0]
    ten_num = count_stat[count_stat["区间"] == "十万热度热搜"]["数量"].iloc[0]

    million_pct = round(million_num / total_target, 2)
    ten_pct = round(ten_num / total_target, 2)

    def create_liquid_html(pct, title_name):
        # 1. 缩小原始画布尺寸，从380px → 320px，减少外围大白边
        c = (
            Liquid(init_opts=opts.InitOpts(width="320px", height="320px"))
            .add(
                "",
                [pct],
                is_outline_show=True,
                shape='circle',
                color='#4285F4',
                # 2. 降低外圈留白，缩小空白区域
                outline_border_distance=12,
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title=title_name,
                    title_textstyle_opts=opts.TextStyleOpts(color="#004085"),
                    pos_top="3%"
                )
            )
            .set_series_opts(
                itemstyle_opts=opts.ItemStyleOpts(
                    color='#99CCFF',
                    border_color='#4285F4',
                ),
                # 3. 关键：自定义百分比文字大小，限制字体不超大
                label_opts=opts.LabelOpts(
                    font_size=36,
                    color="#003366"
                )
            )
        )
        # 同步降低渲染高度，匹配小画布
        return c.render_embed(width="100%", height="360px")

    col_left, col_right = st.columns(2, gap="large")
    with col_left:
        html_million = create_liquid_html(million_pct, "百万热度热搜占比")
        st.components.v1.html(html_million, height=360, width=None)
    with col_right:
        html_ten = create_liquid_html(ten_pct, "十万热度热搜占比")
        st.components.v1.html(html_ten, height=360, width=None)

    with st.expander("热度区间统计明细"):
        st.dataframe(count_stat, use_container_width=True)
else:
    st.info("暂无热搜数据，无法生成水球图")

