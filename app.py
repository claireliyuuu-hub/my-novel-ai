import streamlit as st
import google.generativeai as genai
import json
import os
import time

# --- 1. 系统基础配置 ---
# 配置 Gemini API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
# 设置页面布局
st.set_page_config(page_title="终极文学创作引擎", layout="wide")

# --- 2. 完整 CSS 样式注入 (确保没有任何遗漏) ---
st.markdown("""
    <style>
    /* 调整聊天气泡内字体 */
    .stChatMessage { font-size: 13px !important; line-height: 1.7 !important; }
    /* 调整段落和列表字体 */
    p, li, span, div[data-testid="stMarkdownContainer"] { font-size: 13px !important; line-height: 1.7 !important; }
    /* 调整输入框字体及高度 */
    .stTextArea textarea { font-size: 14px !important; min-height: 200px !important; }
    /* 调整侧边栏输入框字体 */
    .stTextInput input { font-size: 13px !important; }
    /* 强制按钮样式统一 */
    .stButton>button { width: 100%; border-radius: 5px; }
    /* 调整状态栏的字体大小 */
    .stStatus { font-size: 13px !important; }
    </style>
""", unsafe_allow_html=True)

# 物理存储路径定义
SAVE_FILE = "novel_save.json"

# --- 3. 稳健的数据持久化层 (完整实现，不缩略) ---
def load_data():
    """从物理文件加载配置与历史记录"""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"加载存档文件失败: {e}")
            return {}
    return {}

def sync_data(state_dict):
    """将 session_state 中的关键数据同步到磁盘"""
    try:
        data_to_save = {
            "chat_history": state_dict.get("chat_history", []),
            "ml_info": state_dict.get("ml_info", ""),
            "fl_info": state_dict.get("fl_info", ""),
            "bg_info": state_dict.get("bg_info", ""),
            "user_style": state_dict.get("user_style", ""),
            "pre_text": state_dict.get("pre_text", ""),
            "bible_info": state_dict.get("bible_info", "")
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"物理存档保存失败: {e}")

# --- 4. 网络通信防御性编程 (处理并发限制) ---
def safe_send_message(chat_session, prompt):
    """带重试机制的 API 请求"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return chat_session.send_message(prompt)
        except Exception as e:
            # 捕获 429 频率限制异常
            if "ResourceExhausted" in str(e):
                st.warning(f"服务器繁忙，第 {attempt+1} 次重试中...")
                time.sleep(5) # 等待 5 秒
            else:
                raise e # 非频率错误直接报错
    return None

# --- 5. Session State 初始化 ---
data = load_data()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = data.get("chat_history", [])
    st.session_state.ml_info = data.get("ml_info", "")
    st.session_state.fl_info = data.get("fl_info", "")
    st.session_state.bg_info = data.get("bg_info", "")
    st.session_state.user_style = data.get("user_style", "")
    st.session_state.pre_text = data.get("pre_text", "")
    st.session_state.bible_info = data.get("bible_info", "")

# --- 6. 界面布局与交互 ---
st.title("✍️ 终极文学创作引擎")

with st.expander("📚 核心设定与风格配置", expanded=True):
    st.session_state.bible_info = st.text_area("【核心档案库】(随着剧情自动增长)：", value=st.session_state.bible_info, height=150)
    st.session_state.pre_text = st.text_area("【风格例文】(AI 仿写标杆)：", value=st.session_state.pre_text, height=150)
    
    col1, col2 = st.columns(2)
    st.session_state.ml_info = col1.text_input("男主设定：", value=st.session_state.ml_info)
    st.session_state.fl_info = col2.text_input("女主设定：", value=st.session_state.fl_info)
    st.session_state.bg_info = col1.text_input("背景设定：", value=st.session_state.bg_info)
    st.session_state.user_style = col2.text_input("额外要求：", value=st.session_state.user_style)
    
    if st.button("💾 保存所有档案与配置"):
        sync_data(st.session_state)
        st.success("配置已同步至磁盘")

# --- 7. 系统指令注入 ---
system_prompt = f"""
你是一位顶尖小说家。请遵守以下创作规范：
1. 【禁止复述】：严禁在回复中重复用户提示词，严禁出现“好的，为你续写”等废话。
2. 【直接入戏】：每一条输出必须直接从情节、动作、感官、心理或环境描写开始。
3. 【细节扩写】：严禁流水账，通过微表情、动作链条、环境气氛进行深度扩写。
4. 【档案一致性】：续写时必须符合【核心档案库】中的事实逻辑。
5. 【自动档案更新】：续写结束后，必须在末尾附带【档案更新】：标记，总结本段剧情关键信息。

【当前数据环境】：
- 男主：{st.session_state.ml_info}
- 女主：{st.session_state.fl_info}
- 背景：{st.session_state.bg_info}
- 核心档案库：{st.session_state.bible_info}
- 风格参考：{st.session_state.pre_text}
"""

model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)

# --- 8. 内容展示区 ---
for msg in st.session_state.chat_history[-10:]:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["text"])

# --- 9. 输入与操作区 ---
user_input = st.text_area("✨ 下一步情节指令：", key="input_main", height=200)

c1, c2, c3 = st.columns(3)

if c1.button("✨ 立即创作"):
    if user_input:
        with st.status("正在进行深度构思与细节扩写...", expanded=True) as status:
            try:
                # 建立聊天上下文 (仅发送最近 5 条以节省 Token)
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["text"]]} for m in st.session_state.chat_history[-5:]]
                chat = model.start_chat(history=history)
                
                # 执行请求
                response = safe_send_message(chat, user_input)
                
                if response:
                    content = response.text
                    # 捕获自动档案更新
                    if "【档案更新】" in content:
                        parts = content.split("【档案更新】", 1)
                        st.session_state.chat_history.append({"role": "user", "text": user_input})
                        st.session_state.chat_history.append({"role": "model", "text": parts[0].strip()})
                        st.session_state.bible_info += "\n" + parts[1].strip()
                    else:
                        st.session_state.chat_history.append({"role": "user", "text": user_input})
                        st.session_state.chat_history.append({"role": "model", "text": content})
                    
                    sync_data(st.session_state) # 强制物理同步
                    status.update(label="✅ 创作完成，档案已自动更新", state="complete")
                else:
                    st.error("连续重试后仍失败，请稍后再试。")
            except Exception as e:
                st.error(f"发生运行时错误: {str(e)}")
        st.rerun()

if c2.button("↩️ 撤回上一段"):
    if len(st.session_state.chat_history) >= 2:
        st.session_state.chat_history = st.session_state.chat_history[:-2]
        sync_data(st.session_state)
        st.rerun()

if c3.button("🗑️ 清空所有记录"):
    if os.path.exists(SAVE_FILE): os.remove(SAVE_FILE)
    st.session_state.chat_history = []
    st.session_state.bible_info = ""
    st.rerun()
