import streamlit as st
from utils import load_css
load_css("styles.css")

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import jieba
from wordcloud import WordCloud as LocalWordCloud
import numpy as np
from pyecharts.charts import WordCloud, Timeline
from pyecharts import options as opts
from pyecharts.globals import ThemeType
import streamlit_echarts
import os
from PIL import Image
import random

# 全局数据
from data_loader import load_all_data
all_hot_df, comment_df = load_all_data()
all_hot_df = all_hot_df.copy()
comment_df = comment_df.copy()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
stop_word_list = {"的", "了", "是", "在", "和", "有", "我", "你", "他", "这", "那", "都", "就", "也", "不", "很", "一个", "一批", "这个", "没有", "全部", "什么", "怎么", "可以", "还是"}
# 完整彩色色板
color_palette = [
    "#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#1abc9c",
    "#3498db", "#9b59b6", "#8e44ad", "#e91e63", "#009688",
    "#FF4500", "#32CD32", "#1E90FF", "#FF69B4", "#9370DB"
]

# 自定义wordcloud随机彩色函数
def random_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "hsl(%d, 80%%, 40%%)" % np.random.randint(0, 360)

# ========== 蒙版图片读取 ==========
mask_img = None
mask_path = os.path.join(BASE_DIR, "weibo_mask.png")
try:
    mask_img = Image.open(mask_path).convert("L")
    mask_array = np.array(mask_img)
    avg_bright = np.mean(mask_array)
    if avg_bright < 128:
        mask_array = 255 - mask_array
    mask_img = mask_array
except Exception as e:
    mask_img = None

# ========== 字体 ==========
if mask_img is not None:
    wc_mask = LocalWordCloud(
        background_color="white",
        # font_path=valid_font,
        mask=mask_img,
        width=1400, height=700, max_words=1200, max_font_size=130, contour_width=0,
        color_func=random_color_func
    )
else:
    wc_backup = LocalWordCloud(
        background_color="white",
        font_path=valid_font,
        width=1400, height=700, max_words=1200, max_font_size=140,
        color_func=random_color_func
    )

st.title("📝 热搜文本语义挖掘")
st.divider()

if all_hot_df.empty:
    st.error("CSV文件读取失败，请检查数据路径！")
else:
    # 全局总关键词词云（微博图标形状）
    st.subheader("☁️ 全局总关键词词云")
    full_text = "".join(all_hot_df["热搜话题"].astype(str).tolist())
    cut_words = jieba.lcut(full_text)
    clean_words = [word for word in cut_words if word not in stop_word_list and len(word) > 1]
    text_join = " ".join(clean_words)

    try:
        if mask_img is not None:
            wc_mask = LocalWordCloud(
                background_color="white",
                font_path=valid_font,
                mask=mask_img,
                width=1400, height=700, max_words=1200, max_font_size=130, contour_width=0,
                color_func=random_color_func
            )
            wc_mask.generate(text_join)
            st.image(wc_mask.to_image(), width=1200)
        else:
            wc_backup = LocalWordCloud(
                background_color="white",
                font_path=valid_font,
                width=1400, height=700, max_words=1200, max_font_size=140,
                color_func=random_color_func
            )
            wc_backup.generate(text_join)
            st.image(wc_backup.to_image(), width=1200)
    except Exception as e:
        wc_backup = LocalWordCloud(
            background_color="white",
            font_path=valid_font,
            width=1400, height=700, max_words=1200, max_font_size=140,
            color_func=random_color_func
        )
        wc_backup.generate(text_join)
        st.image(wc_backup.to_image(), width=1200)
    st.divider()

    # ====================== 修复：分日期动态时间轴彩色词云 ======================
    st.subheader("📅 分日期动态时间轴词云")
    date_list = sorted(all_hot_df["日期"].unique())
    timeline = Timeline(init_opts=opts.InitOpts(width="100%", height="700px", theme=ThemeType.MACARONS))

    for date in date_list:
        date_data = all_hot_df[all_hot_df["日期"] == date]
        date_text = "".join(date_data["热搜话题"].astype(str))
        words = jieba.lcut(date_text)
        word_count_dict = {}
        for w in words:
            if len(w) >= 2 and w not in stop_word_list:
                word_count_dict[w] = word_count_dict.get(w, 0)
        top30 = sorted(word_count_dict.items(), key=lambda x: x[1], reverse=True)[:30]

        wc_chart = (
            WordCloud(init_opts=opts.InitOpts(width="100%", height="700px"))
            .add(
                series_name="当日热词",
                data_pair=top30,
                word_size_range=[20, 90],
                shape="circle",
                # 1.9.0 标准颜色配置，循环彩色
                textstyle_opts=opts.TextStyleOpts(color=color_palette)
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title=f"{date} 当日热点词汇", title_textstyle_opts=opts.TextStyleOpts(color="#004085", font_size=16))
            )
        )
        timeline.add(wc_chart, date)

    streamlit_echarts.st_pyecharts(timeline, height=700)
    st.divider()

    # ====================== 【彻底修复桑基图报错】旧版Plotly正确写法 ======================
    st.subheader("🌊 热搜分类与热度流量桑基图")
    all_hot_df["热度区间"] = pd.cut(
        all_hot_df["热度值"],
        bins=[0, 500000, 1000000, 5000000, 20000000],
        labels=["0-50万", "50-100万", "100-500万", "500万以上"]
    )
    sankey_df = all_hot_df.groupby(["话题分类", "热度区间"], observed=False)["热搜话题"].count().reset_index()

    node_names = list(set(sankey_df["话题分类"].tolist() + sankey_df["热度区间"].tolist()))
    src, tgt, val = [], [], []
    for _, row in sankey_df.iterrows():
        s_idx = node_names.index(row["话题分类"])
        t_idx = node_names.index(row["热度区间"])
        src.append(s_idx)
        tgt.append(t_idx)
        val.append(row["热搜话题"])

    fig_sankey = go.Figure(go.Sankey(
        node=dict(label=node_names,
                  pad=20,  # 加大节点上下间距，文字不堆叠挤压
                  line=dict(width=1, color="#888888"),
                  ),
        link=dict(source=src, target=tgt, value=val,
                  color="rgba(160,160,160,0.35)"),
        textfont=dict(
            size=15,
            weight="normal",
            color="#000000"
        )
    ))
    # 放大固定宽高，居中全屏展示
    fig_sankey.update_layout(
        title_text="分类-热度区间 桑基图",
        height=900,
        width=1700,
        autosize=False
    )
    st.plotly_chart(fig_sankey, use_container_width=True)

    st.divider()

# ========== 4. 热搜评论情感分析可视化 ==========
    st.subheader("📊 热搜评论情感分析")

    if not comment_df.empty:
        # 获取有评论的热搜列表
        topics_with_comments = comment_df["热搜话题"].unique().tolist()

        if topics_with_comments:
            # 默认选择第一个有评论的热搜
            sentiment_topic = topics_with_comments[0]
            st.info(f"📌 当前分析热搜：**{sentiment_topic}**")

            target_comments = comment_df[comment_df["热搜话题"] == sentiment_topic]
            comments_list = target_comments["博文内容"].dropna().tolist()
            comments_list = [str(c).strip() for c in comments_list if len(str(c)) > 5]

            if len(comments_list) < 3:
                st.warning(f"「{sentiment_topic}」有效评论不足3条，换一个热搜试试")
            else:
                st.info(f"📝 共收集到 **{len(comments_list)}** 条有效评论")


                # ===== 基于情感词典的快速分析 =====
                def simple_sentiment_analysis(texts):
                    """基于情感词典的快速分析"""
                    positive_words = [
                        '好', '棒', '支持', '喜欢', '爱', '赞', '优秀', '精彩', '感动', '期待', '加油',
                        '完美', '绝了', '厉害', '好看', '开心', '高兴', '幸福', '温暖', '善良', '努力',
                        '成功', '进步', '突破', '出色', '了不起', '真棒', '太好了', '不错', '可以',
                        '神', '牛', '强', '绝', '美', '帅', '甜'
                    ]
                    negative_words = [
                        '差', '烂', '讨厌', '恶心', '失望', '垃圾', '坑', '骗', '假', '无语', '气愤',
                        '难听', '糟糕', '丢人', '难看', '伤心', '难过', '痛苦', '愤怒', '吐槽',
                        '不行', '不好', '太差', '一般般', '不如', '失败', '尴尬', '烦', '气', '乱'
                    ]

                    results = []
                    for text in texts:
                        pos_score = sum(1 for w in positive_words if w in text)
                        neg_score = sum(1 for w in negative_words if w in text)

                        if pos_score > neg_score:
                            results.append('正面')
                        elif neg_score > pos_score:
                            results.append('负面')
                        else:
                            results.append('中性')

                    return results


                sentiment_labels = simple_sentiment_analysis(comments_list)

                from collections import Counter

                sentiment_counts = Counter(sentiment_labels)
                total = len(sentiment_labels)

                pos_pct = round(sentiment_counts.get('正面', 0) / total * 100, 1)
                neu_pct = round(sentiment_counts.get('中性', 0) / total * 100, 1)
                neg_pct = round(sentiment_counts.get('负面', 0) / total * 100, 1)

                # ===== 情感分布可视化（饼图 + 指标卡） =====
                col1, col2 = st.columns([1, 1.5])

                with col1:
                    st.markdown("#### 情感分布占比")
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=['正面', '中性', '负面'],
                        values=[pos_pct, neu_pct, neg_pct],
                        hole=0.4,
                        marker=dict(colors=['#4CAF50', '#FFC107', '#F44336']),
                        textinfo='label+percent',
                        textposition='inside'
                    )])
                    fig_pie.update_layout(
                        height=350,
                        margin=dict(l=20, r=20, t=30, b=20),
                        showlegend=False
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

                with col2:
                    st.markdown("#### 情感指标")
                    st.markdown(f"""
                        <div style="margin-bottom:10px;">
                            <span>😊 正面</span>
                            <div style="width:100%;background:#e0e0e0;border-radius:10px;height:20px;">
                                <div style="width:{pos_pct}%;background:#4CAF50;border-radius:10px;height:20px;text-align:center;color:white;font-size:12px;line-height:20px;">
                                    {pos_pct}%
                                </div>
                            </div>
                        </div>
                        <div style="margin-bottom:10px;">
                            <span>😐 中性</span>
                            <div style="width:100%;background:#e0e0e0;border-radius:10px;height:20px;">
                                <div style="width:{neu_pct}%;background:#FFC107;border-radius:10px;height:20px;text-align:center;color:white;font-size:12px;line-height:20px;">
                                    {neu_pct}%
                                </div>
                            </div>
                        </div>
                        <div style="margin-bottom:10px;">
                            <span>😞 负面</span>
                            <div style="width:100%;background:#e0e0e0;border-radius:10px;height:20px;">
                                <div style="width:{neg_pct}%;background:#F44336;border-radius:10px;height:20px;text-align:center;color:white;font-size:12px;line-height:20px;">
                                    {neg_pct}%
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    if pos_pct > max(neu_pct, neg_pct):
                        st.success(f"✅ 整体情感倾向：**正面**（{pos_pct}%）")
                    elif neg_pct > max(pos_pct, neu_pct):
                        st.error(f"❌ 整体情感倾向：**负面**（{neg_pct}%）")
                    else:
                        st.warning(f"⚖️ 整体情感倾向：**中性**（{neu_pct}%）")

        else:
            st.warning("暂无有评论的热搜数据")
    else:
        st.warning("暂无评论数据，请先导入评论CSV文件")
