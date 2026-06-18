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

# 初始化状态
if "chat_history" not in st.session_state: st.session_state.chat_history = saved_data["chat_history"]
if "ml_info" not in st.session_state: st.session_state.ml_info = saved_data["ml_info"]
if "fl_info" not in st.session_state: st.session_state.fl_info = saved_data["fl_info"]
if "bg_info" not in st.session_state: st.session_state.bg_info = saved_data["bg_info"]
if "user_style" not in st.session_state: st.session_state.user_style = saved_data["user_style"]
if "pre_text" not in st.session_state: st.session_state.pre_text = saved_data["pre_text"]

st.title("✍️ 資深文學作家 · 風格模擬器")

# 1. 📚 風格學習區
with st.expander("📚 匯入已寫好的小說（AI 會學習你的文筆）"):
    st.session_state.pre_text = st.text_area("把之前寫好的幾章內容貼在這裡：", value=st.session_state.pre_text, height=150)
    if st.button("💾 保存前文"):
        save_data({
            "chat_history": st.session_state.chat_history, 
            "ml_info": st.session_state.ml_info, 
            "fl_info": st.session_state.fl_info, 
            "bg_info": st.session_state.bg_info, 
            "user_style": st.session_state.user_style, 
            "pre_text": st.session_state.pre_text
        })
        st.success("已保存你的風格參考！")

# 2. ⚙️ 設定區
col1, col2 = st.columns(2)
with col1:
    st.session_state.ml_info = st.text_input("男主：", value=st.session_state.ml_info)
    st.session_state.fl_info = st.text_input("女主：", value=st.session_state.fl_info)
with col2:
    st.session_state.bg_info = st.text_input("背景：", value=st.session_state.bg_info)
    st.session_state.user_style = st.text_input("其他要求：", value=st.session_state.user_style)

# 系统指令
system_prompt = f"""
你是一位資深文學作家。請參考作者提供的前文，模仿其文筆與敘事節奏進行續寫。
【前文風格參考】：{st.session_state.pre_text[:5000]}
【設定】：男主-{st.session_state.ml_info}，女主-{st.session_state.fl_info}
【背景與要求】：{st.session_state.bg_info}，{st.session_state.user_style}
要求：請絕對使用简体中文，保持連貫。
"""

model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)

# 3. 📚 小說章節紀錄
st.subheader("📚 小说章节纪录")
for msg in st.session_state.chat_history:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.write(msg["text"])

# 4. 🚀 續寫輸入框（回來啦！）
user_input = st.text_area("✨ 請輸入接下來的續寫要求：", height=100)

if st.button("✨ 讓 AI 順著往下寫"):
    if user_input:
        chat = model.start_chat(history=[{"role": "user" if m["role"] == "user" else "model", "parts": [m["text"]]} for m in st.session_state.chat_history])
        response = chat.send_message(user_input)
        st.session_state.chat_history.append({"role": "user", "text": user_input})
        st.session_state.chat_history.append({"role": "model", "text": response.text})
        save_data({
            "chat_history": st.session_state.chat_history, 
            "ml_info": st.session_state.ml_info, 
            "fl_info": st.session_state.fl_info, 
            "bg_info": st.session_state.bg_info, 
            "user_style": st.session_state.user_style, 
            "pre_text": st.session_state.pre_text
        })
        st.rerun()

if st.button("🗑️ 清空所有記憶"):
    if os.path.exists(SAVE_FILE): os.remove(SAVE_FILE)
    st.session_state.chat_history = []
    st.rerun()
