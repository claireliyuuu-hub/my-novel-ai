import streamlit as st
import google.generativeai as genai
import json
import os

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
st.set_page_config(page_title="资深文学作家", layout="wide")

# 1. CSS 优化：进一步调小手机端文字，增加行间距，更适合阅读
st.markdown("""
    <style>
    .stChatMessage, .stTextArea textarea, p, li, span { font-size: 13px !important; line-height: 1.6 !important; }
    .stTextInput input { font-size: 13px !important; }
    </style>
""", unsafe_allow_html=True)

SAVE_FILE = "novel_save.json"

def load_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"chat_history": [], "ml_info": "", "fl_info": "", "bg_info": "", "user_style": "", "pre_text": ""}

def save_data(data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

d = load_data()

# 初始化状态
if "chat_history" not in st.session_state: st.session_state.update(d)

# 2. 自动保存逻辑：定义一个函数，每次变动就调用
def sync_data():
    save_data({
        "chat_history": st.session_state.chat_history,
        "ml_info": st.session_state.ml_info,
        "fl_info": st.session_state.fl_info,
        "bg_info": st.session_state.bg_info,
        "user_style": st.session_state.user_style,
        "pre_text": st.session_state.pre_text
    })

st.title("✍️ 深度文学创作引擎")

# 3. 增强版前文与设置区
with st.expander("📚 例文风格学习与人设设置 (自动保存)", expanded=True):
    st.session_state.pre_text = st.text_area("请贴入你的原文/例文，AI 将分析你的文笔风格进行仿写：", value=st.session_state.pre_text, height=150)
    col1, col2 = st.columns(2)
    st.session_state.ml_info = col1.text_input("男主：", value=st.session_state.ml_info)
    st.session_state.fl_info = col2.text_input("女主：", value=st.session_state.fl_info)
    st.session_state.bg_info = col1.text_input("背景：", value=st.session_state.bg_info)
    st.session_state.user_style = col2.text_input("特殊要求：", value=st.session_state.user_style)
    if st.button("💾 手动保存设置"): sync_data()

# 4. 核心：防套路指令 (注入强力写手人格)
system_prompt = f"""
你是一位顶尖小说家。你的核心任务是根据【例文风格】续写。
【例文风格参考】：{st.session_state.pre_text[:8000]}
【人设】：男主-{st.session_state.ml_info}，女主-{st.session_state.fl_info}
【背景】：{st.session_state.bg_info}

创作规则 (严格执行)：
1. 禁止机械化套用提示词，严禁写出类似“以下是续写”的废话。
2. 必须深入描写细节：运用动作描写、微表情、环境渲染、心理活动来推动情节，禁止“流水账”。
3. 保持例文的文风、节奏感与情感深度。
4. 必须使用简体中文。
"""

model = genai.GenerativeModel('gemini-2.5-pro', system_instruction=system_prompt)

# 5. 章节展示与续写
for msg in st.session_state.chat_history:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.write(msg["text"])

user_input = st.text_area("✨ 输入扩写/续写指令：", key="input")
if st.button("✨ 立即创作"):
    if user_input:
        chat = model.start_chat(history=[{"role": "user" if m["role"] == "user" else "model", "parts": [m["text"]]} for m in st.session_state.chat_history])
        response = chat.send_message(user_input)
        st.session_state.chat_history.append({"role": "user", "text": user_input})
        st.session_state.chat_history.append({"role": "model", "text": response.text})
        sync_data() # 自动存档
        st.rerun()

if st.button("🗑️ 清空所有记录"):
    if os.path.exists(SAVE_FILE): os.remove(SAVE_FILE)
    st.session_state.chat_history = []
    st.rerun()
