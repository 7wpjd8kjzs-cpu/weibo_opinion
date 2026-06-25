import streamlit as st
import os


def load_css(css_file="styles.css"):
    """加载全局CSS样式，所有页面统一调用"""
    # 尝试多个路径，兼容不同文件结构
    current_dir = os.path.dirname(os.path.abspath(__file__))
    paths = [
        os.path.join(current_dir, css_file),
        os.path.join(current_dir, "..", css_file),
        os.path.join(os.getcwd(), css_file),
        css_file,
    ]

    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    css = f.read()
                st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
                return True
            except Exception as e:
                print(f"读取CSS失败 {path}: {e}")

    print(f"未找到CSS文件: {css_file}")
    return False


def create_metric_card(value, label, border_color="#4285F4", delta=None):
    """创建统一风格的指标卡片HTML，和截图完全匹配"""
    delta_html = ""
    if delta:
        delta_html = f'<span style="position:absolute;right:25px;bottom:20px;color:#28a745;font-size:22px;font-weight:bold;">{delta}</span>'

    return f"""
        <div class="metric-card" style="border-top:5px solid {border_color};">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
    """