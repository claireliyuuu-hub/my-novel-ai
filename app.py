import streamlit as st
import google.generativeai as genai
import json
import os
import time


genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)


st.set_page_config(
    page_title="深度文学创作引擎 PRO",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown(
"""
<style>

.stChatMessage {
font-size:13px!important;
line-height:1.8!important;
}

p,li,span,
div[data-testid="stMarkdownContainer"] {
font-size:13px!important;
line-height:1.8!important;
}

.stTextArea textarea {
font-size:14px!important;
min-height:200px!important;
}

.stButton>button{
width:100%;
}

</style>
""",
unsafe_allow_html=True
)


SAVE_FILE="novel_save.json"



def load_data():

    if os.path.exists(SAVE_FILE):

        try:

            with open(
                SAVE_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except:

            return {}

    return {}




def sync_data(state):

    data={

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




# 429保护

def safe_send_message(chat,prompt):

    for i in range(5):

        try:

            return chat.send_message(prompt)


        except Exception as e:


            if (
                "429" in str(e)
                or
                "ResourceExhausted" in str(e)
            ):

                wait=(i+1)*10

                st.warning(
                    f"请求过多，等待{wait}秒 ({i+1}/5)"
                )

                time.sleep(wait)


            else:

                raise e


    return None




data=load_data()


if "chat_history" not in st.session_state:

    st.session_state.chat_history=data.get(
        "chat_history",[]
    )

    st.session_state.ml_info=data.get(
        "ml_info",""
    )

    st.session_state.fl_info=data.get(
        "fl_info",""
    )

    st.session_state.bg_info=data.get(
        "bg_info",""
    )

    st.session_state.user_style=data.get(
        "user_style",""
    )

    st.session_state.pre_text=data.get(
        "pre_text",""
    )

    st.session_state.bible_info=data.get(
        "bible_info",""
    )




st.title("✍️ 深度文学创作引擎 PRO")



with st.sidebar:

    st.header("🛡️ 数据守护中心")


    if st.button("📥 导出备份"):

        export=json.dumps(
            st.session_state.chat_history,
            ensure_ascii=False
        )


        st.download_button(
            "下载JSON",
            export,
            "backup.json"
        )




with st.expander(
    "📚 核心档案与风格学习",
    expanded=True
):


    st.session_state.bible_info=st.text_area(
        "核心档案库:",
        st.session_state.bible_info,
        height=150
    )


    st.session_state.pre_text=st.text_area(
        "参考例文:",
        st.session_state.pre_text,
        height=200
    )


    c1,c2=st.columns(2)


    st.session_state.ml_info=c1.text_input(
        "男主:",
        st.session_state.ml_info
    )

    st.session_state.fl_info=c2.text_input(
        "女主:",
        st.session_state.fl_info
    )

    st.session_state.bg_info=c1.text_input(
        "背景:",
        st.session_state.bg_info
    )

    st.session_state.user_style=c2.text_input(
        "额外风格:",
        st.session_state.user_style
    )


    if st.button("💾 保存"):

        sync_data(
            st.session_state
        )

        st.success("保存完成")

# ===============================
# 文学系统
# ===============================


example_text = st.session_state.pre_text[-8000:]


system_prompt=f"""

你是一名顶尖小说作者。

你的任务不是解释，
而是直接输出小说正文。



【最高优先级】

用户提供的参考例文，是唯一风格标准。

必须学习：

- 句式
- 节奏
- 叙事距离
- 情绪表达
- 对白方式
- 描写密度


禁止输出普通AI文章。

禁止改变参考例文气质。



【禁止】

不要出现：

好的

以下是

根据你的要求

续写如下

这些AI套话。



必须直接进入故事。



【描写要求】

不能流水账。

必须加入：

环境氛围
光影声音气味
动作细节
微表情
心理活动
人物潜台词
对白冲突



【人物】

男主:
{st.session_state.ml_info}


女主:
{st.session_state.fl_info}


背景:
{st.session_state.bg_info}



【核心档案】

{st.session_state.bible_info}



【参考例文】

{example_text}



【额外要求】

{st.session_state.user_style}



每次正文结束追加：

【档案更新】

记录：

剧情变化
人物关系
新增设定
伏笔


"""



model=genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction=system_prompt
)





# ===============================
# 显示历史
# ===============================


for msg in st.session_state.chat_history[-10:]:

    with st.chat_message(
        "user"
        if msg["role"]=="user"
        else "assistant"
    ):

        st.markdown(
            msg["text"]
        )





# ===============================
# 输入
# ===============================


user_input=st.text_area(
    "✨ 输入剧情要求:",
    key="input_main",
    height=200
)


c1,c2,c3=st.columns(3)





# ===============================
# 创作
# ===============================


if c1.button("✨ 立即创作"):


    if user_input:


        with st.status(
            "正在分析例文并创作...",
            expanded=True
        ) as status:


            try:


                history=[

                    {
                        "role":
                        "user"
                        if x["role"]=="user"
                        else "model",

                        "parts":
                        [x["text"]]

                    }

                    for x in st.session_state.chat_history[-5:]

                ]



                chat=model.start_chat(
                    history=history
                )



                response=safe_send_message(
                    chat,
                    user_input
                )


                if response:


                    result=response.text



                    st.session_state.chat_history.append(
                        {
                        "role":"user",
                        "text":user_input
                        }
                    )


                    if "【档案更新】" in result:


                        text,update=result.split(
                            "【档案更新】",
                            1
                        )


                        st.session_state.chat_history.append(
                            {
                            "role":"model",
                            "text":text.strip()
                            }
                        )


                        st.session_state.bible_info += (
                            "\n"+update.strip()
                        )


                    else:


                        st.session_state.chat_history.append(
                            {
                            "role":"model",
                            "text":result
                            }
                        )



                    sync_data(
                        st.session_state
                    )


                    status.update(
                        label="✅ 完成",
                        state="complete"
                    )


                else:

                    st.error(
                        "没有生成内容"
                    )



            except Exception as e:

                st.error(
                    f"错误:{e}"
                )


        st.rerun()





# ===============================
# 撤回
# ===============================


if c2.button("↩️ 撤回上一段"):


    if len(st.session_state.chat_history)>=2:


        st.session_state.chat_history=(
            st.session_state.chat_history[:-2]
        )


        sync_data(
            st.session_state
        )

        st.rerun()





# ===============================
# 清空
# ===============================


if c3.button("🗑️ 清空记录"):


    if os.path.exists(SAVE_FILE):

        os.remove(SAVE_FILE)


    st.session_state.chat_history=[]

    st.session_state.bible_info=""


    st.rerun()
