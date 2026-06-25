# ========== 页面第一行，强制恢复np.float别名，适配sklearn硬编码 ==========
import numpy as np
# 临时补上sklearn需要的废弃别名，只补sklearn必须的这一条，不额外改int/bool
if not hasattr(np, "float"):
    np.float = np.float64
import numpy as np

import streamlit as st
# set_page_config 必须在任何 Streamlit API 调用之前执行
st.set_page_config(
    page_title="地域空间可视化",
    layout="wide"
)

# ===================== 加载样式 =====================
from utils import load_css
load_css("styles.css")  # 🔥 加载外部CSS

# ===================== 导入其他模块 =====================
import pandas as pd
import plotly.express as px
import os

from data_loader import load_all_data, hot_data_folder

# ===================== 数据加载 =====================
all_hot_df, comment_df = load_all_data()
# 使用副本避免修改缓存数据（防止切页后数据被污染）
if isinstance(all_hot_df, pd.DataFrame):
    all_hot_df = all_hot_df.copy()
if isinstance(comment_df, pd.DataFrame) and not comment_df.empty:
    comment_df = comment_df.copy()

# ===================== 1. 城市-省份映射字典（覆盖你全部城市） =====================
city_province_map = {
    # 直辖市
    "北京": "北京市",
    "上海": "上海市",
    "重庆": "重庆市",
    "天津": "天津市",
    # 广东省
    "广州": "广东省", "深圳": "广东省", "东莞": "广东省", "珠海": "广东省", "江门": "广东省",
    "惠州": "广东省", "汕头": "广东省", "汕尾": "广东省", "中山": "广东省", "清远": "广东省",
    # 江苏省
    "南通": "江苏省", "苏州": "江苏省", "徐州": "江苏省", "淮安": "江苏省", "南京": "江苏省",
    "无锡": "江苏省", "镇江": "江苏省",
    # 浙江省
    "杭州": "浙江省", "温州": "浙江省", "嘉兴": "浙江省", "台州": "浙江省", "金华": "浙江省",
    "衢州": "浙江省", "绍兴": "浙江省", "丽水": "浙江省", "宁波": "浙江省",
    # 山东省
    "青岛": "山东省", "济南": "山东省", "潍坊": "山东省", "烟台": "山东省", "滨州": "山东省",
    "淄博": "山东省", "菏泽": "山东省",
    # 四川省
    "成都": "四川省", "眉山": "四川省", "乐山": "四川省", "德阳": "四川省", "自贡": "四川省",
    "凉山彝族自治州": "四川省", "内江": "四川省", "广安": "四川省",
    # 河南省
    "郑州": "河南省", "驻马店": "河南省", "济源": "河南省", "商丘": "河南省", "平顶山": "河南省",
    "濮阳": "河南省", "开封": "河南省", "周口": "河南省", "信阳": "河南省",
    # 湖北省
    "武汉": "湖北省", "襄阳": "湖北省", "荆州": "湖北省", "黄冈": "湖北省",
    # 湖南省
    "株洲": "湖南省", "长沙": "湖南省", "岳阳": "湖南省", "常德": "湖南省", "怀化": "湖南省",
    "衡阳": "湖南省",
    # 福建省
    "福州": "福建省", "泉州": "福建省", "厦门": "福建省", "龙岩": "福建省", "南平": "福建省",
    "宁德": "福建省",
    # 河北省
    "保定": "河北省", "邯郸": "河北省", "衡水": "河北省", "邢台": "河北省", "石家庄": "河北省",
    "秦皇岛": "河北省",
    # 安徽省
    "合肥": "安徽省", "芜湖": "安徽省", "六安": "安徽省", "淮北": "安徽省", "宿州": "安徽省",
    # 广西壮族自治区
    "河池": "广西壮族自治区", "钦州": "广西壮族自治区", "玉林": "广西壮族自治区",
    # 陕西省
    "西安": "陕西省", "宝鸡": "陕西省",
    # 山西省
    "太原": "山西省", "晋中": "山西省", "大同": "山西省", "运城": "山西省",
    # 辽宁省
    "沈阳": "辽宁省", "大连": "辽宁省", "本溪": "辽宁省", "丹东": "辽宁省",
    # 吉林省
    "长春": "吉林省", "吉林市": "吉林省", "通化": "吉林省",
    # 黑龙江省
    "哈尔滨": "黑龙江省", "七台河": "黑龙江省", "佳木斯": "黑龙江省",
    # 云南省
    "昆明": "云南省", "保山": "云南省", "曲靖": "云南省",
    # 新疆维吾尔自治区
    "乌鲁木齐": "新疆维吾尔自治区", "伊犁哈萨克自治州": "新疆维吾尔自治区",
    # 甘肃省
    "张掖": "甘肃省",
    # 宁夏回族自治区
    "吴忠": "宁夏回族自治区",
    # 江西省
    "九江": "江西省", "南昌": "江西省", "萍乡": "江西省", "上饶": "江西省", "鹰潭": "江西省",
    # 海南省
    "琼海": "海南省", "海口": "海南省",
    # 贵州省
    "贵阳": "贵州省", "黔南布依族苗族自治州": "贵州省",
    # 内蒙古自治区
    "包头": "内蒙古自治区",
    # 台湾省
    "台中市": "台湾省",
    # 其他城市
    "盐城": "江苏省", "安阳": "河南省", "湖州": "浙江省",
    "东营": "山东省", "朔州": "山西省", "河源": "广东省",
    "南充": "四川省", "攀枝花": "四川省", "揭阳": "广东省", "云浮": "广东省"
}

# ===================== 页面基础配置 =====================
# 页面配置已在文件顶部设置（避免重复调用 set_page_config）

# ===================== 加载评论数据 + 数据清洗 =====================
# 使用安全读取函数，统一报告异常类型与信息
# comment_df 已由 data_loader 返回，此处只做空值保护
if comment_df is None:
    comment_df = pd.DataFrame()

# 数据清洗逻辑
if not comment_df.empty and "发布城市" in comment_df.columns:
    # 1. 删除发布城市为「未知」的数据
    comment_df = comment_df[comment_df["发布城市"] != "未知"].copy()
    # 2. 根据城市匹配省份
    def get_province(city):
        return city_province_map.get(city, "其他地区")
    comment_df["省份"] = comment_df["发布城市"].apply(get_province)
    # 过滤无匹配省份的脏数据
    comment_df = comment_df[comment_df["省份"] != "其他地区"].copy()

# ===================== 页面标题 =====================
st.title("🗺️ 舆情地域分布可视化")


if comment_df.empty or "发布城市" not in comment_df.columns:
    st.warning("缺少评论城市数据，展示热搜分类替代图表")
    city_top = all_hot_df["话题分类"].value_counts().head(10)
    fig_city_bar = px.bar(city_top.reset_index(), x="话题分类", y="count", title="热搜分类热度排行")
    st.plotly_chart(fig_city_bar)
else:
    # ---------------------- 1. 全国城市互动量TOP10柱状图 ----------------------
    st.subheader("🏙️ 全国城市互动评论TOP10")
    city_stat = comment_df["发布城市"].value_counts().reset_index()
    city_stat.columns = ["城市", "互动评论数"]
    fig_city_bar = px.bar(
        city_stat.head(10),
        x="城市", y="互动评论数", color="互动评论数",
        color_continuous_scale="Blues",
        title="城市评论数量TOP10"
    )
    fig_city_bar.update_layout(height=450)
    st.plotly_chart(fig_city_bar, use_container_width=True)

    st.divider()

    # ---------------------- 2. 完整中国省份填充色块地图 ----------------------
    st.subheader("🌍 全国省份舆情热度色块地图")

    # 定义所有中国省份
    all_provinces = [
        "北京市", "天津市", "上海市", "重庆市",
        "河北省", "山西省", "辽宁省", "吉林省", "黑龙江省",
        "江苏省", "浙江省", "安徽省", "福建省", "江西省", "山东省",
        "河南省", "湖北省", "湖南省", "广东省", "海南省",
        "四川省", "贵州省", "云南省", "陕西省", "甘肃省", "青海省",
        "西藏自治区", "内蒙古自治区", "广西壮族自治区", "宁夏回族自治区",
        "新疆维吾尔自治区", "香港特别行政区", "澳门特别行政区", "台湾省"
    ]

    # 省份中心坐标
    province_centers = {
        "北京市": [39.9, 116.4], "天津市": [39.1, 117.2], "上海市": [31.2, 121.5], "重庆市": [29.6, 106.5],
        "河北省": [38.0, 114.5], "山西省": [37.9, 112.6], "辽宁省": [41.8, 123.4], "吉林省": [43.9, 125.3],
        "黑龙江省": [45.8, 126.6], "江苏省": [33.0, 119.8], "浙江省": [29.2, 120.2], "安徽省": [31.8, 117.3],
        "福建省": [26.1, 118.3], "江西省": [27.6, 115.9], "山东省": [36.7, 117.0],
        "河南省": [33.9, 113.5], "湖北省": [30.6, 114.3], "湖南省": [27.1, 111.5], "广东省": [23.1, 113.3],
        "海南省": [19.2, 109.8], "四川省": [30.6, 102.2], "贵州省": [26.6, 106.7], "云南省": [25.0, 101.9],
        "陕西省": [35.0, 109.0], "甘肃省": [36.1, 103.8], "青海省": [35.5, 96.0],
        "西藏自治区": [32.0, 89.0], "内蒙古自治区": [44.0, 113.0], "广西壮族自治区": [23.8, 108.4],
        "宁夏回族自治区": [37.5, 106.3], "新疆维吾尔自治区": [42.0, 87.0],
        "香港特别行政区": [22.3, 114.2], "澳门特别行政区": [22.2, 113.5], "台湾省": [24.0, 121.0]
    }

    province_stat = comment_df["省份"].value_counts().reset_index()
    province_stat.columns = ["省份", "热度总和"]

    # 规范化省份名称以匹配 GeoJSON
    prov_norm_map = {
        "西藏": "西藏自治区", "青海": "青海省", "内蒙古": "内蒙古自治区",
        "新疆": "新疆维吾尔自治区", "广西": "广西壮族自治区", "宁夏": "宁夏回族自治区",
        "香港": "香港特别行政区", "澳门": "澳门特别行政区",
        "北京": "北京市", "上海": "上海市", "天津": "天津市", "重庆": "重庆市",
    }


    def normalize_prov(name):
        if not isinstance(name, str):
            return name
        name = name.strip()
        if name in prov_norm_map:
            return prov_norm_map[name]
        for suf in ["省", "市", "自治区", "特别行政区"]:
            if name.endswith(suf):
                return name
        return name + "省"


    province_stat["省份"] = province_stat["省份"].apply(normalize_prov)

    # 补全缺失省份，热度值设为0
    province_stat = province_stat.set_index("省份").reindex(all_provinces, fill_value=0).reset_index()
    province_stat.columns = ["省份", "热度总和"]

    # 色块地图
    fig_prov_map = px.choropleth_mapbox(
        province_stat,
        locations="省份",
        geojson="https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json",
        featureidkey="properties.name",
        color="热度总和",
        hover_data={"省份": True, "热度总和": True},
        mapbox_style="carto-positron",
        zoom=3,
        center={"lat": 35, "lon": 104},
        title="全国各省舆情评论热度热力图",
        color_continuous_scale="Reds"
    )

    #  使用 Scattermapbox 添加省份名称标签
    import plotly.graph_objects as go

    # 准备标签数据 - 显示所有省份
    label_data = []
    for _, row in province_stat.iterrows():
        prov = row["省份"]
        heat = row["热度总和"]
        if prov in province_centers:
            lat, lon = province_centers[prov]
            short_name = prov.replace("省", "").replace("市", "").replace("自治区", "").replace("特别行政区", "")
            label_data.append({
                "lat": lat,
                "lon": lon,
                "name": short_name,
                "heat": heat
            })

    # 添加散点标签图层
    if label_data:
        label_df = pd.DataFrame(label_data)
        fig_prov_map.add_trace(
            go.Scattermapbox(
                lat=label_df["lat"],
                lon=label_df["lon"],
                mode="text",
                text=label_df["name"],
                textfont=dict(size=12, color="#333333", family="SimHei, Microsoft YaHei, Arial Unicode MS"),
                showlegend=False,
                hoverinfo="none",
                textposition="middle center"
            )
        )

    # 注意：只对第一个trace（choropleth）设置边框
    fig_prov_map.update_traces(marker_line_width=1, selector=dict(type='choroplethmapbox'))

    fig_prov_map.update_layout(height=700)
    st.plotly_chart(fig_prov_map, use_container_width=True)
    st.divider()