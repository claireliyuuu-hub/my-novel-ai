import streamlit as st
import google.generativeai as genai
import json
import os
import time

# --- 1. 系统配置：保持页面参数的严谨性 ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
st.set_page_config(
    page_title="深度小说创作引擎", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. 完整 CSS 注入：确保所有界面元素尺寸统一 ---
st.markdown("""
    <style>
    /* 调整聊天气泡、提示词输入框、文档阅读区的字体大小 */
    .stChatMessage, p, li, span, div[data-testid="stMarkdownContainer"], textarea { 
        font-size: 13px !important; 
        line-height: 1.7 !important; 
    }
    /* 强制所有输入区域拥有舒适的最小高度 */
    .stTextArea textarea { 
        font-size: 14px !important; 
        min-height: 200px !important; 
    }
    /* 让按钮宽度占满所在的列，提供更好的操作触感 */
    .stButton>button { width: 100%; }
    </style>
""", unsafe_allow_html=True)

# 定义物理存储文件路径
SAVE_FILE = "novel_save.json"

# --- 3. 稳健的数据持久化层 (无缩略) ---
def load_data():
    """读取本地 JSON 文件，如果文件不存在或格式损坏，返回空字典"""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"读取存档文件出错: {e}")
            return {}
    return {}

def sync_data(state_dict):
    """将当前的 session_state 完整同步到磁盘"""
    data_to_save = {
        "chat_history": state_dict.get("chat_history", []),
        "ml_info": state_dict.get("ml_info", ""),
        "fl_info": state_dict.get("fl_info", ""),
        "bg_info": state_dict.get("bg_info", ""),
        "user_style": state_dict.get("user_style", ""),
        "pre_text": state_dict.get("pre_text", ""),
        "bible_info": state_dict.get("bible_info", "")
    }
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"写入存档文件出错: {e}")

# --- 4. 网络请求的防御性编程 (无缩略) ---
def safe_send_message(chat_session, prompt):
    """带自动重试功能的 API 请求函数"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return chat_session.send_message(prompt)
        except Exception as e:
            # 如果是资源耗尽/频率限制，等待后重试
            if "ResourceExhausted" in str(e):
                st.warning(f"服务器繁忙，正在尝试第 {attempt+1} 次自动重试...")
                time.sleep(5)
            else:
                # 其他类型的错误直接抛出，让界面显示具体的报错内容
                raise e
    return None

# --- 5. 初始化 Session State ---
data = load_data()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = data.get("chat_history", [])
    st.session_state.ml_info = data.get("ml_info", "")
    st.session_state.fl_info = data.get("fl_info", "")
    st.session_state.bg_info = data.get("bg_info", "")
    st.session_state.user_style = data.get("user_style", "")
    st.session_state.pre_text = data.get("pre_text", "")
    st.session_state.bible_info = data.get("bible_info", "")

# --- 6. 界面展示逻辑 (完整布局) ---
st.title("✍️ 深度文学创作引擎")

with st.expander("📚 核心设定与风格配置", expanded=True):
    st.session_state.bible_info = st.text_area("【核心档案库】：填入重要剧情进展、世界观设定（AI 永远记得）：", value=st.session_state.bible_info, height=150)
    st.session_state.pre_text = st.text_area("【风格例文】：贴入几段代表性文风（作为 AI 仿写标杆）：", value=st.session_state.pre_text, height=150)
    
    col1, col2 = st.columns(2)
    st.session_state.ml_info = col1.text_input("男主设定：", value=st.session_state.ml_info)
    st.session_state.fl_info = col2.text_input("女主设定：", value=st.session_state.fl_info)
    st.session_state.bg_info = col1.text_input("背景设定：", value=st.session_state.bg_info)
    st.session_state.user_style = col2.text_input("其他特殊风格要求：", value=st.session_state.user_style)
    
    if st.button("💾 手动保存所有设置"): 
        sync_data(st.session_state)
        st.success("配置已保存到物理磁盘")

# --- 7. 系统指令：严密的负面约束 ---
system_prompt = f"""
你是一位顶尖小说家。请严格遵守以下创作法则，否则视为创作失败：

【核心禁止行为】：
1. 严禁任何形式的复述、引用或照搬用户的提示词。
2. 严禁输出 AI 典型的引导废话（如“好的，为你续写如下”、“以下是续写内容”）。
3. 严禁使用总结性的叙述，必须直接切入场景描写。

【创作强制指南】：
1. 深度分析参考例文的语感与节奏，必须与其保持一致。
2. 每一个续写指令必须扩写，利用环境渲染、感官细节、微表情描写推动情节。
3. 必须遵循【核心档案库】中的事实进行创作，禁止产生剧情矛盾。

【当前的设定数据】：
- 男主设定：{st.session_state.ml_info}
- 女主设定：{st.session_state.fl_info}
- 背景设定：{st.session_state.bg_info}
- 核心档案库：{st.session_state.bible_info}
- 参考例文风格：{st.session_state.pre_text}
"""

model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)

# --- 8. 内容展示区 ---
for msg in st.session_state.chat_history[-10:]:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["text"])

# --- 9. 创作输入区 (交互体验优化) ---
user_input = st.text_area("✨ 下一步情节（直接在此输入扩写指令）：", key="input_main", height=200)

c1, c2, c3 = st.columns(3)

# 创作按钮逻辑
if c1.button("✨ 立即创作"):
    if user_input:
        with st.status("正在进行深度构思与润色...", expanded=True) as status:
            try:
                # 仅发送最近的 5 条历史，避免 Token 爆炸
                history_list = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["text"]]} for m in st.session_state.chat_history[-5:]]
                chat = model.start_chat(history=history_list)
                
                # 执行带自动重试的生成
                response = safe_send_message(chat, user_input)
                
                if response:
                    st.session_state.chat_history.append({"role": "user", "text": user_input})
                    st.session_state.chat_history.append({"role": "model", "text": response.text})
                    sync_data(st.session_state) # 强制物理同步
                    status.update(label="✅ 创作完成", state="complete")
                else:
                    st.error("连续重试后仍无法获取响应，请检查网络或稍后再试。")
            except Exception as e:
                st.error(f"运行时发生错误: {str(e)}")
        st.rerun()

# 撤回与清空逻辑
if c2.button("↩️ 撤回上一段"):
    if len(st.session_state.chat_history) >= 2:
        st.session_state.chat_history = st.session_state.chat_history[:-2]
        sync_data(st.session_state)
        st.rerun()

if c3.button("🗑️ 清空所有记录"):
    if os.path.exists(SAVE_FILE): os.remove(SAVE_FILE)
    st.session_state.chat_history = []
    st.rerun()
