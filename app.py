import streamlit as st
import google.generativeai as genai
import json
import os
import time


# --- 1. 系统配置 ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(
    page_title="深度文学创作引擎",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --- 2. CSS ---
st.markdown("""
<style>

.stChatMessage {
    font-size: 13px !important;
    line-height: 1.7 !important;
}

p, li, span, div[data-testid="stMarkdownContainer"] {
    font-size: 13px !important;
    line-height: 1.7 !important;
}

.stTextArea textarea {
    font-size: 14px !important;
    min-height: 200px !important;
}

.stTextInput input {
    font-size: 13px !important;
}

.stButton>button {
    width:100%;
    border-radius:5px;
}

.stStatus {
    font-size:13px !important;
}

</style>
""", unsafe_allow_html=True)


SAVE_FILE = "novel_save.json"



# --- 3. 数据层 ---

def load_data():

    if os.path.exists(SAVE_FILE):

        try:
            with open(
                SAVE_FILE,
                "r",
                encoding="utf-8"
            ) as f:
                return json.load(f)

        except Exception as e:
            st.error(f"读取存档失败:{e}")

    return {}



def sync_data(state):

    data = {

        "chat_history":
            state.get("chat_history",[]),

        "ml_info":
            state.get("ml_info",""),

        "fl_info":
            state.get("fl_info",""),

        "bg_info":
            state.get("bg_info",""),

        "user_style":
            state.get("user_style",""),

        "pre_text":
            state.get("pre_text",""),

        "bible_info":
            state.get("bible_info","")
    }


    try:

        with open(
            SAVE_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4
            )

    except Exception as e:
        st.error(f"保存失败:{e}")



# --- 4. API 重试 ---

def safe_send_message(chat,prompt):

    for attempt in range(3):

        try:

            return chat.send_message(prompt)

        except Exception as e:

            if "ResourceExhausted" in str(e):

                st.warning(
                    f"服务器繁忙，第{attempt+1}次重试"
                )

                time.sleep(5)

            else:
                raise e


    return None





# --- 5. 初始化 ---

data = load_data()


if "chat_history" not in st.session_state:

    st.session_state.chat_history = data.get(
        "chat_history",[]
    )

    st.session_state.ml_info = data.get(
        "ml_info",""
    )

    st.session_state.fl_info = data.get(
        "fl_info",""
    )

    st.session_state.bg_info = data.get(
        "bg_info",""
    )

    st.session_state.user_style = data.get(
        "user_style",""
    )

    st.session_state.pre_text = data.get(
        "pre_text",""
    )

    st.session_state.bible_info = data.get(
        "bible_info",""
    )




# --- 6. 页面 ---

st.title("✍️ 深度文学创作引擎")



# 侧栏备份

with st.sidebar:

    st.header("🛡️ 数据守护中心")


    if st.button("📥 导出当前备份"):

        export = json.dumps(
            {
                "chat_history":
                    st.session_state.chat_history,

                "bible_info":
                    st.session_state.bible_info,

                "pre_text":
                    st.session_state.pre_text,

                "ml_info":
                    st.session_state.ml_info,

                "fl_info":
                    st.session_state.fl_info,

                "bg_info":
                    st.session_state.bg_info

            },
            ensure_ascii=False
        )


        st.download_button(
            "下载 JSON",
            export,
            "novel_backup.json"
        )






with st.expander(
    "📚 核心设定与风格配置",
    expanded=True
):


    st.session_state.bible_info = st.text_area(
        "【核心档案库】AI长期记忆:",
        value=st.session_state.bible_info,
        height=150
    )


    st.session_state.pre_text = st.text_area(
        "【参考例文】AI学习文风:",
        value=st.session_state.pre_text,
        height=150
    )


    c1,c2 = st.columns(2)


    st.session_state.ml_info = c1.text_input(
        "男主设定:",
        value=st.session_state.ml_info
    )


    st.session_state.fl_info = c2.text_input(
        "女主设定:",
        value=st.session_state.fl_info
    )


    st.session_state.bg_info = c1.text_input(
        "背景设定:",
        value=st.session_state.bg_info
    )


    st.session_state.user_style = c2.text_input(
        "风格要求:",
        value=st.session_state.user_style
    )



    if st.button("💾 保存全部设置"):

        sync_data(st.session_state)

        st.success(
            "已同步到磁盘"
        )






# --- 7. 核心文学系统提示 ---

system_prompt = f"""

你是一位顶尖小说家。

请严格遵守以下创作法则：

【核心禁令】

1.
绝对禁止重复、引用或复述用户提示词。

2.
绝对禁止出现：
“以下是续写”
“我来写一段”
“根据你的要求”
等任何AI式说明。

3.
输出必须直接进入小说正文，
像出版小说一样开始叙事。



【创作指南】

1.
风格基准：

深度分析参考例文，
模仿它的语感、节奏、句式密度、
叙事距离和情绪表达。


2.
细节扩写：

禁止流水账。

必须使用：

- 环境侧写
- 动作链条
- 微表情
- 心理活动
- 感官细节

推动剧情。


3.
人物必须符合：

男主：
{st.session_state.ml_info}

女主：
{st.session_state.fl_info}


背景：
{st.session_state.bg_info}



4.
必须遵守核心档案库。

禁止产生人物、时间线、事件矛盾。



5.
正文结束后必须追加：

【档案更新】

总结本段新增：
- 剧情事件
- 人物关系变化
- 新增伏笔
- 重要设定


【核心档案库】

{st.session_state.bible_info}



【参考例文】

{st.session_state.pre_text}



【额外风格】

{st.session_state.user_style}

"""





model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction=system_prompt
)





# --- 8. 展示 ---

for msg in st.session_state.chat_history[-10:]:

    with st.chat_message(
        "user" if msg["role"]=="user"
        else "assistant"
    ):

        st.markdown(
            msg["text"]
        )





# --- 9. 创作 ---

user_input = st.text_area(
    "✨ 下一步情节:",
    key="input_main",
    height=200
)



c1,c2,c3 = st.columns(3)



if c1.button("✨ 立即创作"):


    if user_input:


        with st.status(
            "正在进行文学创作...",
            expanded=True
        ) as status:


            try:


                history = [

                    {
                    "role":
                    "user" if m["role"]=="user"
                    else "model",

                    "parts":
                    [m["text"]]

                    }

                    for m in st.session_state.chat_history[-5:]

                ]



                chat = model.start_chat(
                    history=history
                )



                response = safe_send_message(
                    chat,
                    user_input
                )


                if response:


                    text = response.text



                    if "【档案更新】" in text:


                        body,update = text.split(
                            "【档案更新】",
                            1
                        )


                        st.session_state.chat_history.append(
                            {
                            "role":"user",
                            "text":user_input
                            }
                        )


                        st.session_state.chat_history.append(
                            {
                            "role":"model",
                            "text":body.strip()
                            }
                        )


                        st.session_state.bible_info += (
                            "\n"+update.strip()
                        )


                    else:


                        st.session_state.chat_history.append(
                            {
                            "role":"user",
                            "text":user_input
                            }
                        )

                        st.session_state.chat_history.append(
                            {
                            "role":"model",
                            "text":text
                            }
                        )


                    sync_data(
                        st.session_state
                    )


                    status.update(
                        label="✅ 创作完成",
                        state="complete"
                    )


                else:

                    st.error(
                        "生成失败"
                    )


            except Exception as e:

                st.error(
                    str(e)
                )



        st.rerun()





if c2.button("↩️ 撤回上一段"):

    if len(st.session_state.chat_history)>=2:

        st.session_state.chat_history = (
            st.session_state.chat_history[:-2]
        )

        sync_data(
            st.session_state
        )

        st.rerun()





if c3.button("🗑️ 清空"):


    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)


    st.session_state.chat_history=[]
    st.session_state.bible_info=""


    st.rerun()
