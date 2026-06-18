import streamlit as st
import google.generativeai as genai
import json
import os

# --- 1. 系统配置 ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
st.set_page_config(page_title="深度小说创作引擎", layout="wide")

# 完整 CSS 注入：确保移动端阅读体验
st.markdown("""
    <style>
    .stChatMessage, .stTextArea textarea, p, li, span, div[data-testid="stMarkdownContainer"] { 
        font-size: 13px !important; 
        line-height: 1.7 !important; 
    }
    .stButton>button { width: 100%; }
    </style>
""", unsafe_allow_html=True)

SAVE_FILE = "novel_save.json"

# --- 2. 稳健的数据持久化层 ---
def load_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def sync_data(state_dict):
    data_to_save = {
        "chat_history": state_dict.get("chat_history", []),
        "ml_info": state_dict.get("ml_info", ""),
        "fl_info": state_dict.get("fl_info", ""),
        "bg_info": state_dict.get("bg_info", ""),
        "user_style": state_dict.get("user_style", ""),
        "pre_text": state_dict.get("pre_text", "")
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)

# 初始化加载
data = load_data()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = data.get("chat_history", [])
    st.session_state.ml_info = data.get("ml_info", "")
    st.session_state.fl_info = data.get("fl_info", "")
    st.session_state.bg_info = data.get("bg_info", "")
    st.session_state.user_style = data.get("user_style", "")
    st.session_state.pre_text = data.get("pre_text", "")

# --- 3. 界面交互 ---
st.title("✍️ 深度文学创作引擎")

with st.expander("📚 例文风格学习与人设配置", expanded=False):
    st.session_state.pre_text = st.text_area("贴入你的原文/例文，AI 将以此为基准进行续写：", value=st.session_state.pre_text, height=120)
    col1, col2 = st.columns(2)
    st.session_state.ml_info = col1.text_input("男主设定：", value=st.session_state.ml_info)
    st.session_state.fl_info = col2.text_input("女主设定：", value=st.session_state.fl_info)
    st.session_state.bg_info = col1.text_input("背景设定：", value=st.session_state.bg_info)
    st.session_state.user_style = col2.text_input("风格要求：", value=st.session_state.user_style)
    if st.button("💾 保存所有设置"): 
        sync_data(st.session_state)
        st.success("已保存配置到物理磁盘")

# --- 4. 创作核心逻辑 ---
system_prompt = f"""
你是一位顶尖小说家。请严格遵守以下创作法则，否则将视为创作失败：

【核心禁令】
1. 绝对禁止重复、引用或复述用户的提示词。
2. 绝对禁止使用“根据你的要求”、“以下是续写”、“我来写一段”等 AI 惯用废话。
3. 直接开始描写情节，直接进入叙事状态，就像小说书本里的文字一样。

【创作指南】
1. 风格基准：深度分析【例文风格】(见下文)，模仿其语感、节奏。
2. 细节扩写：严禁流水账。必须通过环境侧写、动作微表情、心理活动、感官细节（视觉/听觉/嗅觉）进行扩写。
3. 设定约束：男主-{st.session_state.ml_info}，女主-{st.session_state.fl_info}，背景-{st.session_state.bg_info}。

【参考例文】：{st.session_state.pre_text}
"""


model = genai.GenerativeModel('gemini-2.5-pro', system_instruction=system_prompt)

# 展示记录
for msg in st.session_state.chat_history:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["text"])

# 创作与撤回区
user_input = st.text_area("✨ 输入扩写/续写要求（例如：『写一段两人对视时的心理描写』）：", key="input_area")

c1, c2, c3 = st.columns(3)
if c1.button("✨ 立即创作"):
    if user_input:
        with st.status("正在进行深度构思...", expanded=True) as status:
            chat = model.start_chat(history=[{"role": "user" if m["role"] == "user" else "model", "parts": [m["text"]]} for m in st.session_state.chat_history])
            response = chat.send_message(user_input)
            st.session_state.chat_history.append({"role": "user", "text": user_input})
            st.session_state.chat_history.append({"role": "model", "text": response.text})
            sync_data(st.session_state)
            status.update(label="✅ 创作完成", state="complete")
        st.rerun()

if c2.button("↩️ 撤回上一段"):
    if len(st.session_state.chat_history) >= 2:
        st.session_state.chat_history = st.session_state.chat_history[:-2]
        sync_data(st.session_state)
        st.rerun()

if c3.button("🗑️ 清空所有记录"):
    if os.path.exists(SAVE_FILE): os.remove(SAVE_FILE)
    st.session_state.chat_history = []
    st.rerun()
