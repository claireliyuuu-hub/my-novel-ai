import streamlit as st
import google.generativeai as genai
import json
import os
import time


# ===============================
# 1. 基础配置
# ===============================

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)


st.set_page_config(
    page_title="深度文学创作引擎 PRO",
    layout="wide",
    initial_sidebar_state="expanded"
)



# ===============================
# 2. CSS
# ===============================

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


.stTextInput input {
    font-size:13px!important;
}


.stButton>button {
    width:100%;
    border-radius:6px;
}


</style>
""",
unsafe_allow_html=True
)



SAVE_FILE="novel_save.json"




# ===============================
# 3. 存档系统
# ===============================


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

    save = {

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
            save,
            f,
            ensure_ascii=False,
            indent=4
        )





# ===============================
# 4. API重试
# ===============================


def safe_send_message(chat,prompt):

    for i in range(3):

        try:

            return chat.send_message(prompt)

        except Exception as e:

            if "ResourceExhausted" in str(e):

                st.warning(
                    f"服务器繁忙，重试 {i+1}/3"
                )

                time.sleep(5)

            else:

                raise e


    return None





# ===============================
# 5. 初始化
# ===============================


data=load_data()


if "chat_history" not in st.session_state:


    st.session_state.chat_history = (
        data.get("chat_history",[])
    )


    st.session_state.ml_info = (
        data.get("ml_info","")
    )


    st.session_state.fl_info = (
        data.get("fl_info","")
    )


    st.session_state.bg_info = (
        data.get("bg_info","")
    )


    st.session_state.user_style = (
        data.get("user_style","")
    )


    st.session_state.pre_text = (
        data.get("pre_text","")
    )


    st.session_state.bible_info = (
        data.get("bible_info","")
    )






# ===============================
# 6. UI
# ===============================


st.title(
    "✍️ 深度文学创作引擎 PRO"
)




with st.sidebar:


    st.header(
        "🛡️ 数据守护中心"
    )


    if st.button(
        "📥 导出备份"
    ):


        export=json.dumps(
            st.session_state.chat_history,
            ensure_ascii=False
        )


        st.download_button(
            "下载JSON",
            export,
            "novel_backup.json"
        )






with st.expander(
    "📚 核心档案与风格学习",
    expanded=True
):


    st.session_state.bible_info = st.text_area(
        "【核心档案库】长期剧情记忆:",
        st.session_state.bible_info,
        height=150
    )


    st.session_state.pre_text = st.text_area(
        "【参考例文】AI学习此文风:",
        st.session_state.pre_text,
        height=200
    )


    c1,c2=st.columns(2)


    st.session_state.ml_info=c1.text_input(
        "男主设定:",
        st.session_state.ml_info
    )


    st.session_state.fl_info=c2.text_input(
        "女主设定:",
        st.session_state.fl_info
    )


    st.session_state.bg_info=c1.text_input(
        "背景:",
        st.session_state.bg_info
    )


    st.session_state.user_style=c2.text_input(
        "额外风格要求:",
        st.session_state.user_style
    )



    if st.button(
        "💾 保存"
    ):

        sync_data(
            st.session_state
        )

        st.success(
            "保存完成"
        )





# ===============================
# 7. 核心文学系统
# ===============================


system_prompt=f"""

你是一名顶尖商业小说作者。

你的任务不是解释，
不是回答，
而是直接创作小说正文。


【最高优先级：参考例文】

用户提供的【参考例文】
是唯一最高风格标准。

你必须分析并模仿：

- 句式结构
- 语言节奏
- 叙事视角
- 情绪推进方式
- 描写密度
- 对白风格
- 人物表达习惯


禁止写成普通AI文章。

不要改变参考例文的文学气质。





【输出规则】

1.
禁止复述用户指令。

2.
禁止出现：

“好的”
“以下是”
“根据你的要求”
“续写如下”

等AI说明。


3.
必须直接进入小说场景。

输出应该像小说书页。





【描写要求】

禁止流水账。

必须通过：

- 环境氛围
- 光影声音气味
- 人物动作链
- 微表情
- 心理活动
- 对话停顿
- 潜台词

推进剧情。




【对白要求】

人物说话必须符合身份。

对白不能只是传递信息，
必须体现：

情绪、
关系、
冲突、
隐藏目的。




【人物设定】

男主：
{st.session_state.ml_info}


女主：
{st.session_state.fl_info}


背景：
{st.session_state.bg_info}



"""

# ===============================
# 8. 继续系统提示
# ===============================


system_prompt += f"""

【核心档案库】

以下内容是绝对事实：

{st.session_state.bible_info}



【用户额外风格要求】

{st.session_state.user_style}



【剧情一致性】

写作过程中：

- 不得改变已经确定的人物性格
- 不得推翻已发生事件
- 不得制造时间线矛盾
- 不得遗忘重要关系


如果发现剧情需要扩展，
优先补充合理细节，
不要修改既有事实。



【结尾档案】

每次正文结束后必须追加：

【档案更新】

记录：

1. 本段发生的重要事件
2. 人物关系变化
3. 新增设定
4. 未解决伏笔


"""


# ===============================
# 9. 使用 Gemini Pro
# ===============================


model = genai.GenerativeModel(
    "gemini-2.5-pro",
    system_instruction=system_prompt
)




# ===============================
# 10. 历史展示
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
# 11. 创作输入
# ===============================


user_input = st.text_area(
    "✨ 输入剧情要求:",
    key="input_main",
    height=200
)



c1,c2,c3=st.columns(3)




# ===============================
# 12. 生成
# ===============================


if c1.button("✨ 立即创作"):


    if user_input:


        with st.status(
            "正在分析例文风格并创作...",
            expanded=True
        ) as status:


            try:


                history=[

                    {
                    "role":
                    "user"
                    if m["role"]=="user"
                    else "model",

                    "parts":
                    [
                        m["text"]
                    ]
                    }

                    for m in st.session_state.chat_history[-10:]

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



                    if "【档案更新】" in result:


                        text,update=result.split(
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
                            "text":text.strip()
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
                            "text":result
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
                        "生成失败，请稍后再试"
                    )



            except Exception as e:

                st.error(
                    f"错误:{e}"
                )


        st.rerun()





# ===============================
# 13. 撤回
# ===============================


if c2.button("↩️ 撤回上一段"):


    if len(
        st.session_state.chat_history
    )>=2:


        st.session_state.chat_history = (
            st.session_state.chat_history[:-2]
        )


        sync_data(
            st.session_state
        )


        st.rerun()





# ===============================
# 14. 清空
# ===============================


if c3.button("🗑️ 清空记录"):


    if os.path.exists(SAVE_FILE):

        os.remove(SAVE_FILE)



    st.session_state.chat_history=[]

    st.session_state.bible_info=""


    st.rerun()
