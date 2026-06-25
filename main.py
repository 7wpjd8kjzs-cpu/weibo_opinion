# -*- coding: utf-8 -*-
import streamlit as st

# ===================== 全局页面配置（必须第一个 Streamlit 命令） =====================
st.set_page_config(
    page_title="微博舆情大数据可视化系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== 导入其他模块（此时 set_page_config 已执行） ==========
import sys
import os
import importlib.util

# 加载 utils（用于 load_css）
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir

spec_utils = importlib.util.spec_from_file_location(
    "utils",
    os.path.join(project_root, "utils.py")
)
utils = importlib.util.module_from_spec(spec_utils)
spec_utils.loader.exec_module(utils)
load_css = utils.load_css

# 加载全局蓝色样式（此时可以安全调用 st.markdown）
load_css("styles.css")

# ===================== 自定义侧边栏样式（蓝色调补充） =====================
st.markdown("""
<style>
/* 隐藏Streamlit默认多余元素 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
/* 侧边栏标题样式 */
.sidebar-title {
    font-size: 22px;
    font-weight: bold;
    color: #004085;  /* 改为蓝色 */
    text-align: center;
    margin-bottom: 30px;
}
</style>
""", unsafe_allow_html=True)

# ===================== 侧边栏导航区域 =====================
with st.sidebar:
    st.markdown('<p class="sidebar-title">📊 舆情分析系统</p >', unsafe_allow_html=True)
    st.divider()
    st.info("请点击上方菜单选择功能模块")

# ===================== 系统首页内容 =====================
st.title("📊 微博舆情大数据可视化综合系统")
st.divider()

st.markdown("""
### 📌 系统介绍
本系统基于7天微博热搜数据，集成**数据统计、时序分析、文本挖掘、地域分布、用户画像、智能交互**六大核心模块，
实现舆情全流程可视化分析 + AI 智能问答 + 相似内容推荐。

### 🧩 功能模块清单
1. **舆情总览驾驶舱**：核心指标、TOP热搜、百万热度占比
2. **热搜时序趋势**：每日热度走势、排名-热度预测
3. **文本语义挖掘**：词云、时间轴热词、语义聚类、桑基图、环形图
4. **地域空间可视化**：城市/省份评论热力分布
5. **用户受众画像**：兴趣雷达、互动统计
6. **智能交互模块**：知识图谱 + AI舆情问答 + 语义相似推荐

### 🚀 使用说明
1. 左侧侧边栏选择对应功能页面
2. 智能交互模块已接入**硅基流动免费大模型**，无需代理
3. 所有数据自动读取本地CSV文件，无需额外配置
""")

st.divider()
st.success("✅ 系统初始化完成，请从左侧导航进入各功能页面！")