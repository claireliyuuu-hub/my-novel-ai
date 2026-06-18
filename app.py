import streamlit as st
import google.generativeai as genai

# 1. 初始化設定與金鑰
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="资深文学作家", layout="wide")

# 🌟 核心修改：利用 CSS 把網頁上所有小說文字、輸入框的字體調小，完美適配手機螢幕
st.markdown(
    """
    <style>
    /* 調整小說對話框、文本區域、一般文字的字體大小 */
    .stChatMessage, .stTextArea textarea, p, li, span {
        font-size: 14px !important;  /* 您可以根據需要把 14px 改成 13px 或 12px */
    }
    /* 調整輸入框標題的字體大小 */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-size: 20px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 2. 記憶保險箱
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 3. 側邊欄：記憶管理
with st.sidebar:
    st.title("⚙️ 创作控制台")
    st.write("如果想换全新故事，请点击下方：")
    if st.button("🗑️ 清空所有故事记忆（开新书）", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

st.title("✍️ 资深文学作家 · 长篇续写器")

# 4. 頂部：故事基礎設定區（大綱設定）
st.markdown("### 🎬 故事开镜筹备区")
st.caption("在开始写作前，请先在这里定义你的世界与主角！")

col1, col2 = st.columns(2)
with col1:
    ml_info = st.text_input("👤 男主角设定：", placeholder="例如：沈墨，27岁，高冷腹黑的帝国总裁，内心深情")
    fl_info = st.text_input("💃 女主角设定：", placeholder="例如：苏清微，24岁，天才外科医生，活泼开朗略带娇憨")

with col2:
    bg_info = st.text_input("🌌 背景与前提设定：", placeholder="例如：现代豪门、隐婚、女主一开始不知道男主身份")
    user_style = st.text_input("🎯 你的特定写作要求：", placeholder="例如：多点甜宠互动、节奏要慢...")

# 5. 構造系統指令（🌟 強制 AI 必須用簡體中文輸出）
system_prompt = f"""
你是一位资深的文学作家。请严格遵守以下设定进行长篇小说创作：
【男主角】：{ml_info if ml_info else "由你发挥"}
【女主角】：{fl_info if fl_info else "由你发挥"}
【背景前提】：{bg_info if bg_info else "由你发挥"}
【写作风格与要求】：{user_style if user_style else "文笔优美，细节丰富，擅长环境描写与心理刻画"}

核心要求：
1. 请必须、绝对完全使用【简体中文（Simplified Chinese）】进行小说正文的创作，不要混杂繁体字。
2. 请根据使用者的续写指令，不断延续情节，并确保人设与背景绝对不崩溃。
"""

# 初始化模型
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=system_prompt
)

st.divider()

# 6. 畫面顯示小說進度
st.subheader("📚 小说章节纪录")
chat_container = st.container()

with chat_container:
    if not st.session_state.chat_history:
        st.info("💡 故事还没开始呢！请在上方填好设定，并在下方输入第一个指令（例如：『请开始写第一章』）来启动故事吧！")
    else:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="💡"):
                    st.write(msg["text"])
            else:
                with st.chat_message("assistant", avatar="✍️"):
                    st.write(msg["text"])

# 7. 與 Gemini 進行記憶連動
gemini_history = []
for msg in st.session_state.chat_history:
    gemini_history.append({
        "role": "user" if msg["role"] == "user" else "model",
        "parts": [msg["text"]]
    })

chat = model.start_chat(history=gemini_history)

# 8. 輸入區（靈感與續寫指令）
st.divider()
st.subheader("🚀 下一步情节指令")
user_input = st.text_area("请输入接下来想发生的剧情或要求（例如：『请开始第一章，写两人在医院初次相遇』）：", height=100)

if st.button("✨ 让 AI 顺着往下写", type="primary"):
    if user_input.strip() != "":
        with st.spinner("AI 正在翻阅大纲与前情提要，撰写新章节中..."):
            try:
                response = chat.send_message(user_input)
                
                # 储存到历史纪录
                st.session_state.chat_history.append({"role": "user", "text": user_input})
                st.session_state.chat_history.append({"role": "model", "text": response.text})
                
                st.rerun()
            except Exception as e:
                st.error(f"生成出错了：{e}")
    else:
        st.warning("请先输入指令喔！")
