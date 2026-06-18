import streamlit as st
import google.generativeai as genai

# 1. 初始化設定與金鑰
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="資深文學作家", layout="wide")

# 2. 側邊欄：設定角色人設與記憶管理
with st.sidebar:
    st.title("⚙️ 創作工作台")
    
    st.header("👤 角色設定庫")
    ml_name = st.text_input("男主角姓名：", placeholder="例如：沈墨", value="")
    ml_traits = st.text_area("男主角性格/外貌：", placeholder="例如：高冷腹黑、劍眉星目、內心深情...", height=100)
    
    st.divider()
    
    fl_name = st.text_input("女主角姓名：", placeholder="例如：蘇清微", value="")
    fl_traits = st.text_area("女主角性格/外貌：", placeholder="例如：活潑開朗、醫術高超、略帶嬌憨...", height=100)
    
    st.divider()
    
    other_chars = st.text_area("其他配角或世界觀：", placeholder="例如：反派李傲（陰險狡詐）、背景是修仙世界...", height=100)
    
    st.divider()
    
    if st.button("🗑️ 忘記情節（開新小說）", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# 3. 構造系統指令（讓 AI 記住人設）
system_prompt = f"""
你是一位資深的文學作家。請嚴格遵守以下角色人設進行創作，確保情節不崩壞：
【男主角】：{ml_name if ml_name else "未設定"}。性格背景：{ml_traits if ml_traits else "由你發揮"}
【女主角】：{fl_name if fl_name else "未設定"}。性格背景：{fl_traits if fl_traits else "由你發揮"}
【其他設定】：{other_chars if other_chars else "無"}

寫作風格：文筆優美，細節豐富，擅長環境描寫與心理刻畫。請根據使用者的指令不斷延續情節。
"""

# 初始化模型（帶入人設指令）
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=system_prompt
)

st.title("✍️ 資深文學作家 · 長篇續寫器")
st.info("💡 提示：在左側設定男女主角人設後，AI 會寫出更精準的互動哦！")

# 4. 記憶保險箱
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 5. 畫面顯示小說進度
st.subheader("📚 小說章節紀錄")
chat_container = st.container()

with chat_container:
    if not st.session_state.chat_history:
        st.write("目前還沒有情節，請在下方輸入開頭或指令。")
    else:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="💡"):
                    st.write(msg["text"])
            else:
                with st.chat_message("assistant", avatar="✍️"):
                    st.write(msg["text"])

# 6. 與 Gemini 進行記憶連動
gemini_history = []
for msg in st.session_state.chat_history:
    gemini_history.append({
        "role": "user" if msg["role"] == "user" else "model",
        "parts": [msg["text"]]
    })

chat = model.start_chat(history=gemini_history)

# 7. 輸入區
st.divider()
user_input = st.text_area("🚀 請輸入接下來的靈感或指令（例如：『請開始第一章，描寫兩人初次見面』）：", height=100)

if st.button("✨ 讓 AI 順著往下寫", type="primary"):
    if user_input.strip() != "":
        with st.spinner("AI 正在帶入人設並構思章節..."):
            try:
                response = chat.send_message(user_input)
                
                # 儲存到歷史紀錄
                st.session_state.chat_history.append({"role": "user", "text": user_input})
                st.session_state.chat_history.append({"role": "model", "text": response.text})
                
                st.rerun()
            except Exception as e:
                st.error(f"生成出錯了：{e}")
    else:
        st.warning("請先輸入指令喔！")
