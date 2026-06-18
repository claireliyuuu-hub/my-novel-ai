import streamlit as st
import google.generativeai as genai
import json
import os

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
st.set_page_config(page_title="资深文学作家", layout="wide")

SAVE_FILE = "novel_save.json"

def load_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return {"chat_history": [], "ml_info": "", "fl_info": "", "bg_info": "", "user_style": "", "pre_text": ""}

def save_data(data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

saved_data = load_data()

# 狀態初始化
if "chat_history" not in st.session_state: st.session_state.chat_history = saved_data["chat_history"]
if "ml_info" not in st.session_state: st.session_state.ml_info = saved_data["ml_info"]
if "fl_info" not in st.session_state: st.session_state.fl_info = saved_data["fl_info"]
if "bg_info" not in st.session_state: st.session_state.bg_info = saved_data["bg_info"]
if "user_style" not in st.session_state: st.session_state.user_style = saved_data["user_style"]
if "pre_text" not in st.session_state: st.session_state.pre_text = saved_data.get("pre_text", "")

st.title("✍️ 資深文學作家 · 風格模擬器")

# 1. 📚 風格學習區
with st.expander("📚 匯入已寫好的小說（AI 會學習你的文筆）"):
    pre_text = st.text_area("把之前寫好的幾章內容貼在這裡：", value=st.session_state.pre_text, height=200)
    if st.button("💾 確認匯入風格"):
        st.session_state.pre_text = pre_text
        save_data({"chat_history": st.session_state.chat_history, "ml_info": st.session_state.ml_info, "fl_info": st.session_state.fl_info, "bg_info": st.session_state.bg_info, "user_style": st.session_state.user_style, "pre_text": pre_text})
        st.success("已成功匯入你的文筆風格！")

# 2. ⚙️ 設定區
col1, col2 = st.columns(2)
with col1:
    ml_info = st.text_input("男主：", value=st.session_state.ml_info)
    fl_info = st.text_input("女主：", value=st.session_state.fl_info)
with col2:
    bg_info = st.text_input("背景：", value=st.session_state.bg_info)
    user_style = st.text_input("其他要求：", value=st.session_state.user_style)

# 系統指令（加上了前文參考）
system_prompt = f"""
你是一位資深文學作家。請參考作者提供的前文，模仿其文筆與敘事節奏進行續寫。
【前文風格參考】：{st.session_state.pre_text[:5000]} (只截取部分供參考)
【角色設定】：男主-{st.session_state.ml_info}，女主-{st.session_state.fl_info}
【背景與要求】：{st.session_state.bg_info}，{st.session_state.user_style}

要求：請絕對使用简体中文，文筆要與前文保持一致。
"""

model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)

# 顯示與輸入邏輯 (略，與上一版相同)
# ... (為了節省篇幅，這部分保持上一版的 chat_history 邏輯即可)
