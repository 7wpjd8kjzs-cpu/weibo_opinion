import streamlit as st
import pandas as pd
import os

# 项目根目录与数据目录
if os.path.exists("/home/aistudio"):
    hot_data_folder = "/home/aistudio/data"
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    hot_data_folder = os.path.join(BASE_DIR, "微博热搜数据")

def safe_read_csv(file_path):
    """安全读取CSV，兼容所有中文编码，避免乱码报错"""
    encodings = ["utf-8-sig", "utf-8", "gbk", "gb2312"]
    for enc in encodings:
        try:
            return pd.read_csv(file_path, encoding=enc)
        except Exception:
            continue
    try:
        return pd.read_csv(file_path, engine="python")
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_all_data():
    """全局缓存加载所有热搜+评论数据，所有页面共用"""
    # 7天热搜数据
    hot_file_names = [
        "6月10日微博热搜数据.csv",
        "6月11日微博热搜数据.csv",
        "6月12日微博热搜数据.csv",
        "6月13日微博热搜数据.csv",
        "6月14日微博热搜数据.csv",
        "6月15日微博热搜数据.csv",
        "6月16日微博热搜数据.csv"
    ]
    df_hot = pd.DataFrame()
    for filename in hot_file_names:
        full_path = os.path.join(hot_data_folder, filename)
        temp = safe_read_csv(full_path)
        if temp.empty:
            continue
        # 自动补全日期列
        if "日期" not in temp.columns:
            try:
                temp["日期"] = filename.split("日")[0] + "日"
            except Exception:
                temp["日期"] = ""
        df_hot = pd.concat([df_hot, temp], ignore_index=True)

    # 评论数据
    comment_path = os.path.join(hot_data_folder, "热搜评论.csv")
    df_comment = safe_read_csv(comment_path)
    if df_comment.empty:
        df_comment = pd.DataFrame()

    # 统一热度值为数值类型，避免计算报错
    if "热度值" in df_hot.columns:
        df_hot["热度值"] = pd.to_numeric(df_hot["热度值"], errors="coerce")

    return df_hot, df_comment