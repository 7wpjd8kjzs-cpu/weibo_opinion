# 顶部路径适配，解决导入报错
# ========== 页面第一行，强制恢复np.float别名，适配sklearn硬编码 ==========
import numpy as np
# 临时补上sklearn需要的废弃别名，只补sklearn必须的这一条，不额外改int/bool
if not hasattr(np, "float"):
    np.float = np.float64
import sys
import os
current_file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_file_dir, ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

import streamlit as st
from utils import load_css
load_css("styles.css")

# 兼容旧numpy语法
import numpy as np

import pandas as pd
from streamlit_agraph import agraph, Node, Edge, Config
from sklearn.metrics.pairwise import cosine_similarity
import os
from openai import OpenAI
from dotenv import load_dotenv
# ========== 旧版0.28.1正确导入方式 ==========
from data_loader import load_all_data

# 加载环境变量密钥
load_dotenv()
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")

# 密钥校验
if not SILICONFLOW_API_KEY:
    st.error("未读取.env中的SILICONFLOW_API_KEY，请检查.env配置文件！")
    st.stop()

# 实例化客户端，把api_key、api_base写在这里
# ========== 核心改动：增加硅基base_url ==========
client = OpenAI(
    api_key=SILICONFLOW_API_KEY,
    base_url="https://api.siliconflow.cn/v1",
    timeout=60.0
)

# 读取全局数据
all_hot_df, comment_df = load_all_data()
all_hot_df = all_hot_df.copy()
comment_df = comment_df.copy()

st.title("🤖 智能交互：知识图谱 + AI舆情问答 + 语义相似热搜推荐")
st.divider()

# 1.实体知识图谱模块
st.subheader("🕸️ 热搜实体关联知识图谱")
node_list = [
    Node(id="白鹿", label="明星", size=25, color="#4285F4"),
    Node(id="热门影视剧", label="影视", size=25, color="#34A853"),
    Node(id="高考", label="教育", size=25, color="#FBBC05"),
    Node(id="世界杯", label="体育赛事", size=25, color="#EA4335"),
    Node(id="巴西", label="国家", size=25, color="#004085")
]
edge_list = [
    Edge(source="白鹿", target="热门影视剧", label="参演"),
    Edge(source="世界杯", target="巴西", label="参赛")
]
graph_config = Config(width=1200, height=600, directed=True, physics=True)
agraph(nodes=node_list, edges=edge_list, config=graph_config)
st.divider()

# 2. 硅基流动免费模型舆情问答（仅改model名称，流式逻辑不变）
st.subheader("💬 硅基流动免费大模型舆情问答助手")

# 构造热搜上下文给AI作为参考依据
def get_hot_context(df):
    total = len(df)
    top1 = df.loc[df["热度值"].idxmax()]

    cate_stat = df.groupby("话题分类").agg(
        热搜数量=("热搜话题", "count"),
        分类最高热度=("热度值", "max")
    ).sort_values("分类最高热度", ascending=False)

    # ===== 关键改动：将所有热搜标题+分类压缩成紧凑列表 =====
    # 格式："标题1(分类A)、标题2(分类B)、标题3(分类C)..."
    title_list = []
    for _, row in df.iterrows():
        title_list.append(f"{row['热搜话题']}({row['话题分类']})")
    # 只取前100条（如果数据量大），您的7天数据估计也就200-300条
    titles_str = "、".join(title_list[:100])  # 限制条数防止token爆炸

    text = f"""7天微博热搜完整数据（共{total}条）：

【热搜标题及分类列表】
{titles_str}

【分类统计】
{cate_stat.to_string()}

【热度第一】
{top1['热搜话题']}({top1['话题分类']})，热度值：{top1['热度值']}

回答规则：
1. 用户问"某关键词有几条热搜"：从【热搜标题及分类列表】中检索包含该关键词的条目，返回具体数量和标题
2. 用户问"某分类有几条热搜"：从【分类统计】中查找该分类的"热搜数量"
3. 如果找不到，回复"暂无相关数据"
4. 严禁编造数据
"""
    return text

hot_context = get_hot_context(all_hot_df)

# 多轮对话记忆缓存
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "system",
            "content": f"你是专业舆情分析师，仅允许基于提供的热搜数据回答用户问题，严禁编造不存在的数据。参考数据：{hot_context}"
        }
    ]

# 渲染历史对话
for msg in st.session_state.chat_history[1:]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_question = st.chat_input("输入舆情相关问题，例如：热度最高的热搜是什么？哪个分类热度整体最高？")
if user_question:
    st.session_state.chat_history.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.write(user_question)

    # 流式调用+异常捕获，防止超时页面崩溃
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_ans = ""
        try:
            stream = client.chat.completions.create(
                model="Qwen/Qwen2.5-7B-Instruct",
                messages=st.session_state.chat_history,
                stream=True,
                temperature=0.1
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_ans += delta
                    response_placeholder.markdown(full_ans)
        except Exception as e:
            response_placeholder.error(f"请求异常：{str(e)}，请检查API密钥或网络")
    if full_ans:
        st.session_state.chat_history.append({"role": "assistant", "content": full_ans})

st.divider()

# 硅基向量接口函数
# def get_embedding(text_list):
#     resp = client.embeddings.create(
#         model="BAAI/bge-large-zh-v1.5",
#         input=text_list
#     )
#     emb = [item.embedding for item in resp.data]
#     return np.array(emb)

def get_embedding(text_list):
    resp = client.embeddings.create(
        model="BAAI/bge-large-zh-v1.5",
        input=text_list
    )
    emb = [item.embedding for item in resp.data]
    return np.array(emb)

# 3. 语义级相似热搜推荐
st.subheader("🔗 内容相似热搜推荐")
select_hot_topic = st.selectbox("选择热搜", all_hot_df["热搜话题"].head(40))
target_row = all_hot_df[all_hot_df["热搜话题"] == select_hot_topic].iloc[0]
target_cate = target_row["话题分类"]

# 分层候选池
same_cate = all_hot_df[(all_hot_df["话题分类"] == target_cate) & (all_hot_df["热搜话题"] != select_hot_topic)]
diff_cate = all_hot_df[(all_hot_df["话题分类"] != target_cate) & (all_hot_df["热搜话题"] != select_hot_topic)]
all_candidate = pd.concat([same_cate, diff_cate], ignore_index=True)

# 批量生成向量（缓存优化，避免重复请求）
if "emb_cache" not in st.session_state:
    st.session_state.emb_cache = {}
# 重复热搜标题，强化人名、专属关键词语义权重
text_pool = (all_candidate["热搜话题"] + " " + all_candidate["热搜话题"] + "，分类：" + all_candidate["话题分类"]).tolist()
target_text = target_row["热搜话题"] + " " + target_row["热搜话题"] + "，分类：" + target_row["话题分类"]

# 向量计算
pool_emb = get_embedding(text_pool)
t_emb = get_embedding([target_text])[0]
sim = cosine_similarity([t_emb], pool_emb).flatten()

# 跨分类衰减
mask = all_candidate["话题分类"] != target_cate
sim[mask] *= 0.3

# 筛选有效数据
top_idx = sim.argsort()[-5:][::-1]
top_idx = [i for i in top_idx if sim[i] > 0.05]
while len(top_idx) < 5:
    top_idx.append(-1)

# 渲染
c1, c2, c3, c4, c5 = st.columns(5)
cols = [c1,c2,c3,c4,c5]
for idx, col in enumerate(cols):
    i = top_idx[idx]
    if i == -1:
        col.metric("相似热搜", "无匹配")
    else:
        row = all_candidate.iloc[i]
        col.metric(f"相似热搜｜{row['话题分类']}", row["热搜话题"], f"语义分:{round(sim[i],3)}")